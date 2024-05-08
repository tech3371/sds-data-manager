"""Define lambda to support the upload API."""

import json
import logging
import os

import boto3
import botocore
import imap_data_access

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET_NAME = os.getenv("S3_BUCKET")
S3_CLIENT = boto3.client("s3")


def _file_exists(s3_key_path):
    """Check if a file exists in the SDS storage bucket at this key."""
    try:
        S3_CLIENT.head_object(Bucket=BUCKET_NAME, Key=s3_key_path)
        # If the head_object operation succeeds, that means there
        # is a file already at the specified path, so return a 409
        return True
    except botocore.exceptions.ClientError:
        # No file exists
        return False


def _generate_signed_upload_response(s3_key_path, tags=None):
    """Create a presigned url for a file in the SDS storage bucket.

    Parameters
    ----------
    s3_key_path : str
        The fully qualified path of the object to upload.
    tags : dict, optional
         Additional S3 object metadata to add to the object.

    Returns
    -------
    Response with status code and a pre-signed URL for the object.
    """
    if _file_exists(s3_key_path):
        # We already have a file at this location, return a 409
        return {
            "statusCode": 409,
            "body": json.dumps(f"{s3_key_path} already exists."),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
    # We know there isn't an object at this location, so
    # generate a pre-signed URL for the client to upload to
    url = S3_CLIENT.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": s3_key_path,
            "Metadata": tags or dict(),
        },
        ExpiresIn=3600,
    )

    if url is None:
        return {
            "statusCode": 400,
            "body": json.dumps(
                "A pre-signed URL could not be generated. Please ensure that the "
                "file name matches mission file naming convention "
                f"{imap_data_access.FILENAME_CONVENTION} or is a valid SPICE file."
            ),
        }

    return {"statusCode": 200, "body": json.dumps(url)}


def lambda_handler(event, context):
    """Entry point to the upload API lambda.

    This function returns an S3 signed-URL based on the input filename,
    which the user can then use to upload a file into the SDS.

    Parameters
    ----------
    event : dict
        Specifically looking at the event['pathParameters']['proxy'], which
        specifies the filename to upload.
    context : None
        Currently not used

    Returns
    -------
    dict
        A pre-signed url where users can upload a data file to the SDS.

    """
    path_params = event.get("pathParameters", {}).get("proxy", None)
    logger.debug("Parsing path parameters=[%s] from event=" "[%s]", path_params, event)

    if not path_params:
        return {
            "statusCode": 400,
            "body": json.dumps(
                "No filename given for the upload. Please provide a filename "
                "in the path. Eg. /upload/path/to/file/filename.pkts"
            ),
        }

    filename = os.path.basename(path_params)
    try:
        return _spice_file_upload(filename)
    except imap_data_access.SPICEFilePath.InvalidSPICEFileError:
        # Not a good SPICE filename, continue on and try science file type next
        pass

    # Upload for science files, which will catch other filetype errors
    return _science_file_upload(filename)


def _spice_file_upload(filename):
    """Handle SPICE file uploads and place them in the proper location."""
    # Will raise SPICEFilePath.InvalidSPICEFileError if the filename is invalid
    # We catch that in the calling routine
    spice_file = imap_data_access.SPICEFilePath(filename)

    s3_key_path = spice_file.construct_path()
    # Strip off the data directory for s3 uploads
    s3_key_path = s3_key_path.relative_to(
        imap_data_access.config["DATA_DIR"]
    ).as_posix()
    s3_key_path = str(s3_key_path)
    # check if this SPICE file already exists, return a 409 if so

    return _generate_signed_upload_response(s3_key_path)


def _science_file_upload(filename):
    """Handle Science file uploads and place them in the proper location."""
    try:
        science_file = imap_data_access.ScienceFilePath(filename)
    except imap_data_access.ScienceFilePath.InvalidScienceFileError as e:
        logger.error(str(e))
        return {"statusCode": 400, "body": str(e)}

    s3_key_path = science_file.construct_path()
    # Strip off the data directory to get the upload path + name
    # Must be posix style for the URL
    s3_key_path_str = str(
        s3_key_path.relative_to(imap_data_access.config["DATA_DIR"]).as_posix()
    )

    return _generate_signed_upload_response(s3_key_path_str)
