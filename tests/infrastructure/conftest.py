"""Setup items for the infrastructure tests."""

import pytest
from aws_cdk import App, Environment


@pytest.fixture(scope="module")
def account():
    """Set the account number to test with."""
    return "1234567890"


@pytest.fixture(scope="module")
def region():
    """Set the region to test with."""
    return "us-east-1"


@pytest.fixture(scope="module")
def env(account, region):
    """Set the environment to test with."""
    return Environment(account=account, region=region)


@pytest.fixture(scope="module")
def app():
    """Return the app to test with."""
    return App()
