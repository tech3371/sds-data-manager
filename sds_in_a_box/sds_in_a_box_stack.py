from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
import aws_cdk.aws_s3 as s3
import aws_cdk as cdk

class SdsInABoxStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "IMAP-SDC-DATA-BUCKET-DEVELOPMENT", versioned=True, removal_policy=cdk.RemovalPolicy.DESTROY, auto_delete_objects=True)
        
