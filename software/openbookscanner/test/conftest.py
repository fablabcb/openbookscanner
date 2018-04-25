import os
import time
import pytest
from pytest import fixture
from openbookscanner.states import State, FinalState, StateMachine, PollingState, TransitionOnReceivedMessage
from openbookscanner.states.hardware_listener import HardwareListener
from openbookscanner.broker import LocalBroker, ParseBroker, BufferingBroker
from unittest.mock import Mock
from openbookscanner.message import message

#import hanging_threads
#
#hanging_threads.start_monitoring()

# register parse connection
from parse_rest.connection import register
register("OpenBookScanner", "pytest")

class State1(State):
    
    def receive_message2(self, message):
        self.transition_into(State2())
    
    def is_state1(self):
        return True
    
    def is_state2(self):
        return False

class State2(State):
    
    def receive_message1(self, message):
        self.transition_into(State1())
    
    def is_state1(self):
        return False
    
    def is_state2(self):
        return True


class PollingStateX(PollingState):
    
    sleep = 0.0001
    
    def poll(self):
        if self.state_machine.stop_polling:
            self.transition_into(PollingDone())

    def is_done_polling(self):
        return False

class ErrorPollingStateX(PollingState):
    
    def poll(self):
        raise RuntimeError("Polling broken")


class PollingDone(State):

    def is_done_polling(self):
        return True

class StateMachineX(StateMachine):

    def __init__(self, state):
        super().__init__()
        self.stop_polling = False
        self.transition_into(state)

    def transition_into(self, new_state):
        print(self, "transitions into", new_state)
        super().transition_into(new_state)

class StateMachine1(StateMachineX): pass
class StateMachine2(StateMachineX): pass
        
@fixture
def m(s1):
    """Return a state machine."""
    return StateMachineX(s1)

@fixture
def s1():
    return State1()

@fixture
def s2():
    return State2()

@fixture
def mp():
    return StateMachineX(PollingStateX())

@fixture
def epm():
    return StateMachineX(ErrorPollingStateX())


@fixture
def broker():
    return LocalBroker()


@fixture
def mock():
    return Mock()


@fixture
def parse_broker(parse_required):
    return ParseBroker("pytest")


@fixture
def buffering_broker():
    return BufferingBroker()

#
# Interacting state machines
#


class CountingState(State):

    counter = 10

    def on_enter(self):
        print("entering", self)
        self.deliver_message(message.count_down(stm=self.state_machine))
    
    def receive_count_down(self, m):
        assert m["stm"] != self.state_machine
        self.counter -= 1
        if self.counter < 1:
            self.transition_into(FinalState())
        else:
            self.deliver_message(message.count_down(stm=self.state_machine))
    
    def __repr__(self):
        return "<{} at {}>".format(self.__class__.__name__, self.counter)

@fixture
def two_linked_state_machines():
    m1 = StateMachine1(TransitionOnReceivedMessage(CountingState()))
    m2 = StateMachine2(TransitionOnReceivedMessage(CountingState()))
    m1_messages = Mock()
    m2_messages = Mock()
    m1.subscribe(m2)
    m1.subscribe(m1_messages)
    m2.subscribe(m1)
    m2.subscribe(m2_messages)
    print("m1.subscribers", m1.subscribers)
    return m1, m2, m1_messages, m2_messages


#
# Parse
#


@fixture
def parse_required():
    if "PARSE_API_ROOT" not in os.environ:
       pytest.skip()

#
# Hardware Listener
#


class TestHardwareListener(HardwareListener):

    driver_support = False
    
    timout_for_driver_detection = 0.0001
    timout_for_hardware_changes = 0.0001
    
    def __init__(self):
        super().__init__()
        print("init")


    def has_driver_support(self):
        return self.driver_support
    
    new_test_hardware = []
    
    def listen_for_hardware(self):
        #print("x")
        if self.new_test_hardware:
            print("test1", self.new_test_hardware, self.get_hardware(), id(self), vars(self))
            self.found_new_hardware(self.new_test_hardware.pop())
            print("test2", self.new_test_hardware, self.get_hardware(), id(self), vars(self))


@fixture
def hardware_listener():
    hl = TestHardwareListener()
    hl.print_state_changes()
    yield hl
    hl.stop()

@fixture
def observer(hardware_listener):
    mock = Mock()
    hardware_listener.register_hardware_observer(mock)
    return mock


def timeout(condition, description=None, seconds=1, delay=0.001):
    stop = time.time() + seconds
    while stop > time.time() and not condition():
        time.sleep(delay)
    assert condition(), "The test condition timed out" + (": " + str(description) if description else ".")
__builtins__["timeout"] = timeout

