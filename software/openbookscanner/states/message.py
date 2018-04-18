"""
This module contains a way to create new messages and document the accordingly.

"""


class MessageCreator:
    """A simple way to create new massages."""

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

message = MessageCreator()
message.update.describe_as("""This message is used to update the states of state machines.

If states are running they can not update the state machine.
In this case, this message allows the state to transition.
""")

