"""
ANSI terminal control.
"""

from typing import Tuple, BinaryIO
from ._platform import Platform

def reset(out_file: BinaryIO) -> None:
    out_file.write(b"c")

def hide_cursor(out_file: BinaryIO) -> None:
    out_file.write(b"[?25l")

def show_cursor(out_file: BinaryIO) -> None:
    out_file.write(b"[?25h")

def request_terminal_dim(dim: Tuple[int, int], out_file: BinaryIO) -> None:
    w, h = dim
    out_file.write(b"[8;%i;%it" % (h, w))

def request_terminal_title(title: str, out_file: BinaryIO) -> None:
    out_file.write(b"]0;%s\007" % (title.encode('utf8')))

def set_cursor_pos(pos: Tuple[int, int], out_file: BinaryIO) -> None:
    x, y = pos
    out_file.write(b"[%i;%if" % (y, x))

def clear_screen(out_file: BinaryIO) -> None:
    out_file.write(b"[2J")

def _get_cursor_position(out_file: BinaryIO, platform: Platform) -> Tuple[int, int]:
    out_file.write(b"[6n")
    out_file.flush()
    if platform.getch() == b'' and platform.getch() == b'[':
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
    out_file.write(b"[%i;%iH" % (b, b))
    out_file.flush()
    w, h = _get_cursor_position(out_file, platform)
    if w == 0 and h == 0:
        return 80, 24
    return w, h

def make_set_colours_true(
    fg: Tuple[int, int, int, int],
    bg: Tuple[int, int, int, int],
) -> bytes:
    return b"[38;2;%i;%i;%im[48;2;%i;%i;%im" \
        % (fg[0], fg[1], fg[2], bg[0], bg[1], bg[2])
