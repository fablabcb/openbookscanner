from .broker import ParseBroker, MessagePrintingSubscriber, ParsePublisher, BufferingBroker, ParseSubscriber
from .parse_update import ParseUpdater
from .update_strategy import BatchStrategy
from .states.status import StatusStateMachine
from .states.state import StateChangeToMessageReceiveAdapter

import time


class OpenBookScanner:
    """This is the main class working on the scanner."""
    
    public_channel_name_outgoing = "OpenBookScannerOutgoing"
    public_channel_name_incoming = "OpenBookScannerIncoming"

    def __init__(self):
        """Create a new book scanner.
        
        status(StatusStateMachine) --message--> public_message_buffer(BufferingBroker) --message---
        ---> public_message_broker(ParseBroker) --"""
        self.update_strategy = BatchStrategy()
        self.outgoing_messages = BufferingBroker()
        self.outgoing_messages_publisher = ParsePublisher(self.public_channel_name_outgoing, self.update_strategy)
        
        
        self.incoming_messages = ParseSubscriber(self.public_channel_name_incoming)

        self.status = self.public_state_machine(StatusStateMachine())
    
    def public_state_machine(self, state_machine):
        """Make the state machine public"""
        updater = ParseUpdater(state_machine, self.update_strategy)
        state_machine.observe_state(updater)
        state_machine.subscribe(self.outgoing_messages)
        state_machine.observe_state(StateChangeToMessageReceiveAdapter(self.outgoing_messages))
        return state_machine

    def run(self):
         """Run the update in a loop."""
         while 1:
             self.update()
             time.sleep(0.5)
    
    def update(self):
        """Update the book scanner, send and receive messages."""
        self.outgoing_messages.flush()
        self.incoming_messages.flush()
        self.update_strategy.batch()
        
    def print_messages(self):
        """Attach a receiver to the message broker to print them."""
        self.outgoing_messages.subscribe(MessagePrintingSubscriber(self.public_channel_name_outgoing))
        self.incoming_messages.subscribe(MessagePrintingSubscriber(self.public_channel_name_incoming))



