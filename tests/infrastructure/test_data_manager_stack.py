from aws_cdk.assertions import Template

from sds_data_manager.sds_data_manager_stack import SdsDataManagerStack


def test_sds_data_manager_stack(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = SdsDataManagerStack(app, stack_name, sds_id)
    template = Template.from_stack(stack)

    # Test for S3 data bucket
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

    # tests for opensearch cluster
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)

    # tests for IAM
    template.resource_count_is("AWS::IAM::Policy", 7)

    # tests for lambdas
    template.resource_count_is("AWS::Lambda::Function", 7)
    template.resource_count_is("AWS::Lambda::Url", 3)

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"file-indexer-{sds_id}",
        }
    )

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"upload-api-handler-{sds_id}",
        }
    )

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"query-api-handler-{sds_id}",
        }
    )

    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"download-query-api-{sds_id}",
        }
    )
