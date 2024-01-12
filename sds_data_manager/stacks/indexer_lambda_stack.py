# Standard
import pathlib

# Installed
import aws_cdk as cdk
from aws_cdk import (
    Stack,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_lambda_python_alpha as lambda_alpha_,
)
from aws_cdk import (
    aws_secretsmanager as secrets,
)
from constructs import Construct


class IndexerLambda(Stack):
    """Stack for indexer lambda."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env: cdk.Environment,
        db_secret_name: str,
        vpc: ec2.Vpc,
        vpc_subnets,
        rds_security_group,
        data_bucket,
        **kwargs,
    ) -> None:
        """IndexerLambda Stack

        Parameters
        ----------
        scope : Construct
            Parent construct.
        construct_id : str
            A unique string identifier for this construct.
        """
        super().__init__(scope, construct_id, env=env, **kwargs)

        indexer_lambda = lambda_alpha_.PythonFunction(
            self,
            id="IndexerLambda",
            function_name="file-indexer",
            entry=str(
                pathlib.Path(__file__).parent.joinpath("..", "lambda_code").resolve()
            ),
            index="SDSCode/indexer.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.minutes(15),
            memory_size=1000,
            allow_public_subnet=True,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=[rds_security_group],
            environment={
                "DATA_TRACKER_INDEX": "data_tracker",
                "S3_DATA_BUCKET": data_bucket.s3_url_for_object(),
                "SECRET_NAME": db_secret_name,
            },
        )

        indexer_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        rds_secret = secrets.Secret.from_secret_name_v2(
            self, "rds_secret", db_secret_name
        )
        rds_secret.grant_read(grantee=indexer_lambda)
