"""
This module contains a way to create new messages and document the accordingly.

"""

class MessageDispatcher:
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


def to_arduino(message):
    """Convert a message to the form that the arduino can use it.
    
    The message is a whole line ending with "\\r\\n".
    The name of the message is the content.
    """
    return message["name"] + "\r\n"

def from_arduino(string):
    """Get a message from the arduino.
    
    Messages starting with a "[" should have a "]" in it.
    These are log messages.
    All other messages expect a name of the message as the body.
    """
    string = string.strip()
    if string[0] == "[":
        print("string", repr(string))
        end_of_level = string.index("]")
        level = string[1:end_of_level]
        text = string[end_of_level + 1:].strip()
        return message.log(level=level, text=text)
    name = string
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

