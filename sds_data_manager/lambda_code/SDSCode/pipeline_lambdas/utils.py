"""Utility functions for the SDS pipeline lambdas."""

import logging
import os
from datetime import datetime

import boto3
import spiceypy

# Define constants needed in the file
SPACECRAFT_ID = -43
minimum_mission_time = datetime(2010, 1, 1)
maximum_mission_time = datetime(2145, 1, 1)
MAXIMUM_DATETIME_INTERVAL = [[minimum_mission_time, maximum_mission_time]]
MAXIMUM_SCLK_INTERVAL = [
    ["1/0410227203:00000", "1/4288750963:38093"]
]  # Calculated from the above datetimes seperately
MAXIMUM_J2000_INTERVAL = [
    [725803269.1839136, 4575787269.183866]
]  # Calculated from the above datetimes seperately

# Set constants for the time interval calculations
COVERAGE_ANGULAR_VELOCITY_ONLY = False  # Only include segments with angular velocity?
COVERAGE_SPICE_ARRAY_LENGTH = 10000  # Use an array size of 10000 for coverage calc
COVERAGE_LEVEL = "INTERVAL"  # the granularity at which the coverage is examined
COVERAGE_TOLERANCE = 0.0  # Tolerance value expressed in ticks of the spacecraft.
COVERAGE_TIME_SYSTEM = "TDB"  # Whether to use J2000 (TDB) or spacecraft clock (SCLK)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_file_ingestion_date(file_path):
    """Get s3 file ingestion date.

    Parameters
    ----------
    file_path: str
        S3 object path. Eg. filepath/filename.ext

    Returns
    -------
    file_ingestion_date: datetime.datetime
        Last modified data of s3 file.

    """
    # Create an S3 client
    s3_client = boto3.client("s3")

    # Retrieve the metadata of the object
    bucket_name = os.getenv("S3_BUCKET")
    logger.info(f"looking up ingestion date for {file_path}")

    response = s3_client.head_object(Bucket=bucket_name, Key=file_path)
    file_ingestion_date = response["LastModified"]

    # LastModified looks like this:
    # 2024-01-25 23:35:26+00:00
    return file_ingestion_date


def furnish_best_spice_file(kernel_type: str):
    """Furnish the best kernel for given type.

    Parameters
    ----------
    kernel_type: str
        Kernel type to furnish, e.g. 'leapseconds' or 'spacecraft_clock'.

    Returns
    -------
    highest_version_spice_file: Path
        The path to the SPICE file that was furnished
    """
    # Query for latest kernel
    metakernel_response = spice_metakernel_api.lambda_handler(
        {
            "queryStringParameters": {
                "start_time": 0,
                "end_time": MAXIMUM_J2000_INTERVAL[0][1],
                "list_files": "True",
                "file_types": kernel_type,
            }
        },
        None,
    )
    if metakernel_response["statusCode"] != 200:
        raise FileNotFoundError(
            f"Unable to find the latest {kernel_type} kernel. "
            "Please ensure that the kernel is available in the database."
        )
    kernel_filename = json.loads(metakernel_response["body"])[0]
    logger.info(f"Furnishing the latest {kernel_type} kernel: {kernel_filename}")
    # Download the latest kernel file
    highest_version_spice_file = download(kernel_filename)
    logger.info(f"Downloaded SPICE file: {highest_version_spice_file}")
    # Furnish the SPICE file
    spiceypy.furnsh(str(highest_version_spice_file))
    return highest_version_spice_file
