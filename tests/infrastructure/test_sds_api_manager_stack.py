"""Test the SDS API manager stack."""

import pytest
from aws_cdk.assertions import Template

from sds_data_manager.stacks.api_gateway_stack import ApiGateway
from sds_data_manager.stacks.data_bucket_stack import DataBucketStack
from sds_data_manager.stacks.networking_stack import NetworkingStack
from sds_data_manager.stacks.sds_api_manager_stack import SdsApiManager


@pytest.fixture(scope="module")
def data_bucket(app, env):
    """Return the data bucket stack."""
    stack = DataBucketStack(app, "indexer-data-bucket", env=env)
    return stack


@pytest.fixture(scope="module")
def networking_stack(app, env):
    """Return the networking stack."""
    networking = NetworkingStack(app, "Networking", env=env)
    return networking


@pytest.fixture(scope="module")
def api_gateway(app, env):
    """Return the API gateway stack."""
    apigw = ApiGateway(
        app,
        construct_id="Api-manager-ApigwTest",
    )
    return apigw


@pytest.fixture(scope="module")
def template(app, networking_stack, data_bucket, api_gateway, lambda_layer_stack, env):
    """Return a template API manager."""
    stack = SdsApiManager(
        app,
        "api-manager",
        api=api_gateway,
        env=env,
        data_bucket=data_bucket.data_bucket,
        vpc=networking_stack.vpc,
        rds_security_group=networking_stack.rds_security_group,
        db_secret_name="test-secrets",  # noqa
        layers=[lambda_layer_stack],
    )

    template = Template.from_stack(stack)

    return template


def test_indexer_role(template):
    """Ensure that the template has appropriate IAM roles."""
    template.resource_count_is("AWS::IAM::Role", 4)


def test_lambda_count(template):
    """Ensure that the template has appropriate lambda count."""
    template.resource_count_is("AWS::Lambda::Function", 4)
