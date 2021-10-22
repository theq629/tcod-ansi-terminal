"""
ANSI terminal control.
"""

from typing import Tuple, BinaryIO
from tcod import Console
from ._console_utils import get_console_order
from ._platform import Platform

_PAD_FG = (0, 0, 0, 0)

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

def _set_colours_true(
    fg: Tuple[int, int, int, int],
    bg: Tuple[int, int, int, int],
    out_file: BinaryIO
) -> None:
    out_file.write(b"[38;2;%i;%i;%im[48;2;%i;%i;%im" \
                   % (fg[0], fg[1], fg[2], bg[0], bg[1], bg[2]))

def render_console(
    console: Console,
    term_dim: Tuple[int, int],
    align: Tuple[float, float],
    clear_colour: Tuple[int, int, int],
    out_file: BinaryIO
) -> None:
    # pylint: disable=too-many-locals

    order = get_console_order(console)
    pad_bg = clear_colour + (0,)

    con_dim = console.buffer.shape
    if order == "F":
        def get_buf(x: int, y: int) \
                -> Tuple[bytes, Tuple[int, int, int, int], Tuple[int, int, int, int]]:
            return console.buffer[x, y] # type: ignore
    elif order == "C":
        con_dim = con_dim[1], con_dim[0]
        def get_buf(x: int, y: int) \
                -> Tuple[bytes, Tuple[int, int, int, int], Tuple[int, int, int, int]]:
            return console.buffer[y, x] # type: ignore
    else:
        assert False, "unknown console order"

    draw_dim = tuple(min(con_dim[i], term_dim[i]) for i in range(2))
    pad_left = int((term_dim[0] - draw_dim[0]) * align[0])
    pad_right = term_dim[0] - draw_dim[0] - pad_left
    pad_top = int((term_dim[1] - draw_dim[1]) * align[0])
    pad_bottom = term_dim[1] - draw_dim[1] - pad_top

    term_y = 1

    _set_colours_true(_PAD_FG, pad_bg, out_file)
    for _ in range(pad_top):
        out_file.write(b"[%i;1H" % (term_y))
        out_file.write(b"[2K")
        term_y += 1

    for con_y in range(draw_dim[1]):
        out_file.write(b"[%i;%iH" % (term_y, pad_left + 1))
        _set_colours_true(_PAD_FG, pad_bg, out_file)
        out_file.write(b"[1K")
        for con_x in range(draw_dim[0]):
            c, fg, bg = get_buf(con_x, con_y)
            _set_colours_true(fg, bg, out_file)
            out_file.write(c)
        if pad_right > 0:
            _set_colours_true(_PAD_FG, pad_bg, out_file)
            out_file.write(b"[0K")
        term_y += 1

    _set_colours_true(_PAD_FG, pad_bg, out_file)
    for _ in range(pad_bottom):
        out_file.write(b"[%i;1H" % (term_y))
        out_file.write(b"[2K")
        term_y += 1
