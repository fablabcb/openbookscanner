"""This module deals with the conversion of images to certain formats.

"""
from .message import MessageReceiver, message
from openbookscanner.broker import LocalBroker
import tempfile


class Image:
    """This is an image to the user's liking."""
    
    def __init__(self, scanner, path, mime_type, reference):
        """Create a new image."""
        self.id = id(self)
        self.scanner = scanner
        self.path = path
        self.mime_type = mime_type
        self.reference = reference
        

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


class Converter(LocalBroker, MessageReceiver):
    """Convert images in different ways."""
    
    def __init__(self):
        super().__init__()
        self.conversion_strategy = ConvertCommand(".jpg", "image/jpeg")

    def receive_new_scan(self, message):
        scan = message["scan"]
        image = self.conversion_strategy.convert_scan_to_image(scan)
        self.deliver_message(message.new_image(image=image))
    
    # TODO: configure conversion




