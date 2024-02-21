"""Tests the batch starter."""

from datetime import datetime
from pathlib import Path

import boto3
import pytest
from imap_data_access import ScienceFilePath
from moto import mock_batch, mock_sts
from sqlalchemy.orm import Session

from sds_data_manager.lambda_code.SDSCode.batch_starter import (
    append_attributes,
    find_upstream_dependencies,
    lambda_handler,
    load_data,
    prepare_data,
    query_instrument,
    query_upstream_dependencies,
    send_lambda_put_event,
)
from sds_data_manager.lambda_code.SDSCode.database import database as db
from sds_data_manager.lambda_code.SDSCode.database.models import FileCatalog


@pytest.fixture()
def test_file_catalog_simulation(test_engine):
    """Adds tests records to the database."""
    test_record_1 = FileCatalog(
        file_path="/path/to/file",
        instrument="ultra-45",
        data_level="l2",
        descriptor="science",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
        version="v00-01",
        extension="cdf",
        ingestion_date=datetime.strptime(
            "2024-01-25 23:35:26+00:00", "%Y-%m-%d %H:%M:%S%z"
        ),
    )

    test_record_2 = FileCatalog(
        file_path="/path/to/file",
        instrument="hit",
        data_level="l0",
        descriptor="science",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
        version="v00-01",
        extension="cdf",
        ingestion_date=datetime.strptime(
            "2024-01-25 23:35:26+00:00", "%Y-%m-%d %H:%M:%S%z"
        ),
    )
    with Session(db.get_engine()) as session:
        session.add(test_record_1)
        session.add(test_record_2)
        session.commit()

    return session


@pytest.fixture()
def batch_client(_aws_credentials):
    """Return a batch client to test with."""
    with mock_batch():
        yield boto3.client("batch", region_name="us-west-2")


@pytest.fixture()
def sts_client(_aws_credentials):
    """Return a mock sts client to test with."""
    with mock_sts():
        yield boto3.client("sts", region_name="us-west-2")


def test_query_instrument(test_file_catalog_simulation):
    """Test query_instrument function."""

    upstream_dependency = {
        "instrument": "ultra-45",
        "data_level": "l2",
        "version": "v00-01",
    }

    "Tests query_instrument function."
    record = query_instrument(
        test_file_catalog_simulation, upstream_dependency, "20240101", "20240102"
    )

    assert record.instrument == "ultra-45"
    assert record.data_level == "l2"
    assert record.version == "v00-01"
    assert record.start_date == datetime(2024, 1, 1)
    assert record.end_date == datetime(2024, 1, 2)


def test_append_attributes(test_file_catalog_simulation):
    """Test append_attributes function."""
    downstream_dependents = [{"instrument": "codice", "data_level": "l3b"}]

    complete_dependents = append_attributes(
        test_file_catalog_simulation,
        downstream_dependents,
        "20240101",
        "20240102",
        "v00-01",
    )

    expected_complete_dependent = {
        "instrument": "codice",
        "data_level": "l3b",
        "version": "v00-01",
        "start_date": "20240101",
        "end_date": "20240102",
    }

    assert complete_dependents[0] == expected_complete_dependent


def test_load_data():
    """Test load_data function."""
    base_directory = Path(__file__).resolve()
    base_path = (
        base_directory.parents[2] / "sds_data_manager" / "lambda_code" / "SDSCode"
    )
    filepath = base_path / "downstream_dependents.json"

    data = load_data(filepath)

    assert data["codice"]["l0"][0]["data_level"] == "l1a"


def test_find_upstream_dependencies():
    """Test find_upstream_dependencies function."""
    base_directory = Path(__file__).resolve()
    base_path = (
        base_directory.parents[2] / "sds_data_manager" / "lambda_code" / "SDSCode"
    )
    filepath = base_path / "downstream_dependents.json"

    data = load_data(filepath)

    upstream_dependencies = find_upstream_dependencies("codice", "l3b", "v00-01", data)

    expected_result = [
        {"instrument": "codice", "data_level": "l2", "version": "v00-01"},
        {"instrument": "codice", "data_level": "l3a", "version": "v00-01"},
        {"instrument": "mag", "data_level": "l2", "version": "v00-01"},
    ]

    assert upstream_dependencies == expected_result


def test_query_upstream_dependencies(test_file_catalog_simulation):
    """Test query_upstream_dependencies function."""
    base_directory = Path(__file__).resolve()
    filepath = (
        base_directory.parents[2]
        / "sds_data_manager"
        / "lambda_code"
        / "SDSCode"
        / "downstream_dependents.json"
    )

    data = load_data(filepath)

    downstream_dependents = [
        {
            "instrument": "hit",
            "data_level": "l1a",
            "version": "v00-01",
            "start_date": "20240101",
            "end_date": "20240102",
        },
        {
            "instrument": "hit",
            "data_level": "l3",
            "version": "v00-01",
            "start_date": "20240101",
            "end_date": "20240102",
        },
    ]

    result = query_upstream_dependencies(
        test_file_catalog_simulation, downstream_dependents, data, "bucket_name", "sci"
    )

    assert list(result[0].keys()) == ["command"]


def test_prepare_data():
    """Test prepare_data function."""

    upstream_dependencies = [
        {
            "instrument": "hit",
            "data_level": "l0",
            "start_date": "20240101",
            "end_date": "20240102",
            "version": "v00-01",
        }
    ]

    filename = "imap_hit_l1a_sci_20240101_20240102_v00-01.cdf"
    file_params = ScienceFilePath.extract_filename_components(filename)
    prepared_data = prepare_data(
        instrument=file_params["instrument"],
        data_level=file_params["data_level"],
        start_date=file_params["start_date"],
        end_date=file_params["end_date"],
        version=file_params["version"],
        upstream_dependencies=upstream_dependencies,
    )

    expected_prepared_data = [
        "--instrument",
        "hit",
        "--data_level",
        "l1a",
        "--start-date",
        "20240101",
        "--end-date",
        "20240102",
        "--version",
        "v00-01",
        "--dependency",
        f"{upstream_dependencies}",
        "--use-remote",
    ]
    assert prepared_data == expected_prepared_data


def test_lambda_handler(test_file_catalog_simulation, batch_client, sts_client):
    """Test lambda_handler function."""
    event = {
        "detail": {"object": {"key": "imap_hit_l1a_sci_20240101_20240102_v00-01.cdf"}}
    }
    context = {"context": "sample_context"}

    lambda_handler(event, context)


def test_send_lambda_put_event(events_client):
    """Test send_lambda_put_event function."""
    input_command = [
        "--instrument",
        "mag",
        "--data_level",
        "l1a",
        "--start-date",
        "20231212",
        "--end-date",
        "20231212",
        "--version",
        "v00-01",
        "--dependency",
        """[
            {
                'instrument': 'swe',
                'data_level': 'l0',
                'descriptor': 'lveng-hk',
                'start_date': '20231212',
                'end_date': '20231212',
                'version': 'v01-00',
            },
            {
                'instrument': 'mag',
                'data_level': 'l0',
                'descriptor': 'lveng-hk',
                'start_date': '20231212',
                'end_date': '20231212',
                'version': 'v00-01',
            }]""",
        "--use-remote",
    ]

    result = send_lambda_put_event(input_command)
    assert result["ResponseMetadata"]["HTTPStatusCode"] == 200