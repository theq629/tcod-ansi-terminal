"""
This is the internal event system including hooks for the context.
"""

from typing import Union, Optional, Callable, Iterator, List, Tuple, BinaryIO
from tcod.event import KeySym, Scancode, MouseButton, KeyDown, KeyUp, TextInput, Quit, \
    WindowResized, MouseMotion, MouseWheel, MouseButtonUp, MouseButtonDown, WindowEvent, \
    KMOD_NONE, KMOD_SHIFT
from ._logging import logger
from ._platform import Platform
from . import _ansi

_catchup_read_timeout = 100

TerminalEvent = Union[
    KeyDown,
    KeyUp,
    TextInput,
    Quit,
    WindowResized,
    MouseMotion,
    MouseWheel,
    MouseButtonUp,
    MouseButtonDown,
    WindowEvent,
]

class EventsManager:
    def __init__(
        self,
        platform: Platform,
        out_file: BinaryIO,
        resize_callback: Callable[[Tuple[int, int]], None]
    ) -> None:
        self._platform = platform
        self._out_file = out_file
        self._got_quit = False
        self._got_resize = False
        self._waiting_events: List[TerminalEvent] = []
        self._resize_callback = resize_callback
        self._last_mouse_motion: Optional[Tuple[int, int]] = None
        self._current_mouse_button_down: Optional[int] = None
        self._last_term_dim: Optional[Tuple[int, int]] = None
        platform.watch_quit(self._on_quit)
        platform.watch_resize(self._on_resize)
        self._catchup()

    def wait(self, timeout: Optional[float] = None) -> Iterator[TerminalEvent]:
        self._catchup()
        if self._waiting_events:
            yield from self._waiting_events
            self._waiting_events.clear()
        yield from self._handle_input(timeout)

    def get_terminal_dim(self) -> Optional[Tuple[int, int]]:
        self._got_resize = True
        self._catchup()
        return self._last_term_dim

    def _catchup(self) -> None:
        if self._got_resize:
            _ansi.save_cursor_pos(self._out_file)
            _ansi.request_get_terminal_dim(self._out_file)
            self._out_file.flush()
            while self._got_resize:
                self._waiting_events += self._handle_input(_catchup_read_timeout)

    def _on_quit(self) -> None:
        self._got_quit = True

    def _on_resize(self) -> None:
        self._got_resize = True

    def _handle_input(self, timeout: Optional[float]) -> Iterator[TerminalEvent]:
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

    def _handle_resize(self, event: _ansi.WindowResizeInput) -> Iterator[TerminalEvent]:
        self._got_resize = False
        _ansi.restore_cursor_pos(self._out_file)
        if event.dim != self._last_term_dim:
            self._resize_callback(event.dim)
            self._last_term_dim = event.dim
            yield WindowResized(
                type='WINDOWRESIZED',
                width=event.dim[0],
                height=event.dim[1],
            )

    def _handle_key_press(self, key: bytes) -> Iterator[TerminalEvent]:
        try:
            key_text = key.decode('ascii')
        except UnicodeDecodeError:
            return
        if key.isupper():
            key = key.lower()
            mod = KMOD_SHIFT
        else:
            mod = KMOD_NONE
        key_sym = ord(key)
        yield KeyDown(sym=key_sym, scancode=Scancode.UNKNOWN, mod=mod)
        yield TextInput(text=key_text)
        yield KeyUp(sym=key_sym, scancode=Scancode.UNKNOWN, mod=mod)

    def _handle_special_key(self, key_sym: KeySym) -> Iterator[TerminalEvent]:
        yield KeyDown(sym=key_sym, scancode=Scancode.UNKNOWN, mod=KMOD_NONE)
        yield KeyUp(sym=key_sym, scancode=Scancode.UNKNOWN, mod=KMOD_NONE)

    def _handle_mouse_motion(self, event: _ansi.MouseMotionInput) -> Iterator[TerminalEvent]:
        if self._last_mouse_motion is not None:
            motion = (
                event.pos[0] - self._last_mouse_motion[0],
                event.pos[1] - self._last_mouse_motion[1],
            )
        else:
            motion = (0, 0)
        self._last_mouse_motion = event.pos
        yield MouseMotion(position=event.pos, motion=motion, tile=event.pos)

    def _handle_mouse_button(self, event: _ansi.MouseButtonInput) -> Iterator[TerminalEvent]:
        if self._last_mouse_motion is None:
            logger.warning("mouse button but don't have position")
            return
        if event.button == 3:
            if self._current_mouse_button_down is None:
                logger.warning("mouse button up but didn't know it was down")
                return
            button = self._current_mouse_button_down
            self._current_mouse_button_down = None
            yield MouseButtonUp(
                pixel=self._last_mouse_motion,
                tile=self._last_mouse_motion,
                button=button,
            )
        else:
            if event.button == 0:
                button = MouseButton.LEFT
            elif event.button == 1:
                button = MouseButton.MIDDLE
            elif event.button == 2:
                button = MouseButton.RIGHT
            else:
                logger.warning("unhandled mouse button: %r", event)
            self._current_mouse_button_down = button
            yield MouseButtonDown(
                pixel=self._last_mouse_motion,
                tile=self._last_mouse_motion,
                button=button,
            )

    def _handle_mouse_wheel(self, event: _ansi.MouseWheelInput) -> Iterator[TerminalEvent]:
        if event.button == 0:
            yield MouseWheel(x=0, y=1, flipped=False)
        elif event.button == 1:
            yield MouseWheel(x=0, y=-1, flipped=False)
        else:
            logger.warning("unhandled mouse wheel button: %r", event)

    def _handle_escape_input(self, event: _ansi.EscapeInputEvent) -> Iterator[TerminalEvent]:
        if isinstance(event, _ansi.WindowResizeInput):
            yield from self._handle_resize(event)
        elif isinstance(event, _ansi.SpecialKeyInput):
            yield from self._handle_special_key(event.key_sym)
        elif isinstance(event, _ansi.MouseMotionInput):
            yield from self._handle_mouse_motion(event)
        elif isinstance(event, _ansi.MouseButtonInput):
            yield from self._handle_mouse_button(event)
        elif isinstance(event, _ansi.MouseWheelInput):
            yield from self._handle_mouse_wheel(event)
        elif isinstance(event, _ansi.WindowFocusGained):
            yield WindowEvent(type='WindowFocusGained')
        elif isinstance(event, _ansi.WindowFocusLost):
            yield WindowEvent(type='WindowFocusLost')
        else:
            logger.warning("unhandled escape input: %r", event)
