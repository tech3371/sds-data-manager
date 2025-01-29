"""Functions to write SPICE ingested files to EFS."""

import logging
from datetime import datetime
from pathlib import Path

import boto3
import pandas as pd
from imap_processing.spice.time import met_to_utc

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the paths
spice_mount_path = Path("spice")  # Eg. /mnt/spice

# Create an S3 client
s3_client = boto3.client("s3")


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
    key = "imap_2025_122_2025_122_01.spin.csv"
    data_df = pd.read_csv(key)
    version = key.split("_")[-1].split(".")[0]
    # find earliest time and get the row
    min_start_time = data_df[
        data_df["spin_start_sec"] == data_df["spin_start_sec"].min()
    ]
    max_start_time = data_df[
        data_df["spin_start_sec"] == data_df["spin_start_sec"].max()
    ]

    # Write start and end date in this format - yyyymmddTHHMMSS
    # round up the end time and round down the start time so that we
    # query enough data for the user input
    # yyyymmddTHHMMSS
    # Eg. for SDC maintained spin file.
    # imap_yyyymmmTHHMMSS_yyyymmmTHHMMSS_##.spin.csv

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

    file_start_time_utc = met_to_utc(file_start_sc_time, precision=6)
    file_end_time_utc = met_to_utc(file_end_sc_time, precision=6)

    # Format date to yyyymmddTHHMMSS
    file_start_time_obj = datetime.strptime(file_start_time_utc, "%Y-%m-%dT%H:%M:%S.%f")
    file_end_time_obj = datetime.strptime(file_end_time_utc, "%Y-%m-%dT%H:%M:%S.%f")
    file_start_time = file_start_time_obj.strftime("%Y%m%dT%H%M%S")
    file_end_time = file_end_time_obj.strftime("%Y%m%dT%H%M%S")

    sdc_filename = f"imap_{file_start_time}_{file_end_time}_{version}.spin.csv"
    # copy data from input csv to new csv file
    data_df.to_csv(sdc_filename, index=False)
    # Upload the file to S3
    s3_client.upload_file(sdc_filename, s3_bucket, f"spice/spin/{sdc_filename}")


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
