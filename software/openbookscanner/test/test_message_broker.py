from openbookscanner.message import message


def test_can_subscribe_to_broker(broker, mock):
    broker.subscribe(mock)


def test_subscribers_receive_messages(broker, mock):
    broker.subscribe(mock)
    m = message.test()
    broker.deliver_message(m)
    mock.receive_message.assert_called_once_with(m)


def test_defer_messages(buffering_broker, mock):
    buffering_broker.subscribe(mock)
    m = message.test()
    buffering_broker.deliver_message(m)
    mock.receive_message.assert_not_called()
    buffering_broker.flush()
    mock.receive_message.assert_called_once_with(m)
    
