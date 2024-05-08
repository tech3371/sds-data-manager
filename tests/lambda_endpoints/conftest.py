"""Setup testing environment to test lambda handler code."""

from unittest.mock import patch

import boto3
import pytest
from moto import mock_events, mock_s3
from sqlalchemy import create_engine

from sds_data_manager.lambda_code.SDSCode.database import database as db
from sds_data_manager.lambda_code.SDSCode.database.models import Base


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    """Set global environment variables."""
    monkeypatch.setenv("S3_BUCKET", "test-data-bucket")
    # Mock AWS Credentials for moto
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture()
def s3_client():
    """Mock S3 Client, so we don't need network requests."""
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture()
def events_client():
    """Mock EventBridge client."""
    with mock_events():
        yield boto3.client("events", region_name="us-west-2")


# NOTE: This test_engine scope is function.
# With this scope, all the changes to the database
# is only visible in each test function. It gets
# cleaned up after each function.
@pytest.fixture()
def test_engine():
    """Create an in-memory SQLite database engine."""
    with patch.object(db, "get_engine") as mock_engine:
        engine = create_engine("sqlite:///:memory:")
        mock_engine.return_value = engine
        Base.metadata.create_all(engine)
        # When we use yield, it waits until session is complete
        # and waits for to be called whereas return exits fast.
        yield engine
