"""
ANSI terminal control.
"""

from typing import Union, Optional, Tuple, BinaryIO, NamedTuple
import dataclasses
from tcod.event import KeySym
from ._logging import logger
from ._platform import Platform

escape = b"\x1B"

class _EscapeInputResult(NamedTuple):
    start: bytes
    end: Optional[bytes]
    arg0: int
    arg1: Optional[int]

@dataclasses.dataclass(frozen=True)
class WindowResizeInput:
    width: int
    height: int

@dataclasses.dataclass(frozen=True)
class SpecialKeyInput:
    key_sym: KeySym

@dataclasses.dataclass(frozen=True)
class MouseMotionInput:
    pos: Tuple[int, int]

@dataclasses.dataclass(frozen=True)
class MouseButtonInput:
    button: int

@dataclasses.dataclass(frozen=True)
class MouseWheelInput:
    button: int

@dataclasses.dataclass(frozen=True)
class WindowFocusGained:
    pass

@dataclasses.dataclass(frozen=True)
class WindowFocusLost:
    pass

EscapeInputEvent = Union[
    WindowResizeInput,
    SpecialKeyInput,
    MouseMotionInput,
    MouseButtonInput,
    MouseWheelInput,
    WindowFocusGained,
    WindowFocusLost,
]

def reset(out_file: BinaryIO) -> None:
    out_file.write(b"%sc" % (escape))

