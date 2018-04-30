"""This module deals with the conversion of images to certain formats.

"""
from .message import MessageDispatcher, message
from openbookscanner.broker import LocalSubscriber
import tempfile
from .file_server import NullFileServer
from flask import send_file
import os
import shutil
import subprocess


class Image:
    """This is an image to the user's liking."""
    
    def __init__(self, scanner, path, mime_type, reference):
        """Create a new image."""
        self.scanner = scanner
        self.paths = [path]
        self.mime_type = mime_type
        self.reference = reference
        self.server = NullFileServer()
    
    @property
    def path(self):
        """Return the main path of the image."""
        return self.paths[0]
    
    def get_id(self):
        """Return the id of the image."""
        return str(id(self))
        
    def get_storage_file_name(self):
        return self.get_id() + os.path.splitext(self.path)[1]
        
    def served_by(self, server):
        """This image is served by a server."""
        self.server = server
    
    def flask_send_file(self):
        """Send this as a response of a flask server."""
        return send_file(self.path, mimetype=self.mime_type)
    
    def toJSON(self):
        """Return the JSON represenation of the image."""
        return {"url": {"path": self.server.get_file_content_path(self), "port": self.server.get_port()},
                "mimetype": self.mime_type, "paths": self.paths,
                "type": self.__class__.__name__, "id": self.get_id(),
                "name": self.get_storage_file_name(), "scanner": self.scanner.toJSON()}
    
    def copy_to(self, path):
        """Store at the other location."""
        shutil.copy(self.path, path)
        self.paths.append(path)
        
    def __repr__(self):
        """Return a string representation."""
        return "<{} at {}>".format(self.__class__.__name__, " and ".join(self.paths))


class ConvertCommand:
    """Convert images using the convert command."""
    
    def __init__(self, file_ending, mime_type):
        """Create a new convert command."""
        self.file_ending = file_ending
        self.mime_type = mime_type
    
    def convert_scan_to_image(self, scan):
        """Convert a scan and return an image."""
        directory = tempfile.TemporaryDirectory()
        jpg_image = os.path.join(directory.name, "scan" + self.file_ending)
        subprocess.run(["convert", scan.get_path(), jpg_image], check=True)
        return Image(scan.get_scanner(), jpg_image, self.mime_type, directory)


class Converter(MessageDispatcher, LocalSubscriber):
    """Convert images in different ways."""
    
    def __init__(self):
        super().__init__()
        self.conversion_strategy = ConvertCommand(".jpg", "image/jpeg")

    def receive_new_scan(self, message_):
        scan = message_["scan"]
        image = self.conversion_strategy.convert_scan_to_image(scan)
        self.deliver_message(message.new_image(image=image))
    
    # TODO: configure conversion




