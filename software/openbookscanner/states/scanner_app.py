"""This module waits for scanner apps to appear.

"""


from .hardware_listener import HardwareListener
from .state import StateMachine, MessageReceivingTransition, TimingOut
from flask import request
from pprint import pprint

class ScannerAppStateMixin:
    """Functionality for all scanner app states."""
    
    def can_scan(self):
        """Whether the app is able to scan right now."""
        return False
    
    def is_connected(self):
        """Whether the app is connected."""
        return True
    

class ReadyToScan(TimingOut, ScannerAppStateMixin):
    """The app is ready to scan and waiting for the app to reach out again."""
    
    def state_when_the_timeout_was_reached(self):
        """When the timeout was reached, the app is not reponding."""
        return NotReponding()
    
    @property
    def timeout_seconds(self):
        """This is the time in which the app is expected to respond back."""
        return self.state_machine.APP_TIMES_OUT_IF_NOT_RESPONDING_AFTER_SECONDS

    def can_scan(self):
        """Whether the app is able to scan right now."""
        return True

    def notification_from_app(self):
        """The app is there again!"""
        self.transition_into(ReadyToScan())
    


class NotReponding(MessageReceivingTransition, ScannerAppStateMixin):
    """The app is not responding then it is expected to."""
    
    def notification_from_app(self):
        """The app is there again!"""
        self.transition_into(ReadyToScan())
    
    def is_connected(self):
        """Whether the app is connected."""
        return False


class ScannerApp(StateMachine):
    """A state machine for the scanner app."""

    REFRESH_APP_AFTER_SECONDS = 0.5
    APP_TIMES_OUT_IF_NOT_RESPONDING_AFTER_SECONDS = 1
    
    first_state = ReadyToScan
        
    def get_notification_response(self):
        """Respond to the app."""
        return {"status": "ok",
                "refresh": self.REFRESH_APP_AFTER_SECONDS} # TODO: change the refresh interval depending on when the next scan is expected


class ScannerAppListener(HardwareListener):
    """A listener for scanner apps.
    
    Please see the API description in the OpenBookScannerApp folder.
    """
    
    def __init__(self, flask_server):
        """Start a scanner app listener on a FlaskServer."""
        self._server = flask_server
        self._server.route("/scanner", methods=["POST"])(self._post_scanner)
        self._apps = {} # id : app
        super().__init__()
    
    def _post_scanner(self):
        """Get a notification from a scanner app."""
        data = request.json
        print(__name__, "_post_scanner:", data)
        assert data.get("type") == "scanner", "The type attribute must be set to scanner to indicate the willingness to scan."
        name = data.get("name")
        assert isinstance(name, str), "The name MUST be a string so we can display it tothe user."
        id = data.get("id")
        assert isinstance(id, str), "The id must be a string so we can compare it to other ids."
        app = self._apps.get(id, None)
        if not app:
            self._apps[id] = app = ScannerApp(id, name, self._server)
        return app.get_notification_response()
    
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
    listener.run_update_loop_in_parallel()
    server.run(debug=True)


