from pathlib import Path

from aws_cdk import (
    Duration,
    Environment,
    Stack,
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
    def __init__(
        self,
        scope: Construct,
        id: str,
        sds_id: str,
        env: Environment,
        dynamodb_table_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, env=env, **kwargs)
        """
        This stack creates the processing step function.

        Parameters
        ----------
        scope : Construct
            The scope of the CDK construct.
        id : str
            The ID of the CDK construct.
        env : Environment
            The environment of the CDK construct. It contains account number and region.
        dynamodb_table_name : str
            The name of the DynamoDB table.
        kwargs : dict
            Other parameters.
        """

        # Get AWS managed policies to attach to lambda role.
        aws_managed_lambda_permissions = [
            "service-role/AWSLambdaBasicExecutionRole",
            "AmazonS3FullAccess",
            "AmazonDynamoDBFullAccess",
        ]

        # Set path of main folder for lambda code.
        lambda_code_main_folder = f"{Path(__file__).parent}/../lambda_images/"

        # Set processing lambda code path. This path should contain Dockerfile.
        imap_processing_lambda_code_path = (
            f"{lambda_code_main_folder}/imap_processing_lambda/"
        )
        imap_processing_lambda = lambda_stack.LambdaWithDockerImageStack(
            scope,
            sds_id=f"ProcessingLambda-{sds_id}",
            lambda_name=f"processing-lambda-{sds_id}",
            managed_policy_names=aws_managed_lambda_permissions,
            timeout=300,
            lambda_code_folder=imap_processing_lambda_code_path,
        )

        # Set data checker lambda code path. This path should contain Dockerfile.
        data_checker_lambda_code_path = (
            f"{lambda_code_main_folder}/data_checker_lambda/"
        )
        data_checker_lambda = lambda_stack.LambdaWithDockerImageStack(
            scope,
            sds_id=f"DataCheckerLambda-{sds_id}",
            lambda_name=f"data-checker-lambda-{sds_id}",
            managed_policy_names=aws_managed_lambda_permissions,
            timeout=300,
            lambda_code_folder=data_checker_lambda_code_path,
            lambda_environment_vars={"DYNAMODB_TABLE": dynamodb_table_name},
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

        # Create a Lambda task for the state machine
        # This Lambda returns status equal success if instrument is
        # SWE or else failed.
        processing_task = tasks.LambdaInvoke(
            self,
            "Decom Lambda",
            lambda_function=imap_processing_lambda.fn,
            payload=sfn.TaskInput.from_object({"instrument": "codice"}),
            output_path="$.Payload",
        )
        # This lambda check DynamoDB table for data. If data found,
        # it returns status_code 200 or else 204 for empty response.
        checker_task = tasks.LambdaInvoke(
            self,
            "DataCheckerTask Lambda",
            lambda_function=data_checker_lambda.fn,
            payload=sfn.TaskInput.from_object({"instrument": "codice"}),
            output_path="$.Payload",
        )

        # fail and success states
        success_state = sfn.Succeed(self, "SuccessState")
        empty_state = sfn.Fail(
            self, "No Data to Process", cause="No data to process", error="EmptyError"
        )
        invalid_status_state = sfn.Fail(
            self,
            "Invalid Status Code",
            cause="Invalid status code",
            error="InvalidStatusCodeError",
        )
        sfn.Fail(
            self,
            "Processing Failed",
            cause="Failed to process",
            error="FailedProcessError",
        )
        not_supported = sfn.Fail(
            self,
            "Not Supported",
            cause="Instrument not supported",
            error="NotSupportedError",
        )

        # Define the state machine definition
        # IMAP processing lambda returns status. This Choice path
        # checks status and based on status invokes fail or succes state.
        process_status = sfn.Choice(self, "Processing status?")
        process_status.when(
            sfn.Condition.string_equals("$.status", "SUCCEEDED"), success_state
        ).when(sfn.Condition.string_equals("$.status", "UNSUPPORTED"), not_supported)

        # Data checker lambda returns status code. This Choice path
        # checks status code and based on status code invokes fail or next state.
        data_checker = sfn.Choice(self, "Data Status Check?")
        data_checker.when(
            sfn.Condition.number_equals("$.status_code", 200),
            processing_task.next(process_status),
        ).when(
            sfn.Condition.number_equals("$.status_code", 204), empty_state
        ).otherwise(
            invalid_status_state
        )

        # First call data checker lambda. Based on response invoke processing lambda.
        definition = checker_task.next(data_checker)

        # Create the Step Functions state machine
        sfn.StateMachine(
            self,
            "MyStateMachine",
            definition=definition,
            timeout=Duration.minutes(5),
            role=step_function_role,
        )
