"""
This module contains the common states of all objects.

"""
from concurrent.futures import ThreadPoolExecutor
import sys
from openbookscanner.message import message
import time
from openbookscanner.broker import LocalBroker
import atexit


class State:
    """This is the base state for all the states of state machines."""

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
                "description": self.__class__.__doc__,
                "is_waiting_for_a_message_to_transition_to_the_next_state": self.is_waiting_for_a_message_to_transition_to_the_next_state(), 
                "is_error": self.is_error()
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
        """Receive a message and handle it.
        
        The message has a "name" key.
        If the state defines a method named "receive_" + the name, 
        this method handles the message.
        Otherwise, receive_unknown_message handles the message.
        """
        message_name = message["name"]
        method_name = "receive_" + message_name
        method = getattr(self, method_name, self.receive_unknown_message)
        method(message)

    def receive_unknown_message(self, message):
        """The state reacts to all messages which are not explicitely handeled."""
    
    def is_waiting_for_a_message_to_transition_to_the_next_state(self):
        """Return whether the transition to a next state is determined but deferred."""
        return False
    
    def deliver_message(self, message):
        """Deliver a message to the state machine which delivers it to the subscribers."""
        self.state_machine.deliver_message(message)
        
    def __repr__(self):
        """Return the string representation."""
        return "<{} at {}>".format(self.__class__.__name__, hex(id(self)))

    def receive_message_from_other_state(self, message):
        """Receive a message from the state before this state."""
        self.receive_message(message)
    
    def is_error(self):
        """Whether this state is an error state."""
        return False
    
    
class FirstState(State):
    """This is the first state so one has a state to come from."""

    def receive_unknown_message(self, message):
        """The first state should not receive messages."""
        raise ValueError("Please use transition_into to get away from this state for {}!".format(self.state_machine))


class StateMachine(LocalBroker):
    """This is the base class for all state machines.
    
    A state machine "stm" implements these patterns:
    
    - a publisher
      stm.subscribe(subscriber) adds a subscriber to publish to
      stm.deliver_message(message) delivers the message to all subscribers
    - a subscriber
      stm.receive_message(message) sends the message to the state which then can transition
    - an observable
      state_machine.register_state_observer(observer) adds a new observer which is notified on state changes
      observer.state_changed(stm) notifies the observers about the state change
    """
    
    first_state = FirstState
    
    def __init__(self):
        """Create a new state machine."""
        super().__init__()
        self.state_observers = []
        self.state = FirstState()
        self.transition_into(self.first_state())
    
    def register_state_observer(self, observer):
        """The observer observes the state of the state machine."""
        self.state_observers.append(observer)
    
    def state_changed(self):
        for observer in list(self.state_observers):
            observer.state_changed(self)

    def transition_into(self, state):
        """Transition into a new state."""
        self.state.leave(self)
        self.state = state
        self.state.enter(self)
        self.state_changed()

    def receive_message(self, message):
        """Receive a message and send it to the state."""
        self.state.receive_message(message)
    
    def toJSON(self):
        """Return the JSON representation of the object."""
        return {"type": self.__class__.__name__, "state": self.state.toJSON(), 
                "description": self.__class__.__doc__}
    
    def update(self):
        """Send an update message to the state machine.
        
        If the state machine is in a state which is 
        is_waiting_for_a_message_to_transition_to_the_next_state,
        this can trigger the transition.
        """
        self.receive_message(message.update())

    def __repr__(self):
        return "<{} at state {}>".format(self.__class__.__name__, self.state)

    def print_state_changes(self):
        """Start printing the state changes."""
        self.register_state_observer(PrintStateChanges())
    
    def stop(self):
        """Stop the state machine in case a state is running."""
        if self.state.is_running():
            self.state.stop()
            
    def is_scanner(self):
        """Whether this state machine is a scanner."""
        return False
            

class FinalState(State):
    """This state can no be left."""

    def is_final(self):
        return True

class ErrorState(State):
    """This state is an error state."""

    def is_final(self):
        return True


class DoneRunning(State):
    """This is the state the state machine goes to if parallel exeuction in a RunningState finishes
    and no other transition is specified.
    """        

class ErrorRaisingState(ErrorState):
    """This state raises the error it was created with once a message is received."""

    def __init__(self, error):
        """Create a new state which raises the error."""
        self.error = error

    def receive_message(self, message):
        """Raise the error, do not handle the message."""
        raise self.error

