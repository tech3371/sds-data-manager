from aws_cdk import (
    Environment,
    Stack,
)
from constructs import Construct

from sds_data_manager.stacks import (
    ecr_stack,
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
        ecr_stack.EcrRepo(
            scope,
            f"ECR-{sds_id}",
            env=env,
            ecr_repo_name=f"imap_processing_ecr{sds_id}",
            ecr_tag_name="v1.0.1",
            source_code_path="sds_data_manager/ecr_image/imap_processing/",
        )

        # create batch job using above ecr image
