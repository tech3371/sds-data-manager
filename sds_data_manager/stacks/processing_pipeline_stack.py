from aws_cdk import (
    Environment,
    Stack,
)
from constructs import Construct

from sds_data_manager.stacks import (
    ecr_stack,
    lambda_stack,
)


class ProcessingPipelineStack(Stack):
    """Stack for processing pipeline."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        env: Environment,
        **kwargs,
    ) -> None:
        """ProcessingPipelineStack

        Parameters
        ----------
        scope : App
        construct_id : str
        sds_id: str
        env : Environment
            Account and region
        """
        super().__init__(scope, construct_id, env=env, **kwargs)
        # create ECR
        ecr_repo_name = f"imap_processing_ecr-{sds_id}"
        ecr_image_version = "v1.0.1"

        ecr_stack.EcrRepo(
            scope,
            f"ECR-{sds_id}",
            env=env,
            ecr_repo_name=ecr_repo_name,
            ecr_tag_name=ecr_image_version,
            source_code_path="sds_data_manager/ecr_image/imap_processing/",
        )

        aws_managed_lambda_permissions = [
            "service-role/AWSLambdaBasicExecutionRole",
            "AmazonS3FullAccess",
            "AmazonDynamoDBFullAccess",
        ]
        lambda_stack.LambdaWithEcrImageStack(
            scope,
            sds_id=f"LambdaWithEcrImageStack-{sds_id}",
            ecr_repo_name=ecr_repo_name,
            ecr_image_version=ecr_image_version,
            lambda_name=f"IMAP-processing-lambda-{sds_id}",
            managed_policy_names=aws_managed_lambda_permissions,
            timeout=300,
        )
