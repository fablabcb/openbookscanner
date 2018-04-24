"""This is the general state of the book scanner.

"""
from .state import StateMachine, State


class Working(State):
    """The OpenBookScanner is working fine."""
    
    def on_enter(self):
        print("Working")
    
    def receive_error_occurred(self, message):
        self.transition_into(Error())


class Error(State):
    """The state machine is in a state where an error needs to be removed by hand."""

    def on_enter(self):
        print("Error")
    
    def receive_error_has_been_removed(self, message):
        """The error has been removed."""
        self.transition_into(Working())
    

class StatusStateMachine(StateMachine):
    """This state machine tracks the status of the whole machine."""

    first_state = Working

