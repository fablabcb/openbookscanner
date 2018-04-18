"""
This module contains the message broker which distributes messages.

https://en.wikipedia.org/wiki/Message_broker
"""

class LocalBroker:
    """This is a local broker which just forwards the messages."""

    def __init__(self):
        """Create a new broker object."""
        self.subscribers = []
    
    def subscribe(self, subscriber):
        """Subscribe to all messages sent over the broker."""
        self.subscribers.append(subscriber)
    
    def receive_message(self, message):
        """Send a message to all the subscribers."""
        for subscriber in self.subscribers:
            subscriber.receive_message(message)






