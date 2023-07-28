from aws_cdk import (
    Environment,
    Stack,
)
from constructs import Construct

from sds_data_manager.stacks import (
    step_function_stack,
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
        step_function_stack.ProcessingStepFunctionStack(
            scope, f"IMAPProcessingStepFunctionStack-{sds_id}", sds_id
        )
