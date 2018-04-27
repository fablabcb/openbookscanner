"""
This module controls the scanners.

"""

from .hardware_listener import HardwareListener
from .state import StateMachine, RunningState, FinalState, State, TransitionOnReceivedMessage, PollingState
import subprocess
import tempfile
import os


class ScannerStateMixin:
    """Shortcut methods for scanner states."""

    @property
    def scanner(self):
        """The scanner."""
        return self.state_machine
        
    def can_scan(self):
        """Whether the scanner is able to scan right now."""
        return False
    
    def is_plugged_in(self):
        """Whether the scanner is plugged in"""
        return True


class WithoutAScannedImage(State, ScannerStateMixin):
    """The scanner just got attached. There is no image to show."""
    
    timeout = 3

    def receive_scan(self, message):
        """Scan an image."""
        self.transition_into(Scanning())
        
    def receive_update(self, message):
        if self.scanner.device not in self.scanner.listener.list_currect_device_ids():
            self.transition_into(Unplugged("The scanner could not be found in the scanner listing."))
            return

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
            self.transition_into(UnableToScan(p.stderr.decode()))
            return
        jpg_image = os.path.join(directory.name, "scan.jpg")
        command = ["convert", scan_image, jpg_image]
        p = subprocess.run(command, stderr=subprocess.PIPE)
        if p.returncode != 0:
            self.transition_into(UnableToConvertScannedImage(p.stderr.decode()))
            return
        self.transition_into(HoldingAScannedImage(jpg_image, directory))

    
class AddDescriptionMixin:
    """Add the description of the first argument to json."""

    def __init__(self, description):
        super().__init__()
        self.description = self.__class__.__doc__ + "\n\n" + description
    
    def toJSON(self):
        json = super().toJSON()
        json["description"] = self.description
        return json

    
class Unplugged(AddDescriptionMixin, FinalState, ScannerStateMixin):
    """The scanner can not be used because it was unplugged from the computer."""

    def is_plugged_in(self):
        """Whether the scanner is plugged in"""
        return False


class UnableToScan(AddDescriptionMixin, WithoutAScannedImage):
    """The scanner could not scan the image because an error occurred."""


class UnableToConvertScannedImage(AddDescriptionMixin, WithoutAScannedImage):
    """Could not convert the image."""
    
    def is_error(self):
        """This is an error state."""
        return True


class HoldingAScannedImage(WithoutAScannedImage):
    """The scanner has an image."""
    
    def __init__(self, image, reference):
        self.image = image
        self.reference = reference


class Scanner(StateMachine):
    """A Scanner which is connected to the computer."""
    
    def first_state(self):
        """Wait for a message to arrive so we can create scanners with no cost."""
        return TransitionOnReceivedMessage(WithoutAScannedImage())
    
    def __init__(self, listener, number, device, type, model, producer):
        """Create a fixed image scanner."""
        super().__init__()
        self.number = number
        self.device = device
        self.type = type
        self.model = model
        self.producer = producer
        self.id = self.device
        self.listener = listener
        
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
        if isinstance(self.state, ScannerStateMixin):
            json["can_scan"] = self.state.can_scan()
            json["is_plugged_in"] = self.state.is_plugged_in()
        json["number"] = self.number
        json["device"] = self.device
        json["hardware"] = self.type
        json["model"] = self.model
        json["producer"] = self.producer
        json["id"] = self.id
        json["name"] = "{} № {}".format(self.type, self.number)
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
    
    timout_for_hardware_changes = 3
    timout_for_driver_detection = 10
    
    def __init__(self):
        super().__init__()
        self.device_list = set()
        self.new_device_list = set()
        
    def list_currect_device_ids(self):
        return self.device_list | self.new_device_list
    
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
        self.new_device_list = set()
        for line in p.stdout.decode().splitlines():
            number, device, type, model, producer = line.split("|")
            self.new_device_list.add(device)
            scanner = Scanner(self, number, device, type, model, producer)
            if scanner not in self.get_hardware():
                self.found_new_hardware(scanner)
                scanner.update()
        self.device_list = self.new_device_list
        print("scanner list", self.list_currect_device_ids())
        
            
      
    



