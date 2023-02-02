import json
import urllib.parse
import boto3
import logging 
import os 
import sys
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.payload import Payload
from sds_in_a_box.SDSCode.opensearch_utils.action import Action
from sds_in_a_box.SDSCode.opensearch_utils.client import Client
from sds_in_a_box.SDSCode.opensearch_utils.query import Query
from opensearchpy import OpenSearch, RequestsHttpConnection

def _create_open_search_client():
    hosts = [{"host":os.environ["OS_DOMAIN"], "port":int(os.environ["OS_PORT"])}]
    auth = (os.environ["OS_ADMIN_USERNAME"], os.environ["OS_ADMIN_PASSWORD_LOCATION"])
    return Client(hosts=hosts, http_auth=auth, use_ssl=True, verify_certs=True, connnection_class=RequestsHttpConnection)

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))
    
    query = Query(event["queryStringParameters"])
    client = _create_open_search_client()

    search_result = client.search(query, Index(os.environ["OS_INDEX"]))
    logger.info("Query Search Results: " + json.dumps(search_result))
    return search_resultresult