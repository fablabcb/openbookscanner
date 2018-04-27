"""This module contains the operations on images."""
from .parse import GCReference
from .state import StateMachine

class ParseImage:

    def __init__(self, scanned_image):
        """Create a new parsed image from a openbookscanner.scanner.Image."""
        self.scanned_image = image


class CollectionOfImages(StateMachine):
    """When a new image is scanned, this uploads it to parse."""
    
    def __init__(self):
        """Create a new observer which uploads images once they are found"""
        self.uploaded_images = {} # id: image
    
    def new_image_scanned(self, scanned_image):
        f = File(scanned_image.get_name(), scanned_image.get_raw_data(), scanned_image.get_mime_type())
        self.update_strategy.save(file, callback=lambda: scanned_image.set_url(f.url))
        self.scanned_image.add_reference(GCReference(f, self.update_strategy))

    def get_raw_data(self):
        """Return the raw image data"""
        with open(self.image_path, "rb") as f:
            return f.read()
    
    def get_mime_type(self):
        """Return the mime type of the image's raw data."""
        # see https://stackoverflow.com/a/37266399
        return "image/jpeg"
    
    def get_name(self):
        """Return a name for the image."""
        return "scanned-image.jpg"

