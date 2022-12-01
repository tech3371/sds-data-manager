from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from opensearchpy import OpenSearch, RequestsHttpConnection


class Client():
    """
    Class to represent the connection with the OpenSearch cluster.

    ...

    Attributes
    ----------
    hosts: list
        list of dicts containing the host and port.
        ex: [{'host': host, 'port': port}]
    http_auth: tuple
        tuple containing the authentication username and password for the 
        OpenSearch cluster.
    use_ssl: boolean
        turn on / off SSL.
    verify_certs: boolean
        turn on / off verification of SSL certificates.
    connection_class: 
        


    Methods
    -------
    create_index(index):
        creates an index in the OpenSearch cluster.
    create_document(document):
        creates a document in the OpenSearch cluster.
    delete_document(document):
        deletes a document in the OpenSearch cluster.
    update_document(document):
        updates a document in the OpenSearch cluster.
    index_document(document):
        creates new document in OpenSearch cluster if it does not exist,
        updates the existing one if it does exist.
    send_payload(payload):
        Sends a bulk payload of documents to the OpenSearch cluster.


    """
    def __init__(self, hosts, http_auth, use_ssl=True, verify_certs=True, connnection_class=RequestsHttpConnection):
        self.hosts = hosts
        self.http_auth = http_auth
        self.use_ssl = use_ssl
        self.verify_certs = verify_certs
        self.connnection_class = connnection_class
        self.client = OpenSearch(hosts=self.hosts, http_auth=self.http_auth, 
        use_ssl=self.use_ssl, verify_certs=self.verify_certs, connection_class=self.connnection_class)

    def create_index(self, index):
        """
        Creates an index in the OpenSearch cluster.

        Parameters
        ----------
        index: Index
            index to be created in the OpenSearch cluster

        """
        response = self.client.indices.create(index=index.get_name(), body=index.get_body()) 

    def delete_index(self, index):
        """
        Deletes an index in the OpenSearch cluster.

        Parameters
        ----------
        index: Index
            index to be deleted in the OpenSearch cluster

        """
        self.client.indices.delete(index=index.get_name())
        
    def index_exists(self, index):
        """
        Checks if a particular index exists.

        Parameters
        ----------
        index: Index, list
            index or list of indicies
        """
        return self.client.indices.exists(index.get_name())
            
        
    def create_document(self, document):
        """
        Creates the document in the OpenSearch cluster. Returns a 409 response 
        when a document with a same ID already exists in the index.

        Parameters
        ----------
        document: Document 
            Document to be added to the OpenSearch cluster

        """
        self.client.create(index=document.get_index(), id=document.get_identifier(), body=document.get_body())

    def delete_document(self, document):
        """
        Deletes the document in the OpenSearch cluster.

        Parameters
        ----------
        document: Document
            Document to be deleted from the OpenSearch cluster

        """
        self.client.delete(index=document.get_index(), id=document.get_identifier())

    def update_document(self, document):
        """
        Updates the document in the OpenSearch cluster if it exists, returns an error
        if it doesn't exist.

        Parameters
        ----------
        document: Document
             Document to be updated in the OpenSearch cluster

        """
        body = {'doc': document.get_body()}
        self.client.update(index=document.get_index(), id=document.get_identifier(), body = body)

    def index_document(self, document):
        """
        Creates the document in the OpenSearch cluster if it does not already exist. 
        If the document does exist, it will update the document.

        Parameters
        ----------
         document: Document 
            Document to be created or updated in the OpenSearch cluster

        """
        self.client.index(index=document.get_index(), id=document.get_identifier(), body = document.get_body())

    def document_exists(self, document):
        """Returns an boolean indicating whether the document exists in the index"""
        return self.client.exists(index=document.get_index(), id=document.get_identifier())

    def perform_document_action(self, document):
        # TODO: not sure if it's better to get the action from the document
        # or to be explicit with method names (above). This probably depends
        # on how we end up handling documents
        pass

    def send_payload(self, payload):
        """
        Sends a bulk payload of documents to the OpenSearch cluster

        Parameters
        ----------
        payload: Payload
            payload containing bulk documents to be sent to the OpenSearch cluster
        """
        self.client.bulk(payload.get_contents(), params={"request_timeout":1000000})

    def get_document(self, document):
        """Returns the specified document"""
        return self.client.get(index=document.get_index(), id=document.get_identifier())

    def close(self):
        """Close the Transport and all internal connections"""
        self.client.close()