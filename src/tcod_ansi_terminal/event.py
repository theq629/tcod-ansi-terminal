"""
Implementation of event handling for terminals.

This provides a `wait()` that generates the events which can be supported on
terminals. Import constants, event types, etc. from the regular `tcod.event`
module.

Supported events are given by the union type `TerminalEvent`.

Limitations on keyboard input:
- Only the shift modifier is supported.
- Key scancodes are not supported and will always be `K_UNKNOWN`.
- Key up events will be generated immediately after key down events.
"""

from typing import Optional, Iterator
try:
    from typing import Protocol # pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Protocol # type: ignore
from tcod.event import Event
from ._internal_context import get_terminal_context_stack, get_events_manager
from ._internal_event import TerminalEvent

__all__ = (
    'TerminalEvent',
    'TerminalCompatibleEventWait',
    'wait',
)

class TerminalCompatibleEventWait(Protocol):
    """
    Protocol for event wait interface that can be supported on terminals.

    Regular TCOD `wait()` should satisfy this protocol, as does the `wait()`
    here.
    """
    def __call__(self, timeout: Optional[float] = None) -> Iterator[Event]:
        ...

def wait(timeout: Optional[float] = None) -> Iterator[TerminalEvent]:
    """
    Block until events exist, then return an event iterator.

    `timeout` is the maximum number of seconds to wait, as for regular TCOD
    `wait()`.
    """
    context_stack = get_terminal_context_stack()
    assert context_stack, "wait() can only be called inside a context"
    return get_events_manager(context_stack[-1]).wait(timeout)
