import pytest
from aws_cdk.assertions import Template
from aws_cdk.assertions import Match

from sds_data_manager.sds_data_manager_stack import SdsDataManagerStack


@pytest.fixture()
def stack(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = SdsDataManagerStack(app, stack_name, sds_id)
    return stack


def test_s3_buckets(stack, sds_id):
    template = Template.from_stack(stack)
    # test s3 bucket resource count
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


def test_s3_bucket_policy(stack, sds_id):
    template = Template.from_stack(stack)
    # test s3 bucket policy resource count
    template.resource_count_is("AWS::S3::BucketPolicy", 1)

    # Now test the resource properties we expect
    template.has_resource_properties(
        "AWS::S3::BucketPolicy",
        props={
            "Bucket": {"Ref": Match.string_like_regexp("DATABUCKET*")},
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": ["s3:GetBucket*", "s3:List*", "s3:DeleteObject*"],
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
                                    Match.string_like_regexp("DATABUCKET*"),
                                    "Arn",
                                ]
                            },
                            {
                                "Fn::Join": [
                                    "",
                                    [
                                        {
                                            "Fn::GetAtt": [
                                                Match.string_like_regexp("DATABUCKET*"),
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


def test_opensearch(stack, sds_id):
    template = Template.from_stack(stack)
    # test opensearch domain count
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)
    # test opensearch domain properties
    template.has_resource_properties(
        "AWS::OpenSearchService::Domain",
        {
            "DomainName": f"sdsmetadatadomain-{sds_id}",
            "EngineVersion": "OpenSearch_1.3",
            "ClusterConfig": {"InstanceType": "t3.small.search", "InstanceCount": 1},
            "EBSOptions": {"EBSEnabled": True, "VolumeSize": 10, "VolumeType": "gp2"},
            "NodeToNodeEncryptionOptions": {"Enabled": True},
            "EncryptionAtRestOptions": {"Enabled": True},
        },
    )


def test_custom_resources(stack, sds_id):
    template = Template.from_stack(stack)

    # test custom resources count
    template.resource_count_is("Custom::S3AutoDeleteObjects", 1)
    template.resource_count_is("Custom::S3BucketNotifications", 1)

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
            "BucketName": {"Ref": Match.string_like_regexp("DATABUCKET*")},
        },
    )

    template.has_resource_properties(
        "Custom::S3BucketNotifications",
        {
            "ServiceToken": {
                "Fn::GetAtt": [
                    Match.string_like_regexp("BucketNotificationsHandler*"),
                    "Arn",
                ]
            },
            "BucketName": {"Ref": Match.string_like_regexp("DATABUCKET*")},
            "NotificationConfiguration": {
                "LambdaFunctionConfigurations": [
                    {
                        "Events": ["s3:ObjectCreated:*"],
                        "LambdaFunctionArn": {
                            "Fn::GetAtt": [Match.string_like_regexp("IndexerLambda*"), "Arn"]
                        },
                    }
                ]
            },
            "Managed": True,
        },
    )


def test_aim_roles(stack, sds_id):
    template = Template.from_stack(stack)
    # test IAM role count
    template.resource_count_is("AWS::IAM::Role", 7)


def test_iam_policies(stack, sds_id):
    template = Template.from_stack(stack)
    # test IAM policy count
    template.resource_count_is("AWS::IAM::Policy", 7)
    # test IAM role count
    template.resource_count_is("AWS::IAM::Role", 7)

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "s3:PutObject",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [
                                    {
                                        "Fn::GetAtt": [
                                            Match.string_like_regexp("DATABUCKET*"),
                                            "Arn",
                                        ]
                                    },
                                    "/*",
                                ],
                            ]
                        },
                    },
                ],
            },
            "PolicyName": Match.string_like_regexp(
                "UploadAPILambdaServiceRoleDefaultPolicy*"
            ),
        },
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "logs:PutResourcePolicy",
                        "Resource": "*",
                    },
                    {
                        "Effect": "Allow",
                        "Action": "logs:DeleteResourcePolicy",
                        "Resource": "*",
                    },
                ],
            },
        },
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "es:UpdateDomainConfig",
                        "Resource": {
                            "Fn::GetAtt": [
                                Match.string_like_regexp("SDSMetadataDomain*"),
                                "Arn",
                            ]
                        },
                    }
                ],
            },
            "PolicyName": Match.string_like_regexp(
                "SDSMetadataDomainAccessPolicyCustomResourcePolicy*"
            ),
        },
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "es:ESHttp*",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [
                                    {
                                        "Fn::GetAtt": [
                                            Match.string_like_regexp(
                                                "SDSMetadataDomain*"
                                            ),
                                            "Arn",
                                        ]
                                    },
                                    "/*",
                                ],
                            ]
                        },
                    }
                ],
            },
            "PolicyName": Match.string_like_regexp(
                "IndexerLambdaServiceRoleDefaultPolicy*"
            ),
        },
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "s3:PutBucketNotification",
                        "Resource": "*",
                    }
                ],
            },
            "PolicyName": Match.string_like_regexp("BucketNotificationsHandler*"),
        },
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "es:ESHttpGet",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [
                                    {
                                        "Fn::GetAtt": [
                                            Match.string_like_regexp(
                                                "SDSMetadataDomain*"
                                            ),
                                            "Arn",
                                        ]
                                    },
                                    "/*",
                                ],
                            ]
                        },
                    }
                ],
            },
            "PolicyName": Match.string_like_regexp(
                "QueryAPILambdaServiceRoleDefaultPolicy*"
            ),
        },
    )

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "es:ESHttp*",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [
                                    {
                                        "Fn::GetAtt": [
                                            Match.string_like_regexp(
                                                "SDSMetadataDomain*"
                                            ),
                                            "Arn",
                                        ]
                                    },
                                    "/*",
                                ],
                            ]
                        },
                    },
                    {
                        "Effect": "Allow",
                        "Action": "s3:GetObject",
                        "Resource": {
                            "Fn::Join": [
                                "",
                                [
                                    {
                                        "Fn::GetAtt": [
                                            Match.string_like_regexp("DATABUCKET*"),
                                            "Arn",
                                        ]
                                    },
                                    "/*",
                                ],
                            ]
                        },
                    },
                ],
            },
            "PolicyName": Match.string_like_regexp(
                "DownloadQueryAPILambdaServiceRoleDefaultPolicy*"
            ),
        },
    )


