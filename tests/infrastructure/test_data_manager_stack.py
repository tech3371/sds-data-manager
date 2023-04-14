import pytest
from aws_cdk.assertions import Match, Template

from sds_data_manager.sds_data_manager_stack import SdsDataManagerStack


@pytest.fixture()
def template(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = SdsDataManagerStack(app, stack_name, sds_id)
    template = Template.from_stack(stack)
    return template


def test_s3_buckets(template, sds_id):
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


def test_s3_bucket_policy(template, sds_id):
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


def test_lambda_permissions(template, sds_id):
    template.resource_count_is("AWS::Lambda::Permission", 4)

    template.has_resource_properties(
        "AWS::Lambda::Permission",
        {
            "Action": "lambda:InvokeFunction",
            "FunctionName": {
                "Fn::GetAtt": [Match.string_like_regexp("IndexerLambda*"), "Arn"]
            },
            "Principal": "s3.amazonaws.com",
            "SourceAccount": {"Ref": "AWS::AccountId"},
            "SourceArn": {
                "Fn::GetAtt": [Match.string_like_regexp("DATABUCKET*"), "Arn"]
            },
        },
    )
    template.has_resource_properties(
        "AWS::Lambda::Permission",
        {
            "Action": "lambda:InvokeFunctionUrl",
            "FunctionName": {
                "Fn::GetAtt": [Match.string_like_regexp("UploadAPILambda*"), "Arn"]
            },
            "Principal": "*",
            "FunctionUrlAuthType": "NONE",
        },
    )
    template.has_resource_properties(
        "AWS::Lambda::Permission",
        {
            "Action": "lambda:InvokeFunctionUrl",
            "FunctionName": {
                "Fn::GetAtt": [Match.string_like_regexp("QueryAPILambda*"), "Arn"]
            },
            "Principal": "*",
            "FunctionUrlAuthType": "NONE",
        },
    )
    template.has_resource_properties(
        "AWS::Lambda::Permission",
        {
            "Action": "lambda:InvokeFunctionUrl",
            "FunctionName": {
                "Fn::GetAtt": [
                    Match.string_like_regexp("DownloadQueryAPILambda*"),
                    "Arn",
                ]
            },
            "Principal": "*",
            "FunctionUrlAuthType": "NONE",
        },
    )


def test_opensearch(template, sds_id):
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


def test_custom_s3_auto_delete(template):
    template.resource_count_is("Custom::S3AutoDeleteObjects", 1)

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


def test_custom_s3_bucket_notifications(template):
    template.resource_count_is("Custom::S3BucketNotifications", 1)

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
                            "Fn::GetAtt": [
                                Match.string_like_regexp("IndexerLambda*"),
                                "Arn",
                            ]
                        },
                    }
                ]
            },
            "Managed": True,
        },
    )


def test_custom_cloudwatch_log_resource_policy(template):
    template.resource_count_is("Custom::CloudwatchLogResourcePolicy", 1)


def test_custom_opensearch_access_policy(template):
    template.resource_count_is("Custom::OpenSearchAccessPolicy", 1)

    template.has_resource(
        "Custom::OpenSearchAccessPolicy",
        {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )

    template.has_resource_properties(
        "Custom::OpenSearchAccessPolicy",
        {
            "ServiceToken": {"Fn::GetAtt": [Match.string_like_regexp("AWS*"), "Arn"]},
            "Create": {
                "Fn::Join": [
                    "",
                    [
                        '{"action":"updateDomainConfig","service":"OpenSearch","parameters":{"DomainName":"',
                        {"Ref": Match.string_like_regexp("SDSMetadataDomain*")},
                        '","AccessPolicies":"{\\"Statement\\":[{\\"Action\\":\\"es:*\\",\\"Effect\\":\\"Allow\\",\\"Principal\\":{\\"AWS\\":\\"*\\"},\\"Resource\\":\\"',
                        {
                            "Fn::GetAtt": [
                                Match.string_like_regexp("SDSMetadataDomain*"),
                                "Arn",
                            ]
                        },
                        '/*\\"}],\\"Version\\":\\"2012-10-17\\"}"},"outputPaths":["DomainConfig.AccessPolicies"],"physicalResourceId":{"id":"',
                        {"Ref": Match.string_like_regexp("SDSMetadataDomain*")},
                        'AccessPolicy"}}',
                    ],
                ]
            },
            "Update": {
                "Fn::Join": [
                    "",
                    [
                        '{"action":"updateDomainConfig","service":"OpenSearch","parameters":{"DomainName":"',
                        {"Ref": Match.string_like_regexp("SDSMetadataDomain*")},
                        '","AccessPolicies":"{\\"Statement\\":[{\\"Action\\":\\"es:*\\",\\"Effect\\":\\"Allow\\",\\"Principal\\":{\\"AWS\\":\\"*\\"},\\"Resource\\":\\"',
                        {
                            "Fn::GetAtt": [
                                Match.string_like_regexp("SDSMetadataDomain*"),
                                "Arn",
                            ]
                        },
                        '/*\\"}],\\"Version\\":\\"2012-10-17\\"}"},"outputPaths":["DomainConfig.AccessPolicies"],"physicalResourceId":{"id":"',
                        {"Ref": Match.string_like_regexp("SDSMetadataDomain*")},
                        'AccessPolicy"}}',
                    ],
                ]
            },
            "InstallLatestAwsSdk": True,
        },
    )


def test_log_groups(template):
    template.resource_count_is("AWS::Logs::LogGroup", 3)

    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "DeletionPolicy": "Retain",
            "UpdateReplacePolicy": "Retain",
        },
    )
    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "DeletionPolicy": "Retain",
            "UpdateReplacePolicy": "Retain",
        },
    )
    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "DeletionPolicy": "Retain",
            "UpdateReplacePolicy": "Retain",
        },
    )

    template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})
    template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})
    template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})


def test_aim_roles(template, sds_id):
    # test IAM role count
    template.resource_count_is("AWS::IAM::Role", 7)

    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
                "Version": "2012-10-17",
            }
        },
    )


def test_iam_policies(template, sds_id):
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


def test_lambdas(template, sds_id):
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
    # AWS Lambda
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "Handler": "index.handler",
            "Runtime": "nodejs14.x",
            "Timeout": 120,
            "Role": {
                "Fn::GetAtt": [
                    "AWS679f53fac002430cb0da5b7982bd2287ServiceRoleC1EA0FF2",
                    "Arn",
                ]
            },
        },
    )
    # Bucket Notification Lambda
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "Handler": "index.handler",
            "Runtime": "python3.9",
            "Timeout": 300,
            "Role": {
                "Fn::GetAtt": [
                    "BucketNotificationsHandler050a0587b7544547bf325f094a3db834RoleB6FB88EC",
                    "Arn",
                ]
            },
        },
    )


def test_secrets_manager(template, sds_id):
    # test secrets manager resource count
    template.resource_count_is("AWS::SecretsManager::Secret", 1)

    template.has_resource(
        "AWS::SecretsManager::Secret",
        {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )
