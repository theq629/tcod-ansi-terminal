"""
This is the internal event system including hooks for the context.
"""

from typing import Optional, Callable, Iterator, List, BinaryIO
import time
from tcod.event import Event, KeyDown, KeyUp, TextInput, Quit, WindowResized, KeySym, Scancode, \
    KMOD_NONE, KMOD_SHIFT
from ._logging import logger
from ._platform import Platform
from . import _ansi

_terminal_response_delay = 0.01
_catchup_read_timeout = 100

class EventsManager:
    def __init__(
            self,
            platform: Platform,
            out_file: BinaryIO,
            resize_callback: Callable[[int, int], None],
    ):
        self._platform = platform
        self._out_file = out_file
        self._got_quit = False
        self._got_resize = False
        self._waiting_events: List[Event] = []
        self._resize_callback = resize_callback
        platform.watch_quit(self._on_quit)
        platform.watch_resize(self._on_resize)
        self.catchup()

    def catchup(self) -> None:
        if self._got_resize:
            _ansi.request_get_terminal_dim(self._out_file)
            time.sleep(_terminal_response_delay)
            self._waiting_events += self._handle_input(_catchup_read_timeout)

    def wait(self, timeout: Optional[float] = None) -> Iterator[Event]:
        self.catchup()
        if self._waiting_events:
            yield from self._waiting_events
            self._waiting_events.clear()
        yield from self._handle_input(timeout)

    def request_resize_event(self) -> None:
        self._got_resize = True
        self.catchup()

    def _on_quit(self) -> None:
        self._got_quit = True

    def _on_resize(self) -> None:
        self._got_resize = True

    def _finalize_resize(self, width: int, height: int) -> None:
        self._got_resize = False
        self._resize_callback(width, height)

    def _handle_input(self, timeout: Optional[float]) -> Iterator[Event]:
        key = self._platform.getch(timeout)
        if self._got_quit:
            yield Quit()
            self._got_quit = False
        if key is not None:
            if key == _ansi.escape:
                result = _ansi.get_escape_input(self._platform)
                if result is not None:
                    yield from self._handle_escape_input(result)
            else:
                yield from self._handle_key_press(key)

    def _handle_key_press(self, key: bytes) -> Iterator[Event]:
        key_text = key.decode('ascii')
        if key.isupper():
            key = key.lower()
            mod = KMOD_SHIFT
        else:
            mod = KMOD_NONE
        key_sym = ord(key)
        yield KeyDown(sym=key_sym, scancode=Scancode.UNKNOWN, mod=mod)
        yield TextInput(text=key_text)
        yield KeyUp(sym=key_sym, scancode=Scancode.UNKNOWN, mod=mod)

    def _handle_special_key(self, key_sym: KeySym) -> Iterator[Event]:
        yield KeyDown(sym=key_sym, scancode=Scancode.UNKNOWN, mod=KMOD_NONE)
        yield KeyUp(sym=key_sym, scancode=Scancode.UNKNOWN, mod=KMOD_NONE)

    def _handle_escape_input(self, event: _ansi.EscapeInputEvent) -> Iterator[Event]:
        if isinstance(event, _ansi.WindowResizeInput):
            self._finalize_resize(event.width, event.height)
            yield WindowResized(
                type='WINDOWRESIZED',
                width=event.width,
                height=event.height,
            )
        elif isinstance(event, _ansi.SpecialKeyInput):
            yield from self._handle_special_key(event.key_sym)
        else:
            logger.warning("unhandled escape input: %r", event)
