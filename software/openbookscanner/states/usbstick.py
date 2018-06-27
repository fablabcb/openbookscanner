from openbookscanner.states.state import StateMachine, State, FinalState, RunningState, PollingState
import time
import tempfile
import subprocess


class USBStickStateMixin: # rename to mixin

    def can_write(self):
        return False
    
    def toJSON(self):
        d = super().toJSON(self)
        d["writable"] = self.can_write()
        return d

class PluggedIn(USBStickStateMixin, State):
    
    def on_enter(self):
        self.transition_into(USBStickIsMounting())

class USBStickIsMounting(USBStickStateMixin, RunningState):

    def run(self):
        """Mount the USBStick"""
        # Create temporary directory
        tempdir = tempfile.mkdtemp(prefix='openbookscanner-usbstick-')
        # Mount USBStick to temporary directory
        # Requires root privilege
        p = subprocess.run(["mount", self.state_machine.get_mount_partition_path(), tempdir], stdout=subprocess.PIPE)
        if p.returncode == 0:
            self.transition_into(Mounted(tempdir))
        else:
            self.transition_into(ErrorMounting())

class ErrorMounting(USBStickStateMixin, State):
    pass

class Mounted(USBStickStateMixin, PollingState):
    
    timeout = 0.1
    
    def __init__(self, path):
        self.path = path
    
    def poll(self):
        """Check if USBStick is still mounted"""
        p = subprocess.run(["mount"], stdout=subprocess.PIPE)
        path = self.path.encode()
        if path not in p.stdout or not self.state_machine.is_plugged_in():
            self.transition_into(UnMounted())
        for line in p.stdout.splitlines():
            if path in line and not b"(rw" in line:
                self.transition_into(MountedReadOnly())
    
    def can_write(self):
        return True
    
    def no_space_left(self):
        self.transition_into(NoSpaceLeft())
        

class UnMounted(USBStickStateMixin, FinalState):
    pass


class MountedReadOnly(USBStickStateMixin, FinalState):
    pass


class NoSpaceLeft(USBStickStateMixin, FinalState):
    pass


class USBStick(StateMachine):

    def __init__(self, device, listener):
        """Create a new USB device.
        
        - device: is a path to a device in /dev/
        """
        super().__init__()
        self._device = device
        self.listener = listener
        self.transition_into(PluggedIn())

    def __repr__(self):
        return '<{} device {} at state {}>'.format(self.__class__.__name__, self._device, self.state)
    
    def can_save_file(self):
        return self.state.can_write()
    
    def save_file(self, file):
        """Save a file on the USB Stick."""

        # if error: no space left: TODO:
        # self.state.receive_message({"type": "message", "name": "no_space_left"})

    def is_usb_stick(self):
        """Tell callers if this object is a USB stick"""
        return True

    def is_scanner(self):
        """Tell callers if this object is a scanner"""
        return False

    def get_mount_partition_path(self):
        return "/dev/" + self._device + "1"

    def is_plugged_in(self):
        return self._device in self.listener.get_block_devices()

    @property
    def label(self):
        """The label of the USB Stick."""
        return "TODO" # TODO

    @property
    def id(self):
        """This identifies the USB Stick among others."""
        return self._device + "-" + str(id(self))

    def toJSON(self):
        d = super().toJSON()
        d["id"] = self.id
        d["label"] = self.label
        return d
