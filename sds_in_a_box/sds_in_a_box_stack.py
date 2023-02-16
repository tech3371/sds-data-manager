import os
import string
import random
from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    #aws_lambda_python_alpha
)
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_lambda_python_alpha as lambda_alpha_
import aws_cdk.aws_iam as iam
import aws_cdk.aws_opensearchservice as opensearch
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_cognito as cognito
from aws_cdk.aws_lambda_event_sources import S3EventSource, SnsEventSource

class SdsInABoxStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
########### INIT
        # Determines the initial configuration
        SDS_ID = self.node.try_get_context("SDSID")

########### DATA STORAGE 
        # This is the S3 bucket where the data will be stored
        data_bucket = s3.Bucket(self, "DATA-BUCKET",
                                bucket_name=f"sds-data-{SDS_ID}",
                                versioned=True,
                                removal_policy=RemovalPolicy.DESTROY,
                                auto_delete_objects=True
                                )

########### DATABASE
        # Need to make a secret username/password for OpenSearch
        os_secret = secretsmanager.Secret(self, "OpenSearchPassword")

        # Create the opensearch cluster
        sds_metadata_domain = opensearch.Domain(
            self,
            "SDSMetadataDomain",
            # Version 1.3 released 07/27/22
            version=opensearch.EngineVersion.OPENSEARCH_1_3,
            # Define the Nodes
            # Supported EC2 instance types:
            # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/supported-instance-types.html
            capacity=opensearch.CapacityConfig(
                # Single node for DEV
                data_nodes=1,
                data_node_instance_type="t3.small.search"
            ),
            # 10GB standard SSD storage, 10GB is the minimum size
            ebs=opensearch.EbsOptions(
                volume_size=10,
                volume_type=ec2.EbsDeviceVolumeType.GP2,
            ),
            # Enable logging
            logging=opensearch.LoggingOptions(
                slow_search_log_enabled=True,
                app_log_enabled=True,
                slow_index_log_enabled=True,
            ),
            # Enable encryption
            node_to_node_encryption=True,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
            # Require https connections
            enforce_https=True,
            # Destroy OS with cdk destroy
            removal_policy=RemovalPolicy.DESTROY,
            fine_grained_access_control=opensearch.AdvancedSecurityOptions(
              master_user_name="master-user",
              master_user_password=os_secret.secret_value
            )
        )

        # add an access policy for opensearch
        sds_metadata_domain.add_access_policies(
            iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            principals=[
                iam.AnyPrincipal()
            ],
            actions=["es:*"],
            resources=[sds_metadata_domain.domain_arn + "/*"]
            ))

