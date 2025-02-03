"""Module containing constructs for SDC maintained Spin and Repointing files."""

from aws_cdk import Duration, Environment
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from constructs import Construct


class SDCSpinRepoint(Construct):
    """Generic Construct with customizable runtime code."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env: Environment,
        data_bucket: s3.Bucket,
        code: lambda_.Code,
        layers: list,
        **kwargs,
    ):
        """SDCSpinRepoint Constructor.

        Parameters
        ----------
        scope : Construct
            Parent construct.
        construct_id : str
            A unique string identifier for this construct.
        env : Environment
            Account and region
        data_bucket: s3.Bucket
            S3 bucket
        code : lambda_.Code
            Lambda code bundle
        layers : list
            List of Lambda layers cdk.cdfnOutput names
        kwargs : dict
            Keyword arguments

        """
        super().__init__(scope, construct_id, **kwargs)

        # Define Lambda Environment Variables
        # TODO: if we need more variables change so we can pass as input
        lambda_environment = {
            "S3_BUCKET": f"{data_bucket.bucket_name}",
            "ACCOUNT": f"{env.account}",
            "REGION": f"{env.region}",
            "SDC_SPIN_S3_PATH": "spice/sdc/spin",
            "SDC_REPOINT_S3_PATH": "spice/sdc/repoint",
        }

        self._lambda = lambda_.Function(
            self,
            "SDCSpinRepointLambda",
            function_name="SDCSpinRepoint",
            code=code,
            handler="SDSCode.spice.sdc_maintained_spin_repoint_handler.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            environment=lambda_environment,
            memory_size=512,
            timeout=Duration.minutes(1),
            allow_public_subnet=True,
            layers=layers,
            architecture=lambda_.Architecture.ARM_64,
        )

        # Permissions to send event to EventBridge
        # and submit batch job
        lambda_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["events:PutEvents"],
            resources=[
                "*",
            ],
        )
        self._lambda.add_to_role_policy(lambda_policy)

        data_bucket.grant_read_write(self._lambda)
