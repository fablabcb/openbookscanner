from openbookscanner.message import message


def test_first_state_is_deferred(two_linked_state_machines):
    m1, m2, m1_messages, m2_messages = two_linked_state_machines
    assert m1.state.is_waiting_for_a_message_to_transition_to_the_next_state()
    assert m2.state.is_waiting_for_a_message_to_transition_to_the_next_state()
    m1_messages.receive_message.assert_not_called()
    m2_messages.receive_message.assert_not_called()
    

def test_update_triggers_the_collective_transition(two_linked_state_machines):
    m1, m2, m1_messages, m2_messages = two_linked_state_machines
    print("m1.subscribers", m1.subscribers)
    m1.update()
    print("m1.subscribers", m1.subscribers)
    print("m1 messages:\n", m1_messages.receive_message.call_args_list)
    assert m1.state.is_final()
    assert m2.state.is_final()
    assert m1_messages.receive_message.call_count == 10
    print("m2 messages:\n", m2_messages.receive_message.call_args_list)
    assert m2_messages.receive_message.call_count == 10

