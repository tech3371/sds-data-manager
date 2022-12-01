import unittest
import json
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.action import Action
from opensearchpy import OpenSearch, RequestsHttpConnection


class TestDocument(unittest.TestCase):

    def setUp(self):
        self.document_body = {"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}
        self.index_name = "my_index"
        self.index = Index(self.index_name)
        self.identifier = 1
        self.action = Action.CREATE

    def test_update_body(self):
        """
        test that the update_body method correctly updates the body
        of the document.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action)
        body_true = self.document_body

        ## Act ##
        document.update_body(self.document_body)
        body_out = document.get_body()

        ## Assert ##
        assert body_out == body_true

    def test_update_body_error(self):
        """
        test that the update_body method throws an error when the 
        wrong type is passed in.
        """
        ## Arrange ##
        body = 12
        document = Document(self.index, self.identifier, self.action)

        ## Act / Assert ##
        self.assertRaises(TypeError, document.update_body, body)
        
    def test_get_body(self):
        """
        test that the get_body method returns the document body as a string.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action, self.document_body)
        body_true = self.document_body
        
        ## Act ##
        body_out = document.get_body()

        ## Assert ##
        assert body_out == body_true

    def test_get_index(self):
        """
        test that the get_index method correctly returns the document's index's name of the index.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action)
        index_true = self.index.get_name()

        ## Act ##
        index_out = document.get_index()

        ## Assert ##
        assert index_out == index_true

    def test_get_action(self):
        """
        test that the get_action method correctly returns the document's action.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action)
        action_true = self.action

        ## Act ##
        action_out = document.get_action()

        ## Assert ##
        assert action_out == action_true

    def test_get_identifier(self):
        """
        test that the get_identifier method correctly returns the document's identifier.
        """
        ## Arrange ##
        identifier_true = str(self.identifier)
        document = Document(self.index, identifier_true, self.action)

        ## Act ##
        identifier_out = document.get_identifier()
        
        ## Assert ##
        assert identifier_out == identifier_true
    
    def test_get_contents(self):
        """
        test that the get_contents method correctly returns the document
        contents as a string.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action, self.document_body)
        contents_true = '{ "create": { "_index": "my_index", "_id": "1" } }\n{"mission": "imap", "level": "l0", "instrument": "*", "date": "*", "version": "*", "extension": "fits"}\n'

        ## Act ##
        contents_out = document.get_contents()
        
        ## Assert ##
        print()
        print(contents_true)
        print(contents_out)
        assert contents_out == contents_true


    def test_size_in_bytes(self):
        """
        test that the size_in_bytes method correctly returns the document's size in bytes.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action, self.document_body)
        doc = '{ "create": { "_index": "my_index", "_id": "1" } }\n{\'mission\': \'imap\', \'level\': \'l0\', \'instrument\': \'*\', \'date\': \'*\', \'version\': \'*\', \'extension\': \'fits\'}\n'
        size_in_bytes_true = len(doc.encode("ascii"))

        ## Act ##
        size_in_bytes_out = document.size_in_bytes()

        ## Assert ##
        assert size_in_bytes_out == size_in_bytes_true
    
    def test_is_document_true(self):
        """
        test that the static method is_document correctly returns whether the input is of type Document.
        """
        ## Arrange ##
        document = Document(self.index, self.identifier, self.action)
        result_true = True

        ## Act ##
        result_out = Document.is_document(document)

        ## Assert ##
        assert result_out == result_true

    def test_is_document_false(self):
        """
        test that the static method is_document correctly returns whether the input is of type Document.
        """
        ## Arrange ##
        document = "string, not a document"
        result_true = False

        ## Act ##
        result_out = Document.is_document(document)

        ## Assert ##
        assert result_out == result_true

if __name__ == '__main__':
    unittest.main()