"""
This module contains the message broker which distributes messages.

https://en.wikipedia.org/wiki/Message_broker
"""
from parse_rest.datatypes import Object
import json


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
        for subscriber in self.subscribers:
            subscriber.receive_message(message)
    receive_message = deliver_message

CHANNEL_CLASS_PREFIX = "Channel3"

def get_channel_class(channel_name):
    return Object.factory(CHANNEL_CLASS_PREFIX + channel_name)


class ParseSubscriber:
    """A ParseBroker subscribes to all messages sent under ist name."""


    def __init__(self, channel_name):
        """Create a parse message subscriber which is subscribed to all messages of a channel."""
        self.channel_class = get_channel_class(channel_name)
        message_holder = self.channel_class()
        message_holder.messages = []
        message_holder.save()
        print(vars(message_holder))
        self.message_holder_id = message_holder.objectId
        self.subscribers = []
        
    def get_message_holder(self):
        return self.channel_class.Query.get(objectId=self.message_holder_id)

    def subscribe(self, subscriber):
        """Subscribe to all messages sent over the broker."""
        self.subscribers.append(subscriber)

    def receive_messages(self):
        """Receive the messages."""
        message_holder = self.get_message_holder()
        while message_holder.messages:
            message = message_holder.messages[0]
            message_holder.removeFromArray("messages", [message])
            message_holder.save()
            print("message", message)
            if message:
                for subscriber in self.subscribers:
                    subscriber.receive_message(json.loads(message))


class ParsePublisher:
    """This class publishes messages no a specific channel."""

    def __init__(self, channel_name):
        self.message_holder_class = Object.factory(CHANNEL_CLASS_PREFIX + channel_name)
    
    def deliver_message(self, message):
        message = json.dumps(message)
        for subscriber in self.message_holder_class.Query.all():
            subscriber.addToArray("messages", [message])
            subscriber.save()


class ParseBroker:
    """This is a parse broker which can send and receive on a channel."""

    def __init__(self, channel_name):
        """Create a new ParseBroker for messages delivering and receiving on the channel."""
        self.publisher = ParsePublisher(channel_name)
        self.subscriber = ParseSubscriber(channel_name)
    
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

