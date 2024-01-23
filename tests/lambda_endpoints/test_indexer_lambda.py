"""Test indexer lambda"""


import pytest
from sqlalchemy.orm import Session

from sds_data_manager.lambda_code.SDSCode import indexer
from sds_data_manager.lambda_code.SDSCode.database import database as db
from sds_data_manager.lambda_code.SDSCode.database.models import PreProcessingDependency


@pytest.fixture()
def populate_db(test_engine):
    """Populate database with test data"""
    test_data = [
        PreProcessingDependency(
            primary_instrument="swe",
            primary_data_level="l2",
            dependent_instrument="glows",
            dependent_data_level="l3",
            relationship="HARD",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="swe",
            primary_data_level="l1b",
            dependent_instrument="mag",
            dependent_data_level="l2",
            relationship="HARD",
            direction="UPSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="swe",
            primary_data_level="l1b",
            dependent_instrument="hi-45",
            dependent_data_level="l1c",
            relationship="SOFT",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="swe",
            primary_data_level="l1b",
            dependent_instrument="lo",
            dependent_data_level="l1c",
            relationship="SOFT",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="swe",
            primary_data_level="l1b",
            dependent_instrument="ultra-45",
            dependent_data_level="l1c",
            relationship="SOFT",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="codice",
            primary_data_level="l1b",
            dependent_instrument="hi-45",
            dependent_data_level="l1c",
            relationship="SOFT",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="codice",
            primary_data_level="l1b",
            dependent_instrument="lo",
            dependent_data_level="l1c",
            relationship="SOFT",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="codice",
            primary_data_level="l1b",
            dependent_instrument="ultra-45",
            dependent_data_level="l1c",
            relationship="SOFT",
            direction="DOWNSTREAM",
        ),
        PreProcessingDependency(
            primary_instrument="hit",
            primary_data_level="l2",
            dependent_instrument="glows",
            dependent_data_level="l3",
            relationship="HARD",
            direction="DOWNSTREAM",
        ),
    ]

    with Session(db.get_engine()) as session:
        session.add_all(test_data)
        session.commit()
        yield session


def test_batch_job_event(test_engine):
    # TODO: replace event with other event source
    # dict. We don't use "Records" anymore. But
    # leaving for now to test database capabilities.
    # Will remove in upcoming PR.
    event = {
        "Records": [
            {
                "detail-type": "Object Created",
                "source": "aws.s3",
                "s3": {
                    "version": "0",
                    "bucket": {"name": "sds-data-449431850278"},
                    "object": {
                        "key": "imap_hit_l0_sci-test_20240101_20240104_v02-01.pkts",
                        "reason": "PutObject",
                    },
                },
            }
        ]
    }
    returned_value = indexer.lambda_handler(event=event, context={})
    assert returned_value is None


def test_downstream_dependency(test_engine, populate_db):
    """Test downstream dependency"""
    pass
