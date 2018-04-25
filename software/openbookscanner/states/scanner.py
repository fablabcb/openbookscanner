"""
This module controls the scanners.

"""

from .hardware_listener import HardwareListener
from .state import StateMachine
import subprocess


class Scanner(StateMachine):
    """A Scanner which is connected to the computer."""
    
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


class ScannerListener(HardwareListener):
    """Listen if new scanners get attached.
    
    This scanner requires the packages
    - sane sane-utils
      see https://www.cyberciti.biz/faq/linux-scan-image-commands/
    - simple-scan
      see https://www.linuxquestions.org/questions/linux-hardware-18/scanning-using-scanner-canon-lide-120-canon-with-sane-4175609129/

    """
    
    def has_driver_support(self):
        """Check if scanimage is installed."""
        # from https://stackoverflow.com/a/11270665
        p = subprocess.run(["which", "scanimage"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.returncode == 0
    
    def listen_for_hardware(self):
        """See if we have hardware installed."""
        p = subprocess.run(["scanimage", "-f", "%i|%d|%t|%m|%v"],
                           stdout=subprocess.PIPE, check=True)
        for line in p.stdout.decode().splitlines():
            number, device, type, model, producer = line.split("|")
            scanner = Scanner(number, device, type, model, producer)
            if scanner not in self.get_hardware():
                self.found_new_hardware(scanner)
            
      
    



