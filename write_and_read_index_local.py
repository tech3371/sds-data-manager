from opensearchpy import RequestsHttpConnection
from sds_in_a_box.SDSCode.opensearch_utils.action import Action
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.payload import Payload
from sds_in_a_box.SDSCode.opensearch_utils.client import Client
import os


def lambda_handler(event, context):
    # create opensearch client
    hosts = [{"host":os.environ["OS_DOMAIN"], "port":int(os.environ["OS_PORT"])}]
    auth = (os.environ["OS_ADMIN_USERNAME"], os.environ["OS_ADMIN_PASSWORD"])
    client = Client(hosts=hosts, http_auth=auth, use_ssl=True, verify_certs=True, connnection_class=RequestsHttpConnection)
    index = 'metadata'

    sample_payload = {
        "Records": [
            {
            "s3": {
                "bucket": {
                "name": "IMAP-Data-Bucket"
                },
                "object": {
                "key": "imap_l0_instrument_date_version.fits",
                "size": 1305107
                }
            }
            }
        ]
    }

    index = Index('metadata')
    # try:
    #     client.delete_index(index)
    # except:
    #     pass

    # client.create_index(index)

    # create document and payload
    body = {'mission': 'imap', 'level': 'l0', 'instrument': 'instrument', 'date': 'date', 'version': 'version', 'extension': 'fits'}
    identifier = sample_payload['Records'][0]['s3']['object']['key']
    action = Action.CREATE
    document = Document(index, identifier, action, body=body)
    payload = Payload()

    # upload document
    filename = sample_payload["Records"][0]['s3']['object']['key']
    document = Document(index, filename, action, body)
    payload.add_documents(documents=document)
    client.send_payload(payload)
    # search index
    response = client.client.search(index='metadata')

    print(response)

lambda_handler(None, None)