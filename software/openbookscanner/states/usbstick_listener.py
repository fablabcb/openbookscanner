
import subprocess

from .state import State
from openbookscanner.states.hardware_listener import HardwareListener
from openbookscanner.states.usbstick import USBStick


class InitializationFailed(State):
    """One of the constructor's shell commands did not return successfully."""
    
    def is_error():
        """This is an error state."""
        return True

class USBStickListener(HardwareListener): 

    def __init__(self):
        super().__init__()

        self._block_devices = self.get_block_devices()

    def get_block_devices(self):
        p = subprocess.run(["lsblk | grep disk"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        return set([line.split()[0].decode() for line in p.stdout.splitlines()])

    def has_driver_support(self):
        """Each system possesses the necessary drivers for mounting of USB sticks."""
        return True

    def listen_for_hardware(self):
            
        new_block_devices = self.get_block_devices()
        
        for new_block_device in new_block_devices.difference(self._block_devices):
            self.found_new_hardware(USBStick(new_block_device, self))

        self._block_devices = new_block_devices

