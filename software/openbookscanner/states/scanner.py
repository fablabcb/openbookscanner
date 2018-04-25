"""
This module controls the scanners.

"""

from .hardware_listener import HardwareListener
from .state import StateMachine, RunningState, FinalState, State, TransitionOnReceivedMessage
import subprocess

class ScannerStateMixin:
    """Shorcut methods for scanner states."""

    @property
    def scanner(self):
        """The scanner."""
        return self.state_machine
        
    def can_scan(self):
        """Whether the scanner is able to scan right now."""
        return False


class NoImagesScanned(State, ScannerStateMixin):
    """The scanner just got attached. There is no image to show."""

    def receive_scan(self, message):
        """Scan an image."""
        self.transition_into(Scanning)

    def can_scan(self):
        """The scanner is able to scan right now."""
        return True


class Scanning(RunningState, ScannerStateMixin):
    """The scanner is currently scanning an image."""
    
    def run(self):
        """Perform a scan."""
        directory = tempfile.TemporaryDirectory()
        scan_image = os.path.join(directory.name, "scan.pnm")
        command = ["scanimage", "--device", self.scanner.device,
                                "--format", "pnm"]
        with open(scan_image, "wb") as stdout:
            p = subprocess.run(command, stdout=stdout, stderr=subprocess.PIPE)
        if p.returncode != 0:
            self.transition_into(Unplugged(p.stderr.decode()))
            return
        jpg_image = os.path.join(directory.name, "scan.jpg")
        command = ["convert", scan_image, jpg_image]
        p = subprocess.run(command, stderr=subprocess.PIPE)
        if p.returncode != 0:
            self.transition_into(CouldNotConvert(p.stderr.decode()))
            return
        self.transition_into(HasImage(jpg_image, directory))

    
class AddDescriptionMixin:
    """Add the description of the first argument to json."""

    def __init__(self, description):
        self.description = self.__class__.__doc__ + "\n\n" + description
    
    def toJSON(self):
        json = super().toJSON()
        json["description"] = self.description
        return json

    
class Unplugged(FinalState, ScannerStateMixin):
    """The scanner can not be used because it was unplugged from the computer."""


class CouldNotConvert(NoImagesScanned, AddDescriptionMixin):
    """Could not convert the image."""
    
    def is_error(self):
        """This is an error state."""
        return True


class HasImage(State, ScannerStateMixin):
    """The scanner has an image."""
    
    def __init__(self, image, reference):
        self.image = image
        self.reference = reference

    def receive_scan(self, message):
        """Scan an image."""
        self.transition_into(Scanning())

    def can_scan(self):
        """The scanner is able to scan right now."""
        return True
    
    
class ScannerTransitionOnReceivedMessage(TransitionOnReceivedMessage, ScannerStateMixin):
    pass


class Scanner(StateMachine):
    """A Scanner which is connected to the computer."""
    
    def first_state(self):
        """Wait for a message to arrive so we can create scanners with no cost."""
        return ScannerTransitionOnReceivedMessage(NoImagesScanned())
    
    def __init__(self, number, device, type, model, producer):
        """Create a fixed image scanner."""
        super().__init__()
        self.number = number
        self.device = device
        self.type = type
        self.model = model
        self.producer = producer
        self.id = self.device
        
    def is_scanner(self):
        """This is a scanner."""
        return True

    def __eq__(self, other):
        """Check if this scanner is equal to another scanner."""
        return hasattr(other, "is_scanner") and other.is_scanner() and other.id == self.id
    
    def __hash__(self):
        """Return the hash value."""
        return hash(self.id)
    
    def __repr__(self):
        """String representation."""
        return "<{} with id {}>".format(self.__class__.__name__, self.id)
    
    def toJSON(self):
        json = super().toJSON()
        json["can_scan"] = self.state.can_scan()
        json["number"] = self.number
        json["device"] = self.device
        json["hardware"] = self.type
        json["model"] = self.model
        json["producer"] = self.producer
        json["id"] = self.id
        return json


class ScannerListener(HardwareListener):
    """Listen if new scanners get attached.
    """

    driver_message = """This scanner requires the packages
    - sane sane-utils
      see https://www.cyberciti.biz/faq/linux-scan-image-commands/
    - simple-scan
      see https://www.linuxquestions.org/questions/linux-hardware-18/scanning-using-scanner-canon-lide-120-canon-with-sane-4175609129/

    """
    
    def has_driver_support(self):
        """Check if scanimage is installed."""
        # from https://stackoverflow.com/a/11270665
        scanimage = subprocess.run(["which", "scanimage"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        convert = subprocess.run(["which", "convert"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return convert.returncode == 0 and scanimage.returncode == 0
    
    def listen_for_hardware(self):
        """See if we have hardware installed."""
        p = subprocess.run(["scanimage", "-f", "%i|%d|%t|%m|%v"],
                           stdout=subprocess.PIPE, check=True)
        for line in p.stdout.decode().splitlines():
            number, device, type, model, producer = line.split("|")
            scanner = Scanner(number, device, type, model, producer)
            if scanner not in self.get_hardware():
                self.found_new_hardware(scanner)
                scanner.update()
            
      
    



