"""The OpenBookScanner has an Arduino which is responsible to move the parts.

This module contains the connection to the Arduino.

"""

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


