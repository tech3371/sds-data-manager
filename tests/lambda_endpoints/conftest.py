"""Setup testing environment to test lambda handler code"""
import os

import boto3
import pytest
from moto import mock_s3
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sds_data_manager.lambda_code.SDSCode.database.models import Base


@pytest.fixture()
def _aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture()
def s3_client(_aws_credentials):
    """Mocked S3 Client, so we don't need network requests."""
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture()
def test_db_uri(mocker):
    """Patch get_db_uri from indexer lambda for test"""
    mock_get_db_uri = mocker.patch(
        "sds_data_manager.lambda_code.SDSCode.indexer.get_db_uri"
    )
    mock_get_db_uri.return_value = "sqlite:///:memory:"
    return mock_get_db_uri


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database engine"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def db_session(test_engine):
    """Creates a new database session for a test."""
    connection = test_engine.connect()
    session = scoped_session(sessionmaker(bind=connection))

    return session
