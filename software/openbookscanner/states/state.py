"""
This module contains the common states of all objects.

"""
from concurrent.futures import ThreadPoolExecutor
import sys

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
        """"""
    
    def transition_into(self, new_state):
        self.state_machine.transition_into(new_state)
    
    def toJSON(self):
        return {"type": self.__class__.__name__,
                "is_final": self.is_final()
                }
    
    def is_final(self):
        return False


class FirstState(State):
    """This is the first state so one has a state to come from."""

    def receive_unknown_message(self, message):
        """The first state should not receive messages."""
        raise ValueError("Please use transition_into to get away from this state for {}!".format(self.state_machine))


class StateMachine:
    """This is the base class for all states."""
    
    state = FirstState()


    def transition_into(self, state):
        self.state.leave(self)
        self.state = state
        self.state.enter(self)

    def receive_message(self, message):
        assert message.get("type") == "message"
        message_name = message["name"]
        method_name = "receive_" + message_name
        method = getattr(self, method_name, self.receive_unknown_message)
        method(message)
    
    def receive_unknown_message(self, message):
        pass
    
    def toJSON(self):
        return {"type": self.__class__.__name__, "state": self.state.toJSON()}


class FinalState(State):
    """This state can no be left."""

    def is_final(self):
        return True

class DoneRunning(State):
    pass        


class RunningState(State):

    next_state = DoneRunning()

    def enter(self, state_machine):
        super().enter(self, state_machine)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = self.executor.submit(self.run)
    
    def run(self):
        """This is called when the state machine enters the state.
        
        While running, you can transition_into other states.
        When running is done, the state machine will enter the new state.
        """
        
    def is_running(self):
        return self.future.running()

    def transition_into(self, next_state):
        self.next_state = next_state
    
    def receive_message(self, message):
        if self.is_running():
            super().receive_message(self, message)
        else:
            if self.future.exception() is not None: # Errors should never pass silently.
                raise self.future.exception()
            self.state_machine.transition_into(self.next_state)
            self.state_machine.receive_message(message)

    
