"""
Presenters which handle presenting a console on a terminal.
"""

from typing import Tuple, BinaryIO
try:
    from typing import Protocol # pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Protocol # type: ignore
from tcod import Console
from ._console_utils import get_console_order
from ._ansi import set_colours_true

_PAD_FG = (0, 0, 0, 0)

class Presenter(Protocol):
    """
    Presenter which handles presenting a console on a terminal.
    """

    def present(
        self,
        *,
        console: Console,
        term_dim: Tuple[int, int],
        out_file: BinaryIO,
        clear_colour: Tuple[int, int, int],
        align: Tuple[float, float]
    ) -> None:
        ...

class NaivePresenter(Presenter):
    """
    Basic presenter which always writes the whole console to the terminal.
    """

    def present(
        self,
        *,
        console: Console,
        term_dim: Tuple[int, int],
        out_file: BinaryIO,
        clear_colour: Tuple[int, int, int],
        align: Tuple[float, float]
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

        set_colours_true(_PAD_FG, pad_bg, out_file)
        for _ in range(pad_top):
            out_file.write(b"[%i;1H" % (term_y))
            out_file.write(b"[2K")
            term_y += 1

        for con_y in range(draw_dim[1]):
            out_file.write(b"[%i;%iH" % (term_y, pad_left + 1))
            set_colours_true(_PAD_FG, pad_bg, out_file)
            out_file.write(b"[1K")
            for con_x in range(draw_dim[0]):
                c, fg, bg = get_buf(con_x, con_y)
                set_colours_true(fg, bg, out_file)
                out_file.write(c)
            if pad_right > 0:
                set_colours_true(_PAD_FG, pad_bg, out_file)
                out_file.write(b"[0K")
            term_y += 1

        set_colours_true(_PAD_FG, pad_bg, out_file)
        for _ in range(pad_bottom):
            out_file.write(b"[%i;1H" % (term_y))
            out_file.write(b"[2K")
            term_y += 1

        out_file.flush()
