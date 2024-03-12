"""Tests for the indexer lambda."""

import os

import pytest
from imap_data_access import ScienceFilePath
from sqlalchemy import select
from sqlalchemy.orm import Session

from sds_data_manager.lambda_code.SDSCode import indexer
from sds_data_manager.lambda_code.SDSCode.database import database as db
from sds_data_manager.lambda_code.SDSCode.database import models
from sds_data_manager.lambda_code.SDSCode.indexer import (
    batch_event_handler,
    send_event_from_indexer,
)


@pytest.fixture()
def write_to_s3(s3_client):
    """Write test data to s3."""
    # first create test bucket
    s3_client.create_bucket(
        Bucket="test-data-bucket",
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
    )
    # write file to s3
    s3_client.put_object(
        Bucket="test-data-bucket",
        Key=("imap/swapi/l1/2023/01/imap_swapi_l1_sci-1m_20230724_v001.cdf"),
        Body=b"test",
    )
    s3_client.put_object(
        Bucket="test-data-bucket",
        Key=("imap/hit/l0/2024/01/imap_hit_l0_sci-test_20240101_v001.pkts"),
        Body=b"test",
    )
    return s3_client


def test_batch_job_event(test_engine, write_to_s3, events_client, set_env):
    """Test batch job event."""
    # Send s3 event first to write initial data to satus
    # table
    custom_event = {
        "detail-type": "Job Started",
        "source": "imap.lambda",
        "detail": {
            "instrument": "swapi",
            "data_level": "l1",
            "start_date": "20230724",
            "version": "v001",
            "status": "INPROGRESS",
            "dependency": {"codice": "s3-filepath", "mag": "s3-filepath"},
        },
    }

    # Test for good event
    returned_value = indexer.lambda_handler(event=custom_event, context={})
    assert returned_value["statusCode"] == 200

    # TODO: Will update this test further
    # when I extend batch job event handler.
    event = {
        "detail-type": "Batch Job State Change",
        "source": "aws.batch",
        "detail": {
            "jobArn": (
                "arn:aws:batch:us-west-2:012345678910:"
                "job/26242c7e-3d49-4e41-9387-74fcaf9630bb"
            ),
            "jobName": "swe-l0-job",
            "jobId": "26242c7e-3d49-4e41-9387-74fcaf9630bb",
            "jobQueue": (
                "arn:aws:batch:us-west-2:012345678910:"
                "job-queue/swe-fargate-batch-job-queue"
            ),
            "status": "FAILED",
            "statusReason": "some error message",
            "jobDefinition": (
                "arn:aws:batch:us-west-2:012345678910:"
                "job-definition/fargate-batch-job-definitionswe:1"
            ),
            "container": {
                "image": (
                    "123456789012.dkr.ecr.us-west-2.amazonaws.com/" "swapi-repo:latest"
                ),
                "command": [
                    "--instrument",
                    "swapi",
                    "--level",
                    "l1",
                    "--start-date",
                    "20230724",
                    "--version",
                    "v001",
                    "--dependency",
                    """[
                        {
                            'instrument': 'swapi',
                            'level': 'l0',
                            'start_date': 20230724,
                            'version': 'v001'
                        }
                    ]""",
                    "--use-remote",
                ],
                "logStreamName": (
                    "fargate-batch-job-definitionswe/default/"
                    "8a2b784c7bd342f69ea5dac3adaed26f"
                ),
            },
        },
    }
    returned_value = indexer.lambda_handler(event=event, context={})
    assert returned_value["statusCode"] == 200

    # check that data was written to status table
    with Session(db.get_engine()) as session:
        event_details = custom_event["detail"]
        query = select(models.StatusTracking.__table__).where(
            models.StatusTracking.instrument == event_details["instrument"],
            models.StatusTracking.data_level == event_details["data_level"],
            models.StatusTracking.version == event_details["version"],
        )

        status_tracking = session.execute(query).first()
        assert status_tracking.status == models.Status.FAILED

    # Test for succeeded case
    event["detail"]["status"] = "SUCCEEDED"
    returned_value = indexer.lambda_handler(event=event, context={})
    assert returned_value["statusCode"] == 200

    with Session(db.get_engine()) as session:
        event_details = custom_event["detail"]
        query = select(models.StatusTracking.__table__).where(
            models.StatusTracking.instrument == event_details["instrument"],
            models.StatusTracking.data_level == event_details["data_level"],
            models.StatusTracking.version == event_details["version"],
        )

        status_tracking = session.execute(query).first()
        assert status_tracking.status == models.Status.SUCCEEDED

    # Test for file that is not in status table
    event["detail"]["container"]["command"][1] = "swe"
    result = batch_event_handler(event)
    assert result["statusCode"] == 200

    with Session(db.get_engine()) as session:
        query = select(models.StatusTracking.__table__).where(
            models.StatusTracking.instrument == "swe"
        )

        status_tracking = session.execute(query).first()
        assert status_tracking.status == models.Status.SUCCEEDED


