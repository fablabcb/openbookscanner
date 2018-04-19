from openbookscanner.message import message
import time
from pytest import raises

class TestStateTransition:

    def test_state1(self, s1):
        assert s1.is_state1()
        assert not s1.is_state2()


    def test_state2(self, s2):
        assert s2.is_state2()
        assert not s2.is_state1()


    def test_first_state_is_state1(self, m):
        assert m.state.is_state1()


    def test_receive_message1_stays_in_state1(self, m):
        m.receive_message(message.message1())
        assert m.state.is_state1()


    def test_receive_message2_goes_into_state2(self, m):
        m.receive_message(message.message2())
        assert m.state.is_state2()
        

    def test_receive_message2_goes_into_state2_and_stays(self, m):
        m.receive_message(message.message2())
        m.receive_message(message.message2())
        assert m.state.is_state2()
    
class TestPollingState:

    def test_polling_state_is_running(self, mp):
        print(mp.state)
        print(mp.state.future)
        mp.update()
        print(mp.state)
        assert mp.state.is_running()
        assert not mp.state.is_done_polling()
        mp.stop_polling = True


    def test_can_exit_polling_state(self, mp):
        mp.stop_polling = True
        mp.state.wait(1)
        print(mp.state)
        print(mp.state.future)
        mp.update()
        print(mp.state)
        assert mp.state.is_done_polling()
    

    def test_transition_into_error_state(self, epm):
        epm.state.wait()
        with raises(RuntimeError):
            epm.update()
        with raises(RuntimeError):
            epm.update()

class TestStateMachineObserver:
    """The state machine implements an observer pattern."""
    
    def test_no_state_change_on_update(self, m, mock):
        m.observe_state(mock)
        m.update()
        mock.state_changed.assert_not_called()
    
    def test_state_change_notifies_observers(self, m, mock):
        m.observe_state(mock)
        m.receive_message(message.message2())
        mock.state_changed.assert_called_once_with(m)
        
    

