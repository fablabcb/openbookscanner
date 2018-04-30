"""The OpenBookScanner has an Arduino which is responsible to move the parts.

This module contains the connection to the serial connection of the Arduino.

"""
from .message import message
from .broker import LocalSubscriber


def list_serial_ports():
    """Returns a list of serial ports.
    
    This allows us to check if the Arduino is attached.
    """
    ## got the code from
    ## http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    import os
    from serial.tools import list_ports
    # Windows
    if os.name == 'nt':
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append('COM'+str(i + 1))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        # Mac / Linux
        return [port[0] for port in list_ports.comports()]


def message_to_serial(message):
    """Convert a message to the form that a serial connection can use it.
    
    The message is a whole line ending with "\\r\\n".
    The name of the message is the content.
    """
    return message["name"] + "\r\n"

def message_from_serial(string):
    """Get a message from a serial connection.
    
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


class SerialMessageAdapter(LocalSubscriber):
    """A message sending and receiving adapter for the Arduino or any serial connection."""
    

    def __init__(self, serial):
        """Initialize the adapter with a serial connection.
        
        See https://pythonhosted.org/pyserial/pyserial_api.html#serial.Serial
        """
        self.serial = serial
    
    def flush(self):
        """Receive the messages from the serial connection."""
        if self.serial.in_waiting:
            bytes = self.serial.readline()
            self.deliver_message(message_from_serial(bytes.decode("ASCII")))
    
    def receive_message(self, message):
        """Send a message to the arduino."""
        bytes = message_to_serial(message).encode("ASCII")
        self.serial.write(bytes)
    
        
        
        
