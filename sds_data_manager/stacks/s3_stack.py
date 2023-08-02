import pathlib

from aws_cdk import Environment, RemovalPolicy, Stack
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import (
    aws_s3_deployment as s3_deploy,
)
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
        s3.Bucket(
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
        config_bucket = s3.Bucket(
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
            destination_bucket=config_bucket,
        )
