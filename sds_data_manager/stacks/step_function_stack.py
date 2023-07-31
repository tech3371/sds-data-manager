from pathlib import Path

from aws_cdk import (
    Duration,
    Stack,
    Environment,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_stepfunctions as sfn,
)
from aws_cdk import (
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct

from sds_data_manager.stacks import (
    lambda_stack,
)


class ProcessingStepFunctionStack(Stack):
    def __init__(self, scope: Construct, id: str, sds_id: str, env: Environment, dynamodb_table_name: str, **kwargs) -> None:
        super().__init__(scope, id, env=env, **kwargs)

        aws_managed_lambda_permissions = [
            "service-role/AWSLambdaBasicExecutionRole",
            "AmazonS3FullAccess",
            "AmazonDynamoDBFullAccess",
        ]

        lambda_code_main_folder = f"{Path(__file__).parent}/../lambda_images/"
        imap_processing_lambda = lambda_stack.LambdaWithDockerImageStack(
            scope,
            sds_id=f"ProcessingLambda-{sds_id}",
            lambda_name=f"processing-lambda-{sds_id}",
            managed_policy_names=aws_managed_lambda_permissions,
            timeout=300,
            lambda_code_folder=f"{lambda_code_main_folder}/imap_process_kickoff_lambda/",
        )

        data_checker_lambda = lambda_stack.LambdaWithDockerImageStack(
            scope,
            sds_id=f"DataCheckerLambda-{sds_id}",
            lambda_name=f"data-checker-lambda-{sds_id}",
            managed_policy_names=aws_managed_lambda_permissions,
            timeout=300,
            lambda_code_folder=f"{lambda_code_main_folder}/data_checker_lambda/",
            lambda_environment_vars={'DYNAMODB_TABLE': dynamodb_table_name}
        )

        # Create the IAM role for the Step Functions state machine
        step_function_role = iam.Role(
            self,
            "MyStateMachineRole",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            description="IAM role for the Step Functions state machine",
        )
        # Add a policy statement to the role with at least one resource
        lambda_invoke_policy_statement = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["lambda:InvokeFunction"], resources=["*"]
        )

        # Attach the policy statement to the role
        step_function_role.add_to_policy(lambda_invoke_policy_statement)

        # # Create a Lambda task for the state machine
        # # This Lambda returns status equal success if instrument is SWE or else failed.
        # tasks.LambdaInvoke(
        #     self,
        #     "LambdaTask",
        #     lambda_function=imap_processing_lambda,
        #     payload=sfn.TaskInput.from_object({"instrument": "MAG"}),
        #     output_path="$.Payload",
        # )
        # checker_task = tasks.LambdaInvoke(
        #     self,
        #     "DataCheckerTask",
        #     lambda_function=data_checker_lambda,
        #     payload=sfn.TaskInput.from_object({"instrument": "MAG"}),
        #     output_path="$.Payload",
        # )

        # failure_state = sfn.Pass(self, "FailureState")
        # success_state = sfn.Pass(self, "SuccessState")
        # # Define the state machine definition
        # data_checker = sfn.Choice(self, "Data checker?")
        # data_checker.when(
        #     sfn.Condition.number_equals("$.Payload.status_code", 204), failure_state
        # ).when(sfn.Condition.number_equals("$.Payload.status_code", 200), success_state)

        # process_status = sfn.Choice(self, "Processing status?")
        # process_status.when(
        #     sfn.Condition.string_equals("$.Payload.status", "FAILED"), failure_state
        # ).when(
        #     sfn.Condition.string_equals("$.Payload.status", "SUCCEEDED"), success_state
        # )

        # definition = checker_task.next(process_status)

        # # Create the Step Functions state machine
        # sfn.StateMachine(
        #     self,
        #     "MyStateMachine",
        #     definition=definition,
        #     timeout=Duration.minutes(5),
        #     role=step_function_role,
        # )