def test_lambdas(stack, sds_id):
    template = Template.from_stack(stack)
    # tests for lambdas
    # 4 lambda function files, but there are 7 lambda
    # function resources. The other three lambdas are:
    # - CustomS3AutoDeletion lambda function
    # - AWS lambda function?
    # - Bucket Notification Handler lambda function
    # test lambda function resource count
    template.resource_count_is("AWS::Lambda::Function", 7)
    # test lambda url resource count
    template.resource_count_is("AWS::Lambda::Url", 3)

    # test lambda function resource properties
    # indexer.py
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"file-indexer-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.indexer.lambda_handler",
            "MemorySize": 1000,
            "Timeout": 15 * 60,
        },
    )
    # upload_api.py
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"upload-api-handler-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.upload_api.lambda_handler",
            "MemorySize": 1000,
            "Timeout": 15 * 60,
        },
    )
    # queries.py
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"query-api-handler-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.queries.lambda_handler",
            "MemorySize": 1000,
            "Timeout": 60,
        },
    )
    # download_query_api.py
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "FunctionName": f"download-query-api-{sds_id}",
            "Runtime": "python3.9",
            "Handler": "SDSCode.download_query_api.lambda_handler",
            "Timeout": 60,
        },
    )


def test_secrets_manager(stack, sds_id):
    template = Template.from_stack(stack)

    # test secrets manager resource count
    template.resource_count_is("AWS::SecretsManager::Secret", 1)

    template.has_resource(
        "AWS::SecretsManager::Secret",
        {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )
