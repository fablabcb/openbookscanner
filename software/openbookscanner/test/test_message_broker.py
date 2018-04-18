from openbookscanner.message import message


def test_can_subscribe_to_broker(broker, mock):
    broker.subscribe(mock)


def test_subscribers_receive_messages(broker, mock):
    broker.subscribe(mock)
    m = message.test()
    broker.deliver_message(m)
    mock.receive_message.assert_called_once_with(m)


def test_defer_messages(deferring_broker, mock):
    deferring_broker.subscribe(mock)
    m = message.test()
    deferring_broker.deliver_message(m)
    mock.receive_message.assert_not_called()
    deferring_broker.receive_messages()
    mock.receive_message.assert_called_once_with(m)
    
