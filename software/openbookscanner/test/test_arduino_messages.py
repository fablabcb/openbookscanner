"""Test the message conversion for the serial.

This converts the messages from and to the dictionary form.
"""

from openbookscanner.serial import message_to_serial, message_from_serial, SerialMessageAdapter
from openbookscanner.message import message
from pytest import mark, fixture
from unittest.mock import Mock, call


class TestMessagesToTheserial:
    
    @mark.parametrize("message,expected_result", [
        (message.test(), "test\r\n"),
        (message.asdhsakhdahskdhas(asd="assda"), "asdhsakhdahskdhas\r\n")
    ])
    def test_message_with_only_name(self, message, expected_result):
        result = message_to_serial(message)
        assert result == expected_result

class TestMessagesFromTheserial:

    @mark.parametrize("expected_result,message", [
        (message.test(), "test\r\n"),
        (message.asdhsakhdahskdhas(), "asdhsakhdahskdhas\r\n")
    ])
    def test_message_with_only_name(self, message, expected_result):
        result = message_from_serial(message)
        assert result == expected_result

    @mark.parametrize("expected_result,message", [
        (message.log(level="debug", text="test test debug"), "[debug]test test debug\r\n"),
        (message.log(level="error", text="Oh No!"), "[error] Oh No!\r\n")
    ])
    def test_handle_log_messages(self, message, expected_result):
        result = message_from_serial(message)
        assert result == expected_result


class TestMessageAdapter:

    @fixture
    def serial(self):
        return Mock()
        
    @fixture
    def adapter(self, serial):
        return SerialMessageAdapter(serial)
        
    @fixture
    def subscriber(self, adapter):
        subscriber = Mock()
        adapter.subscribe(subscriber)
        return subscriber
    
    def test_sending_message_transforms_it_into_bytes(self, adapter, serial):
        adapter.receive_message(message.test())
        # see https://pythonhosted.org/pyserial/pyserial_api.html#serial.Serial.write
        serial.write.assert_called_once_with(b"test\r\n")
    
    def test_messages_arrive_in_order(self, adapter, serial):
        adapter.receive_message(message.test1())
        adapter.receive_message(message.test2())
        serial.write.assert_has_calls([call(b"test1\r\n"), call(b"test2")])
    
    @mark.parametrize("bytes,message", [
        (message.test(), b"test\r\n"),
        (message.asdhsakhdahskdhas(), b"asdhsakhdahskdhas\r\n")
    ])
    def test_reading_one_line(self, adapter, serial, bytes, message, mock):
        serial.in_waiting.side_effect = [len(bytes), 0]
        serial.readline.return_value = bytes
        adapter.deliver_message = mock
        adapter.flush()
        serial.readline.assert_called_once()
        mock.assert_called_once_with(message)
        
        
        
        
        
        
        
        
        
        
