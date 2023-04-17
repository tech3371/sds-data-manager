import pytest
from aws_cdk.assertions import Match, Template

from sds_data_manager.sds_data_manager_stack import SdsDataManagerStack


@pytest.fixture()
def template(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = SdsDataManagerStack(app, stack_name, sds_id)
    template = Template.from_stack(stack)
    return template


def test_s3_data_bucket_count(template):
    # test s3 bucket resource count
    template.resource_count_is("AWS::S3::Bucket", 1)


def test_s3_data_bucket(template, sds_id):
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


def test_s3_data_bucket_policy(template, sds_id):
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


def test_log_groups_count(template):
    template.resource_count_is("AWS::Logs::LogGroup", 3)


def test_sdsmetadatadomain_slow_search_logs(template):
    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "DeletionPolicy": "Retain",
            "UpdateReplacePolicy": "Retain",
        },
    )
    template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})


def test_sdsmetadatadomain_slow_index_logs(template):
    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "DeletionPolicy": "Retain",
            "UpdateReplacePolicy": "Retain",
        },
    )
    template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})


def test_sdsmetadatadomain_app_logs(template):
    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "DeletionPolicy": "Retain",
            "UpdateReplacePolicy": "Retain",
        },
    )
    template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})


def test_iam_roles_count(template):
    # test IAM role count
    template.resource_count_is("AWS::IAM::Role", 7)


def test_s3_auto_delete_iam_role(template):
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


def test_indexer_lambda_iam_role(template):
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


def test_bucket_notification_iam_role(template):
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


def test_upload_api_iam_role(template):
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


def test_query_api_iam_role(template):
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


def test_download_api_iam_role(template):
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


def test_aws_iam_role(template):
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


def test_iam_policy_resource_count(template, sds_id):
    template.resource_count_is("AWS::IAM::Policy", 7)


def test_upload_lambda_api_aim_policy(template):
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


def test_sdsmetadatadomain_esloggroup_iam_policy(template):
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
            "PolicyName": Match.string_like_regexp(
                "SDSMetadataDomainESLogGroupPolicyc*"
            ),
        },
    )


def test_sdsmetadatadomain_accesspolicy_iam_policy(template):
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


def test_indexer_lambda_iam_policy(template):
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


def test_bucket_notification_iam_policy(template):
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


def test_queryapilambda_iam_policy(template):
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


def test_downloadquerylambda_iam_policy(template):
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


def test_lambda_urls_count(template, sds_id):
    # test lambda url resource count
    template.resource_count_is("AWS::Lambda::Url", 3)


def test_upload_api_lambda_url(template):
    # Upload API
    template.has_resource_properties(
        "AWS::Lambda::Url",
        {
            "AuthType": "NONE",
            "TargetFunctionArn": {
                "Fn::GetAtt": [Match.string_like_regexp("UploadAPILambda*"), "Arn"]
            },
            "Cors": {"AllowMethods": ["*"], "AllowOrigins": ["*"]},
        },
    )


def test_query_api_lambda_url(template):
    # Query API
    template.has_resource_properties(
        "AWS::Lambda::Url",
        {
            "AuthType": "NONE",
            "TargetFunctionArn": {
                "Fn::GetAtt": [Match.string_like_regexp("QueryAPILambda*"), "Arn"]
            },
            "Cors": {"AllowMethods": ["GET"], "AllowOrigins": ["*"]},
        },
    )


def test_download_api_lambda_url(template):
    # Download API
    template.has_resource_properties(
        "AWS::Lambda::Url",
        {
            "AuthType": "NONE",
            "TargetFunctionArn": {
                "Fn::GetAtt": [
                    Match.string_like_regexp("DownloadQueryAPILambda*"),
                    "Arn",
                ]
            },
            "Cors": {"AllowMethods": ["GET"], "AllowOrigins": ["*"]},
        },
    )


def test_lambda_function_count(template, sds_id):
    # test for lambda function resource count
    template.resource_count_is("AWS::Lambda::Function", 7)


def test_indexer_lambda_function(template, sds_id):
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


def test_upload_api_lambda_function(template, sds_id):
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


def test_query_api_lambda_function(template, sds_id):
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


def test_download_api_lambda_function(template, sds_id):
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


def test_aws_lambda_function(template):
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


def test_aws_bucket_notification_lambda_function(template):
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

    # Custom S3 AutoDelete
    template.has_resource_properties(
        "AWS::Lambda::Function",
        props={
            "Handler": "__entrypoint__.handler",
            "Runtime": "nodejs14.x",
            "Timeout": 900,
            "MemorySize": 128,
            "Role": {
                "Fn::GetAtt": [
                    "CustomS3AutoDeleteObjectsCustomResourceProviderRole3B1BD092",
                    "Arn",
                ]
            },
        },
    )


def test_lambda_permission_count(template):
    template.resource_count_is("AWS::Lambda::Permission", 4)


def test_indexer_lambda_permission(template):
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


def test_upload_api_lambda_permission(template):
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


def test_query_api_lambda_permission(template):
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


def test_download_api_lambda_permission(template):
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
