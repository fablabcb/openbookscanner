"""This module contains a framework to listen to hardware changes.

"""

from .state import StateMachine, PollingState, State, TransitionOnReceivedMessage


class Checks:
    """This is a sum of check values."""
    
    is_detecting_driver_support = False
    could_not_detect_driver_support = False
    finding_hardware_changes = False
    

class DetectingDriverSupport(PollingState, Checks):
    """Check if the necessary software is installed properly."""
    
    is_detecting_driver_support = True
    
    @property
    def timeout(self):
        """How long to wait between detections."""
        return self.state_machine.timeout_for_driver_detection

    def poll(self):
        """Detect if the hardware is supported."""
        if self.state_machine.has_driver_support():
            self.transition_into(ListeningForHardwareChanges())
        else:
            self.transition_into_not_supported()
    
    def transition_into_not_supported(self):
        self.transition_into(NotSupported())


class NotSupported(DetectingDriverSupport, Checks):
    """The necessary drivers are not installed. Let me chack again ... ."""
    
    could_not_detect_driver_support = True
    
    def is_error(self):
        """This is an error state."""
        return True

    def transition_into_not_supported(self):
        pass
    
    def toJSON(self):
        json = super().toJSON()
        json["description"] = self.__class__.__doc__ + self.state_machine.driver_message
        return json
    

class ListeningForHardwareChanges(PollingState, Checks):
    """We listen for hardware changes if new hardware can be used."""
    
    finding_hardware_changes = True
    
    @property
    def timeout(self):
        """How long to wait between hardware changes."""
        return self.state_machine.timeout_for_hardware_changes
    
    def poll(self):
        """Listen for new hardware."""
        if self.state_machine.has_new_hardware():
            self.transition_into(NotifyingAboutNewHardware())
        else:
            self.state_machine.listen_for_hardware()


class NotifyingAboutNewHardware(State, Checks):
     """Notify all the observers in a threadsave manner about the new hardware changes."""

     finding_hardware_changes = True

     def on_enter(self):
         """Notify the observers about the new hardware."""
         self.state_machine.notify_about_new_hardware()
         self.transition_into(TransitionOnReceivedMessage(ListeningForHardwareChanges()))


class HardwareListener(StateMachine):
    """These objects listen to hardware changes.
    
    A hardware listener has these states:
    
    -> DetectingDriverSupport - to detect, if we can use this
      -> NotSupported (error) - no driver was installed, actively waiting for the hardware to be supported.
    -> ListeningForHardwareChanges - to actively scan for hardware changes
    
    As all these operations take time, these states run their actions in parallel.
    """
    
    first_state = DetectingDriverSupport
    timeout_for_driver_detection = 1
    timeout_for_hardware_changes = 0.5
    
    driver_message = "The necessary drivers need to be installed."
    
    def __init__(self):
        """Create a new hardware listener."""
        super().__init__()
        self._hardware_observers = []
        self._added_hardware = []
        self._new_hardware = []
    
    def has_driver_support(self):
        """Return whether all the necessary software is installed so we can run this successfully.
        
        Please replace this method.
        """
        return True
    
    def listen_for_hardware(self):
        """Listen for hardware.
        
        If new hardware is detected, 
        Note: This runs in parallel. Use self.add_new_hardware() to add new hardware.
        
        Please replace this method.
        """

    def found_new_hardware(self, new_hardware):
        """Add new hardware to the list of added hardware.
        
        hardware observers will be notified about the new hadware.
        You can access all added hardware with self.get_hardware().
        """
        self._added_hardware.append(new_hardware)
        self._new_hardware.append(new_hardware)

    def get_hardware(self):
        """Return all the found hardware."""
        return self._added_hardware[:]

    def register_hardware_observer(self, observer):
        """Register a hardware observer to be notified about hardware changes.
        
        observer.new_hardware_detected(new_hardware) will be called once new hardware was found.
        If hardware is removed, this is the responsibility of the hardware object.
        """
        self._hardware_observers.append(observer)

    def notify_about_new_hardware(self):
        """Notify the hardware observers about lately added hardware.
        """
        while self._new_hardware:
            new_hardware = self._new_hardware.pop()
            for observer in self._hardware_observers:
                print('test', observer, new_hardware)
                observer.new_hardware_detected(new_hardware)

    def has_new_hardware(self):
        """Return whether we have new hardware detected."""
        return bool(self._new_hardware)

    def update_hardware(self):
        """Update all the hardware."""
        for hardware in self.get_hardware():
            hardware.update()

