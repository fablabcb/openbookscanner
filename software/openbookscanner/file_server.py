"""Serve the files over the web server."""
from .message import MessageDispatcher
from flask import Flask, abort
from weakref import WeakValueDictionary
import threading


class NullFileServer:
    """This is a server which does not serve any file."""
    
    def get_file_content_path(self):
        """There is no path."""
        return None
        
    def get_port(self):
        """There is no port."""
        return None


class NoFile:
    """The file was not found."""

    def flask_send_file(self):
        """404 no file was found."""
        abort(404)


class FileServer(MessageDispatcher):
    """Serve files via an http server."""
    
    FILE_CONTENT = "/file/"
    
    def __init__(self, port=8001):
        """Create a new file server."""
        self.app = Flask(self.__class__.__name__)
        self.files = WeakValueDictionary()
        self.app.route(self.FILE_CONTENT + "<id>")(self.serve_file_content_by_id)
        self.port = port
        
    def serve_file_content_by_id(self, id):
        """Serve a file by an id."""
        file = self.files.get(id, NoFile())
        return file.flask_send_file()
    
    def add_file(self, file):
        """Serve a file until noone needs it."""
        self.files[str(file.get_id())] = file
        file.served_by(self)
    
    def receive_new_image(self, message):
        """React to new images."""
        image = message["image"]
        self.add_file(image)

    def get_file_content_path(self, file):
        """Return the path component for the file."""
        return self.FILE_CONTENT + str(file.get_id())
    
    def get_port(self):
        """Return the port used to serve the files."""
        return self.port
    
    def run(self):
        """Run the server."""
        self.app.run(host="0.0.0.0", port=self.port)
       
    def run_in_parallel(self):
        """Run the server in parellel."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()


