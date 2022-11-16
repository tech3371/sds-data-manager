import json
from sds_in_a_box.SDSCode.opensearch_utils.index import Index
from sds_in_a_box.SDSCode.opensearch_utils.action import Action


class Document():

    def __init__(self, index, doc_id, action, body="",):
        self.index = Index.validate_index(index)
        self.identifier = self.__validate_identifier(doc_id)
        self.body = body
        self.action = Action.validate_action(action)
        self.contents = ""
        self.size = 0

        self.__update_contents()

    def update_body(self, body):
        """
        Updates the body of the document.

        Parameters
        ----------
        body: str
            updated body text for the document.
        """
        if type(body) is str:
            self.body = body
            self.__update_contents()
        else:
            raise TypeError("Document body passed in as type {}, but must be of type str".format(type(body)))
            
    
    def get_body(self):
        """Returns the body of the document as a string"""
        return self.body

    def get_index(self):
        """Returns the name of the document's index as a string"""
        return self.index.get_name()

    def get_action(self):
        """Returns the document's action as a string"""
        return self.action

    def get_identifier(self):
        """Returns the document's id as an int"""
        return self.identifier
    
    def size_in_bytes(self):
        """Returns the size of the document's bulk request json string in bytes."""
        return self.size

    def __update_contents(self):
        action_string = \
                '{ "' \
                + self.action.value \
                + '" : {"_index": "' \
                + self.index.get_name() \
                + '", "_id" : "' \
                + str(self.identifier) + '"}}\n'
        self.contents = action_string + self.body + "\n"
        self.size = len(self.contents.encode("ascii"))

    def __validate_identifier(self, identifier):
        if type(identifier) is int:
            return identifier
        else:
            raise TypeError("Identifier is of type {}, but must be of type int".format(type(index)))
            
            

    def __repr__(self):
        return str(self.contents)
