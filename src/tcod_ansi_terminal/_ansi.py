"""
ANSI terminal control.
"""

from typing import Union, Optional, Tuple, BinaryIO, NamedTuple
import dataclasses
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

EscapeInputEvent = Union[
    WindowResizeInput,
]

def reset(out_file: BinaryIO) -> None:
    out_file.write(b"%sc" % (escape))

def hide_cursor(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?25l" % (escape))

def show_cursor(out_file: BinaryIO) -> None:
    out_file.write(b"%s[?25h" % (escape))

def request_terminal_dim(dim: Tuple[int, int], out_file: BinaryIO) -> None:
    w, h = dim
    out_file.write(b"%s[8;%i;%it" % (escape, h, w))

def request_terminal_title(title: str, out_file: BinaryIO) -> None:
    out_file.write(b"%s]0;%s\007" % (escape, title.encode('utf8')))

def set_cursor_pos(pos: Tuple[int, int], out_file: BinaryIO) -> None:
    x, y = pos
    out_file.write(b"%s[%i;%if" % (escape, y, x))

def clear_screen(out_file: BinaryIO) -> None:
    out_file.write(b"%s[2J" % (escape))

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

def get_escape_input(
    platform: Platform,
    timeout: Optional[int] = None,
) -> Optional[EscapeInputEvent]:
    result = _read_escape_input(platform, timeout)
    if result is None:
        return None
    if result.start == b'[':
        if result.end == b'R' and result.arg1 is not None:
            return WindowResizeInput(width=result.arg1, height=result.arg0)
    logger.debug("unknown escape: %r", result)
    return None

def request_get_terminal_dim(out_file: BinaryIO) -> None:
    b = 2**16 - 1
    out_file.write(b"%s[%i;%iH" % (escape, b, b))
    out_file.flush()
    out_file.write(b"%s[6n" % (escape))
    out_file.flush()

def make_set_colours_true(
    fg: Tuple[int, int, int, int],
    bg: Tuple[int, int, int, int],
) -> bytes:
    return b"%s[38;2;%i;%i;%im%s[48;2;%i;%i;%im" \
        % (escape, fg[0], fg[1], fg[2], escape, bg[0], bg[1], bg[2])
