from opensearchpy import OpenSearch

class Index():
    def __init__(self, index_name, index_body=None):
        self.index_name = index_name
        self.index_body = index_body

    def create(self, client):
        response = client.indicies.create(self.index_name, body=self.index_body)

    def name(self):
        return self.index_name

    def __repr__(self):
        return str({self.index_name:self.index_body})
