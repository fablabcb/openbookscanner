"""
This module contains the message broker which distributes messages.

https://en.wikipedia.org/wiki/Message_broker

A broker has two responsibilities, as publisher and as subscriber


"""
from parse_rest.datatypes import Object
import json
from .update_strategy import OnChangeStrategy
from pprint import pprint
from .message import MessageDispatcher


class LocalSubscriber:
    """This is a local broker which just forwards the messages."""

    def __init__(self):
        """Create a new broker object."""
        self.subscribers = []
    
    def subscribe(self, subscriber):
        """Subscribe to all messages sent over the broker."""
        self.subscribers.append(subscriber)
    
    def deliver_message(self, message):
        """Send a message to all the subscribers."""
        for subscriber in list(self.subscribers):
            subscriber.receive_message(message)
    

class LocalBroker(LocalSubscriber):
    """Add receiving messages to the subscriber."""
    def receive_message(self, message):
        """When a broker receives a message, it delivers it."""
        self.deliver_message(message)


class BufferingBroker(LocalBroker):
    """This is a local broker which sends delivers the messages later."""
    
    def __init__(self):
        """Create a new broker which saves messages."""
        super().__init__()
        self.messages = []
    
    def deliver_message(self, message):
        """Save the message for receiving later."""
        self.messages.append(message)
    
    def flush(self):
        """Receive all saved messages."""
        while self.messages:
            message = self.messages.pop()
            super().deliver_message(message)


CHANNEL_CLASS_PREFIX = "Channel"

def get_channel_class(channel_name):
    return Object.factory(CHANNEL_CLASS_PREFIX + channel_name)


class ParseSubscriber:
    """A ParseBroker subscribes to all messages sent under ist name."""


    def __init__(self, channel_name, update_strategy=OnChangeStrategy()):
        """Create a parse message subscriber which is subscribed to all messages of a channel."""
        self.channel_name = channel_name
        self.channel_class = get_channel_class(channel_name)
        message_holder = self.channel_class()
        message_holder.messages = []
        message_holder.save()
        self.message_holder_id = message_holder.objectId
        self.subscribers = []
        self.update_strategy = update_strategy
        
    @property
    def channel(self):
        """The name of the channel we listen to."""
        return self.channel_name
        
    def _get_message_holder(self):
        return self.channel_class.Query.get(objectId=self.message_holder_id)

    def subscribe(self, subscriber):
        """Subscribe to all messages sent over the broker."""
        self.subscribers.append(subscriber)

    def flush(self):
        """Receive the messages."""
        message_holder = self._get_message_holder()
        messages = list(message_holder.messages)
        self.update_strategy.removeFromArray(message_holder, "messages", messages)
        for message in messages:
            for subscriber in self.subscribers:
                subscriber.receive_message(json.loads(message))

    def delete(self):
        """Delete the own objects on the parse server."""
        self.update_strategy.delete(self._get_message_holder())


class ParsePublisher:
    """This class publishes messages on a specific channel."""

    def __init__(self, channel_name, update_strategy=OnChangeStrategy()):
        """Create a new publisher and publish messages on a channel."""
        self.message_holder_class = Object.factory(CHANNEL_CLASS_PREFIX + channel_name)
        self.update_strategy = update_strategy
    
    def deliver_message(self, message):
        """Deliver a message to all Subscribers on a channel."""
        message = json.dumps(message)
        for subscriber in self.message_holder_class.Query.all():
#            print("deliver", message, "to", subscriber)
            self.update_strategy.addToArray(subscriber, "messages", [message])
    
    def receive_message(self, message):
        """When a publisher receives the message, it delivers it."""
        self.deliver_message(message)


class ParseBroker:
    """This is a parse broker which can send and receive on a channel."""

    def __init__(self, channel_name, update_strategy=OnChangeStrategy()):
        """Create a new ParseBroker for messages delivering and receiving on the channel."""
        self.publisher = ParsePublisher(channel_name, update_strategy)
        self.subscriber = ParseSubscriber(channel_name, update_strategy)
    
    def subscribe(self, subscriber):
        """Subscribe to the brokers messages."""
        self.subscriber.subscribe(subscriber)
    
    def flush(self):
        """Receive all messages and forward them to the subscribers."""
        self.subscriber.flush()
    
    def deliver_message(self, message):
        """Deliver a message to all brokers in the channel."""
        self.publisher.deliver_message(message)
    receive_message = deliver_message
    
    def delete(self):
        """Delete the own objects on the parse server."""
        self.subscriber.delete()


class MessagePrintingSubscriber:
    """When the this object receives a message, it prints it.
    
    This can be useful to debug activity of a subscriber."""
    
    def __init__(self, *args):
        """All arguments are passed to print."""
        self.args = args

    def receive_message(self, message):
        """Print a message."""
        print(*self.args, end=" ")
        pprint(message)

