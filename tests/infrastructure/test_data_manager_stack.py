from aws_cdk.assertions import Template

from sds_data_manager.sds_data_manager_stack import SdsDataManagerStack


def test_sds_data_manager_stack(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = SdsDataManagerStack(app, stack_name, sds_id)
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::S3::Bucket", 2)
    # Delete and update are outside of the Properties section
    template.has_resource(
        "AWS::S3::Bucket",
        {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )
    # Now test the sds-data bucket has the resource properties we expect
    template.has_resource_properties(
        "AWS::S3::Bucket",
        props={
            "BucketName": f"sds-data-{sds_id}",
            "VersioningConfiguration": {"Status": "Enabled"},
            "PublicAccessBlockConfiguration": {"RestrictPublicBuckets": True},
        },
    )
    # Now test the sds-config bucket has the resource properties we expect
    template.has_resource_properties(
        "AWS::S3::Bucket",
        props={
            "BucketName": f"sds-config-{sds_id}",
            "VersioningConfiguration": {"Status": "Enabled"},
            "PublicAccessBlockConfiguration": {"RestrictPublicBuckets": True},
        },
    )
