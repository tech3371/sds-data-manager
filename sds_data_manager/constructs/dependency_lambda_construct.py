"""Module containing constructs for dependency Lambda functions."""

from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class DependencyLambda(Construct):
    """Generic Construct with customizable runtime code."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        function_name: str,
        code: lambda_.Code,
        rds_security_group: ec2.SecurityGroup,
        subnets: ec2.SubnetSelection,
        vpc: ec2.Vpc,
        layers: list,
        batch_start_lambda: lambda_.Function,
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
        batch_start_lambda : lambda_.Function
            The BatchStarterLambda function
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

        # Add a resource-based policy to the dependency Lambda
        # This ensures that the BatchStarterLambda has explicit
        # permission to invoke this lambda.
        self.dependency_lambda.add_permission(
            "AllowBatchStarterInvoke",
            principal=iam.ServicePrincipal("lambda.amazonaws.com"),  # Invoker's service
            action="lambda:InvokeFunction",
            source_arn=batch_start_lambda.function_arn,
        )