_shutdown = False
def _python_exit():
    global _shutdown
    _shutdown = True

atexit.register(_python_exit)

class RunningState(State):

    next_state = _initial_next_state = DoneRunning()
    _stopped = False
    
    def should_stop(self):
        """ Please stop running the threads.
        
        The Python program is exiting right now or it should be stopped.
        """
        return _shutdown or self._stopped
    
    def is_waiting_for_a_message_to_transition_to_the_next_state(self):
        """Return whether the state likes to transition."""
        return self.next_state != self._initial_next_state

    def enter(self, state_machine):
        """Enter the state and start the parallel execution."""
        super().enter(state_machine)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = self.executor.submit(self.run)
    
    def run(self):
        """This is called when the state machine enters the state.
        
        While running, you can transition_into other states.
        When running is done, the state machine will enter the new state.
        
        Please check sometimes for self.should_stop().
        If this is True, the program is exiting right now and you should stop running.
        """
        
    def is_running(self):
        """Whether this state is currently running."""
        return not self.future.done()
        
    def wait(self, timeout=None):
        """Wait for the parallel task to finish.
        
        timeout is given in seconds.
        """
        self.future.exception(timeout)

    def transition_into(self, next_state):
        """Transition into the next state but defer the transition until the parallel execution is finished.
        
        When the execution is finished, the next incoming message will start a transition.
        The next state receives the message.
        """
        self.next_state = next_state
    
    def receive_message(self, message):
        """Receive a message and transition when the parallel execution is done."""
        if self.is_running():
            super().receive_message(message)
        else:
            if self.future.exception() is not None: # Errors should never pass silently.
                self.next_state = self.get_error_state()
            super().transition_into(self.next_state)
            self.next_state.receive_message_from_other_state(message)

    def receive_message_from_other_state(self, message):
        """Discard messages from previous states if I am completed."""
        if not self.is_running():
            super().receive_message(message)

    def stop(self):
        """Stop the state if it is running."""
        self._stopped = True
        self.wait()
        
    def get_error_state(self):
        """Return the error state."""
        return ErrorRaisingState(self.future.exception())


class PollingState(RunningState):
    """This state runs the poll function all "timeout" seconds and stops on transition."""
    
    timeout = 0.001

    def run(self):
        """Call self.poll() on a regular basis, waiting self.timeout in between.
        
        If the Python program stops, a SystemExit error is raised.
        """
        while not self.is_waiting_for_a_message_to_transition_to_the_next_state():
            self.poll()
            if not self.is_waiting_for_a_message_to_transition_to_the_next_state():
                time.sleep(self.timeout)
            if self.should_stop():
                raise SystemExit("The program is exiting.")
    
    def poll(self):
        """This is called regularly.
        
        When you use self.transition_into(new_state), this will not be called any more.
        """


class TransitionOnReceivedMessage(State):
    """This state waits for a message to be received and then transitions into the text state.
    
    
    This can be used if you have several state machines which are interacting and you want to
    postpone entering the states e.g. because they send messages on_enter.

    If you inherit from this state and you explicitely handle messages,
    they do not trigger the transition.
    """
    
    def __init__(self, next_state):
        """Wait until a message arrives and transition."""
        self.next_state = next_state
    
    def toJSON(self):
        """Return the JSON of the state including the next state."""
        d = super().toJSON()
        d["next_state"] = self.next_state.toJSON()
        return d
    
    def receive_unknown_message(self, message):
        """If we receive an unknown message, we can transition into the next state.
        
        The next state receives the message.
        """
        self.transition_into(self.next_state)
        self.next_state.receive_message(message)

    def is_waiting_for_a_message_to_transition_to_the_next_state(self):
        """This state always defers the transition until a message arrives."""
        return True
        
    def __repr__(self):
        """The string representation."""
        return "<{} into {}>".format(self.__class__.__name__, self.next_state)


class StateChangeToMessageReceiveAdapter:
    """If the state changes, this adapter sends a change message."""
    
    def __init__(self, publisher):
        """Create a new adapter wich sends messages to the publisher."""
        self.publisher = publisher
    
    def state_changed(self, state_machine):
        """When the state changes, a message is sent to the publisher."""
        self.publisher.receive_message(message.state_changed(state_machine=state_machine.toJSON()))


class PrintStateChanges:

    def state_changed(self, state_machine):
        """Print the state change."""
        print("new state:", state_machine)
