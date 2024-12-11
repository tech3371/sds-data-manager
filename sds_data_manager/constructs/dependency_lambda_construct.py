"""Module containing constructs for dependency Lambda functions."""

from aws_cdk import Duration
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

from .api_gateway_construct import ApiGateway


class DependencyLambda(Construct):
    """Generic Construct with customizable runtime code."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        function_name: str,
        code: lambda_.Code,
        layers: list,
        api: ApiGateway,
        **kwargs,
    ):
        """DependencyLambda Constructor.

        Parameters
        ----------
        scope : Construct
            Parent construct.
        construct_id : str
            A unique string identifier for this construct.
        function_name : str
            The name of the Lambda function
        code : lambda_.Code
            Lambda code bundle
        rds_security_group : ec2.SecurityGroup
            RDS security group
        subnets : ec2.SubnetSelection
            RDS subnet selection.
        vpc : ec2.Vpc
            VPC into which to put the resources that require networking.
        layers : list
            List of Lambda layers cdk.cdfnOutput names
        api : ApiGateway
            The API Gateway construct
        kwargs : dict
            Keyword arguments

        """
        super().__init__(scope, construct_id, **kwargs)

        self.dependency_lambda = lambda_.Function(
            self,
            "DependencyLambda",
            function_name=function_name,
            code=code,
            handler="SDSCode.pipeline_lambdas.dependency.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            memory_size=512,
            timeout=Duration.minutes(1),
            layers=layers,
            architecture=lambda_.Architecture.ARM_64,
        )

        api.add_route(
            route="dependency",
            http_method="GET",
            lambda_function=self.dependency_lambda,
            use_path_params=True,
        )
