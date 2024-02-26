from datetime import datetime
from unittest.mock import patch

import boto3
import pytest
from imap_data_access import ScienceFilePath
from moto import mock_batch, mock_sts
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sds_data_manager.lambda_code.SDSCode import (
    downstream_dependency_config,
    upstream_dependency_config,
)
from sds_data_manager.lambda_code.SDSCode.batch_starter import (
    append_attributes,
    get_dependency,
    lambda_handler,
    prepare_data,
    query_instrument,
    query_upstream_dependencies,
    send_lambda_put_event,
)
from sds_data_manager.lambda_code.SDSCode.database import database as db
from sds_data_manager.lambda_code.SDSCode.database.models import (
    Base,
    FileCatalog,
)


@pytest.fixture(scope="module")
def test_engine():
    """Create an in-memory SQLite database engine"""
    with patch.object(db, "get_engine") as mock_engine:
        engine = create_engine("sqlite:///:memory:")
        mock_engine.return_value = engine
        Base.metadata.create_all(engine)
        # When we use yield, it waits until session is complete
        # and waits for to be called whereas return exits fast.
        yield engine


@pytest.fixture()
def populate_db(test_engine):
    all_dependents = (
        downstream_dependency_config.downstream_dependents
        + upstream_dependency_config.upstream_dependents
    )
    # test_data = [
    #     PreProcessingDependency(
    #     primary_instrument="mag",
    #     primary_data_level="l1a",
    #     primary_descriptor="all",
    #     dependent_instrument="mag",
    #     dependent_data_level="l0",
    #     dependent_descriptor="raw",
    #     relationship="HARD",
    #     direction="UPSTREAM",
    # ),
    # ]
    # Setup: Add records to the database
    with Session(db.get_engine()) as session:
        session.add_all(all_dependents)
        session.commit()
        yield session
        session.rollback()
        session.close()


@pytest.fixture()
def test_file_catalog_simulation(test_engine):
    # Setup: Add records to the database

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
        descriptor="sci",
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
    with mock_batch():
        yield boto3.client("batch", region_name="us-west-2")


@pytest.fixture()
def sts_client(_aws_credentials):
    with mock_sts():
        yield boto3.client("sts", region_name="us-west-2")


def test_pre_processing_dependency(test_engine, populate_db):
    """Test pre-processing dependency"""
    # upstream dependency
    upstream_dependency = get_dependency(
        instrument="mag",
        data_level="l1a",
        descriptor="all",
        relationship="HARD",
        direction="UPSTREAM",
    )

    assert upstream_dependency[0]["instrument"] == "mag"
    assert upstream_dependency[0]["data_level"] == "l0"
    assert upstream_dependency[0]["descriptor"] == "raw"

    # downstream dependency
    downstream_dependency = get_dependency(
        instrument="mag",
        data_level="l1b",
        descriptor="normal-mago",
        relationship="HARD",
        direction="DOWNSTREAM",
    )

    assert downstream_dependency[0]["instrument"] == "mag"
    assert downstream_dependency[0]["data_level"] == "l1c"
    assert downstream_dependency[0]["descriptor"] == "normal-mago"


def test_query_instrument(test_file_catalog_simulation):
    "Tests query_instrument function."

    upstream_dependency = {
        "instrument": "ultra-45",
        "data_level": "l2",
        "version": "v00-01",
    }

    "Tests query_instrument function."
    record = query_instrument(
        test_file_catalog_simulation,
        upstream_dependency,
        "20240101",
        "20240102",
        "v00-01",
    )

    assert record.instrument == "ultra-45"
    assert record.data_level == "l2"
    assert record.version == "v00-01"
    assert record.start_date == datetime(2024, 1, 1)
    assert record.end_date == datetime(2024, 1, 2)


def test_append_attributes(test_file_catalog_simulation):
    "Tests append_attributes function."
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


def test_query_upstream_dependencies(test_file_catalog_simulation):
    "Tests query_upstream_dependencies function."

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
        test_file_catalog_simulation, downstream_dependents, "sci"
    )

    assert list(result[0].keys()) == ["command"]


def test_prepare_data():
    "Tests prepare_data function."

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
        "--data-level",
        "l1a",
        "--start-date",
        "20240101",
        "--end-date",
        "20240102",
        "--version",
        "v00-01",
        "--dependency",
        f"{upstream_dependencies}",
        "--upload-to-sdc",
    ]
    assert prepared_data == expected_prepared_data


def test_lambda_handler(test_file_catalog_simulation, batch_client, sts_client):
    # Tests lambda_handler function.
    event = {
        "detail": {"object": {"key": "imap_hit_l1a_sci_20240101_20240102_v00-01.cdf"}}
    }
    context = {"context": "sample_context"}

    lambda_handler(event, context)


def test_send_lambda_put_event(events_client):
    input_command = [
        "--instrument",
        "mag",
        "--data-level",
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
        "--upload-to-sdc",
    ]

    result = send_lambda_put_event(input_command)
    assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
