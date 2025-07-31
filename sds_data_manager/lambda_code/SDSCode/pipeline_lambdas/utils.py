"""Utility functions for the SDS pipeline lambdas."""

import logging
import os

import boto3

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
