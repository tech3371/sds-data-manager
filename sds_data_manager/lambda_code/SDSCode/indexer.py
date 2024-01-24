import datetime
import json
import logging
import os
import sys

import boto3
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from .database import database as db
from .database import models
from .path_helper import FilenameParser

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

s3 = boto3.client("s3")


def get_dependency(instrument, data_level, descriptor, direction, relationship):
    """Make query to dependency table to get dependency.

    TODO: Move it table to batch starter after February demo or keep it here
    based on discussion during that time. This is just to setup and test
    cababilities to make queries to pre-processing dependency table.

    Parameters
    ----------
    instrument : str
        Primary instrument that we are looking for its dependency.
    data_level : str
        Primary data level.
    descriptor : str
        Primary data descriptor.
    direction: str
        Whether it's UPSTREAM or DOWNSTREAM dependency.
    relationship: str
        Whether it's HARD or SOFT dependency.
        HARD means it's required and SOFT means it's nice to have.
    Returns
    -------
    dependency : list
        List of dictionary containing the dependency information.
    """
    dependency = []
    # Send EventBridge event for downstream dependency
    with Session(db.get_engine()) as session:
        results = (
            session.query(models.PreProcessingDependency)
            .filter(models.PreProcessingDependency.primary_instrument == instrument)
            .filter(models.PreProcessingDependency.primary_data_level == data_level)
            .filter(models.PreProcessingDependency.primary_descriptor == descriptor)
            .filter(models.PreProcessingDependency.direction == direction)
            .filter(models.PreProcessingDependency.relationship == relationship)
            .all()
        )
        for result in results:
            dependency.append(result)
    return dependency


def lambda_handler(event, context):
    """Handler function for creating metadata, adding it to the database.

    This function is an event handler for multiple event sources.
    List of event sources are aws.s3, aws.batch and imap.lambda.
    imap.lambda is custom PutEvent from AWS lambda.

    Parameters
    ----------
    event : dict
        The JSON formatted document with the data required for the
        lambda function to process
    context : LambdaContext
        This object provides methods and properties that provide
        information about the invocation, function,
        and runtime environment.
    """
    logger.info("Received event: " + json.dumps(event, indent=2))

    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")
    engine = db.get_engine()

    # We're only expecting one record, but for some reason the Records are a list object
    # TODO: events no longer have a Records key with list. This is already planned for
    # removal in an upcoming PR.
    for record in event["Records"]:
        # Retrieve the Object name
        logger.info(f"Record Received: {record}")
        filename = record["s3"]["object"]["key"]

        logger.info(f"Attempting to insert {os.path.basename(filename)} into database")
        filename_parsed = FilenameParser(os.path.basename(filename))
        filepath = filename_parsed.upload_filepath()

        # confirm that the file is valid
        if filepath["statusCode"] != 200:
            logger.error(filepath["body"])
            break

        # setup a dictionary of metadata parameters to unpack in the
        # instrument table
        metadata_params = {
            "file_path": filepath["body"],
            "instrument": filename_parsed.instrument,
            "data_level": filename_parsed.data_level,
            "descriptor": filename_parsed.descriptor,
            "start_date": datetime.datetime.strptime(
                filename_parsed.startdate, "%Y%m%d"
            ),
            "end_date": datetime.datetime.strptime(filename_parsed.enddate, "%Y%m%d"),
            "version": filename_parsed.version,
            "extension": filename_parsed.extension,
        }

        # Add data to the file catalog
        with Session(engine) as session:
            session.add(models.FileCatalog(**metadata_params))
            session.commit()

            # TODO: These are sanity check. will remove
            # from upcoming PR
            result = session.query(models.FileCatalog).all()
            for row in result:
                print(row.instrument)
                print(row.file_path)

            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            print(table_names)
