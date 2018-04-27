from .broker import ParseBroker, MessagePrintingSubscriber, ParsePublisher, BufferingBroker, ParseSubscriber, LocalBroker
from .parse_update import ParseUpdater
from .update_strategy import BatchStrategy
from .states.status import StatusStateMachine
from .states.state import StateChangeToMessageReceiveAdapter
from .states.scanner import ScannerListener
from parse_rest.datatypes import Object
from .message import message

import time


PUBLIC_MODEL_CLASS_NAME = "OpenBookScanner"


class OpenBookScanner:
    """This is the main class working on the scanner."""
    
    ModelClass = Object.factory(PUBLIC_MODEL_CLASS_NAME)
    
    public_channel_name_outgoing = "OpenBookScannerOutgoing"
    public_channel_name_incoming = "OpenBookScannerIncoming"

    def __init__(self):
        """Create a new book scanner.
        
        status(StatusStateMachine) --message--> public_message_buffer(BufferingBroker) --message---
        ---> public_message_broker(ParseBroker) --"""
        self.create_communication_channels()
        self.create_model()
            
    def create_communication_channels(self):
        """This creates the communication channels to the client."""
        self.update_strategy = BatchStrategy()
        self.outgoing_messages = BufferingBroker()
        self.outgoing_messages_publisher = ParsePublisher(self.public_channel_name_outgoing, self.update_strategy)
        self.incoming_messages = ParseSubscriber(self.public_channel_name_incoming)
        self.internal_messages = LocalBroker()

    def create_model(self):
        """This creates the model which is observable by the client."""
        self.model = self.ModelClass()
        self.model.save()
        # messaging
        self.outgoing_messages.subscribe(self.outgoing_messages_publisher)
        self.outgoing_messages.deliver_message(message.new_book_scanner_server(id=self.model.objectId))
        # status
        self.status = self.public_state_machine("status", StatusStateMachine())
        self.incoming_messages.subscribe(self.status)
        # scanner
        self.scanner_listener = self.public_state_machine("listener", ScannerListener())
        self.scanner_listener.register_hardware_observer(self)
        
    def new_hardware_detected(self, hardware):
        """Add new hardware to myself."""
        print("model -> new hardware", hardware)
        if hardware.is_scanner():
            self.public_state_machine("scanner", hardware)
            self.incoming_messages.subscribe(hardware)

    def public_state_machine(self, relation, state_machine):
        """Make the state machine public"""
        updater = ParseUpdater(state_machine, self.update_strategy)
        state_machine.register_state_observer(updater)
        state_machine.subscribe(self.outgoing_messages)
        state_machine.register_state_observer(StateChangeToMessageReceiveAdapter(self.internal_messages))
        self.model.relation(relation).add([updater.get_parse_object()])
        return state_machine

    def run(self):
         """Run the update in a loop."""
         while 1:
             self.update()
             time.sleep(0.5)
    
    def update(self):
        """Update the book scanner, send and receive messages."""
        self.incoming_messages.flush()
        self.update_state_machines()
        self.outgoing_messages.flush()
        self.update_strategy.batch()
    
    def update_state_machines(self):
        """Send an update message to the state machines."""
        self.scanner_listener.update()
        self.scanner_listener.update_hardware()
        
    def print_messages(self):
        """Attach a receiver to the message broker to print them."""
        self.outgoing_messages.subscribe(MessagePrintingSubscriber(self.public_channel_name_outgoing))
        self.internal_messages.subscribe(MessagePrintingSubscriber("Internal"))
        self.incoming_messages.subscribe(MessagePrintingSubscriber(self.public_channel_name_incoming))



