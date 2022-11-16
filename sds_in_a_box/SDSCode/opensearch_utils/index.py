from opensearchpy import OpenSearch

class Index():
    def __init__(self, name, body=None):
        self.name = name
        self.body = body

    def get_name(self):
        """Returns the name of the index"""
        return self.name
    
    def get_body(self):
        """Returns the body of the index"""
        return self.body()

    def __repr__(self):
        return str({self.index_name:self.index_body})

    @staticmethod
    def validate_index(index):
        """
        Static method used to validate whether an object
        is of type Index. If the input is an Index, the same
        Index is returned. If the input is not an Index, an
        error is raised.

        Parameters
        ----------
        index : an object to be validated as an Index

        Returns
        -------
        Index
            the validated index, same the object input
        
        """
        if type(index) is Index:
            return index
        else:
            raise TypeError("Input is of type {}, but must be of type Index".format(type(index)))