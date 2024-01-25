import json
import logging
import os

import boto3
from SDSCode.path_helper import ScienceFilepathManager

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def _generate_signed_upload_url(key_path, tags=None):
    """
    Create a presigned url for a file in the SDS storage bucket.

    :param key_path: Required.  A string representing the name of the object to upload.
    :param tags: Optional.  A dictionary that will be stored in the S3 object metadata.

    :return: A URL string if the file was found, otherwise None.
    """
    bucket_name = os.environ["S3_BUCKET"]
    url = boto3.client("s3").generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket_name[5:],
            "Key": key_path,
            "Metadata": tags or dict(),
        },
        ExpiresIn=3600,
    )

    return url


def lambda_handler(event, context):
    """
    The entry point to the upload API lambda.

    This function returns an S3 signed-URL based on the input filename,
    which the user can then use to upload a file into the SDS.

    :param event: Dictionary
        Specifically only requires event['queryStringParameters']['filename']
        User-specified key:value pairs can also exist in the 'queryStringParameters',
        storing these pairs as object metadata.
    :param context: Unused

    :return: A pre-signed url where users can upload a data file to the SDS.
    """
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    if "filename" not in event["queryStringParameters"]:
        return {
            "statusCode": 400,
            "body": json.dumps("Please specify a filename to upload"),
        }

    filename = event["queryStringParameters"]["filename"]

    science_file = ScienceFilepathManager(filename)

    if not science_file.is_valid:
        return {"statusCode": 400, "body": science_file.error_message}

    s3_key_path = science_file.construct_upload_path()

    url = _generate_signed_upload_url(s3_key_path, tags=event["queryStringParameters"])

    if url is None:
        return {
            "statusCode": 400,
            "body": json.dumps(
                "A pre-signed URL could not be generated. Please ensure that the "
                "file name matches mission file naming conventions."
            ),
        }

    return {"statusCode": 200, "body": json.dumps(url)}
