from openbookscanner.message import message


def test_can_subscribe_to_broker(parse_broker, mock):
    parse_broker.subscribe(mock)


def test_subscribers_receive_messages(parse_broker, mock):
    parse_broker.subscribe(mock)
    m = message.test()
    parse_broker.deliver_message(m)
    parse_broker.flush()
    mock.receive_message.assert_called_once_with(m)


