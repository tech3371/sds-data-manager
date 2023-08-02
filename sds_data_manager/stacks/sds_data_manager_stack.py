# Standard
import pathlib

# Installed
import aws_cdk as cdk
from aws_cdk import (
    Environment,
    Stack,
    aws_lambda_event_sources,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_lambda_python_alpha as lambda_alpha_,
)
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import (
    aws_secretsmanager as secrets,
)
from constructs import Construct

from sds_data_manager.stacks.s3_data_buckets_stack import S3DataBuckets

# Local
from .dynamodb_stack import DynamoDB
from .opensearch_stack import OpenSearch


class SdsDataManager(Stack):
    """Stack for Data Management."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sds_id: str,
        opensearch: OpenSearch,
        dynamodb_stack: DynamoDB,
        s3_data_bucket: S3DataBuckets,
        env: Environment,
        **kwargs,
    ) -> None:
        """SdsDataManagerStack

        Parameters
        ----------
        scope : App
        construct_id : str
        sds_id: str
        opensearch: OpenSearch
            This class depends on opensearch, which is built with opensearch_stack.py
        dynamodb_stack: DynamoDb
            This class depends on dynamodb_stack, which is built with
            opensearch_stack.py
        env : Environment
            Account and region
        """
        super().__init__(scope, construct_id, env=env, **kwargs)

        # Create policy statements
        s3_write_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:PutObject"],
            resources=[f"{s3_data_bucket.data_bucket.bucket_arn}/*"],
        )
        s3_read_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[
                f"{s3_data_bucket.data_bucket.bucket_arn}/*",
                f"{s3_data_bucket.config_bucket.bucket_arn}/*",
            ],
        )

        dynamodb_write_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["dynamodb:PutItem"],
            resources=["*"],
        )

        # Create lambdas
        indexer_lambda = lambda_alpha_.PythonFunction(
            self,
            id="IndexerLambda",
            function_name=f"file-indexer-{sds_id}",
            entry=str(
                pathlib.Path(__file__).parent.joinpath("..", "lambda_code").resolve()
            ),
            index="SDSCode/indexer.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.minutes(15),
            memory_size=1000,
            environment={
                "OS_ADMIN_USERNAME": "master-user",
                "OS_DOMAIN": opensearch.sds_metadata_domain.domain_endpoint,
                "OS_PORT": "443",
                "METADATA_INDEX": "metadata",
                "DATA_TRACKER_INDEX": "data_tracker",
                "DYNAMODB_TABLE": dynamodb_stack.table_name,
                "S3_DATA_BUCKET": s3_data_bucket.data_bucket.s3_url_for_object(),
                "S3_CONFIG_BUCKET_NAME": f"sds-config-bucket-{sds_id}",
                "SECRET_ID": opensearch.secret_name,
                "REGION": opensearch.region,
            },
        )

        indexer_lambda.add_event_source(
            aws_lambda_event_sources.S3EventSource(
                s3_data_bucket.data_bucket, events=[s3.EventType.OBJECT_CREATED]
            )
        )
        indexer_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Adding Opensearch permissions
        indexer_lambda.add_to_role_policy(opensearch.opensearch_all_http_permissions)
        # Adding s3 read permissions to get config.json
        indexer_lambda.add_to_role_policy(s3_read_policy)
        # Adding dynamodb write permissions
        indexer_lambda.add_to_role_policy(dynamodb_write_policy)

        opensearch_secret = secrets.Secret.from_secret_name_v2(
            self, "opensearch_secret", opensearch.secret_name
        )
        opensearch_secret.grant_read(grantee=indexer_lambda)

        # upload API lambda
        upload_api_lambda = lambda_alpha_.PythonFunction(
            self,
            id="UploadAPILambda",
            function_name=f"upload-api-handler-{sds_id}",
            entry=str(
                pathlib.Path(__file__).parent.joinpath("..", "lambda_code").resolve()
            ),
            index="SDSCode/upload_api.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.minutes(15),
            memory_size=1000,
            environment={
                "S3_BUCKET": s3_data_bucket.data_bucket.s3_url_for_object(),
                "S3_CONFIG_BUCKET_NAME": f"sds-config-bucket-{sds_id}",
            },
        )
        upload_api_lambda.add_to_role_policy(s3_write_policy)
        upload_api_lambda.add_to_role_policy(s3_read_policy)
        upload_api_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # query API lambda
        query_api_lambda = lambda_alpha_.PythonFunction(
            self,
            id="QueryAPILambda",
            function_name=f"query-api-handler-{sds_id}",
            entry=str(
                pathlib.Path(__file__).parent.joinpath("..", "lambda_code").resolve()
            ),
            index="SDSCode/queries.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.minutes(1),
            memory_size=1000,
            environment={
                "OS_ADMIN_USERNAME": "master-user",
                "OS_DOMAIN": opensearch.sds_metadata_domain.domain_endpoint,
                "OS_PORT": "443",
                "OS_INDEX": "metadata",
                "SECRET_ID": opensearch.secret_name,
                "REGION": env.region,
            },
        )
        query_api_lambda.add_to_role_policy(opensearch.opensearch_read_only_policy)

        opensearch_secret.grant_read(grantee=query_api_lambda)

        # download query API lambda
        download_query_api = lambda_alpha_.PythonFunction(
            self,
            id="DownloadQueryAPILambda",
            function_name=f"download-query-api-{sds_id}",
            entry=str(
                pathlib.Path(__file__).parent.joinpath("..", "lambda_code").resolve()
            ),
            index="SDSCode/download_query_api.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(60),
        )
        download_query_api.add_to_role_policy(
            opensearch.opensearch_all_http_permissions
        )
        download_query_api.add_to_role_policy(s3_read_policy)

        self.lambda_functions = {
            "upload": {"function": upload_api_lambda, "httpMethod": "POST"},
            "query": {"function": query_api_lambda, "httpMethod": "GET"},
            "download": {"function": download_query_api, "httpMethod": "GET"},
            "indexer": {"function": indexer_lambda, "httpMethod": "POST"},
        }
