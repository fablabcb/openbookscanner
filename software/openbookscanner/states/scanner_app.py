"""This module waits for scanner apps to appear.

"""


from .hardware_listener import HardwareListener
from .state import StateMachine, RunningState, FinalState, State, TransitionOnReceivedMessage, PollingState, TimingOut
from flask import request
from pprint import pprint



class ScannerApp(StateMachine):
    """"""


class ScannerAppListener(HardwareListener):
    """A listener for scanner apps.
    
    Please see the API description in the OpenBookScannerApp folder."""
    
    def __init__(self, flask_server):
        """Start a scanner app listener on a FlaskServer."""
        self._server = flask_server
        self._server.route("/scanner", methods=["POST"])(self._post_scanner)
    
    def _post_scanner(self):
        """Get a notification from a scanner app."""
        pprint(request.json)
        return "OK"
    
    def has_driver_support(self):
        """The apps are only supported when the server runs."""
        return self._server.is_running()
        
    def listen_for_hardware(self):
        pass
        

def main():
    """Try out this server."""
    from ..flask_server import FlaskServer
    server = FlaskServer()
    listener = ScannerAppListener(server)
    server.run(debug=True)


