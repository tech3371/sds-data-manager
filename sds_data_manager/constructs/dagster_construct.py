#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import (
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_ecr as ecr,
)
from aws_cdk import (
    aws_ecs as ecs,
)
from aws_cdk import (
    aws_ecs_patterns as ecs_patterns,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_rds as rds,
)
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)
from aws_cdk.aws_ecr import Repository
from aws_cdk.aws_ecr_assets import DockerImageAsset, Platform
from cdk_ecr_deployment import DockerImageName, ECRDeployment
from constructs import Construct


class ElasticContainerRegistryStack(Stack):
    """Create the ECR to store the container images."""

    def __init__(self, scope, id, *, repo_name, untagged_image_duration, **kwargs):
        super().__init__(scope, id, **kwargs)

        repo_lifecycle_rule = ecr.LifecycleRule(
            description="Remove old untagged images",
            max_image_age=cdk.Duration.days(untagged_image_duration),
            tag_status=ecr.TagStatus.UNTAGGED,
        )

        self.repo = ecr.Repository(
            self, id, lifecycle_rules=[repo_lifecycle_rule], repository_name=repo_name
        )


class DockerImageStack(Stack):
    """Create the Docker image and push it to ECR."""

    def __init__(
        self,
        scope,
        id,
        *,
        image_name,
        directory,
        file="Dockerfile",
        ecr,
        docker_tag="latest",
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        self.asset = DockerImageAsset(
            self,
            image_name + "_image",
            directory=directory,
            file=file,
            platform=Platform.LINUX_AMD64,
        )

        self.image = ECRDeployment(
            self,
            image_name + "_copy",
            src=DockerImageName(self.asset.image_uri),
            dest=DockerImageName(ecr + ":" + docker_tag),
            memory_limit=4096,
        )


class DagsterEcsStack(Stack):
    """ECS Fargate stack running the Dagster webserver and daemon."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        env_vars: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # RDS PostgreSQL — Dagster storage backend, created in the same stack to
        # avoid cross-stack security group reference cycles.
        rds_security_group = ec2.SecurityGroup(
            self,
            "DagsterRdsSecurityGroup",
            vpc=vpc,
            description="Security group for Dagster RDS instance",
            allow_all_outbound=True,
        )

        db_secret = secretsmanager.Secret(
            self,
            "DagsterDatabaseSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username":"dagster"}',
                generate_string_key="password",
                exclude_characters='"@/\\',
            ),
        )

        db_instance = rds.DatabaseInstance(
            self,
            "DagsterStorageDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.XLARGE2
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            credentials=rds.Credentials.from_secret(db_secret),
            database_name="dagster",
            security_groups=[rds_security_group],
            removal_policy=RemovalPolicy.RETAIN,
        )

        # ECS Cluster
        cluster = ecs.Cluster(self, "DagsterCluster", vpc=vpc)

        ecs_security_group = ec2.SecurityGroup(
            self,
            "DagsterSecurityGroup",
            vpc=vpc,
            description="Security group for Dagster ECS tasks",
            allow_all_outbound=True,
        )

        # Allow ECS tasks to reach RDS on port 5432.
        rds_security_group.add_ingress_rule(
            peer=ecs_security_group,
            connection=ec2.Port.tcp(5432),
            description="Dagster ECS tasks to Dagster RDS",
        )

        # Execution role for pulling images and writing logs
        execution_role = iam.Role(
            self,
            "DagsterExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        # Task role
        task_role = iam.Role(
            self,
            "DagsterTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )
        # TODO: Terrible idea for now
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        # DAGSTER_PG_PASSWORD is injected via ECS Secrets Manager integration so it
        # never appears in plaintext. The execution role is automatically granted
        # GetSecretValue for any secrets added here.
        container_secrets = {
            "DAGSTER_PG_PASSWORD": ecs.Secret.from_secrets_manager(
                db_secret, "password"
            )
        }

        dagster_repo = Repository.from_repository_name(
            self, construct_id, repository_name="dagster-image"
        )
        ecr_image = ecs.EcrImage(dagster_repo, "latest")

        # Merge caller-supplied env vars with the RDS host resolved at synth time.
        # Copy so we can safely append DAGSTER_RUN_BASE_TASK_DEF_ARN below.
        task_env_vars = {
            **env_vars,
            "DAGSTER_PG_HOST": db_instance.db_instance_endpoint_address,
        }

        # Run task definition — used by the ECS run launcher so Dagster can spin up
        # per-run containers. Its ARN is forwarded to all services as an env var.
        run_task_def = ecs.FargateTaskDefinition(
            self,
            "DagsterRunBaseTaskDef",
            cpu=1024,
            memory_limit_mib=2048,
            execution_role=execution_role,
            task_role=task_role,
        )
        run_task_def.add_container(
            "dagster-run",  # Must match the name expected by the ECS run launcher config.
            image=ecr_image,
            environment=task_env_vars,
            secrets=container_secrets,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="DagsterRuns",
                log_group=logs.LogGroup(
                    self, "RunLogs", removal_policy=RemovalPolicy.DESTROY
                ),
            ),
        )
        task_env_vars["DAGSTER_RUN_BASE_TASK_DEF_ARN"] = (
            run_task_def.task_definition_arn
        )

        # Dagster Webserver (UI) — Application Load Balanced Fargate Service
        webserver_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "DagsterWebserver",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecr_image,
                command=[
                    "dagster-webserver",
                    "-h",
                    "0.0.0.0",
                    "-p",
                    "3000",
                    "-w",
                    "orchestration/workspace.yaml",
                ],
                container_port=3000,
                environment=task_env_vars,
                secrets=container_secrets,
                execution_role=execution_role,
                task_role=task_role,
                log_driver=ecs.LogDriver.aws_logs(
                    stream_prefix="DagsterWebserver",
                    log_group=logs.LogGroup(
                        self,
                        "WebserverLogs",
                        removal_policy=RemovalPolicy.DESTROY,
                    ),
                ),
            ),
            public_load_balancer=True,
            # Set to False for VPN/Internal access
            open_listener=False,
            security_groups=[ecs_security_group],
        )
        webserver_service.load_balancer.connections.allow_from(
            ec2.Peer.ipv4("128.138.131.0/24"),
            ec2.Port.tcp(80),
        )

        # Dagster Daemon — handles schedules, sensors, and run queue
        daemon_task_def = ecs.FargateTaskDefinition(
            self,
            "DagsterDaemonTask",
            cpu=16384,
            memory_limit_mib=32768,
            execution_role=execution_role,
            task_role=task_role,
        )
        daemon_task_def.add_container(
            "DaemonContainer",
            image=ecr_image,
            command=["dagster-daemon", "run", "-w", "orchestration/workspace.yaml"],
            environment=task_env_vars,
            secrets=container_secrets,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="DagsterDaemon",
                log_group=logs.LogGroup(
                    self, "DaemonLogs", removal_policy=RemovalPolicy.DESTROY
                ),
            ),
        )
        ecs.FargateService(
            self,
            "DagsterDaemonService",
            cluster=cluster,
            task_definition=daemon_task_def,
            desired_count=1,
            security_groups=[ecs_security_group],
        )
