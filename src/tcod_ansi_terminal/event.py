"""
Implementation of event handling for terminals.

This provides a `wait()` that generates the events which can be supported on terminals. Import
constants, event types, etc. from the regular `tcod.event` module.

Supported events:
- KeyUp
- KeyDown
- TextInput
- Quit
- WindowResized

Limitations on keyboard input:
- Only the shift modifier is supported.
- Key scancodes are not supported and will always be `K_UNKNOWN`.
- Key up events will be generated immediately after key down events.
"""

from typing import Optional, Iterator
from tcod.event import Event
from ._internal_context import get_terminal_context_stack, get_events_manager

__all__ = (
    'wait',
)

def wait(timeout: Optional[float] = None) -> Iterator[Event]:
    context_stack = get_terminal_context_stack()
    assert context_stack, "wait() can only be called inside a context"
    return get_events_manager(context_stack[-1]).wait(timeout)
