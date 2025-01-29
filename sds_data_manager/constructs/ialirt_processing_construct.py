"""Configure the i-alirt processing stack.

This is the module containing the general stack to be built for computation of
I-ALiRT algorithms. It was built using best practices as shown here:

https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/networking-inbound.html
https://aws.amazon.com/elasticloadbalancing/features/#Product_comparisons
"""

from aws_cdk import CfnOutput, Duration, RemovalPolicy
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class IalirtProcessing(Construct):
    """A processing system for I-ALiRT."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        ports: list[int],
        ialirt_bucket: s3.Bucket,
        secret_name: str,
        **kwargs,
    ) -> None:
        """Construct the i-alirt processing stack.

        Parameters
        ----------
        scope : Construct
            Parent construct.
        construct_id : str
            A unique string identifier for this construct.
        vpc : ec2.Vpc
            VPC into which to put the resources that require networking.
        ports : list[int]
            List of ports to listen on for incoming traffic and used by container.
        ialirt_bucket: s3.Bucket
            S3 bucket
        secret_name : str,
            Database secret_name for Secrets Manager
        kwargs : dict
            Keyword arguments

        """
        super().__init__(scope, construct_id, **kwargs)

        self.ports = ports
        self.vpc = vpc
        self.s3_bucket_name = ialirt_bucket.bucket_name
        self.secret_name = secret_name

        # Add a security group in which network load balancer will reside
        self.create_load_balancer_security_group()

        # Create security group in which containers will reside
        self.create_ecs_security_group()

        # Add an ecs service and cluster for each container
        self.add_compute_resources()
        # Add load balancer for each container
        self.add_load_balancer()
        # Add autoscaling for each container
        self.add_autoscaling()

    def create_ecs_security_group(self):
        """Create and return a security group for containers."""
        self.ecs_security_group = ec2.SecurityGroup(
            self,
            "IalirtEcsSecurityGroup",
            vpc=self.vpc,
            description="Security group for Ialirt",
            allow_all_outbound=True,
        )

        # Only allow traffic from the NLB security group
        for port in self.ports:
            self.ecs_security_group.add_ingress_rule(
                peer=ec2.Peer.security_group_id(
                    self.load_balancer_security_group.security_group_id
                ),
                connection=ec2.Port.tcp(port),
                description=f"Allow inbound traffic from the NLB on TCP port {port}",
            )

    def create_load_balancer_security_group(self):
        """Create and return a security group for load balancers."""
        # Create a security group for the NLB
        self.load_balancer_security_group = ec2.SecurityGroup(
            self,
            "NLBSecurityGroup",
            vpc=self.vpc,
            description="Security group for the Ialirt NLB",
        )

        # Allow inbound and outbound traffic from a specific port and IP.
        # IPs: LASP IP, BlueNet (tlm relay)
        ip_ranges = ["128.138.131.0/24", "198.118.1.14/32"]
        for port in self.ports:
            for ip_range in ip_ranges:
                self.load_balancer_security_group.add_ingress_rule(
                    # TODO: allow IP addresses from partners
                    peer=ec2.Peer.ipv4(ip_range),
                    connection=ec2.Port.tcp(port),
                    description=f"Allow inbound traffic on TCP port {port}",
                )

                # Allow outbound traffic.
                self.load_balancer_security_group.add_egress_rule(
                    peer=ec2.Peer.ipv4(ip_range),
                    connection=ec2.Port.tcp(port),
                    description=f"Allow outbound traffic on TCP port {port}",
                )

    def add_compute_resources(self):
        """Add ECS compute resources for a container."""
        # ECS Cluster manages EC2 instances on which containers are deployed.
        self.ecs_cluster = ecs.Cluster(self, "IalirtCluster", vpc=self.vpc)

        # Retrieve the secret from Secrets Manager.
        nexus_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "NexusCredentials", secret_name=self.secret_name
        )

        # Add IAM role and policy for S3 access
        task_role = iam.Role(
            self,
            "IalirtTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:PutObject",
                    "secretsmanager:GetSecretValue",
                ],
                resources=[
                    f"arn:aws:s3:::{self.s3_bucket_name}",
                    f"arn:aws:s3:::{self.s3_bucket_name}/*",
                    nexus_secret.secret_arn,
                ],
            )
        )

        # Required for pulling images from Nexus.
        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/private-auth.html
        execution_role = iam.Role(
            self,
            "IalirtTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy",
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "SecretsManagerReadWrite"
                ),
            ],
        )

        # Grant Secrets Manager access for Nexus credentials.
        execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[nexus_secret.secret_arn],
            )
        )

        # Specifies the networking mode as AWS_VPC.
        # ECS tasks in AWS_VPC mode can be registered with
        # Network Load Balancers (NLB).
        task_definition = ecs.Ec2TaskDefinition(
            self,
            "IalirtTaskDef",
            network_mode=ecs.NetworkMode.AWS_VPC,
            task_role=task_role,
            execution_role=execution_role,
        )

        # Adds a container to the ECS task definition
        # Logging is configured to use AWS CloudWatch Logs.
        container = task_definition.add_container(
            "IalirtContainer",
            image=ecs.ContainerImage.from_registry(
                "lasp-registry.colorado.edu/ialirt/ialirt:latest",
                credentials=nexus_secret,
            ),
            # Allowable values:
            # https://docs.aws.amazon.com/cdk/api/v2/docs/
            # aws-cdk-lib.aws_ecs.TaskDefinition.html#cpu
            memory_limit_mib=512,
            cpu=256,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="Ialirt"),
            environment={"S3_BUCKET": self.s3_bucket_name},
            # Ensure the ECS task is running in privileged mode,
            # which allows the container to use FUSE.
            privileged=True,
        )

        # Map ports to container
        # NLB needs to know which port on the EC2 instances
        # it should forward the traffic to
        for port in self.ports:
            port_mapping = ecs.PortMapping(
                container_port=port,
                host_port=port,
                protocol=ecs.Protocol.TCP,
            )
            container.add_port_mappings(port_mapping)

        # ECS Service is a configuration that
        # ensures application can run and maintain
        # instances of a task definition.
        self.ecs_service = ecs.Ec2Service(
            self,
            "IalirtService",
            cluster=self.ecs_cluster,
            task_definition=task_definition,
            security_groups=[self.ecs_security_group],
            desired_count=1,
            health_check_grace_period=Duration.seconds(3600),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )

    def add_autoscaling(self):
        """Add autoscaling resources."""
        # This auto-scaling group is used to manage the
        # number of instances in the ECS cluster. If an instance
        # becomes unhealthy, the auto-scaling group will replace it.
        auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "AutoScalingGroup",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE
            ),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            vpc=self.vpc,
            desired_capacity=2,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,
                availability_zones=["us-west-2b", "us-west-2c"],
            ),
        )

        auto_scaling_group.apply_removal_policy(RemovalPolicy.DESTROY)

        # Attach the AmazonSSMManagedInstanceCore policy for SSM access
        auto_scaling_group.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # integrates ECS with EC2 Auto Scaling Groups
        # to manage the scaling and provisioning of the underlying
        # EC2 instances based on the requirements of ECS tasks
        capacity_provider = ecs.AsgCapacityProvider(
            self,
            "AsgCapacityProvider",
            auto_scaling_group=auto_scaling_group,
            enable_managed_termination_protection=False,
            enable_managed_scaling=False,
        )

        self.ecs_cluster.add_asg_capacity_provider(capacity_provider)

        # Allow inbound traffic from the Network Load Balancer
        # to the security groups associated with the EC2 instances
        # within the Auto Scaling Group.
        for port in self.ports:
            auto_scaling_group.connections.allow_from(
                self.load_balancer, ec2.Port.tcp(port)
            )

    def add_load_balancer(self):
        """Add a load balancer for a container."""
        # Create the Network Load Balancer and
        # place it in a public subnet.
        selected_subnets = ec2.SubnetSelection(
            availability_zones=["us-west-2b", "us-west-2c"],
            subnet_type=ec2.SubnetType.PUBLIC,
        )

        self.load_balancer = elbv2.NetworkLoadBalancer(
            self,
            "IalirtNLB",
            vpc=self.vpc,
            security_groups=[self.load_balancer_security_group],
            internet_facing=True,
            vpc_subnets=selected_subnets,
            cross_zone_enabled=True,
        )

        # Create a listener for each port specified
        for port in self.ports:
            listener = self.load_balancer.add_listener(
                f"Listener{port}",
                port=port,
                protocol=elbv2.Protocol.TCP,
            )

            # Modify the listener attributes to set the TCP idle timeout
            # Use node.default_child to get access to the L1 construct
            # and modify its properties.
            # https://docs.aws.amazon.com/cdk/v2/guide/cfn_layer.html
            cfn_listener = listener.node.default_child
            cfn_listener.add_property_override(
                "ListenerAttributes",
                [
                    {
                        "Key": "tcp.idle_timeout.seconds",
                        "Value": str(6000),
                    }
                ],
            )

            # Register the ECS service as a target for the listener
            listener.add_targets(
                f"Target{port}",
                port=port,
                # Specifies the container and port to route traffic to.
                targets=[
                    self.ecs_service.load_balancer_target(
                        container_name="IalirtContainer",
                        container_port=port,
                    )
                ],
                # Configures health checks for the target group
                # to ensure traffic is routed only to healthy ECS tasks.
                # Port 7568 is a dummy port used by IOIS to check the
                # health of the container.
                health_check=elbv2.HealthCheck(
                    enabled=True,
                    port=str(7568),
                    protocol=elbv2.Protocol.TCP,
                    interval=Duration.seconds(60),
                    timeout=Duration.seconds(30),
                    unhealthy_threshold_count=5,
                    healthy_threshold_count=5,
                ),
            )

            # This simply prints the DNS name of the
            # load balancer in the terminal.
            CfnOutput(
                self,
                f"LoadBalancerDNS{port}",
                value=f"http://{self.load_balancer.load_balancer_dns_name}:{port}",
            )
