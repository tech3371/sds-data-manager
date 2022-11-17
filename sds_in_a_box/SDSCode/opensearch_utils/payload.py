from uploadTools.Document import Document
import json
from opensearchpy import OpenSearch, RequestsHttpConnection


class Payload():
    """
    Class to represent an OpenSearch bulk file payload.

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
    contents():
        returns the payload contents as a string
    """
    def __init__(self):
        self.payload_contents = ""
        self.payload_size = 0

    def add_documents(self, documents):
        """
        Add document(s) to the payload for a bulk upload.
        
        Parameters
        ----------
        documents: Document, list of Documents
            document(s) to be added to the payload in preparation for a bulk upload.
        """
        if type(documents) is Document:()
            self.payload_contents = self.payload_contents + documents.contents()

        elif type(documents) is list:
            concat_docs = [doc.contents() for doc in documents]
            self.payload_contents = self.payload_contents + "".join(concat_docs)

        else:
            raise TypeError("Input was of type {} must be of type Document or list of Documents.".format(type(documents)))

    def size_in_bytes(self):
        """Returns the size of the payload contents in bytes."""
        return len(self.payload_contents.encode("ascii"))

    def contents(self):
        """Returns the contents of the payload as a string"""
        return self.payload_contents

    def __repr__(self):
        return str(self.payload_contents)