def hide_cursor(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?25l" % (escape))

def show_cursor(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?25h" % (escape))

def enable_mouse_tracking(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?1003h" % (escape))

def disable_mouse_tracking(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?1003l" % (escape))

def enable_focus_reporting(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?1004h" % (escape))

def disable_focus_reporting(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?1004l" % (escape))

def request_terminal_chars_dim(dim: Tuple[int, int], out_file: BinaryIO) -> None:
    w, h = dim
    out_file.write(b"%s[8;%i;%it" % (escape, h, w))

def request_terminal_pixels_dim(dim: Tuple[int, int], out_file: BinaryIO) -> None:
    w, h = dim
    out_file.write(b"%s[4;%i;%it" % (escape, h, w))

def request_terminal_window_pos(pos: Tuple[int, int], out_file: BinaryIO) -> None:
    x, y = pos
    out_file.write(b"%s[3;%i;%it" % (escape, x, y))

def request_terminal_title(title: str, out_file: BinaryIO) -> None:
    out_file.write(b"%s]0;%s\007" % (escape, title.encode('utf8')))

def clear_screen(out_file: BinaryIO) -> None:
    out_file.write(b"%s[2J" % (escape))

def set_cursor_pos(pos: Tuple[int, int], out_file: BinaryIO) -> None:
    x, y = pos
    out_file.write(b"%s[%i;%iH" % (escape, y, x))

def request_get_cursor_pos(out_file: BinaryIO) -> None:
    out_file.write(b"%s[6n" % (escape))

def request_get_terminal_dim(out_file: BinaryIO) -> None:
    b = 2**15 - 1
    set_cursor_pos((b, b), out_file)
    request_get_cursor_pos(out_file)

def _read_terminated_int(
    platform: Platform,
    timeout: Optional[int],
    max_len: int = 16,
) -> Tuple[int, Optional[bytes]]:
    num = 0
    for _ in range(max_len):
        ch = platform.getch(timeout)
        if ch is None:
            break
        if not ch.isdigit():
            return num, ch
        num = num * 10 + int(ch)
    return num, None

def _read_escape_input(platform: Platform, timeout: Optional[int]) -> Optional[_EscapeInputResult]:
    start = platform.getch(timeout)
    if start not in (b'[', b'O'):
        return None
    arg0, end = _read_terminated_int(platform, timeout)
    if end == b';':
        arg1, end = _read_terminated_int(platform, timeout)
    else:
        arg1 = None
    return _EscapeInputResult(start=start, end=end, arg0=arg0, arg1=arg1)

def _get_mouse_input(platform: Platform, timeout: Optional[int]) -> Optional[EscapeInputEvent]:
    cb_ch = platform.getch(timeout)
    x_ch = platform.getch(timeout)
    y_ch = platform.getch(timeout)
    if cb_ch is None or x_ch is None or y_ch is None:
        return None
    cb = cb_ch[0]
    x = x_ch[0] - 33
    y = y_ch[0] - 33
    if cb & 32 != 0:
        if cb & 64 != 0:
            return MouseWheelInput(button=cb & 3)
        return MouseButtonInput(button=cb & 3)
    return MouseMotionInput(pos=(x, y))

def get_escape_input(
    platform: Platform,
    timeout: Optional[int] = None,
) -> Optional[EscapeInputEvent]:
    # pylint: disable=too-many-branches,too-many-return-statements
    result = _read_escape_input(platform, timeout)
    if result is None:
        return None
    if result.start == b'[': # CSI
        if result.end == b'R' and result.arg1 is not None:
            return WindowResizeInput(width=result.arg1, height=result.arg0)
        if result.end == b'M':
            return _get_mouse_input(platform, timeout)
        if result.end == b'I':
            return WindowFocusGained()
        if result.end == b'O':
            return WindowFocusLost()
        if result.end == b'A':
            return SpecialKeyInput(KeySym.UP)
        if result.end == b'B':
            return SpecialKeyInput(KeySym.DOWN)
        if result.end == b'C':
            return SpecialKeyInput(KeySym.RIGHT)
        if result.end == b'D':
            return SpecialKeyInput(KeySym.LEFT)
        if result.end == b'H':
            return SpecialKeyInput(KeySym.HOME)
        if result.end == b'F':
            return SpecialKeyInput(KeySym.END)
        if result.end == b'P':
            return SpecialKeyInput(KeySym.F1)
        if result.end == b'Q':
            return SpecialKeyInput(KeySym.F2)
        if result.end == b'R':
            return SpecialKeyInput(KeySym.F3)
        if result.end == b'S':
            return SpecialKeyInput(KeySym.F4)
        if result.end == b'~' and result.arg0 is not None:
            if result.arg0 == 1:
                return SpecialKeyInput(KeySym.HOME)
            if result.arg0 == 2:
                return SpecialKeyInput(KeySym.INSERT)
            if result.arg0 == 3:
                return SpecialKeyInput(KeySym.DELETE)
            if result.arg0 == 4:
                return SpecialKeyInput(KeySym.END)
            if result.arg0 == 5:
                return SpecialKeyInput(KeySym.PAGEUP)
            if result.arg0 == 6:
                return SpecialKeyInput(KeySym.PAGEDOWN)
            if result.arg0 == 7:
                return SpecialKeyInput(KeySym.HOME)
            if result.arg0 == 8:
                return SpecialKeyInput(KeySym.END)
            if result.arg0 == 11:
                return SpecialKeyInput(KeySym.F1)
            if result.arg0 == 12:
                return SpecialKeyInput(KeySym.F2)
            if result.arg0 == 13:
                return SpecialKeyInput(KeySym.F3)
            if result.arg0 == 14:
                return SpecialKeyInput(KeySym.F4)
            if result.arg0 == 15:
                return SpecialKeyInput(KeySym.F5)
            if result.arg0 == 17:
                return SpecialKeyInput(KeySym.F6)
            if result.arg0 == 18:
                return SpecialKeyInput(KeySym.F7)
            if result.arg0 == 19:
                return SpecialKeyInput(KeySym.F8)
            if result.arg0 == 20:
                return SpecialKeyInput(KeySym.F9)
            if result.arg0 == 21:
                return SpecialKeyInput(KeySym.F10)
            if result.arg0 == 23:
                return SpecialKeyInput(KeySym.F11)
            if result.arg0 == 24:
                return SpecialKeyInput(KeySym.F12)
    elif result.start == b'O': # SS3
        if result.end == b'P':
            return SpecialKeyInput(KeySym.F1)
        if result.end == b'Q':
            return SpecialKeyInput(KeySym.F2)
        if result.end == b'R':
            return SpecialKeyInput(KeySym.F3)
        if result.end == b'S':
            return SpecialKeyInput(KeySym.F4)
    logger.debug("unknown escape: %r", result)
    return None

def make_set_colours_true(
    fg: Tuple[int, int, int, int],
    bg: Tuple[int, int, int, int],
) -> bytes:
    return b"%s[38;2;%i;%i;%im%s[48;2;%i;%i;%im" \
        % (escape, fg[0], fg[1], fg[2], escape, bg[0], bg[1], bg[2])
