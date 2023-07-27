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


class LambdaWithEcrImageStack(Stack):
    def __init__(
        self,
        scope: Construct,
        sds_id: str,
        ecr_repo_name: str,
        ecr_image_version: str,
        lambda_name: str,
        lambda_environment_vars: dict,
        managed_policy_names: dict,
        timeout: int = 3,
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

        # look up ecr by name
        self.ecr_repo = ecr.Repository.from_repository_name(
            self, f"lookUpEcrRepoName-{sds_id}", repository_name=ecr_repo_name
        )

        # look up ecr image with specific tag
        self.ecr_image = self.ecr_repo.repository_uri_for_tag(ecr_image_version)
        # create lambda
        lambda_code_main_folder = (
            f"{Path(__file__).parent}/../lambda_code/imap_processing/"
        )
        lambda_image = lambda_.DockerImageCode.from_image_asset(
            directory=lambda_code_main_folder,
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
