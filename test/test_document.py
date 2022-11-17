import unittest
import json
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.action import Action
from opensearchpy import OpenSearch, RequestsHttpConnection


class TestDocument(unittest.TestCase):

    def test_update_body(self):
        """
        test that the update_body method correctly updates the body.
        of the document
        """
        body = '{"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}'
        index = Index("my_index")
        action = Action.CREATE
        identifier = 1
        document = Document(index, identifier, action)

        document.update_body(body)

        assert document.get_body() == body

    def test_update_body_error(self):
        """
        test that the update_body method throws an error when the 
        wrong type is passed in.
        """
        body = 12
        index = Index("my_index")
        action = Action.CREATE
        identifier = 1
        document = Document(index, identifier, action)

        self.assertRaises(TypeError, document.update_body, body)
        
    def test_get_body(self):
        """
        test that the get_body method returns the document body as a string.
        """

        body = '{"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}'
        index = Index("my_index")
        action = Action.CREATE
        identifier = 1
        document = Document(index, identifier, action, body)

        assert document.get_body() == body

    def test_get_index(self):
        """
        test that the get_index method correctly returns the document's index's name of the index.
        """
        index = Index("my_index")
        action = Action.CREATE
        identifier = 1
        document = Document(index, identifier, action)

        assert document.get_index() == index.get_name()

    def test_get_action(self):
        """
        test that the get_action method correctly returns the document's action.
        """
        # Arrange
        index = Index("my_index")
        action = Action.CREATE
        identifier = 1
        document = Document(index, identifier, action)

        # Act
        action_out = document.get_action()

        # Assert
        assert action_out == action

    def test_get_identifier(self):
        """
        test that the get_identifier method correctly returns the document's identifier.
        """
        ## Arrange ##
        index = Index("my_index")
        action = Action.CREATE
        identifier_true = 1
        document = Document(index, identifier_true, action)

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
        body = '{"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}'
        index = Index("my_index")
        action = Action.CREATE
        identifier_true = 1
        document = Document(index, identifier_true, action, body)
        contents_true = '{ "create" : {"_index": "my_index", "_id" : "1"}}\n{"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}\n'

        ## Act ##
        contents_out = document.get_contents()
        
        ## Assert ##
        assert contents_out == contents_true


    def test_size_in_bytes(self):
        """
        test that the size_in_bytes method correctly returns the document's size in bytes.
        """
        ## Arrange ##
        body = '{"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}'
        index = Index("my_index")
        action = Action.CREATE
        identifier_true = 1
        document = Document(index, identifier_true, action, body)
        doc = '{ "create" : {"_index": "my_index", "_id" : "1"}}\n{"mission":"imap", "level":"l0", "instrument":"*", "date":"*", "version":"*", "extension":"fits"}\n'
        size_in_bytes_true = len(doc.encode("ascii"))

        ## Act ##
        size_in_bytes_out = document.size_in_bytes()

        ## Assert ##
        assert size_in_bytes_out == size_in_bytes_true
    

if __name__ == '__main__':
    unittest.main()