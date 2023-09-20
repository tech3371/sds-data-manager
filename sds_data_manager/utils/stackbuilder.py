"""Module with helper functions for creating standard sets of stacks"""
# Installed
from aws_cdk import App, Environment

# Local
from sds_data_manager.stacks import (
    api_gateway_stack,
    backup_bucket_stack,
    domain_stack,
    dynamodb_stack,
    efs_lambda_stack,
    opensearch_stack,
    sds_data_manager_stack,
    step_function_stack,
    vpc_stack,
    efs_stack,
)


def build_sds(
    scope: App, env: Environment, sds_id: str, use_custom_domain: bool = False
):
    """Builds the entire SDS

    Parameters
    ----------
    scope : App
    env : Environment
        Account and region
    sds_id : str
        Name suffix for stack
    use_custom_domain : bool, Optional
        Build API Gateway using custom domain
    """
    open_search = opensearch_stack.OpenSearch(
        scope, f"OpenSearch-{sds_id}", sds_id, env=env
    )

    dynamodb = dynamodb_stack.DynamoDB(
        scope,
        construct_id=f"DynamoDB-{sds_id}",
        sds_id=sds_id,
        table_name=f"imap-data-watcher-{sds_id}",
        partition_key="instrument",
        sort_key="filename",
        env=env,
    )

    processing_step_function = step_function_stack.ProcessingStepFunctionStack(
        scope,
        f"ProcessingStepFunctionStack-{sds_id}",
        sds_id,
        dynamodb_table_name=dynamodb.table_name,
        env=env,
    )

    data_manager = sds_data_manager_stack.SdsDataManager(
        scope,
        f"SdsDataManager-{sds_id}",
        sds_id,
        open_search,
        dynamodb,
        processing_step_function_arn=processing_step_function.sfn.state_machine_arn,
        env=env,
    )

    domain = domain_stack.Domain(
        scope,
        f"DomainStack-{sds_id}",
        sds_id,
        env=env,
        use_custom_domain=use_custom_domain,
    )

    api_gateway_stack.ApiGateway(
        scope,
        f"ApiGateway-{sds_id}",
        sds_id,
        data_manager.lambda_functions,
        env=env,
        hosted_zone=domain.hosted_zone,
        certificate=domain.certificate,
        use_custom_domain=use_custom_domain,
    )


def build_backup(scope: App, env: Environment, sds_id: str, source_account: str):
    """Builds backup bucket with permissions for replication from source_account.

    Parameters
    ----------
    scope : App
    env : Environment
        Account and region
    sds_id : str
        Name suffix for stack
    source_account : str
        Account number for source bucket for replication
    """
    # This is the S3 bucket used by upload_api_lambda
    backup_bucket_stack.BackupBucket(
        scope, f"BackupBucket-{sds_id}", sds_id, env=env, source_account=source_account
    )


def build_efs(scope: App, env: Environment, sds_id: str):
    """Builds EFS

    Parameters
    ----------
    scope : App
    env : Environment
        Account and region
    sds_id : str
        Name suffix for stack
    """
    # create vpc
    vpc = vpc_stack.VPCStack(scope, f"VpcStack-{sds_id}", sds_id)

    # create EFS
    efs_stack.EFSStack(scope, f"EFSStack-{sds_id}", sds_id, vpc.vpc)

    # create EFS write lambda
    efs_lambda_stack.EFSWriteLambda(scope, f"EFSWriteLambda-{sds_id}", sds_id, vpc.vpc)
