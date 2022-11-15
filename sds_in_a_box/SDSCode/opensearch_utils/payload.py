from uploadTools.Document import Document
import json
from opensearchpy import OpenSearch, RequestsHttpConnection


class Payload():

    def __init__(self):
        self.payload_contents = ""
        self.payload_size = 0

    def add_documents(self, documents):
        if type(documents) is Document:
            documents.format_for_bulk_request()
            self.payload_contents = self.payload_contents + str(documents)

        elif type(documents) is list:
            concat_docs = [str(doc.format_for_bulk_request()) for doc in documents]
            self.payload_contents = self.payload_contents + "".join(concat_docs)

        else:
            pass
            # need to raise some exception here

    def size_in_bytes(self):
        return len(self.payload_contents.encode("ascii"))


    def contents(self):
        return self.payload_contents


    def upload_to(self, client):
        client.bulk(self.payload_contents, params={"request_timeout":1000000})


    def __repr__(self):
        return str(self.payload_contents)