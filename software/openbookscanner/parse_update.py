"""This module contains functionality to publish and update objects.


"""


from parse_rest.datatypes import Object
import json
from .update_strategy import OnChangeStrategy


class ParseUpdater:
    """Update the parsePlatform state of an object."""
    
    def __init__(self, obj, batch_strategy=OnChangeStrategy()):
        """Update the JSON representation of an object.
        
        - obj is the object to update.
          Requirements:
          - obj.toJSON() returns the JSON represenation of the object as dict
            - the "type" field is set to the type of the object
        - batch_mode whether to save the object in batch mode.
        """
        self.batch_strategy = batch_strategy
        self.obj = obj
        self.type = obj.toJSON()["type"]
        self.ParseClass = Object.factory(self.type)
        self.parse_object = self.ParseClass()
        self.update()
        
    @staticmethod
    def set_attr(obj, attr, data, default):
        """Set the attribute of the object depending on whether it is in json."""
        _default = object()
        value = data.get(attr, _default)
        has_value = value is not _default
        if not has_value:
            value = default
        if not isinstance(value, type(default)):
            # Attributes can only be of one type.
            value = default
            has_value = False
        obj[attr] = value
        obj["has_" + attr] = has_value
        obj.setdefault("attributes", [])
        if has_value:
            obj["attributes"].append(attr)
        return has_value

    def set_attributes(self, data):
        """Set the attributes of the parse object from a json dict."""
        self.parse_object.json = json.dumps(data)
        self.set_attr(self.parse_object.__dict__, "description", data, "")
        self.set_attr(self.parse_object.__dict__, "type", data, "unclassified")
        self.set_attr(self.parse_object.__dict__, "state", data, {})
        data_state = self.parse_object.state
        self.parse_object.state = json_state = {"json": json.dumps(data_state)}
        self.set_attr(json_state, "type", data_state, "unclassified")
        self.set_attr(json_state, "is_final", data_state, False)
        self.set_attr(json_state, "description", data_state, "")
        self.set_attr(json_state, "is_waiting_for_a_message_to_transition_to_the_next_state", data_state, False)
    
    def update(self):
        """Update the local represenation of the object using obj.toJSON() and save it to the server.
        """
        self.set_attributes(self.obj.toJSON())
        self.save()
    
    def save(self):
        """Save the object."""
        self.batch_strategy.save(self.parse_object)
    
    def delete(self):
        """Delete the object."""
        self.batch_strategy.delete(self.parse_object)
    
    def state_changed(self, obj):
        """Convinience method for subscribing an update to the state change of a state machine.
        
        The object is saved if it is the own object.
        """
        if obj == self.obj:
            self.update()
    
    def get_parse_object(self):
        """This returns the parse object."""
        return self.parse_object



