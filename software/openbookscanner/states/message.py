
class MessageCreator:
    """A simple way to create new massages."""

    def __getattr__(self, name):
        def create_message(**kw):
            kw.setdefault("type", "message")
            kw["name"] = name
            return kw
        create_message.__name__ += "_" + name
        setattr(self, name, create_message)
        return create_message

message = MessageCreator()


