import json


class Document():

    action_types = ['create', 'delete', 'index', 'update']

    def __init__(self, index, doc_id, contents=None):
        self.index = index
        self.doc_id = doc_id
        self.contents = contents
        self.bulk_doc = ""
        self.doc_size = 0

    def create(self, client):
        client.create(self.index.name(), self.doc_id, body = self.contents)
        
    def delete(self, client):
        client.delete(self.index.name(), self.doc_id)

    def index(self):
        client.index(self.index.name(), self.doc_id, body = self.contents)

    def update(self):
        client.update(self.index.name(), self.doc_id, body = self.contents)

    def format_for_bulk_request(self, action):
        if action not in action_types:
            # raise an error here
        else:
            action_string = \
                    '{ "delete" : {"_index": "' \
                    + self.index.name() \
                    + '", "_id" : "' \
                    + str(self.doc_id) + '"}}\n'
            self.json_doc = action_string + "\n"
            self.doc_size = len(self.json_doc.encode("ascii"))

    def size_in_bytes(self):
        return self.doc_size

    def __repr__(self):
        return str(self.json_doc)