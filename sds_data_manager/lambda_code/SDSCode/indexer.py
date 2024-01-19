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
    for record in event["Records"]:
        # Retrieve the Object name
        logger.info(f"Record Received: {record}")
        filename = record["s3"]["object"]["key"]

        logger.info(f"Attempting to insert {os.path.basename(filename)} into database")
        filename_parsed = FilenameParser(filename)
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
            "ingestion_date": datetime.datetime.now(datetime.timezone.utc),
            "version": filename_parsed.version,
            "extension": filename_parsed.extension,
        }

        # The model lookup is used to match the instrument data
        # to the correct postgres table based on the instrument name.
        model_lookup = {
            "lo": models.LoTable,
            "hi": models.HiTable,
            "ultra": models.UltraTable,
            "hit": models.HITTable,
            "idex": models.IDEXTable,
            "swapi": models.SWAPITable,
            "swe": models.SWETable,
            "codice": models.CoDICETable,
            "mag": models.MAGTable,
            "glows": models.GLOWSTable,
        }

        # FileParser already confirmed that the file has a valid
        # instrument name.
        data = model_lookup[filename_parsed.instrument](**metadata_params)

        # Add data to the corresponding instrument database
        with Session(engine) as session:
            session.add(data)
            session.commit()

            # TODO: These are sanity check. will remove
            # from upcoming PR
            result = session.query(model_lookup[filename_parsed.instrument]).all()
            for row in result:
                print(row.instrument)
                print(row.file_path)

            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            print(table_names)
