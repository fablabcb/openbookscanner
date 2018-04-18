from openbookscanner.states import message
import time


def test_state1(s1):
    assert s1.is_state1()
    assert not s1.is_state2()


def test_state2(s2):
    assert s2.is_state2()
    assert not s2.is_state1()


def test_first_state_is_state1(m):
    assert m.state.is_state1()


def test_receive_message1_stays_in_state1(m):
    m.receive_message(message.message1())
    assert m.state.is_state1()


def test_receive_message2_goes_into_state2(m):
    m.receive_message(message.message2())
    assert m.state.is_state2()
    

def test_receive_message2_goes_into_state2_and_stays(m):
    m.receive_message(message.message2())
    m.receive_message(message.message2())
    assert m.state.is_state2()
    

def test_polling_state_is_running(mp):
    print(mp.state)
    print(mp.state.future)
    mp.update()
    print(mp.state)
    assert mp.state.is_running()
    assert not mp.state.is_done_polling()
    mp.stop_polling = True


def test_can_exit_polling_state(mp):
    mp.stop_polling = True
    mp.state.wait(1)
    print(mp.state)
    print(mp.state.future)
    mp.update()
    print(mp.state)
    assert mp.state.is_done_polling()
    

