"""A server to run and configure flask.

"""
from flask import Flask, request
from urllib.request import urlopen


class FlaskServer:
    """A flask server."""
    
    debug = True

    def __init__(self, port=8001):
        """Create a new file server."""
        self.port = port
        self._app = Flask(self.__class__.__name__)
        self._running = False
        
    def route(self, *args, **kw):
        """Create a route on the flask app."""
        return self._app.route(*args, **kw)

    def run(self, **kw):
        """Run the server."""
        assert not self._running, "A server can only be started once. " \
                                  "Use is_running() to check!"
        self.running = True
        try:
            self._app.run(host="0.0.0.0", port=self.port, **kw)
        finally:
            self._running = False
        
    def is_running(self):
        """Return whether the server is running."""
        return self._running
    
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

