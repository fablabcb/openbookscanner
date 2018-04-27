"""This module handles storage of all the files"""

from .message import MessageReceiver, message
from openbookscanner.broker import LocalBroker
import tempfile
from .file_server import FileServer
import os


class DirectoryStorage:
    """Store the files in a certain directory."""
    
    def __init__(self, directory):
        """Save the files in this directory."""
        self.directory = directory
        self.files = []
    
    def store(self, file):
        """Store the file."""
        file_name = file.get_storage_file_name()
        path = os.path.join(self.directory, file_name)
        file.copy_to(path)
        self.files.append(file)
    
    def toJSON(self):
        """Return the JSON represenation."""
        return {"path": self.directory, "images": [file.toJSON() for file in self.files],
                "type": self.__class__.__name__}


class TemporaryStorageLocation(DirectoryStorage):
    """Store the files in a temporary directory."""
    
    def __init__(self):
        """Create a temporary storage location."""
        self.__temp_directory = tempfile.TemporaryDirectory(prefix="OpenBookScanner-")
        super().__init__(self.__temp_directory.name)
    

class UserDefinedStorageLocation(MessageReceiver, LocalBroker):
    """This gives the user the ability to define the storage location."""
    
    default_storage = TemporaryStorageLocation

    def __init__(self):
        """Create a new storage with user access."""
        super().__init__()
        self.storage = self.default_storage()
        self.server = FileServer()
        self.state_observers = []
        
    def receive_new_image(self, message):
        """A new image has been created."""
        image = message["image"]
        self.add_file(image)
    
    def add_file(self, file):
        """Add a new file to store."""
        self.storage.store(file)
        self.server.add_file(file)
        self.state_changed()
    
    def register_state_observer(self, observer):
        """Notify the observer when the state changes."""
        self.state_observers.append(observer)
    
    def state_changed(self):
        """Notify the overservers about the state change."""
        for observer in self.state_observers:
            observer.state_changed(self)
    
    def toJSON(self):
        """Return a JSON represenation."""
        return {"type": self.__class__.__name__, "storage": self.storage.toJSON(), 
                "description": self.__class__.__doc__}
        
    def run_in_parallel(self):
        """Run the server in parellel."""
        self.server.run_in_parallel()


