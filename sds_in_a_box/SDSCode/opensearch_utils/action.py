from enum import Enum


class Action(Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    INDEX = "index"

    @staticmethod
    def validate_action(action):
        """
        Static method used to validate whether an object
        is of type Action. If the input is an Action, the same
        Action is returned. If the input is not an Action, an
        error is raised.

        Parameters
        ----------
        action : an object to be validated as an action

        Returns
        -------
        Action
            the validated action, same the object input
        
        """
        if type(action) is Action:
            return action
        else:
            raise TypeError("Input is of type {}, but must be of type Action".format(type(action)))