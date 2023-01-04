import os
import string
import random
from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    # aws_sqs as sqs,
)
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_iam as iam
import aws_cdk.aws_opensearchservice as opensearch
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_cognito as cognito
from aws_cdk import aws_apigatewayv2 as apigatewayv2
from aws_cdk.aws_lambda_event_sources import S3EventSource, SnsEventSource

class SdsInABoxStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, random_letters=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if not random_letters:
            random_letters="".join( [random.choice(string.ascii_lowercase) for i in range(8)] )

        # This is the S3 bucket where the data will be stored
        data_bucket = s3.Bucket(self, "DATA-BUCKET",
                                #TODO: bucket_name=f"DataBucket-{random_letters}",
                                versioned=True,
                                removal_policy=RemovalPolicy.DESTROY,
                                auto_delete_objects=True
                                )

        # Need to make a secret username/password for OpenSearch
        os_secret = secretsmanager.Secret(self, "OpenSearchPassword")

        #Create the opensearch 
        sds_metadata_domain = opensearch.Domain(
            self,
            "SDSMetadataDomain",
            # Version 1.2 released 04/22, Version 1.3 released 07/27/22
            version=opensearch.EngineVersion.OPENSEARCH_1_3,
            # Define the Nodes
            # Supported EC2 instance types:
            # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/supported-instance-types.html
            capacity=opensearch.CapacityConfig(
                # Single node for DEV
                data_nodes=1,
                #data_node_instance_type="m5.large.search",
                data_node_instance_type="t3.small.search"
            ),
            # 10GB standard SSD storage, 10GB is the minimum size
            ebs=opensearch.EbsOptions(
                # As of 07/22/22 GP3 not available in us-west-2 Guidence from docs
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

        # This is the role that the lambdas will assume
        # We'll narrow things down later
        lambda_role = iam.Role(self, "Indexer Role", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))
        
        # The purpose of this lambda function is to trigger off of a new file entering the SDC.
        # For now, it just prints the event.  
        indexer_lambda = lambda_.Function(self,
                                          id="IndexerLambda",
                                          function_name=f'file-indexer-{random_letters}',
                                          code=lambda_.Code.from_asset(os.path.join(os.path.dirname(os.path.realpath(__file__)), "SDSCode")),
                                          handler="indexer.lambda_handler",
                                          role=lambda_role,
                                          runtime=lambda_.Runtime.PYTHON_3_9,
                                          timeout=cdk.Duration.minutes(15),
                                          memory_size=1000,
                                          environment={"OS_ADMIN_USERNAME": "master-user", "OS_ADMIN_PASSWORD_LOCATION": os_secret.secret_name}
                                          )

        indexer_lambda.add_event_source(S3EventSource(data_bucket,
                                                      events=[s3.EventType.OBJECT_CREATED]
                                                      )
                                        )
        indexer_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Create the Cognito UserPool
        userpool = cognito.UserPool(self,
                                    id='TeamUserPool',
                                    account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
                                    auto_verify=cognito.AutoVerifiedAttrs(email=True),
                                    standard_attributes=cognito.
                                    StandardAttributes(email=cognito.StandardAttribute(required=True)),
                                    sign_in_aliases=cognito.SignInAliases(username=False, email=True),
                                    removal_policy=cdk.RemovalPolicy.DESTROY
                                    )

        # Add a client sign in for the userpool
        command_line_client = cognito.UserPoolClient(user_pool=userpool, scope=self, id='sdc-command-line',
                                                     id_token_validity=cdk.Duration.minutes(60),
                                                     access_token_validity=cdk.Duration.minutes(60),
                                                     refresh_token_validity=cdk.Duration.minutes(60),
                                                     auth_flows=cognito.AuthFlow(admin_user_password=True,
                                                                                 user_password=True,
                                                                                 user_srp=True,
                                                                                 custom=True),
                                                     prevent_user_existence_errors=True)
        
        # Add a random unique domain name 
        # Users will be able to reset their passwords at https://sds-login-{random_letters}.auth.us-west-2.amazoncognito.com/login?client_id={}&redirect_uri=https://example.com&response_type=code
        userpooldomain = userpool.add_domain(id="TeamLoginCognitoDomain",
                                             cognito_domain=cognito.CognitoDomainOptions(domain_prefix=f"sds-login-{random_letters}"))

        # Adding a lambda that doesn't do much to act as the endpoints to the APIs
        ### NOTE: Deployment of these lambdas depends entirely on 
        layer = lambda_.LayerVersion(self, "SDSDependencies",
                                    code=lambda_.Code.from_asset("/home/vscode/.local/lib/python3.9/site-packages"),
                                    description="A layer that contains all dependencies needed for the lambda functions"
                                )

        api_lambda = lambda_.Function(self,
                                      id="APILambda",
                                      function_name=f'api-handler-{random_letters}',
                                      code=lambda_.Code.from_asset(os.path.join(os.path.dirname(os.path.realpath(__file__)), "SDSCode")),
                                      handler="api.lambda_handler",
                                      role=lambda_role,
                                      runtime=lambda_.Runtime.PYTHON_3_9,
                                      timeout=cdk.Duration.minutes(15),
                                      memory_size=1000,
                                      layers=[layer],
                                      environment={"OS_ADMIN_USERNAME": "master-user", "OS_ADMIN_PASSWORD_LOCATION": os_secret.secret_name,
                                                   "COGNITO_USERPOOL_ID": userpool.user_pool_id, "COGNITO_APP_ID": command_line_client.user_pool_client_id}
        )
        
        api_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        api_url = api_lambda.add_function_url(auth_type=lambda_.FunctionUrlAuthType.NONE,
                                              cors=lambda_.FunctionUrlCorsOptions(allowed_origins=["*"])
        )

        '''
        # Adding in the bare-bones API Gateway authorizors and endpoitns
        httpapi = apigatewayv2.CfnApi(self, "SDSTeamAPI",
                                      name=f"SDS-API-{random_letters}",
                                      protocol_type='HTTP'
                                     )

          
        JWTAuthorizer = apigatewayv2.CfnAuthorizer(self, "APIAuthorizer",
                                                   name=f"SDSCognitoAuthorizer-{random_letters}",
                                                   api_id=httpapi.ref,
                                                   authorizer_type="JWT",
                                                   identity_source=["$request.header.Authorization"],
                                                   jwt_configuration=apigatewayv2.CfnAuthorizer.JWTConfigurationProperty(
                                                   audience=[command_line_client.user_pool_client_id],
                                                   issuer=f"https://cognito-idp.us-west-2.amazonaws.com/{userpool.user_pool_id}"
                                                  )
        )

        #httpapioverrides = apigatewayv2.CfnApiGatewayManagedOverrides(self, "HTTPAPIOverrides",
        #                                                              api_id = httpapi.ref,
        #                                                              route=apigatewayv2.CfnApiGatewayManagedOverrides.RouteOverridesProperty(
        #                                                                authorization_type="JWT",
        #                                                                authorizer_id=JWTAuthorizer.ref
        #                                                              )
        #)

        api_integration = apigatewayv2.CfnIntegration(self, "APILambdaIntegration",
                                                      api_id=httpapi.ref,
                                                      integration_type='AWS_PROXY',
                                                      integration_method="GET",
                                                      integration_uri=api_lambda.function_arn,
                                                      payload_format_version="2.0"
        )

        api_route = apigatewayv2.CfnRoute(self, "APIRoutes",
                                          api_id=httpapi.ref,
                                          route_key="GET /query",
        #                                  authorization_type='JWT',
        #                                  authorizer_id=JWTAuthorizer.ref,
                                          target="integrations/"+api_integration.ref       
        )
        '''
