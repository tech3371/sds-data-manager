"""Functions to generate SDC Spin and Repointing files."""

import logging
import tempfile
from datetime import datetime
from pathlib import Path

import boto3
import botocore
import pandas as pd
from imap_processing.spice.time import met_to_utc

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

session = boto3.Session(profile_name="imap-sdc")
# Create an S3 client
S3_CLIENT = session.client("s3")

SDC_SPIN_S3_PATH = "spice/sdc/spin"  # os.getenv("SDC_SPIN_S3_PATH")
SDC_REPOINT_S3_PATH = "spice/sdc/repoint"  # os.getenv("SDC_REPOINT_S3_PATH")

S3_BUCKET = "sds-data-449431850278"  # os.getenv("S3_BUCKET")


def _file_exists(s3_key_path):
    """Check if a file exists in the SDS storage bucket at this key."""
    try:
        S3_CLIENT.head_object(Bucket=S3_BUCKET, Key=s3_key_path)
        # If the head_object operation succeeds, that means there
        # is a file already at the specified path, so return a 409
        return True
    except botocore.exceptions.ClientError:
        # No file exists
        return False


def produce_sdc_spin_file(s3_key: str):
    """Produce SDC maintained spin file.

    Parameters
    ----------
    s3_bucket : S3 data bucket
        S3 bucket
    s3_key : str
        S3 key or filepath. Filepath of spin data.
        Eg. spice/spin/imap_2025_122_2025_122_01.spin.csv
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # get filename from s3_key
        filename = s3_key.split("/")[-1]
        # Read version from filename for later use
        version = filename.split("_")[-1].split(".")[0]
        tmp_filepath = tmp_dir + "/" + filename
        # Download data from S3
        S3_CLIENT.download_file(S3_BUCKET, s3_key, tmp_filepath)

        # read csv file
        data_df = pd.read_csv(tmp_filepath)

        # find the start time and end date and time
        # of the data in the file.
        min_start_time = data_df[
            data_df["spin_start_sec"] == data_df["spin_start_sec"].min()
        ]
        max_start_time = data_df[
            data_df["spin_start_sec"] == data_df["spin_start_sec"].max()
        ]

        # combine S/C start time sec and subsec to get the start
        # time
        file_start_sc_time = (
            min_start_time["spin_start_sec"].values[0]
            + min_start_time["spin_start_subsec"].values[0] / 1e3
        )
        # combine S/C end time and spin period to get the end time.
        file_end_sc_time = (
            max_start_time["spin_start_sec"].values[0]
            + max_start_time["spin_start_subsec"].values[0] / 1e3
            + max_start_time["spin_period_sec"].values[0]
        )

        # TODO: should we do this and if so how?
        # round up the end time and round down the start time so that we
        # query enough data for the user input time range.

        # Write start and end date in this format - YYYYmmddTHHMMSS. This
        # will be used to create the new file name.
        #   Eg. for SDC maintained spin file.
        #   imap_YYYYmmddTHHMMSS_YYYYmmddTHHMMSS_##.spin.csv
        # Convert S/C time to UTC
        file_start_time_utc = met_to_utc(file_start_sc_time, precision=6)
        file_end_time_utc = met_to_utc(file_end_sc_time, precision=6)

        # Format date to YYYYmmddTHHMMSS
        file_start_time_obj = datetime.strptime(
            file_start_time_utc, "%Y-%m-%dT%H:%M:%S.%f"
        )
        file_end_time_obj = datetime.strptime(file_end_time_utc, "%Y-%m-%dT%H:%M:%S.%f")
        file_start_time = file_start_time_obj.strftime("%Y%m%dT%H%M%S")
        file_end_time = file_end_time_obj.strftime("%Y%m%dT%H%M%S")

        sdc_filename = f"imap_{file_start_time}_{file_end_time}_{version}.spin.csv"

        # copy data from input csv to new csv file
        data_df.to_csv(sdc_filename, index=False)
        upload_s3_path = f"{SDC_SPIN_S3_PATH}/{sdc_filename}"
        if _file_exists(upload_s3_path):
            logger.info(f"{sdc_filename} already exists.")
            return
        # Upload the file to S3
        # S3_CLIENT.upload_file(sdc_filename, s3_bucket, upload_s3_path)


def append_data_to_repoint_file(s3_key: str):
    """Append data to the repoint file."""
    main_repoint_file = "repoint.csv"
    sdc_repoint_s3_path = f"{SDC_REPOINT_S3_PATH}/{main_repoint_file}"
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            sdc_repoint_path = tmp_dir + "/" + main_repoint_file
            # Download repoint file
            S3_CLIENT.download_file(S3_BUCKET, sdc_repoint_s3_path, sdc_repoint_path)
            sdc_repoint_df = pd.read_csv(sdc_repoint_path)
        except botocore.exceptions.ClientError:
            # Create new repoint file if it doesn't exist.
            # Start with an empty dataframe
            sdc_repoint_df = pd.DataFrame()
            pass

        new_repoint_filename = s3_key.split("/")[-1]
        new_repoint_local_path = tmp_dir + "/" + new_repoint_filename
        S3_CLIENT.download_file(S3_BUCKET, s3_key, new_repoint_local_path)
        # Read repoint files
        new_repoint_df = pd.read_csv(new_repoint_local_path)
        # Compare and write only new data to the repoint file
        new_data = new_repoint_df[~new_repoint_df.isin(sdc_repoint_df)].dropna()
        print(new_data)


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
    s3_key = event["detail"]["object"]["key"]
    logger.info(event)

    file_path = Path(s3_key)
    all_suffixes = file_path.suffixes  # Returns ['.spin', '.csv']
    file_extension = "".join(all_suffixes)  # Returns '.spin.csv'
    # Produce SDC maintained spin file
    if file_extension == ".spin.csv":
        produce_sdc_spin_file(s3_key)
        return {
            "statusCode": 200,
            "body": f"SDC spin file produced successfully for {s3_key}",
        }
    # Append data to the repoint file
    elif file_extension == ".repoint.csv":
        append_data_to_repoint_file(s3_key)
        return {
            "statusCode": 200,
            "body": f"Appended data from {s3_key} to repoint file successfully",
        }


if __name__ == "__main__":
    events = [
        {
            "detail-type": "Object Created",
            "source": "aws.s3",
            "account": "449431850278",
            "region": "us-west-2",
            "detail": {
                "version": "0",
                "bucket": {"name": "sds-data-449431850278"},
                "object": {
                    "key": "spice/spin/imap_2025_122_2025_122_01.spin.csv",
                },
            },
        },
        {
            "detail-type": "Object Created",
            "source": "aws.s3",
            "account": "449431850278",
            "region": "us-west-2",
            "detail": {
                "version": "0",
                "bucket": {"name": "sds-data-449431850278"},
                "object": {
                    "key": "spice/repoint/imap_2025_230_2025_230_01.repoint.csv",
                },
            },
        },
    ]
    for event in events:
        lambda_handler(event, None)
