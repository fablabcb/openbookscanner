"""This is the interaction state machine.

Each message, a user sends to the book scanner goes to this machine.
It notifies the other state machines and creates a consistent and understandable transition for the user.

"""
from .state import State, StateMachine
from openbookscanner.message import message

class InteractionStateMixin:
    """These are useful funcitions that all states share."""
    
    def can_receive_test_scan(self):
        return False

class Ready(InteractionStateMixin, State):
    """The book scanner is ready to scan or performany other action."""

    def can_receive_test_scan(self):
        return True
    
    def receive_test_scan(self, message):
        """The user wishes to perform a test scan.
        
        We get a message with the settings and send this over to all the scanners.
        A scanner MUST respond with either a message.
        """
        self.deliver_message(m)


class WaitingForTheScannersToDeliverPicturesForTheTestScan(State):
    """"""
    
        



class Interaction(StateMachine):
    """This is the interaction state machine working on the user messages."""
    


