"""
This module contains the message broker which distributes messages.

https://en.wikipedia.org/wiki/Message_broker
"""
from parse_rest.datatypes import Object
import json
from .update_strategy import OnChangeStrategy

class LocalBroker:
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
    
    def receive_message(self, message):
        """When a broker receives a message, it delivers it."""
        self.deliver_message(message)


class DeferringBroker(LocalBroker):
    """This is a local broker which sends delivers the messages later."""
    
    def __init__(self):
        """Create a new broker which saves messages."""
        super().__init__()
        self.messages = []
    
    def deliver_message(self, message):
        """Save the message for receiving later."""
        self.messages.append(message)
    
    def receive_messages(self):
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
        self.channel_class = get_channel_class(channel_name)
        message_holder = self.channel_class()
        message_holder.messages = []
        message_holder.save()
        self.message_holder_id = message_holder.objectId
        self.subscribers = []
        self.update_strategy = update_strategy
        
    def _get_message_holder(self):
        return self.channel_class.Query.get(objectId=self.message_holder_id)

    def subscribe(self, subscriber):
        """Subscribe to all messages sent over the broker."""
        self.subscribers.append(subscriber)

    def receive_messages(self):
        """Receive the messages."""
        message_holder = self._get_message_holder()
        while message_holder.messages:
            message = message_holder.messages[0]
            message_holder.removeFromArray("messages", [message])
            self.update_strategy.save(message_holder)
            if message:
                for subscriber in self.subscribers:
                    subscriber.receive_message(json.loads(message))


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
            subscriber.addToArray("messages", [message])
            self.update_strategy.save(subscriber)


class ParseBroker:
    """This is a parse broker which can send and receive on a channel."""

    def __init__(self, channel_name, update_strategy=OnChangeStrategy()):
        """Create a new ParseBroker for messages delivering and receiving on the channel."""
        self.publisher = ParsePublisher(channel_name, update_strategy)
        self.subscriber = ParseSubscriber(channel_name, update_strategy)
    
    def subscribe(self, subscriber):
        """Subscribe to the brokers messages."""
        self.subscriber.subscribe(subscriber)
    
    def receive_messages(self):
        """Receive all messages and forward them to the subscribers."""
        self.subscriber.receive_messages()
    
    def deliver_message(self, message):
        """Deliver a message to all brokers in the channel."""
        self.publisher.deliver_message(message)
    receive_message = deliver_message


class MessagePrintingSubscriber:
    """When the this object receives a message, it prints it.
    
    This can be useful to debug activity of a subscriber."""

    def receive_message(self, message):
        """Print a message."""
        pprint(message)

