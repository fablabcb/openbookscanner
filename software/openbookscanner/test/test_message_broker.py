from openbookscanner.message import message


def test_can_subscribe_to_broker(broker, mock):
    broker.subscribe(mock)


def test_subscribers_receive_messages(broker, mock):
    broker.subscribe(mock)
    m = message.test()
    broker.receive_message(m)
    mock.receive_message.assert_called_once_with(m)


