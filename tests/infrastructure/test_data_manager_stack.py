from aws_cdk.assertions import Template
import pytest
from sds_data_manager.sds_data_manager_stack import SdsDataManagerStack

@pytest.fixture()
def stack(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = SdsDataManagerStack(app, stack_name, sds_id)
    return stack

def test_s3_buckets(stack, sds_id):
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::S3::Bucket", 1)
    # Delete and update are outside of the Properties section
    template.has_resource(
        "AWS::S3::Bucket",
        {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )
    # Now test the resource properties we expect
    template.has_resource_properties(
        "AWS::S3::Bucket",
        props={
            "BucketName": f"sds-data-{sds_id}",
            "VersioningConfiguration": {"Status": "Enabled"},
            "PublicAccessBlockConfiguration": {"RestrictPublicBuckets": True},
        },
    )

def test_opensearch(stack, sds_id):
    template = Template.from_stack(stack)
    # tests for opensearch cluster
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)

    template.has_resource_properties(
        "AWS::OpenSearchService::Domain",
        {
            "DomainName": f"sdsmetadatadomain-{sds_id}",
            "EngineVersion": "OpenSearch_1.3",
            "ClusterConfig": {
                "InstanceType": "t3.small.search",
                "InstanceCount": 1
            },
            "EBSOptions": {
               "EBSEnabled": True,
               "VolumeSize": 10,
               "VolumeType": "gp2"
            },
            "NodeToNodeEncryptionOptions": {
               "Enabled": True
            },
            "EncryptionAtRestOptions": {
               "Enabled": True
            }
        }
    )

def test_iam(stack):
    template = Template.from_stack(stack)

    
    # tests for IAM
    template.resource_count_is("AWS::IAM::Policy", 7)

    template.has_resource_properties(
        "AWS::IAM::Policy",
        props={
            "Policies":[
                {
                    "PolicyDocument": {
                        "Effect": "Allow",
                        "Action": "S3:PutObject",
                        "Resource": f"{data_bucket_arn}/*"
                    }
                }
            ]
        }
    )

def test_lambdas(stack, sds_id):
    template = Template.from_stack(stack)
    # tests for lambdas
    template.resource_count_is("AWS::Lambda::Function", 7)
    template.resource_count_is("AWS::Lambda::Url", 3)

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"file-indexer-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.indexer.lambda_handler",
            "MemorySize": 1000,
            "Timeout": 15 * 60
        }
    )

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"upload-api-handler-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.upload_api.lambda_handler",
            "MemorySize": 1000,
            "Timeout": 15 * 60
        }
    )

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"query-api-handler-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.queries.lambda_handler",
            "MemorySize": 1000,
            "Timeout": 60
        }
    )

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"download-query-api-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.download_query_api.lambda_handler",
            "Timeout": 60
        }
    )