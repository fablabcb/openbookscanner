from .broker import ParseBroker, MessagePrintingSubscriber
from .parse_update import ParseUpdater
from .update_strategy import BatchStrategy
from .state.status import StatusStateMachine


class OpenBookScanner:
    """This is the main class working on the scanner."""
    
    public_channel_name = "OpenBookScanner"

    def __init__(self):
        """Create a new book scanner."""
        self.update_strategy = BatchStrategy()
        self.public_message_broker = ParseBroker(self.public_channel_name, self.update_strategy)
        self.status = self.public_state_machine(StatusStateMachine())
    
    def public_state_machine(self, state_machine):
        """Make the state machine public"""
        updater = ParseUpdater(state_machine, self.update_strategy)
        state_machine.observe_state(updater)
        self.public_message_broker.subscribe(state_machine)
        state_machine.subscribe(self.public_message_broker)
        return state_machine

    def run(self):
         while 1:
             self.update()
    
    def update(self):
        self.public_message_broker.receive_messages()
        self.update_strategy.batch()
        
    def print_messages(self):
        """Attach a receiver to the message broker to print them."""
        self.public_message_broker.subscribe(MessagePrintingSubscriber())



