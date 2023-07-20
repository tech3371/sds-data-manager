import pytest
from aws_cdk.assertions import Template

from sds_data_manager.stacks.dynamo_db_stack import DynamoDB


@pytest.fixture(scope="module")
def template(app, sds_id):
    stack_name = f"stack-{sds_id}"
    stack = DynamoDB(
        app,
        stack_name,
        sds_id,
        table_name=f"table-{sds_id}",
        partition_key="filename",
        sort_key="instrument",
        env=None,
    )
    template = Template.from_stack(stack)
    return template


def test_table_name(template):
    template.resource_count_is("AWS::DynamoDB::Table", 1)


def test_billing_mode(template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table", {"BillingMode": "PAY_PER_REQUEST"}
    )


def test_point_in_time_recovery(template):
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {"PointInTimeRecoverySpecification": {"PointInTimeRecoveryEnabled": True}},
    )


def test_delete_table_policy(template):
    template.has_resource(
        "AWS::DynamoDB::Table",
        {
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )
