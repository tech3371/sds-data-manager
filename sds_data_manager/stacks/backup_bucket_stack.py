from aws_cdk import (
    Environment,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_s3 as s3,
)
from constructs import Construct


class BackupBucket(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        env: Environment,
        source_account: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)

        # This is the S3 bucket used by upload_api_lambda
        backup_bucket = s3.Bucket(
            self,
            f"DataBucket-{sds_id}",
            bucket_name=f"sds-data-{sds_id}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"{backup_bucket.bucket_arn}/*"],
        )

        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"{backup_bucket.bucket_arn}/*"],
        )

        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["cognito-idp:*"],
            resources=["*"],
        )

        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:ReplicateObject", "s3:ReplicateDelete"],
            principals=[
                iam.ArnPrincipal(
                    f"arn:aws:iam::{source_account}:role/service-role/BackupRole"
                )
            ],
            resources=[f"{backup_bucket.bucket_arn}/*"],
        )
