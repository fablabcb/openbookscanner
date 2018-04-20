"""
Run the main program controlling the book scanner.
"""
from .model import OpenBookScanner
from .broker import ParseSubscriber, MessagePrintingSubscriber, ParsePublisher
from pprint import pprint
import time
from parse_rest.connection import register
from pprint import pprint
from .message import message
import click
from .update_strategy import BatchStrategy

APPLICATION_ID = "OpenBookScanner"


@click.group()
def cli():
    """OpenBookScanner
    
    This command line interface can control the book scanner.
    
    You can find the commands below and use --help behind a command to get more information about it.
    """

@cli.command()
@click.option("--print-messages", type=bool, default=False,
                help="Print the messages of the message broker.")
def run(print_messages):
    """Run the book scanner."""
    register(APPLICATION_ID, "OpenBookScanner")
    openbookscanner = OpenBookScanner()
    if print_messages:
        openbookscanner.print_messages()
    openbookscanner.run()


@cli.command()
@click.argument("channel", type=str, nargs=-1)
def receive(channel):
    """Only listen to the book scanner.
    
    These channels exist:
    "OpenBookScanner" is the channel for the book scanner messages. This is the default one.
    "OpenBookScannerStateChanges" is the channel for state changes.
    """
    register(APPLICATION_ID, "MessageListener")
    channels = channel or [OpenBookScanner.public_channel_name]
    click.echo("Listening to channel"+ ("s" if len(channels) > 1 else "") + " \"" + ", ".join(channels) + "\".")
    update = BatchStrategy()
    subscribers = [ParseSubscriber(channel, update) for channel in channels]
    try:
        for subscriber in subscribers:
            subscriber.subscribe(MessagePrintingSubscriber(subscriber.channel))
        while True:
            time.sleep(0.5)
            for subscriber in subscribers:
                subscriber.receive_messages()
            update.batch()
    finally:
        subscriber.delete()


@cli.command()
@click.argument("channel", type=str, nargs=-1)
def send(channel):
    """Send messages to the message bus.
    
    These channels exist:
    "OpenBookScanner" is the channel for the book scanner messages. This is the default one.
    "OpenBookScannerStateChanges" is the channel for state changes.
    """
    register(APPLICATION_ID, "MessageSender")
    channels = channel or [OpenBookScanner.public_channel_name]
    click.echo("Writing to channel"+ ("s" if len(channels) > 1 else "") + " \"" + ", ".join(channels) + "\".")
    update = BatchStrategy()
    publishers = [ParsePublisher(c, update) for c in channels]
    
    while True:
        print("----  Send Message  ----")
        data = {}
        name = input("name=")
        send = True
        while True:
            try:
                entry = input("[Press ENTER to send, Control+C to Abort] Attribute:Value=")
            except KeyboardInterrupt:
                send = False
                break
            if not ":" in entry:
                break
            key, value = entry.split(":", 1)
            data[key] = eval(value)
        if send:
            m = message(name, data)
            pprint(m)
            print("Sending message ...", end="", flush=True)
            for publisher in publishers:
                publisher.deliver_message(m)
            print("batch")
            update.batch()
            print(" done.")

