import os
os.environ["PARSE_API_ROOT"] = "http://localhost:1337/parse"

from pytest import fixture
from openbookscanner.states import State, FinalState, StateMachine, PollingState, TransitionOnReceivedMessage
import time
from openbookscanner.broker import LocalBroker, ParseBroker
from unittest.mock import Mock

from parse_rest.connection import register
register("APPLICATION_ID", "pytest")

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
        self.stop_polling = False
        self.transition_into(state)

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
def parse_broker():
    return ParseBroker("pytest")


#
# Interacting state machines
#


class CountingState(State):

    counter = 10

    def on_enter(self):
        self.deliver_message(message.count_down(stm=self.state_machine))
    
    def receive_count_down(self, message):
        assert message["stm"] != self.stm
        self.counter -= 1
        if self.counter < 0:
            self.transition_into(FinalState())

@fixture
def 




