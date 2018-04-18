from openbookscanner.states.state import StateMachine, State, FinalState
import time
import tempfile


class USBStickState(State):

    def can_write(self):
        return False
    
    def toJSON(self):
        d = super().toJSON(self)
        d["writable"] = self.can_write()
        return d

class PluggedIn(State, USBStickState):
    
    def on_enter(self):
        self.transition_into(USBStickIsMounting())

class USBStickIsMounting(RunningState, USBStickState):

    def run(self):
        """Mount the USBStick"""
        # TODO
        path = "/media/stick"
        # use tempfile.TemporaryDirectory()
        if True: # it mounted
            self.transition_into(Mounted(path))
        else:
            self.transition_into(ErrorMounting())

class ErrorMounting(State, USBStickState):
    pass

class Mounted(RunningState, USBStickState):
    
    def __init__(self, path):
        self.path = path
        self.space_is_left = True
    
    def run(self):
        while self.space_is_left:
            p = subprocess.run(["mount"], stdout=subprocess.PIPE)
            path = self.path.encode()
            if path not in p.stdout:
                self.transition_into(UnMounted())
                break
            for line in p.stdout.splitlines():
                if path in line:
                    if not b"(rw" in line:
                        self.transition_into(MountedReadOnly())
                        break
            time.sleep(0.1)
    
    def can_write(self):
        return True
    
    def no_space_left(self):
        self.space_is_left = False
        self.transition_into(NoSpaceLeft())
        

class UnMounted(FinalState, USBStickState):
    pass


class MountedReadOnly(FinalState, USBStickState):
    pass


class NoSpaceLeft(FinalState, USBStickState):
    pass


class USBStick(StateMachine):

    def __init__(self, device):
        """Create a new USB device.
        
        - device: is a path to a device in /dev/
        """
        self.transition_into(PluggedIn())
    
    def can_save_file(self):
        return self.state.can_write()
    
    def save_file(self, file):
        """Save a file on the USB Stick."""
        # if error: no space left: TODO:
        # self.state.receive_message({"type": "message", "name": "no_space_left"})

