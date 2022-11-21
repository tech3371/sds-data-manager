import unittest
from sds_in_a_box.SDSCode.opensearch_utils.action import Action
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.payload import Payload
from sds_in_a_box.SDSCode.opensearch_utils.client import Client
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3

class TestClient(unittest.TestCase):

    def setUp(self):
        #Opensearch client Params
        host = 'search-sds-metadata-uum2vnbdbqbnh7qnbde6t74xim.us-west-2.es.amazonaws.com/'
        port = 443
        region = 'us-west-2'
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, region)

        self.client = Client(hosts=host, http_auth=auth)

        self.index = Index("test_index")
        self.identifier = 1
        self.action = Action.CREATE
        self.body = "test body"
        self.document = Document(self.index, self.identifier, self.action, self.body)
        self.payload = Payload()

    def test_create_index(self):
        """
        test that the create_index method correctly creates a new index in OpenSearch.
        """
        #pass
        ## Arrange ## 
        index_exists_true = True

        ## Act ##
        self.client.create_index(self.index)

        index_exists_out = self.client.client.indices.exists(index.get_name())
        

        ## Assert ##
        assert index_exists_out == index_exists_true

    def test_create_document(self):
        """
        test that the create_document method correctly creates the specified document in OpenSearch.
        """
        ## Arrange ##
        #document_true = 

        ## Act ##
        #self.client.create_document(self.document)
        #document_out = client.get(self.identifier)

        ## Assert ##
        #print(document_out)
        pass


    def test_delete_document(self):
        """
        test that the create_document method correctly deletes the specified document in OpenSearch.
        """
        ## Arrange ##

        ## Act ##

        ## Assert ##
        pass
    
    def test_update_document(self):
        """
        test that the update_document method correctly updates the specified document in OpenSearch.
        """
        ## Arrange ##

        ## Act ##

        ## Assert ##
        pass

    def test_index_document(self):
        """
        test that the index_document method correctly indexes the specified document in OpenSearch.
        """
        ## Arrange ##

        ## Act ##

        ## Assert ##
        pass

    def test_send_payload(self):
        """
        test that the spend payload method correctly sends a bulk upload of the specified payload
        to OpenSearch.
        """
        ## Arrange ##
        #doc1 = Document(self.index, self.identifier, self.action, self.body)
        #doc2 = Document(self.index, 2, self.action, self.body)
        #self.payload.add_documents([doc1, doc2])

        ## Act ##
        #self.client.send_payload(self.payload)

        ## Assert ##
        pass

if __name__ == '__main__':
    unittest.main()
