import json
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from opensearchpy import OpenSearch, RequestsHttpConnection


class Payload():
    """
    Class to represent an OpenSearch bulk document payload.

    ...


    Attributes
    ----------
    payload_contents: str
        json string with the payload contents.
    payload_size: int
        size of the payload contents as an encoded ascii string
        in bytes.

    Methods
    -------
    size_in_bytes():
        returns the size of the encoded ascii payload in bytes.
    get_contents():
        returns the payload contents as a string
    """
    def __init__(self):
        self.payload_contents = []
        self.payload_size = []

    def add_documents(self, documents):
        """
        Add document(s) to the payload for a bulk upload.
        
        Parameters
        ----------
        documents: Document, list of Documents
            document(s) to be added to the payload in preparation for a bulk upload.
        """       
        if Document.is_document(documents):
            self.__add_to_payload(documents)

        elif type(documents) is list:
            # check that all the objects in documents are of type Document
            if all(isinstance(doc, Document) for doc in documents): 
                concat_docs = [self.__add_to_payload(doc) for doc in documents]
            
            else:
                raise TypeError("Document list contained at least one object that was not of type Document")

        else:
            raise TypeError("Input was of type {} must be of type Document or list of Documents.".format(type(documents)))

    def get_contents(self):
        """Returns the contents of the payload as a string"""
        full_contents = "".join(self.payload_contents)
        return full_contents

    def __repr__(self):
        return str(self.payload_contents)

    def __add_to_payload(self, document):
        # TODO: not sure what the actual request limit is or how it's determined,
        # but the size of the encoded string seems to be the most consistent way to check
        # if the limit is hit and it seems to be somewhere around the bytes below
        request_limit = 5281500 #bytes

        if len(self.payload_contents) > 0 and self.__size_in_bytes(self.payload_contents[-1]) + document.size_in_bytes() < request_limit:
            self.payload_contents[-1] = self.payload_contents[-1] + document.get_contents()
        else:
            self.payload_contents.append(document.get_contents())

    def __size_in_bytes(self, payload):
        """Returns the size of the payload contents in bytes."""
        return len(payload.encode("ascii"))
