"""Setup testing environment to test lambda handler code."""

from unittest.mock import patch

import boto3
import pytest
from moto import mock_events, mock_s3
from sqlalchemy import create_engine

from sds_data_manager.lambda_code.SDSCode.database import database as db
from sds_data_manager.lambda_code.SDSCode.database.models import Base

BUCKET_NAME = "test-data-bucket"


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    """Set global environment variables."""
    monkeypatch.setenv("S3_BUCKET", BUCKET_NAME)
    # Mock AWS Credentials for moto
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture(scope="module")
def science_file():
    """Path to a valid science file."""
    return "imap/swe/l1a/2010/01/imap_swe_l1a_test-description_20100101_v000.cdf"


@pytest.fixture(scope="module")
def spice_file():
    """Path to a valid spice file."""
    return "imap/spice/ck/test_v000.bc"


@pytest.fixture(autouse=True, scope="module")
def s3_client(science_file, spice_file):
    """Mock S3 Client, so we don't need network requests."""
    with mock_s3():
        s3_client = boto3.client("s3", region_name="us-east-1")

        s3_client.create_bucket(
            Bucket=BUCKET_NAME,
        )
        result = s3_client.list_buckets()
        assert len(result["Buckets"]) == 1
        assert result["Buckets"][0]["Name"] == BUCKET_NAME

        # upload testing files
        for key in [
            science_file,
            spice_file,
            # These are expected by the indexer
            "imap/swapi/l1/2023/01/imap_swapi_l1_sci-1min_20230724_v001.cdf",
            "imap/hit/l0/2024/01/imap_hit_l0_sci-test_20240101_v001.pkts",
        ]:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=b"",
            )

        file_list = s3_client.list_objects(Bucket=BUCKET_NAME)["Contents"]
        assert len(file_list) == 4

        yield s3_client


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
