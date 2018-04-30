"""Test the message conversion for the arduino.

This converts the messages from and to the dictionary form.
"""

from openbookscanner.message import to_arduino, from_arduino, message
from pytest import mark

class TestMessagesToTheArduino:
    
    @mark.parametrize("message,expected_result", [
        (message.test(), b"test\r\n"),
        (message.asdhsakhdahskdhas(asd="assda"), b"asdhsakhdahskdhas\r\n")
    ])
    def test_message_with_only_name(self, message, expected_result):
        result = to_arduino(message)
        assert result == expected_result

class TestMessagesFromTheArduino:

    @mark.parametrize("expected_result,message", [
        (message.test(), b"test\r\n"),
        (message.asdhsakhdahskdhas(), b"asdhsakhdahskdhas\r\n")
    ])
    def test_message_with_only_name(self, message, expected_result):
        result = from_arduino(message)
        assert result == expected_result

    @mark.parametrize("expected_result,message", [
        (message.log(level="debug", text="test test debug"), b"[debug]test test debug\r\n"),
        (message.log(level="error", text="Oh No!"), b"[error] Oh No!\r\n")
    ])
    def test_handle_log_messages(self, message, expected_result):
        result = from_arduino(message)
        assert result == expected_result

