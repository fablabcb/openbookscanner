"""
This module contains the common states of all objects.

"""
from concurrent.futures import ThreadPoolExecutor
import sys
from openbookscanner.states.message import message
import time

class State:

    def enter(self, state_machine):
        """The state machine enters this state."""
        self.state_machine = state_machine
        self.on_enter()
    
    def on_enter(self):
        """Called when the state is entered."""
        
    
    def leave(self, state_machine):
        self.on_leave()
    
    def on_leave(self):
        """Calles when the state is left."""
    
    def transition_into(self, new_state):
        """Use this to transition into another state."""
        self.state_machine.transition_into(new_state)
    
    def toJSON(self):
        return {"type": self.__class__.__name__,
                "is_final": self.is_final(),
                "description": self.__class__.__doc__
                }
    
    def is_final(self):
        """This is a marker for the state being final."""
        return False
        
    def is_running(self):
        """Whether this state has some activity running in parallel.
        
        You can use this in connection with wait() if you like to know when it finishes.
        
            if state.is_running():
                state.wait()
        """
        return False

    def receive_message(self, message):
        message_name = message["name"]
        method_name = "receive_" + message_name
        method = getattr(self, method_name, self.receive_unknown_message)
        method(message)

    def receive_unknown_message(self, message):
        pass
    
class FirstState(State):
    """This is the first state so one has a state to come from."""

    def receive_unknown_message(self, message):
        """The first state should not receive messages."""
        raise ValueError("Please use transition_into to get away from this state for {}!".format(self.state_machine))


class StateMachine:
    """This is the base class for all state machines."""
    
    state = FirstState()

    def transition_into(self, state):
        self.state.leave(self)
        self.state = state
        self.state.enter(self)

    def receive_message(self, message):
        self.state.receive_message(message)
    
    def toJSON(self):
        return {"type": self.__class__.__name__, "state": self.state.toJSON()}
    
    def update(self):
        self.receive_message(message.update())


class FinalState(State):
    """This state can no be left."""

    def is_final(self):
        return True

class DoneRunning(State):
    pass        


class RunningState(State):

    next_state = _initial_next_state = DoneRunning()
    
    def has_transitioned(self):
        return self.next_state != self._initial_next_state

    def enter(self, state_machine):
        super().enter(state_machine)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = self.executor.submit(self.run)
    
    def run(self):
        """This is called when the state machine enters the state.
        
        While running, you can transition_into other states.
        When running is done, the state machine will enter the new state.
        """
        
    def is_running(self):
        return not self.future.done()
        
    def wait(self, timeout=None):
        self.future.exception(timeout)

    def transition_into(self, next_state):
        self.next_state = next_state
    
    def receive_message(self, message):
        if self.is_running():
            super().receive_message(message)
        else:
            if self.future.exception() is not None: # Errors should never pass silently.
                raise self.future.exception()
            self.state_machine.transition_into(self.next_state)
            self.state_machine.receive_message(message)


class PollingState(RunningState):
    """This state runs the poll function all "timeout" seconds and stops on transition."""
    
    timeout = 0.001

    def run(self):
        if not self.has_transitioned():
            self.poll()
        while not self.has_transitioned():
            time.sleep(self.timeout)
            self.poll()
    
    def poll(self):
        pass

