"""
ANSI terminal control.
"""

from typing import Tuple, BinaryIO
from ._platform import Platform

escape = b"\x1B"

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

def _get_cursor_position(out_file: BinaryIO, platform: Platform) -> Tuple[int, int]:
    out_file.write(b"%s[6n" % (escape))
    out_file.flush()
    if platform.getch() == escape and platform.getch() == b'[':
        buf = b""
        while True:
            char = platform.getch()
            if char is None:
                continue
            if char == b'R':
                break
            buf += char
        result = tuple(int(x) for x in buf.split(b';'))
        y, x = result[:2]
        return x, y
    return 0, 0

def get_terminal_size(out_file: BinaryIO, platform: Platform) -> Tuple[int, int]:
    b = 2**16 - 1
    out_file.write(b"%s[%i;%iH" % (escape, b, b))
    out_file.flush()
    w, h = _get_cursor_position(out_file, platform)
    if w == 0 and h == 0:
        return 80, 24
    return w, h

def make_set_colours_true(
    fg: Tuple[int, int, int, int],
    bg: Tuple[int, int, int, int],
) -> bytes:
    return b"%s[38;2;%i;%i;%im%s[48;2;%i;%i;%im" \
        % (escape, fg[0], fg[1], fg[2], escape, bg[0], bg[1], bg[2])
