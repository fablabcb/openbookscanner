"""
This module contains a way to create new messages and document the accordingly.

"""

class MessageReceiver:
    """Dispatch messages to methods."""

    def receive_message(self, message):
        """Receive a message and handle it.
        
        The message has a "name" key.
        If the state defines a method named "receive_" + the name, 
        this method handles the message.
        Otherwise, receive_unknown_message handles the message.
        """
        message_name = message["name"]
        method_name = "receive_" + message_name
        method = getattr(self, method_name, self.receive_unknown_message)
        method(message)

    def receive_unknown_message(self, message):
        """The state reacts to all messages which are not explicitely handeled."""


ARDUINO_ENCODING = "ASCII"

def to_arduino(message, encoding=ARDUINO_ENCODING):
    """Convert a message to the form that the arduino can use it."""
    return message["name"].encode(encoding) + b"\r\n"

def from_arduino(byte_sequence, encoding=ARDUINO_ENCODING):
    """Get a message from the arduino."""
    name = byte_sequence.strip().decode(encoding)
    return message(name)


class MessageCreator:
    """A simple way to create new messages.
    
    Example:
    
        message = MessageCreator()
        m = message.message_name(key="value")
        m = message("message_name", key="value")
    """

    def __getattr__(self, name):
        def create_message(**kw):
            kw.setdefault("type", "message")
            kw["name"] = name
            kw["description"] = create_message.__doc__
            return kw
        create_message.__name__ += "_" + name
        def document(string):
            create_message.__doc__ = string
        create_message.describe_as = document
        setattr(self, name, create_message)
        return create_message

    def __call__(self, name, data={}):
        """Create a message with a specific name.
        
        The data is a dictionary with the content of the message.
        """
        return getattr(self, name)(**data)

message = MessageCreator()
message.update.describe_as("""This message is used to update the states of state machines.

If states are running they can not update the state machine.
In this case, this message allows the state to transition.
""")
message.test.describe_as("""This is a test message not used in production code.""")
message.state_changed.describe_as("""When a state machine changes a state, this message is sent.""")
message.new_book_scanner_server.describe_as("""This message announces a new book scanner.

This is a debug message which allows you to see if you fetched the right book scanner.
""")
message.new_scan.describe_as("""A scanner made a new scan. This is the output image.""")
message.new_image.describe_as("""A new image was created.""")

