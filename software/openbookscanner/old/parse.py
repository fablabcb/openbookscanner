"""This module contains additional behavior for Parse objects."""


class GCReference:
    """This is a reference to a parse object which deletes the object once it is deleted."""
    
    def __init__(self, parse_object, update_strategy):
        """Delete the object using the preferred update strategy."""
        self.parse_object = parse_object
        self.update_strategy = update_strategy
    
    def delete(self):
        """Delete the object."""
        self.update_strategy.delete(self.parse_object)
    
    def __del__(self):
        """Delete the object when garbage collected."""


