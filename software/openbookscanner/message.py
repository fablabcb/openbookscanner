"""
This module contains a way to create new messages and document the accordingly.

"""


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

    def __call__(self, name, data):
        """Create a message with a specific name."""
        return getattr(self, name)(**data)

message = MessageCreator()
message.update.describe_as("""This message is used to update the states of state machines.

If states are running they can not update the state machine.
In this case, this message allows the state to transition.
""")
message.test.describe_as("""This is a test message not used in production code.""")
message.state_changed.describe_as("""When a state machine changes a state, this message is sent.""")
message.new_book_scanner_server("""This message announces a new book scanner.

This is a debug message which allows you to see if you fetched the right book scanner.
""")

