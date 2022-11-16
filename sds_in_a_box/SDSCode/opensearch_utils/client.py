from index import Index
from document import Document


class Client():

    def __init__(self):
        pass

    def create_index(self, index):
        """
        Creates an index in the database.

        Parameters
        ----------
        index: Index
            index to be created in the database

        """"
        response = self.client.indicies.create(index.name(), body=index.body()) 
        
    def create_document(self, document):
        """
        Creates the document in the database. Returns a 409 response 
        when a document with a same ID already exists in the index.

        Parameters
        ----------
        document: Document 
            Document to be added to the database

        """
        self.client.create(document.index().name(), document.id(), body = document.body())

    def delete_document(self, document):
        """
        Deletes the document in the database.

        Parameters
        ----------
        document: Document
            Document to be deleted from the database

        """
        self.client.delete(document.index().name(), document.id())

    def update_document(self, document):
        """
        Updates the document in the database if it exists, returns an error
        if it doesn't exist.

        Parameters
        ----------
        document: Document
             Document to be updated in the database

        """
        client.update(document.index().name(), document.id(), body = document.body())

    def index_document(self, document):
        """
        Creates the document in the database if it does not already exist. 
        If the document does exist, it will update the document.

        Parameters
        ----------
         document: Document 
            Document to be created or updated in the database

        """
        client.index(document.index().name(), document.id(), body = document.body())

    def perform_document_action(self, document):
        # not sure if it's better to get the action from the document
        # or to be explicit with the method name
        pass

    def send_payload(self, payload):
        """
        Sends a bulk payload of documents to the database

        Parameters
        ----------
        payload: Payload
            payload containing bulk documents to be sent to the database
        """
        self.client.bulk(payload.contents(), params={"request_timeout":1000000})