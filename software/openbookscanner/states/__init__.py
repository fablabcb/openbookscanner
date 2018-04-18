"""
This module contains the state machines.

They can send and receive messages.
Via a broker, they can distribute them.

Further Reading
- https://en.wikipedia.org/wiki/State_pattern
- https://en.wikipedia.org/wiki/Strategy_pattern
"""

from .message import message
from .state import *

