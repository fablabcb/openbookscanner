"""
Run the main program controlling the book scanner.
"""
import os
os.environ["PARSE_API_ROOT"] = "http://localhost:1337/parse"
from .model import OpenBookScanner
from .broker import ParseSubscriber, MessagePrintingSubscriber
from pprint import pprint
import time


def main():
    """Run the book scanner."""
    openbookscanner = OpenBookScanner()
    openbookscanner.print_messages()
    openbookscanner.run()


def listen():
    """Only listen to the book scanner."""
    subscriber = ParseSubscriber(self.public_channel_name)
    subscriber.subscribe(MessagePrintingSubscriber())
    
    while True:
        time.sleep(0.5)
        broker.receive_messages()

