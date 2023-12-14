# Standard
import json
import logging
import os
import sys

# Installed
import boto3
from opensearchpy import RequestsHttpConnection
from SDSCode.path_helper import FilenameParser

# Local
from .opensearch_utils.action import Action
from .opensearch_utils.client import Client
from .opensearch_utils.document import Document
from .opensearch_utils.index import Index
from .opensearch_utils.payload import Payload
from .opensearch_utils.snapshot import run_backup

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

s3 = boto3.client("s3")


def _create_open_search_client():
    """Retrieve secrets from Secrets Manager and creates an Open Search client.

    This function retrieves the secret from the Secrets Manager and uses
    the secrets, along with other environment variables, to establish a
    secure connection to the OpenSearch cluster.

    Returns
    -------
    elasticsearch.Elasticsearch
        An instance of the OpenSearch client connected to the specified cluster.
    """
    hosts = [{"host": os.environ["OS_DOMAIN"], "port": int(os.environ["OS_PORT"])}]

    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=os.environ["REGION"]
    )
    response = client.get_secret_value(SecretId=os.environ["SECRET_ID"])

    auth = (os.environ["OS_ADMIN_USERNAME"], response["SecretString"])

    return Client(
        hosts=hosts,
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connnection_class=RequestsHttpConnection,
    )


def lambda_handler(event, context):
    """Handler function for creating metadata, adding it to the payload,
    and sending it to the opensearch instance.

    This function is an event handler called by the AWS Lambda upon the creation of an
    object in a s3 bucket.

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

    # Grab environment variables
    host = os.environ["OS_DOMAIN"]
    snapshot_repo_name = os.environ["SNAPSHOT_REPO_NAME"]
    snapshot_s3_bucket = os.environ["S3_SNAPSHOT_BUCKET_NAME"]
    snapshot_role_arn = os.environ["SNAPSHOT_ROLE_ARN"]
    region = os.environ["REGION"]

    # create opensearch client
    client = _create_open_search_client()
    # create index (AKA 'table' in other database)
    metadata_index = Index(os.environ["METADATA_INDEX"])
    data_tracker_index = Index(os.environ["DATA_TRACKER_INDEX"])

    # create a payload
    document_payload = Payload()

    # We're only expecting one record, but for some reason the Records are a list object
    for record in event["Records"]:
        # Retrieve the Object name
        logger.info(f"Record Received: {record}")
        filename = record["s3"]["object"]["key"]

        logger.info(f"Attempting to insert {os.path.basename(filename)} into database")
        # TODO: change below logics to use new FilenameParser
        # when we create schema and write file metadata to DB
        filename_parsed = FilenameParser(filename)
        filename_parsed.upload_filepath()
        metadata = None

        # TODO: remove this check since upload api validates filename?
        # Found nothing. This should probably send out an error notification
        # to the team, because how did it make its way onto the SDS?
        if metadata is None:
            logger.info("Found no matching file types to index this file against.")
            return None

        logger.info("Found the following metadata to index: " + str(metadata))

        # use the s3 path to file as the ID in opensearch
        s3_path = os.path.join(os.environ["S3_DATA_BUCKET"], filename)
        # create a document for the metadata and add it to the payload
        opensearch_doc = Document(metadata_index, s3_path, Action.CREATE, metadata)
        document_payload.add_documents(opensearch_doc)

        # Write processing status data to opensearch as well.
        data_tracker_doc = Document(
            data_tracker_index, filename, Action.CREATE, metadata
        )
        document_payload.add_documents(data_tracker_doc)

    # send the paylaod to the opensearch instance
    client.send_payload(document_payload)

    # take OpenSearch Snapshot
    run_backup(host, region, snapshot_repo_name, snapshot_s3_bucket, snapshot_role_arn)

    client.close()
