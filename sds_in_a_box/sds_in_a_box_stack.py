from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_iam as iam
import aws_cdk as cdk
from aws_cdk.aws_lambda_event_sources import S3EventSource, SnsEventSource
import os

class SdsInABoxStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # This is the S3 bucket where the data will be stored
        data_bucket = s3.Bucket(self, "DATA-BUCKET",
                                #bucket_name="DataBucket",
                                versioned=True,
                                removal_policy=cdk.RemovalPolicy.DESTROY,
                                auto_delete_objects=True,
                                )
        
        # This is the role that the lambdas will assume
        # We'll narrow things down later
        lambda_role = iam.Role(self, "Indexer Role", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))
        
        # The purpose of this lambda function is to trigger off of a new file entering the SDC.
        # For now, it just prints the event.  
        indexer_lambda = lambda_.Function(self,
                                          id="IndexerLambda",
                                          #function_name='file-indexer',
                                          code=lambda_.Code.from_asset(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lambdas", "file-indexer")),
                                          handler="indexer.lambda_handler",
                                          role=lambda_role,
                                          runtime=lambda_.Runtime.PYTHON_3_9,
                                          timeout=cdk.Duration.minutes(15),
                                          memory_size=1000
                                          )
        indexer_lambda.add_event_source(S3EventSource(data_bucket,
                                                      events=[s3.EventType.OBJECT_CREATED]
                                                      )
                                        )
        indexer_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
