import pathlib

from aws_cdk import Environment, RemovalPolicy, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deploy
from constructs import Construct


class S3DataBuckets(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        env: Environment,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        scope : Construct
        construct_id : str
        sds_id : str
            Name suffix for stack
        env : Environment
        use_custom_domain : bool, Optional
            Build API Gateway using custom domain
        """
        super().__init__(scope, construct_id, env=env, **kwargs)

        # This is the S3 bucket used by upload_api_lambda
        self.data_bucket = s3.Bucket(
            self,
            f"DataBucket-{sds_id}",
            bucket_name=f"sds-data-{sds_id}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # Confirm that a config.json file exists in the expected
        # location before S3 upload
        if (
            not pathlib.Path(__file__)
            .parent.joinpath("..", "config", "config.json")
            .resolve()
            .exists()
        ):
            raise RuntimeError(
                "sds_data_manager/config directory must contain config.json"
            )

        # S3 bucket where the configurations will be stored
        self.config_bucket = s3.Bucket(
            self,
            f"ConfigBucket-{sds_id}",
            bucket_name=f"sds-config-bucket-{sds_id}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # Upload all files in the config directory to the S3 config bucket.
        # This directory should contain a config.json file that will
        # be used for indexing files into the data bucket.
        s3_deploy.BucketDeployment(
            self,
            f"DeployConfig-{sds_id}",
            sources=[
                s3_deploy.Source.asset(
                    str(
                        pathlib.Path(__file__).parent.joinpath("..", "config").resolve()
                    )
                )
            ],
            destination_bucket=self.config_bucket,
        )

        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["cognito-idp:*"],
            resources=["*"],
        )

        s3_replication_configuration_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetReplicationConfiguration", "s3:ListBucket"],
            resources=[f"{self.data_bucket.bucket_arn}"],
        )

        s3_replication_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:GetObjectVersionForReplication",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectVersionTagging",
            ],
            resources=[f"{self.data_bucket.bucket_arn}/*"],
        )

        # Create role for backup bucket in the backup account
        backup_role = iam.Role(
            self,
            "BackupRole",
            assumed_by=iam.ServicePrincipal("s3.amazonaws.com"),
            description="Role for getting permissions to \
                        replicate out of S3 bucket in this account.",
        )

        backup_role.add_to_policy(s3_replication_configuration_policy)
        backup_role.add_to_policy(s3_replication_policy)
