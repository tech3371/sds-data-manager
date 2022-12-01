import unittest
from sds_in_a_box.SDSCode.opensearch_utils.action import Action
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.payload import Payload
from sds_in_a_box.SDSCode.opensearch_utils.client import Client
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from botocore.exceptions import ClientError

class TestClient(unittest.TestCase):

    def setUp(self):
        #Opensearch client Params
        host = 'search-sds-metadata-uum2vnbdbqbnh7qnbde6t74xim.us-west-2.es.amazonaws.com'
        port = 443
        hosts = [{"host":host, "port":port}]
        
        secret_name = "OpenSearchPassword9643DC3D-uVH94BjrbF9u"
        region_name = "us-west-2"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response['SecretString']

        auth = ("master-user", secret)
        self.client = Client(hosts=hosts, http_auth=auth, use_ssl=True, verify_certs=True, connnection_class=RequestsHttpConnection)

        self.index = Index("test_index")
        self.action = Action.INDEX
        self.document = Document(self.index, 1, self.action, {'test body': 10})

        self.payload = Payload()

    def test_create_index(self):
        """
        test that the create_index method correctly creates a new index in OpenSearch.
        """
        ## Arrange ## 
        index_exists_true = True

        ## Act ##
        self.client.create_index(self.index)

        index_exists_out = self.client.index_exists(self.index)      

        ## Assert ##
        assert index_exists_out == index_exists_true

    def test_create_document(self):
        """
        test that the create_document method correctly creates the specified document in OpenSearch.
        """
        ## Arrange ##
        self.client.create_index(self.index)
        document_true = {'_index': 'test_index', '_type': '_doc', '_id': '1', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'test body': 10}}

        ## Act ##
        self.client.create_document(self.document)
        document_out = self.client.get_document(self.document)

        ## Assert ##
        assert document_true == document_out

        ## TearDown ##
        self.client.delete_document(self.document)


    def test_delete_document(self):
        """
        test that the create_document method correctly deletes the specified document in OpenSearch.
        """
        ## Arrange ##
        self.client.create_index(self.index)
        self.client.create_document(self.document)
        exists_true = False

        exists_confirm = self.client.document_exists(self.document)
        assert exists_confirm == True

        ## Act ##
        self.client.delete_document(self.document)
        exists_out = self.client.document_exists(self.document)

        ## Assert ##
        assert exists_out == exists_true
    
    def test_update_document(self):
        """
        test that the update_document method correctly updates the specified document in OpenSearch.
        """
        ## Arrange ##
        self.client.create_index(self.index)
        self.client.create_document(self.document)
        self.document.update_body({'test body': 20})
        # the version number increments each time a doc is updated (starts at 1)
        # _seq_no increments for each operation performed on the document (starts at 0)
        document_true = {'_index': 'test_index', '_type': '_doc', '_id': '1', '_version': 2, '_seq_no': 1, '_primary_term': 1, 'found': True, '_source': {'test body': 20}}
        
        ## Act ##
        self.client.update_document(self.document)
        document_out = self.client.get_document(self.document)

        ## Assert ##
        assert document_out == document_true

        ## TearDown ##
        self.client.delete_document(self.document)

    def test_index_document(self):
        """
        test that the index_document method correctly indexes the specified document in OpenSearch.
        """
        ## Arrange ##
        self.client.create_index(self.index)
        document_true = {'_index': 'test_index', '_type': '_doc', '_id': '1', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'test body': 10}}
        
        ## Act ##
        self.client.index_document(self.document)
        document_out = self.client.get_document(self.document)

        
        ## Assert ##
        assert document_out == document_true

        ## TearDown ##
        self.client.delete_document(self.document)

    def test_send_payload(self):
        """
        test that the spend payload method correctly sends a bulk upload of the specified payload
        to OpenSearch.
        """
        ## Arrange ##
        self.client.create_index(self.index)
        document2 = Document(self.index, 2, self.action, {'test body': 10})
        self.payload.add_documents([self.document, document2])

        document_true = {'_index': 'test_index', '_type': '_doc', '_id': '1', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'test body': 10}}
        document2_true = {'_index': 'test_index', '_type': '_doc', '_id': '2', '_version': 1, '_seq_no': 0, '_primary_term': 1, 'found': True, '_source': {'test body': 10}}

        ## Act ##
        self.client.send_payload(self.payload)
        document_out = self.client.get_document(self.document)
        document2_out = self.client.get_document(document2)

        ## Assert ##
        assert (document_out == document_true) and (document2_out == document2_true)

        ## TearDown ##
        self.client.delete_document(self.document)
        self.client.delete_document(document2)

    def tearDown(self):
        self.client.delete_index(self.index)
        self.client.close()

if __name__ == '__main__':
    unittest.main()
