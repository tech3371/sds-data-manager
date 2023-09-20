from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam,
    aws_lambda,
    Duration,
    Fn,
    Stack,
)
from constructs import Construct


class EFSWriteLambda(Stack):
    """
    Creates some Lambdas that write to the EFS file system.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        vpc: ec2.Vpc,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a role for the EFS Lambda
        # Grant the Lambda identity role access to the VPC/EFS
        iam_role_name = f"efs-lambda-role-{sds_id}"
        efs_lambda_role = aws_iam.Role(
            self,
            iam_role_name,
            role_name=iam_role_name,
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonElasticFileSystemClientReadWriteAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonElasticFileSystemFullAccess"
                ),

            ],
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Create a security group that allows network access to mount the EFS
        self.efs_list_runs_lambda_sg = ec2.SecurityGroup(
            self,
            f"LambdaEFSSecurityGroup-{sds_id}",
            vpc=vpc,
            description="Allow calls to internet",
            allow_all_outbound=True,
            security_group_name="LambdaEFSSecurityGroup",
        )

        # NOTE: Workaround to overcome EFS circular dependency when mounting a filesystem
        # https://github.com/aws/aws-cdk/issues/18759
        efs_access_point_id = Fn.import_value(f"efs-access-pt-id-{sds_id}")
        lambda_efs_access = aws_lambda.FileSystem(
            arn=f"arn:aws:elasticfilesystem:{self.region}:{self.account}:access-point/{efs_access_point_id}",
            local_mount_path="/mnt/data",
        )

        lambda_code = aws_lambda.Code.from_asset("sds_data_manager/lambda_code/efs_lambda")

        boto3_layer_arn = f"arn:aws:lambda:{self.region}:770693421928:layer:Klayers-p311-boto3:2"
        layers = [aws_lambda.LayerVersion.from_layer_version_arn(self, id='boto3dependencylayer',
                                                              layer_version_arn=boto3_layer_arn)]


        self.efs_list_runs_lambda = aws_lambda.Function(
            self,
            f"EFSWriteLambda-{sds_id}",
            function_name=f"efs-lambda-{sds_id}",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code=lambda_code,
            handler="lambda_function.lambda_handler",
            role=efs_lambda_role,
            description="Lambda that uses the EFS",
            # Access to the EFS requires to be within the VPC
            vpc=vpc,
            # Mount EFS access point to /mnt/data within the lambda
            filesystem=lambda_efs_access,
            timeout=Duration.minutes(1),
            # Allow access to the EFS over NFS port
            security_groups=[self.efs_list_runs_lambda_sg],
            layers=layers,
            architecture=aws_lambda.Architecture.ARM_64
        )
