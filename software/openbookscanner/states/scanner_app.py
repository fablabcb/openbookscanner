"""This module waits for scanner apps to appear.

"""


from .hardware_listener import HardwareListener
from .state import StateMachine, State
from flask import request
import json
import time
from urllib.parse import quote


class ScannerAppStateMixin:
    """Functionality for all scanner app states."""
    
    def can_scan(self):
        """Whether the app is able to scan right now."""
        return False
    
    def is_connected(self):
        """Whether the app is connected."""
        return True
        
    def wants_to_scan(self):
        """Whether a scan is requested."""
        return False
        
    def toJSON(self):
        """Return a JSON representation of the state."""
        data = super().toJSON()
        data["can_scan"] = self.can_scan()
        data["is_connected"] = self.is_connected()
        data["wants_to_scan"] = self.wants_to_scan()
        return data
    
    @property
    def app(self):
        """Same as self.state_machine."""
        return self.state_machine

    def check_timing(self):
        if self.app.seconds_until_app_should_refresh > 0:
            next = ReadyToScan
        elif self.app.seconds_until_app_is_timed_out > 0:
            next = NotRefreshing
        else:
            next = Gone
        if self.__class__ != next: # avoid changes to same state
            self.transition_into(next())


class ReadyToScan(State, ScannerAppStateMixin):
    """The app is ready to scan and waiting for the app to reach out again."""

    def receive_update(self, message):
        """The state is updated."""
        self.check_timing()

    def can_scan(self):
        """Whether the app is able to scan right now."""
        return True


class NotRefreshing(ReadyToScan):
    """The app is not responding when it is expected to."""

    
class Gone(State, ScannerAppStateMixin):
    """The app seems to be gone and is not responding."""
    
    def receive_update(self, message):
        """The state is updated."""
        self.check_timing()

    def is_connected(self):
        """Whether the app is connected."""
        return False


class Scanning(State):
    """The app is scanning a picure."""
        
    def wants_to_scan(self):
        """Whether a scan is requested."""
        return True

class ScannerApp(StateMachine):
    """A state machine for the scanner app."""

    REFRESH_APP_AFTER_SECONDS = 0.5
    APP_TIMES_OUT_IF_NOT_RESPONDING_AFTER_SECONDS = 5
    
    first_state = ReadyToScan
    
    def __init__(self, id, name, server):
        super().__init__()
        self.id = id
        self.name = name
        self.server = server
        self.create_notification_response()
        
    @property
    def seconds_until_app_should_refresh(self):
        """Seconds until the app should notify again."""
        # TODO: change the refresh interval depending on when the next scan is expected
        delta = self.last_notification + self.REFRESH_APP_AFTER_SECONDS - time.time()
        delta = min(self.seconds_until_app_is_timed_out, delta)
        return (delta if delta > 0 else 0)
        
    @property
    def seconds_until_app_is_timed_out(self):
        """Seconds after which we assume the app to be gone."""
        delta = self.last_notification + self.APP_TIMES_OUT_IF_NOT_RESPONDING_AFTER_SECONDS - time.time()
        return (delta if delta > 0 else 0)
        
    def create_notification_response(self):
        """Respond to the app."""
        self.last_notification = time.time()
        data = {"status": "ok",
                "refresh": self.seconds_until_app_should_refresh, 
                "timeout": self.seconds_until_app_is_timed_out}
        if self.state.wants_to_scan():
            data["picture"] = self.state.get_picture_url()
        return data


class ScannerAppListener(HardwareListener):
    """A listener for scanner apps.
    
    Please see the API description in the OpenBookScannerApp folder.
    """
    
    def __init__(self, flask_server):
        """Start a scanner app listener on a FlaskServer."""
        self._server = flask_server
        self._server.route("/scanner", methods=["POST"])(self._post_scanner)
        self._apps = {} # id : app
        self._new_apps = []
        super().__init__()
    
    def _post_scanner(self):
        """Get a notification from a scanner app."""
        data = request.json
        print(__name__, "_post_scanner:", data)
        assert data.get("type") == "scanner", "The type attribute must be set to scanner to indicate the willingness to scan."
        name = data.get("name")
        assert isinstance(name, str), "The name MUST be a string so we can display it to the user."
        id = data.get("id")
        assert isinstance(id, str), "The id must be a string so we can compare it to other ids."
        app = self._apps.get(id, None)
        if not app:
            self._apps[id] = app = ScannerApp(id, name, self._server)
            self.found_new_hardware(app)
            app.print_state_changes()
        return json.dumps(app.create_notification_response(), indent=4)
    
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
    listener.print_state_changes()
    listener.run_update_loop_in_parallel()
    server.run()


