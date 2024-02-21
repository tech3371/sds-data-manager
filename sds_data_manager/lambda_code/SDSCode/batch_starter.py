"""Functions for supporting the batch starter component of the architecture."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

import boto3
from imap_data_access import ScienceFilePath
from sqlalchemy.orm import Session

from .database import database as db
from .database import models
from .lambda_custom_events import IMAPLambdaPutEvent

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def query_instrument(session, upstream_dependency, start_date, end_date):
    """Append start_time, end_time and version information to downstream dependents.

    Parameters
    ----------
    session : orm session
        Database session.
    upstream_dependency : dict
        Dictionary of upstream dependency.
    start_date : str
        Start date of the event data.
    end_date : str
        End date of the event data.

    Returns
    -------
    record : models.FileCatalog or None
        The first FileCatalog record matching the query criteria.
        None is returned if no record matches the criteria.

    """
    instrument = upstream_dependency["instrument"]
    data_level = upstream_dependency["data_level"]
    version = upstream_dependency["version"]

    record = (
        session.query(models.FileCatalog)
        .filter(
            models.FileCatalog.instrument == instrument,
            models.FileCatalog.data_level == data_level,
            models.FileCatalog.version == version,
            models.FileCatalog.start_date >= datetime.strptime(start_date, "%Y%m%d"),
            models.FileCatalog.end_date <= datetime.strptime(end_date, "%Y%m%d"),
        )
        .first()
    )

    return record


def append_attributes(session, downstream_dependents, start_date, end_date, version):
    """Append start_time, end_time and version information to downstream dependents.

    Parameters
    ----------
    session : orm session
        Database session.
    downstream_dependents : list of dict
        A list of dictionaries where each dictionary corresponds to a record
    start_date : str
        Start date of the event data.
    end_date : str
        End date of the event data.
    version : str
        Version of the event data.

    Returns
    -------
    downstream_dependents : list of dict
        Dictionary containing components with dates and versions appended.

    """
    for dependent in downstream_dependents:
        # TODO: query the version table here for appropriate version
        #  of each downstream_dependent.

        # TODO: add repointing table query if dependent is ENA or GLOWS
        #  Use start_date and end_date to query repointing table.
        # Use pointing start_time and end_time in place of start_date and end_date.
        # Add pointing number to dependent.

        dependent["version"] = version  # placeholder
        dependent["start_date"] = start_date
        dependent["end_date"] = end_date

    return downstream_dependents


def find_upstream_dependencies(
    downstream_dependent_instrument,
    downstream_dependent_inst_level,
    downstream_dependent_version,
    data,
):
    """Find dependency information for each instrument.

    Parameters
    ----------
    downstream_dependent_instrument : str
        Downstream dependent instrument.
    downstream_dependent_inst_level : str
        Downstream dependent data level.
    downstream_dependent_version : str
        Downstream dependent version.
    data : dict
        Dictionary containing dependency data.

    Returns
    -------
    upstream_dependencies : list of dict
        A list of dictionaries containing dependency instrument,
        data level, and version.

    Example:
    upstream_dependencies = find_upstream_dependencies("codice", "l3b", "v00-01", data)

    expected_result = [
        {"instrument": "codice", "data_level": "l2", "version": "v00-01"},
        {"instrument": "codice", "data_level": "l3a", "version": "v00-01"},
        {"instrument": "mag", "data_level": "l2", "version": "v00-01"},
    ]

    """
    upstream_dependencies = []

    for instr, data_levels in data.items():
        for data_level, deps in data_levels.items():
            if any(
                dep["instrument"] == downstream_dependent_instrument
                and dep["data_level"] == downstream_dependent_inst_level
                for dep in deps
            ):
                upstream_dependencies.append(
                    {"instrument": instr, "data_level": data_level}
                )

    for dependency in upstream_dependencies:
        # TODO: query the version table here for appropriate version
        #  of each dependency. Use downstream_dependent_version to query version table.
        dependency["version"] = downstream_dependent_version  # placeholder

    return upstream_dependencies


def query_upstream_dependencies(
    session, downstream_dependents, data, s3_bucket, descriptor
):
    """Find dependency information for each instrument.

    This function looks for upstream dependency of current downstream dependent.

    Parameters
    ----------
    session : orm session
        Database session.
    downstream_dependents : list of dict
        Dictionary containing components with dates and versions appended.
    data : dict
        Dictionary containing dependency data.
    s3_bucket : str
        S3 bucket name.
    descriptor : str
        The filename descriptor

    Returns
    -------
    instruments_to_process : list of dict
        A list of dictionaries containing the filename and prepared data.

    """
    instruments_to_process = []

    # Iterate over each downstream dependent
    for dependent in downstream_dependents:
        instrument = dependent["instrument"]
        data_level = dependent["data_level"]
        version = dependent["version"]
        start_date = dependent["start_date"]
        end_date = dependent["end_date"]

        # For each downstream dependent, find its upstream dependencies
        upstream_dependencies = find_upstream_dependencies(
            instrument, data_level, version, data
        )

        all_dependencies_available = True  # Initialize the flag
        for upstream_dependency in upstream_dependencies:
            # Check to see if each upstream dependency is available
            record = query_instrument(
                session, upstream_dependency, start_date, end_date
            )
            if record is None:
                all_dependencies_available = (
                    False  # Set flag to false if any dependency is missing
                )
                logger.info(
                    f"Missing dependency: {upstream_dependency['instrument']}, "
                    f"{upstream_dependency['data_level']}, "
                    f"{upstream_dependency['version']}"
                )
                break  # Exit the loop early as we already found a missing dependency
            else:
                logger.info(
                    f"Dependency found: {upstream_dependency['instrument']}, "
                    f"{upstream_dependency['data_level']}, "
                    f"{upstream_dependency['version']}"
                )

        # If all dependencies are available, prepare the data for batch job
        if all_dependencies_available:
            prepared_data = prepare_data(
                instrument=instrument,
                data_level=data_level,
                start_date=start_date,
                end_date=end_date,
                version=version,
                upstream_dependencies=upstream_dependencies,
            )
            instruments_to_process.append({"command": prepared_data})
            logger.info(f"All dependencies for {instrument} present.")
        else:
            logger.info(f"Some dependencies for {instrument} are missing.")

    return instruments_to_process


def load_data(filepath: Path):
    """Load dependency data.

    Parameters
    ----------
    filepath : Path
        Path of dependency data.

    Returns
    -------
    data : dict
        Dictionary containing dependency data.

    """
    with filepath.open() as file:
        data = json.load(file)

    return data


def prepare_data(
    instrument, data_level, start_date, end_date, version, upstream_dependencies
):
    """
    Prepare data for batch job.

    Parameters
    ----------
    instrument : str
        Instrument.
    data_level : str
        Data level.
    start_date : str
        Data start date.
    end_date : str
        Data start date.
    version : str
        version.
    upstream_dependencies : list of dict
        A list of dictionaries containing dependency instrument,
        data level, and version.

    Returns
    -------
    prepared_data : str
        Data to submit to batch job.

    """
    # Prepare batch job command
    # NOTE: Batch job expects command like this:
    # "Command": [
    #     "--instrument", "mag",
    #     "--data_level", "l1a",
    #     "--start-date", "20231212",
    #     "--end-date", "20231212",
    #     "--version", "v00-01",
    #     "--dependency", """[
    #         {
    #             'instrument': 'swe',
    #             'data_level': 'l0',
    #             'descriptor': 'lveng-hk',
    #             'start_date': '20231212',
    #             'end_date': '20231212',
    #             'version': 'v01-00',
    #         },
    #         {
    #             'instrument': 'mag',
    #             'data_level': 'l0',
    #             'descriptor': 'lveng-hk',
    #             'start_date': '20231212',
    #             'end_date': '20231212',
    #             'version': 'v00-01',
    #         }]""",
    #     "--use-remote"
    # ]
    prepared_data = [
        "--instrument",
        instrument,
        "--data_level",
        data_level,
        "--start-date",
        start_date,
        "--end-date",
        end_date,
        "--version",
        version,
        "--dependency",
        f"{upstream_dependencies}",
        "--use-remote",
    ]

    return prepared_data


def send_lambda_put_event(command_parameters):
    """Send custom PutEvent to EventBridge.

    Example of what PutEvent looks like:
    event = {
        "Source": "imap.lambda",
        "DetailType": "Job Started",
        "Detail": {
            "status": "INPROGRESS",
            "dependency": "[{
                "codice": "s3-test",
                "mag": "s3-filepath"
            }]")
        },
    }

    Parameters
    ----------
    command_parameters : str
        IMAP cli command input parameters.
        Example of input:
            "Command": [
            "--instrument", "mag",
            "--data_level", "l1a",
            "--start-date", "20231212",
            "--end-date", "20231212",
            "--version", "v00-01",
            "--dependency", \"""[
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
                }]\""",
            "--use-remote"
        ]

    Returns
    -------
    dict
        EventBridge response

    """
    event_client = boto3.client("events")

    # Get event inputs ready
    instrument = command_parameters[1]
    data_level = command_parameters[3]
    start_date = command_parameters[5]
    end_date = command_parameters[7]
    version = command_parameters[9]
    dependency = command_parameters[11]

    # Create event["detail"] information
    detail = {
        "status": models.Status.INPROGRESS.value,
        "instrument": instrument,
        "data_level": data_level,
        "start_date": start_date,
        "end_date": end_date,
        "version": version,
        "dependency": dependency,
    }

    # create PutEvent dictionary
    event = IMAPLambdaPutEvent(detail_type="Job Started", detail=detail)
    event_data = event.to_event()

    logger.info(f"Sending event to EventBridge - {event_data}")
    # Send event to EventBridge
    response = event_client.put_events(Entries=[event_data])
    return response


def lambda_handler(event: dict, context):
    """Entry point to the batch starter lambda."""
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    # Event details:
    filename = event["detail"]["object"]["key"]
    components = ScienceFilePath.extract_filename_components(filename)
    logger.info(f"Parsed filename - {components}")
    instrument = components["instrument"]
    data_level = components["data_level"]
    descriptor = components["descriptor"]
    version = components["version"]
    start_date = components["start_date"]
    end_date = components["end_date"]

    # S3 Bucket name.
    s3_bucket = os.environ.get("S3_BUCKET")

    # Retrieve dependency data.
    dependency_path = Path(__file__).resolve().parent / "downstream_dependents.json"
    data = load_data(dependency_path)
    logger.info(f"loaded dependent data - {data}")
    # Downstream dependents that are candidates for the batch job.
    downstream_dependents = data[instrument][data_level]

    # Get information for the batch job.
    region = os.environ.get("REGION")
    account = os.environ.get("ACCOUNT")
    # Create a batch client
    batch_client = boto3.client("batch")

    job_definition = (
        f"arn:aws:batch:{region}:{account}:job-definition/"
        f"fargate-batch-job-definition{instrument}"
    )
    job_queue = (
        f"arn:aws:batch:{region}:{account}:job-queue/"
        f"{instrument}-fargate-batch-job-queue"
    )

    # Get database engine.
    engine = db.get_engine()

    with Session(engine) as session:
        complete_dependents = append_attributes(
            session, downstream_dependents, start_date, end_date, version
        )

        # decide if we have sufficient upstream dependencies
        downstream_instruments_to_process = query_upstream_dependencies(
            session, complete_dependents, data, s3_bucket, descriptor
        )

        # No instruments to process
        if not downstream_instruments_to_process:
            logger.info("No instruments_to_process. Skipping further processing.")
            return

        # Start Batch Job execution for each instrument
        for downstream_data in downstream_instruments_to_process:
            command = downstream_data["command"]
            logger.info(f"Submitting job with this command - {command}")
            # NOTE: The batch job name should contain only
            # alphanumeric characters and hyphens.
            level_to_process = command[3]
            # Eg. "codice-l1a-job"
            job_name = f"{instrument}-{level_to_process}-job"
            logger.info("Job name: %s", job_name)
            response = batch_client.submit_job(
                jobName=job_name,
                jobQueue=job_queue,
                jobDefinition=job_definition,
                containerOverrides={
                    "command": command,
                },
            )
            logger.info(f"Submitted job - {response}")
            # Send EventBridge event to indexer lambda
            logger.info("Sending EventBridge event to indexer lambda.")
            send_lambda_put_event(command)
            logger.info("EventBridge event sent.")
