"""Functions for supporting the indexer component of the architecture."""

import json
import logging
import os
from datetime import datetime

import boto3
from imap_data_access import ScienceFilePath
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import database as db
from .database import models
from .database_handler import update_file_catalog_table, update_status_table
from .lambda_custom_events import IMAPLambdaPutEvent

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def get_file_creation_date(file_path):
    """Get s3 file creation date.

    Parameters
    ----------
    file_path: str
        S3 object path. Eg. filepath/filename.ext

    creation_date: datetime.datetime
        Last modified data of s3 file.

    """
    # Create an S3 client
    s3_client = boto3.client("s3")

    # Retrieve the metadata of the object
    bucket_name = os.environ.get("S3_DATA_BUCKET")
    logger.info(f"looking up ingestion date for {file_path}")

    response = s3_client.head_object(Bucket=bucket_name, Key=file_path)
    file_creation_date = response["LastModified"]

    # LastModified looks like this:
    # 2024-01-25 23:35:26+00:00
    return file_creation_date


def get_dependency(instrument, data_level, descriptor, direction, relationship):
    """Make query to dependency table to get dependency.

    TODO: Move this function to batch starter after February demo or keep it here
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
        query = select(models.PreProcessingDependency.__table__).where(
            models.PreProcessingDependency.primary_instrument == instrument,
            models.PreProcessingDependency.primary_data_level == data_level,
            models.PreProcessingDependency.primary_descriptor == descriptor,
            models.PreProcessingDependency.direction == direction,
            models.PreProcessingDependency.relationship == relationship,
        )
        results = session.execute(query).all()
        for result in results:
            dependency.append(result)
    return dependency


def http_response(headers=None, status_code=200, body="Success"):
    """Customize HTTP response for the lambda function.

    Parameters
    ----------
    headers : dict, optional
        Content headers for the response, defaults to Content-type: text/html.
    status_code : int, optional
        HTTP status code indicating the result of the operation, defaults to 200.
    body : str, optional
        The content of the response, defaults to 'Success'.

    Returns
    -------
    dict
        A dictionary containing headers, status code, and body, designed to be returned
        by a Lambda function as an API response.

    """
    if headers is None:
        headers = (
            {
                "Content-Type": "text/html",
            },
        )
    return {
        "headers": headers,
        "statusCode": status_code,
        "body": body,
    }


def send_event_from_indexer(filename):
    """Send custom PutEvent to EventBridge.

    Example of what PutEvent looks like:
    event = {
        "Source": "imap.lambda",
        "DetailType": "Processed File",
        "Detail": {
            "object": {
                  "key": filename
            },
        },
    }

    Parameters
    ----------
    filename : str
        The filename to use in the PutEvent

    Returns
    -------
    dict
        EventBridge response

    """
    logger.info("in send event function")
    event_client = boto3.client("events")

    # Create event["detail"] information
    # TODO: This is what batch starter expect
    # as input. Revisit this.
    detail = {"object": {"key": filename}}

    # create PutEvent dictionary
    event = IMAPLambdaPutEvent(detail_type="Processed File", detail=detail)
    event_data = event.to_event()
    logger.info(f"sending this detail to event - {event_data}")

    # Send event to EventBridge
    response = event_client.put_events(Entries=[event_data])
    logger.info(f"response - {response}")
    return response


def s3_event_handler(event):
    """S3 events handler.

    S3 event handler takes s3 event and then writes information to
    file catalog table. It also sends event to the batch starter
    lambda once it finishes writing information to database.

    Parameters
    ----------
    event : dict
        The JSON formatted document with the data required for the
        lambda function to process

    Returns
    -------
    dict
        HTTP response

    """
    # Retrieve the Object name
    s3_filepath = event["detail"]["object"]["key"]

    filename = os.path.basename(s3_filepath)
    # TODO: add checks for SPICE or other
    # data types

    # setup a dictionary of metadata parameters to unpack in the
    # file catalog table. Eg.
    # {
    #     "file_path": None,
    #     "instrument": self.instrument,
    #     "data_level": self.data_level,
    #     "descriptor": self.descriptor,
    #     "start_date": datetime.strptime(self.startdate, "%Y%m%d"),
    #     "end_date": datetime.strptime(self.enddate, "%Y%m%d"),
    #     "version": self.version,
    #     "extension": self.extension,
    #     "ingestion_date": date_object,
    # }
    file_params = ScienceFilePath.extract_filename_components(filename)
    # delete mission key from metadata params
    file_params.pop("mission")
    # TODO: update these later once imap-data-access is updated.
    # It corrects key names temporarily.
    # convert start date and end date to datetime objects
    file_params["data_level"] = file_params.pop("datalevel")
    file_params["start_date"] = datetime.strptime(
        file_params.pop("startdate"), "%Y%m%d"
    )
    file_params["end_date"] = datetime.strptime(file_params.pop("enddate"), "%Y%m%d")

    file_params["file_path"] = s3_filepath

    ingestion_date_object = get_file_creation_date(s3_filepath)

    file_params["ingestion_date"] = ingestion_date_object
    update_file_catalog_table(file_params)
    logger.info("Wrote data to file catalog table")

    # Send event from this lambda for Batch starter
    # lambda
    send_event_from_indexer(filename)
    logger.debug("S3 event handler complete")


def batch_event_handler(event):
    """Batch event handler.

    Parameters
    ----------
    event : dict
        The JSON formatted document with the data required for the
        lambda function to process

    Example event input:
    Kept only parameter of interest
    event = {
        "detail-type": "Batch Job State Change",
        "source": "aws.batch",
        "detail": {
            "jobName": "test-batch-tenzin",
            "status": "FAILED",
            "statusReason": "some error message",
            "container": {
                "image": (
                    "123456789012.dkr.ecr.us-west-2.amazonaws.com/" "codice-repo:latest"
                ),
                "command": [
                    "--instrument",
                    "swe",
                    "--level",
                    "l1b",
                    "--file_path",
                    "imap/swe/l1b/2023/09/imap_swe_l1b_lveng-hk_20230927_20230927_v01-00.cdf",
                    "--dependency",
                    "[{'instrument': 'swe', 'level': 'l0', 'version': 'v00-01'}]"
                ],
            },
        },
    }

    Returns
    -------
    dict
        HTTP response

    """
    command = event["detail"]["container"]["command"]

    # Get filename from batch job command
    file_path_to_create = command[5]
    # Get job status
    job_status = (
        models.Status.SUCCEEDED
        if event["detail"]["status"] == "SUCCEEDED"
        else models.Status.FAILED
    )

    with Session(db.get_engine()) as session:
        # Had to query this way because the select statement
        # returns a RowProxy object when it executes it,
        # not the actual StatusTracking model instance,
        # which is why it can't update table row directly.
        result = (
            session.query(models.StatusTracking)
            .filter(models.StatusTracking.file_path_to_create == file_path_to_create)
            .first()
        )

        if result is None:
            logger.info(
                "No existing record found, creating"
                " new record for {file_path_to_create}"
            )
            status_params = {
                "file_path_to_create": file_path_to_create,
                "status": job_status,
            }
            update_status_table(status_params)
            result = (
                session.query(models.StatusTracking)
                .filter(
                    models.StatusTracking.file_path_to_create == file_path_to_create
                )
                .first()
            )

        result.status = job_status
        result.job_definition = event["detail"]["jobDefinition"]
        # TODO: get other information post discussion
        session.commit()

    return http_response(status_code=200, body="Success")


def custom_event_handler(event):
    """Event handling logic.

    Parameters
    ----------
    event : dict
        The JSON formatted document with the data required for the
        lambda function to process

    PutEvent Example:
        {
        "DetailType": "Batch Job Started",
        "Source": "imap.lambda",
        "Detail": {
          "file_path_to_create": "str",
          "status": "INPRGRESS",
          "dependency": json.dumps({
              "codice": "s3-filepath",
              "mag": "s3-filepath"}
          )
        }}

    Returns
    -------
    dict
        HTTP response

    """
    file_path_to_create = event["detail"]["file_path_to_create"]
    filename = os.path.basename(file_path_to_create)
    logger.info(f"Attempting to insert {filename} into database")

    # Check if the file is a valid science file or not
    sci_file = ScienceFilePath(filename)

    # Write event information to status tracking table.
    logger.info(f"Inserting {filename} into database")
    status_params = {
        "file_path_to_create": str(sci_file.construct_path()),
        "status": models.Status.INPROGRESS,
        "job_definition": None,
    }
    update_status_table(status_params)

    logger.debug("Wrote data to status tracking table")
    return http_response(status_code=200, body="Success")


# Handlers mapping
event_handlers = {
    "aws.s3": s3_event_handler,
    "aws.batch": batch_event_handler,
    "imap.lambda": custom_event_handler,
}


def handle_event(event, handler):
    """Event handling logic."""
    try:
        handler(event)
        return http_response(status_code=200, body="Success")
    except ScienceFilePath.InvalidScienceFileError as e:
        logger.error(str(e))
        return http_response(status_code=400, body=str(e))


def lambda_handler(event, context):
    """Create metadata and add it to the database.

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
    source = event.get("source")

    handler = event_handlers.get(source)
    if handler:
        return handle_event(event, handler)
    else:
        logger.error("Unknown event source")
        return http_response(status_code=400, body="Unknown event source")
