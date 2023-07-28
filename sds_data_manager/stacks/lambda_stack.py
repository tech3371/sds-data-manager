from pathlib import Path

from aws_cdk import (
    Duration,
    Stack,
)
from aws_cdk import (
    aws_ecr as ecr,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from constructs import Construct


class LambdaWithDockerImageStack(Stack):
    def __init__(
        self,
        scope: Construct,
        sds_id: str,
        lambda_name: str,
        managed_policy_names: dict,
        timeout: int = 3,
        lambda_code_folder: str,
        lambda_environment_vars: dict = {},
        **kwargs,
    ):
        super().__init__(scope, sds_id, **kwargs)

        # This stack creates Lambda that runs from an ECR image

        # create role, add permissions
        iam_role_name = f"{lambda_name}-role"
        self.execution_role = iam.Role(
            self,
            iam_role_name,
            role_name=iam_role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        for policy in managed_policy_names:
            self.execution_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name(policy)
            )

        # create lambda image
        lambda_image = lambda_.DockerImageCode.from_image_asset(
            directory=lambda_code_folder,
            build_args={"--platform": "linux/amd64"},
        )
        self.fn = lambda_.DockerImageFunction(
            self,
            lambda_name,
            function_name=lambda_name,
            code=lambda_image,
            role=self.execution_role,
            timeout=Duration.seconds(timeout),
            environment=lambda_environment_vars,
            architecture=lambda_.Architecture.ARM_64,
        )
