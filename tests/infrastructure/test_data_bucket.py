"""Test the data bucket stack."""

import pytest
from aws_cdk.assertions import Match, Template

from sds_data_manager.stacks.data_bucket_stack import DataBucketStack


@pytest.fixture(scope="module")
def template(app, env):
    """Return a template for the data bucket stack."""
    stack = DataBucketStack(app, "data-bucket", env=env)
    template = Template.from_stack(stack)

    return template


def test_s3_bucket_resource_count(template):
    """Ensure the template has the appropriate amount of buckets."""
    template.resource_count_is("AWS::S3::Bucket", 1)


def test_custom_s3_auto_delete_resource_count(template):
    """Ensure the template has S3 auto delete enabled."""
    template.resource_count_is("Custom::S3AutoDeleteObjects", 1)


def test_s3_data_bucket_policy_resource_properties(template):
    """Ensure the template has the appropriate data bucket resource properties."""
    template.has_resource_properties(
        "AWS::S3::BucketPolicy",
        props={
            "Bucket": {"Ref": Match.string_like_regexp("DataBucket*")},
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": [
                            "s3:PutBucketPolicy",
                            "s3:GetBucket*",
                            "s3:List*",
                            "s3:DeleteObject*",
                        ],
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": {
                                "Fn::GetAtt": [
                                    Match.string_like_regexp(
                                        "CustomS3AutoDeleteObjectsCustomResourceProviderRole*"
                                    ),
                                    "Arn",
                                ]
                            }
                        },
                        "Resource": [
                            {
                                "Fn::GetAtt": [
                                    Match.string_like_regexp("DataBucket*"),
                                    "Arn",
                                ]
                            },
                            {
                                "Fn::Join": [
                                    "",
                                    [
                                        {
                                            "Fn::GetAtt": [
                                                Match.string_like_regexp("DataBucket*"),
                                                "Arn",
                                            ]
                                        },
                                        "/*",
                                    ],
                                ]
                            },
                        ],
                    }
                ],
            },
        },
    )


def test_s3_bucket_policy_resource_count(template):
    """Ensure that the template has the appropriate bucket policy."""
    template.resource_count_is("AWS::S3::BucketPolicy", 1)


def test_s3_role(template):
    """Ensure that the template has the appropriate IAM role."""
    template.has_resource_properties("AWS::IAM::Role", props={"RoleName": "BackupRole"})


def test_data_bucket_custom_s3_auto_delete_resource_properties(template):
    """Ensure that the template has custom s3 auto delete resource properties."""
    template.has_resource_properties(
        "Custom::S3AutoDeleteObjects",
        {
            "ServiceToken": {
                "Fn::GetAtt": [
                    Match.string_like_regexp(
                        "CustomS3AutoDeleteObjectsCustomResourceProviderHandler*"
                    ),
                    "Arn",
                ]
            },
            "BucketName": {"Ref": Match.string_like_regexp("DataBucket*")},
        },
    )