########### LAMBDA FUNCTIONS
        
        # The purpose of this lambda function is to trigger off of a new file entering the SDC.
        indexer_lambda = lambda_alpha_.PythonFunction(self,
                                          id="IndexerLambda",
                                          function_name=f'file-indexer-{SDS_ID}',
                                          entry=os.path.join(os.path.dirname(os.path.realpath(__file__)), "SDSCode"),
                                          index = "indexer.py",
                                          handler="lambda_handler",
                                          runtime=lambda_.Runtime.PYTHON_3_9,
                                          timeout=cdk.Duration.minutes(15),
                                          memory_size=1000,
                                          environment={
                                            "OS_ADMIN_USERNAME": "master-user", 
                                            "OS_ADMIN_PASSWORD_LOCATION": os_secret.secret_value.unsafe_unwrap(),
                                            "OS_DOMAIN": sds_metadata_domain.domain_endpoint,
                                            "OS_PORT": "443",
                                            "OS_INDEX": "metadata",
                                            "S3_BUCKET": data_bucket.s3_url_for_object()}
                                          )
        indexer_lambda.add_event_source(S3EventSource(data_bucket,
                                                      events=[s3.EventType.OBJECT_CREATED]
                                                      )
                                        )
        indexer_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Adding Opensearch permissions 
        indexer_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["es:*"],
                resources=[f"{sds_metadata_domain.domain_arn}/*"],
            )
        )
        # Adding S3 Permissions 
        indexer_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=[
                    f"{data_bucket.bucket_arn}/*"
                ],
            )
        )
        
        # Adding a lambda for uploading files to the SDS
        upload_api_lambda = lambda_alpha_.PythonFunction(self,
                                      id="APILambda",
                                      function_name=f'upload-api-handler-{SDS_ID}',
                                      entry=os.path.join(os.path.dirname(os.path.realpath(__file__)), "SDSCode/"),
                                      index="upload_api.py",
                                      handler="lambda_handler",
                                      runtime=lambda_.Runtime.PYTHON_3_9,
                                      timeout=cdk.Duration.minutes(15),
                                      memory_size=1000,
                                      environment={"OS_ADMIN_USERNAME": "master-user", 
                                                   "OS_ADMIN_PASSWORD_LOCATION": os_secret.secret_name,
                                                   "S3_BUCKET": data_bucket.s3_url_for_object()},
        )
        # Adding S3 Permissions 
        upload_api_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=[
                    f"{data_bucket.bucket_arn}/*"
                ],
            )
        )
        upload_api_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        upload_api_url = upload_api_lambda.add_function_url(auth_type=lambda_.FunctionUrlAuthType.NONE,
                                              cors=lambda_.FunctionUrlCorsOptions(allowed_origins=["*"]))

        # The purpose of this lambda function is to trigger off of a lambda URL.
        query_api_lambda = lambda_alpha_.PythonFunction(self,
                                          id="QueryAPILambda",
                                          function_name=f'query-api-handler-{SDS_ID}',
                                          entry=os.path.join(os.path.dirname(os.path.realpath(__file__)), "SDSCode/"),
                                          index="queries.py",
                                          handler="lambda_handler",
                                          runtime=lambda_.Runtime.PYTHON_3_9,
                                          timeout=cdk.Duration.minutes(1),
                                          memory_size=1000,
                                          environment={
                                            "OS_ADMIN_USERNAME": "master-user", 
                                            "OS_ADMIN_PASSWORD_LOCATION": os_secret.secret_value.unsafe_unwrap(),
                                            "OS_DOMAIN": sds_metadata_domain.domain_endpoint,
                                            "OS_PORT": "443",
                                            "OS_INDEX": "metadata"
                                            }
                                          )
        query_api_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["es:*"],
                resources=[f"{sds_metadata_domain.domain_arn}/*"],
            )
        )
        # Adding S3 Permissions 
        query_api_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=[
                    f"{data_bucket.bucket_arn}/*"
                ],
            )
        )
        # add function url for lambda query API
        lambda_query_api_function_url = lambda_.FunctionUrl(self,
                                                 id="QueryAPI",
                                                 function=query_api_lambda,
                                                 auth_type=lambda_.FunctionUrlAuthType.NONE,
                                                 cors=lambda_.FunctionUrlCorsOptions(
                                                                     allowed_origins=["*"],
                                                                     allowed_methods=[lambda_.HttpMethod.GET]))
        # download query API lambda
        download_query_api = lambda_alpha_.PythonFunction(self,
            id="DownloadQueryAPILambda",
            function_name=f'download-query-api-{SDS_ID}',
            entry=os.path.join(os.path.dirname(os.path.realpath(__file__)), "SDSCode/"),
            index='download_query_api.py',
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            timeout=cdk.Duration.seconds(60)
        )
        # Adding Opensearch permissions 
        download_query_api.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["es:*"],
                resources=[f"{sds_metadata_domain.domain_arn}/*"],
            )
        )
        # Adding S3 permissions 
        download_query_api.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=[
                    f"{data_bucket.bucket_arn}/*"
                ],
            )
        )
        # Adding a function URL
        download_api_url = lambda_.FunctionUrl(self,
            id="DownloadQueryAPI",
            function=download_query_api,
            auth_type=lambda_.FunctionUrlAuthType.NONE,

            cors=lambda_.FunctionUrlCorsOptions(
                                allowed_origins=["*"],
                                allowed_methods=[lambda_.HttpMethod.GET])
        )

########### OUTPUTS
        # This is a list of the major outputs of the stack
        cdk.CfnOutput(self, "UPLOAD_API_URL", value=upload_api_url.url)
        cdk.CfnOutput(self, "QUERY_API_URL", value=lambda_query_api_function_url.url)
        cdk.CfnOutput(self, "DOWNLOAD_API_URL", value=download_api_url.url)