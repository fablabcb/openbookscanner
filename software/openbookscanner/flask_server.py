"""A server to run and configure flask.

"""
from flask import Flask, request
from urllib.request import urlopen
from functools import wraps
import traceback

class FlaskServer:
    """A flask server."""

    def __init__(self, port=8001):
        """Create a new file server."""
        self.port = port
        self._app = Flask(self.__class__.__name__)
        
    def route(self, *args, **kw):
        """Create a route on the flask app."""
        add_to_route = self._app.route(*args, **kw)
        @wraps(add_to_route)
        def wrap(func):
            @wraps(func)
            def error_printing_func(*args, **kw):
                """Let us know if there is an error even if we are not in production."""
                try:
                    return func(*args, **kw)
                except:
                    traceback.print_exc()
                    raise
            return add_to_route(error_printing_func)
        return wrap

    def run(self, **kw):
        """Run the server."""
        self._app.run(host="0.0.0.0", port=self.port, **kw)

    def is_running(self):
        """Return whether the server is running."""
        return True # TODO: use a more robust algorithm
    
    def get_port(self):
        """Return the port used to serve the files."""
        return self.port
    
    def shutdown(self):
        """Shutdown the server."""
        self.route("/shutdown")(self._route_shutdown_server)
        urlopen(self.get_url("/shutdown"))
        
    def get_url(self, path="/"):
        return "http://localhost:{}{}".format(self.get_port(), path)
        
    def _route_shutdown_server(self):
        """Perform the shutdown."""
        # from https://stackoverflow.com/a/23575591
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Server is shutting down ..."
    
    


if __name__ == "__main__":
    server = FlaskServer()
    from threading import Thread
    import time
    def shutdown_after():
        time.sleep(2)
        server.shutdown()
    thread = Thread(target=shutdown_after)
    thread.start()
    print("Closing the server after some time...")
    server.run()

