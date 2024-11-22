"""Functions to write SPICE ingested files to EFS."""

import logging
import os
from pathlib import Path

import boto3
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the paths
spice_mount_path = Path("spice")  # Eg. /mnt/spice

# Create an S3 client
s3_client = boto3.client("s3")


def create_symlink(source_path: Path, destination_path: Path) -> None:
    """Create a symlink from source_path to destination_path.

    Parameters
    ----------
    source_path : str
        Source path of the symlink
    destination_path : str
        Destination path of the symlink

    """
    # Remove the old symlink
    destination_path.unlink(missing_ok=True)

    # Create a new symlink pointing to the new file
    destination_path.symlink_to(source_path)


def write_data_to_efs(s3_key: str, s3_bucket: str):
    """Write data to EFS and create/update symlink.

    Parameters
    ----------
    s3_key : str
        S3 object key
    s3_bucket : str
        The S3 bucket

    """
    # Remove 'spice/' prefix from the s3 key. See key example below.
    #   Eg. spice/spin/imap_2025_122_2025_122_02.spin.csv
    # Keep remaining folder path after `spice/` to match the folder structure
    # defined in imap-data-access library.
    s3_folder_path = os.path.dirname(s3_key).replace("spice/", "")
    filename = os.path.basename(s3_key)
    # Download path to EFS
    efs_spice_path = spice_mount_path / s3_folder_path

    try:
        # Create the folder if it does not exist
        efs_spice_path.mkdir(parents=True, exist_ok=True)
        # Download file from S3 to the EFS path
        s3_client.download_file(s3_bucket, s3_key, efs_spice_path / filename)
        logger.info(f"{s3_key} file downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading file: {e!s}")

    logger.info("File was written to EFS path: %s", efs_spice_path)


def produce_sdc_maintained_files(s3_bucket: str, s3_key: str):
    """Produce SDC maintained files.

    Parameters
    ----------
    s3_bucket : str
        S3 bucket
    s3_key : str
        S3 key
    """
    # take in the s3 key and bucket

    # Download s3 file in temporary directory
    # with tempfile.TemporaryDirectory() as tmpdir:
    #     tmpfile = Path(tmpdir) / "tmpfile"
    #     s3_client.download_file(s3_bucket, s3_key, tmpfile)

    #     # Read the csv file
    #     with open(tmpfile, "r") as f:
    #         # Read the first line
    #         first_line = f.readline()

    # read csv file and find the start time and end date and time
    # of the data in the file.
    data_df = pd.read_csv("imap_2025_122_2025_122_01.spin.csv")
    # find earliest time and get the row
    min_start_time = data_df[
        data_df["spin_start_sec"] == data_df["spin_start_sec"].min()
    ]
    max_start_time = data_df[
        data_df["spin_start_sec"] == data_df["spin_start_sec"].max()
    ]
    # start time is the first spin start time.
    file_start_sc_time = (
        min_start_time["spin_start_sec"].values[0]
        + min_start_time["spin_start_subsec"].values[0] / 1e3
    )
    # end time is last spin start time + spin period.
    file_end_sc_time = (
        max_start_time["spin_start_sec"].values[0]
        + max_start_time["spin_start_subsec"].values[0] / 1e3
        + max_start_time["spin_period_sec"].values[0]
    )
    print(file_start_sc_time)
    print(file_end_sc_time)
    # Write start and end date in this format - yyyymmddTHHMMSS
    # round up the end time and round down the start time so that we
    # query enough data for the user input
    # yyyymmddTHHMMSS
    # Eg. for SDC maintained spin file.
    # imap_yyyymmmTHHHMMSS_yyyymmmTHHHMMSS_##.spin.csv


def lambda_handler(event, context):
    """Lambda is triggered by eventbridge.

    Input looks like this:
    {
        "version": "0",
        "id": "3ee8fb2e-856d-790d-1d81-f77e1f3c0987",
        "detail-type": "Object Created",
        "source": "aws.s3",
        "account": "449431850278",
        "time": "2023-10-25T23:53:17Z",
        "region": "us-west-2",
        "resources": [
            "arn:aws:s3:::sds-data-449431850278"
        ],
        "detail": {
            "version": "0",
            "bucket": {
                "name": "sds-data-449431850278"
            },
            "object": {
                "key": "spice/spin/imap_2025_122_2025_122_02.spin.csv",
                "size": 8,
                "etag": "fd33e2e8ad3cb1bdd3ea8f5633fcf5c7",
                "version-id": "w9eElv_lFFeEbifMabOBHjtJl9Ori_At",
                "sequencer": "006539AA6D7936ACF5"
            },
            "request-id": "5V837ESMXGRD39D2",
            "requester": "449431850278",
            "source-ip-address": "128.138.64.30",
            "reason": "PutObject"
        }
    }

    Parameters
    ----------
    event : dict
        Event input
    context : LambdaContext
        This object provides methods and properties that provide information
        about the invocation, function, and runtime environment.

    Returns
    -------
    dict
        Response message

    """
    # Retrieve the S3 bucket and key from the event
    s3_bucket = event["detail"]["bucket"]["name"]
    s3_key = event["detail"]["object"]["key"]
    logger.info(event)

    # write_data_to_efs(s3_key, s3_bucket)
    produce_sdc_maintained_files(s3_bucket, s3_key)

    return {"statusCode": 200, "body": "File downloaded and moved successfully"}


if __name__ == "__main__":
    event = {
        "version": "0",
        "id": "3ee8fb2e-856d-790d-1d81-f77e1f3c0987",
        "detail-type": "Object Created",
        "source": "aws.s3",
        "account": "449431850278",
        "time": "2023-10-25T23:53:17Z",
        "region": "us-west-2",
        "resources": ["arn:aws:s3:::sds-data-449431850278"],
        "detail": {
            "version": "0",
            "bucket": {"name": "sds-data-449431850278"},
            "object": {
                "key": "spice/spin/imap_2025_122_2025_122_02.spin.csv",
                "size": 8,
                "etag": "fd33e2e8ad3cb1bdd3ea8f5633fcf5c7",
                "version-id": "w9eElv_lFFeEbifMabOBHjtJl9Ori_At",
                "sequencer": "006539AA6D7936ACF5",
            },
            "request-id": "5V837ESMXGRD39D2",
            "requester": "449431850278",
            "source-ip-address": "128.138.64.30",
            "reason": "PutObject",
        },
    }
    lambda_handler(event, None)
