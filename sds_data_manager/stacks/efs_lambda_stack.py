from aws_cdk import (
    Duration,
    Fn,
    Stack,
    aws_iam,
    aws_lambda,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_efs as efs,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_events_targets as targets,
)
from aws_cdk import (
    aws_s3 as s3,
)
from constructs import Construct


class EFSWriteLambda(Stack):
    """
    Creates some Lambdas that write to the EFS file system.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        data_bucket: s3.Bucket,
        efs: efs.FileSystem,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a role for the EFS Lambda
        # Grant the Lambda identity role access to the VPC/EFS
        iam_role_name = "efs-lambda-role"
        efs_lambda_role = aws_iam.Role(
            self,
            iam_role_name,
            role_name=iam_role_name,
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonElasticFileSystemFullAccess"
                ),
            ],
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Create a security group that allows network access to mount the EFS
        self.efs_spice_ingest_sg = ec2.SecurityGroup(
            self,
            "LambdaEFSSecurityGroup",
            vpc=vpc,
            description="Allow calls to internet",
            allow_all_outbound=True,
            security_group_name="LambdaEFSSecurityGroup",
        )

        # NOTE: Workaround to overcome EFS circular dependency when mounting
        # a filesystem
        # https://github.com/aws/aws-cdk/issues/18759
        spice_access_point_id = Fn.import_value(efs.spice_access_point_id_name)

        # This access point is used by other resources to read from EFS
        lambda_mount_path = "/mnt/spice"
        lambda_efs_access = aws_lambda.FileSystem(
            arn=f"arn:aws:elasticfilesystem:{self.region}:{self.account}:access-point/{spice_access_point_id}",
            local_mount_path=lambda_mount_path,
        )

        lambda_code = aws_lambda.Code.from_asset(
            "sds_data_manager/lambda_code/efs_lambda"
        )

        self.efs_spice_ingest_lambda = aws_lambda.Function(
            self,
            "EFSWriteLambda",
            function_name="efs-write-lambda",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code=lambda_code,
            handler="lambda_function.lambda_handler",
            role=efs_lambda_role,
            description="Lambda that write data to the EFS",
            # Access to the EFS requires to be within the VPC
            vpc=vpc,
            # Mount EFS access point to /mnt/data within the lambda
            filesystem=lambda_efs_access,
            timeout=Duration.minutes(1),
            # Allow access to the EFS over NFS port
            security_groups=[self.efs_spice_ingest_sg],
            architecture=aws_lambda.Architecture.ARM_64,
            environment={
                "EFS_MOUNT_PATH": lambda_mount_path,
            },
        )

        # Trigger lambda on all s3 object creations through
        # eventbridge

        # Define an EventBridge rule
        event_rule = events.Rule(
            self,
            "EfsWriteLambdaS3EventRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [data_bucket.bucket_name]},
                    "object": {
                        "key": [
                            {"prefix": "imap/spice/imap"},
                            {"suffix": "ah.a"},
                            {"suffix": ".bsp"},
                        ]
                    },
                },
            ),
        )

        # Add the Lambda function as the target for the rule
        event_rule.add_target(targets.LambdaFunction(self.efs_spice_ingest_lambda))