def test_custom_lambda_event(test_engine):
    """Test custom PutEvent from lambda."""
    # Took out unused parameters from event
    event = {
        "detail-type": "Job Started",
        "source": "imap.lambda",
        "detail": {
            "instrument": "swapi",
            "data_level": "l1",
            "start_date": "20230724",
            "version": "v001",
            "status": "INPROGRESS",
            "dependency": {"codice": "s3-filepath", "mag": "s3-filepath"},
        },
    }

    # Test for good event
    returned_value = indexer.lambda_handler(event=event, context={})
    assert returned_value["statusCode"] == 200

    # Check that data was written to database by lambda
    with Session(db.get_engine()) as session:
        result = session.query(models.StatusTracking).all()
        assert len(result) == 1
        assert result[0].instrument == "swapi"
        assert result[0].data_level == "l1"
        assert result[0].version == "v001"
        assert result[0].status == models.Status.INPROGRESS


def test_s3_event(test_engine, events_client, write_to_s3):
    """Test s3 event."""
    # Took out unused parameters from event
    event = {
        "detail-type": "Object Created",
        "source": "aws.s3",
        "time": "2024-01-16T17:35:08Z",
        "detail": {
            "version": "0",
            "bucket": {"name": "sds-data-123456789012"},
            "object": {
                "key": (
                    "imap/hit/l0/2024/01/" "imap_hit_l0_sci-test_20240101_v001.pkts"
                ),
                "reason": "PutObject",
            },
        },
    }
    # Test for good event
    returned_value = indexer.lambda_handler(event=event, context={})
    assert returned_value["statusCode"] == 200

    # Check that data was written to database by lambda
    with Session(db.get_engine()) as session:
        result = session.query(models.FileCatalog).all()
        assert len(result) == 1
        assert (
            result[0].file_path
            == "imap/hit/l0/2024/01/imap_hit_l0_sci-test_20240101_v001.pkts"
        )
        assert result[0].data_level == "l0"
        assert result[0].instrument == "hit"
        assert result[0].extension == "pkts"

    # Test for bad filename input
    event["detail"]["object"]["key"] = (
        "imap/hit/l0/2024/01/" "imap_hit_l0_sci-test_20240101_v001.cdf"
    )

    expected_msg = (
        "Invalid extension. Extension should be pkts for data level l0"
        " and cdf for data level higher than l0 \n"
    )

    with pytest.raises(ScienceFilePath.InvalidScienceFileError) as excinfo:
        ScienceFilePath(os.path.basename(event["detail"]["object"]["key"]))
    # Wrote this test outside because pre-commit complains
    assert str(excinfo.value) == expected_msg


def test_unknown_event(test_engine):
    """Test for unknown event source."""
    event = {"source": "test"}
    returned_value = indexer.lambda_handler(event=event, context={})
    assert returned_value["statusCode"] == 400
    assert returned_value["body"] == "Unknown event source"


def test_send_lambda_put_event(events_client):
    """Test the ``send_event_from_indexer`` function."""
    filename = "imap_swapi_l1_sci-1m_20230724_v001.cdf"

    result = send_event_from_indexer(filename)
    assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
