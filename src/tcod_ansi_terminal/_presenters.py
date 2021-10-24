"""
Presenters which handle presenting a console on a terminal.
"""

from typing import Any, Callable, NamedTuple, Tuple, BinaryIO
try:
    from typing import Protocol # pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Protocol # type: ignore
from numpy.typing import NDArray
import numpy
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

class _ConsoleInfo(NamedTuple):
    con_dim: Tuple[int, int]
    buf_get: Callable[[int, int, NDArray[Any]], Any]

def _get_console_info(console: Console) -> _ConsoleInfo:
    order = get_console_order(console)
    con_dim = console.buffer.shape
    if order == "F":
        def buf_get(x: int, y: int, buf: NDArray[Any]) -> Any:
            return buf[x, y]
    elif order == "C":
        con_dim = con_dim[1], con_dim[0]
        def buf_get(x: int, y: int, buf: NDArray[Any]) -> Any:
            return buf[y, x]
    else:
        assert False, "unknown console order"
    return _ConsoleInfo(con_dim, buf_get)

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

        pad_bg = clear_colour + (0,)
        con_dim, buf_get = _get_console_info(console)

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
                c, fg, bg = buf_get(con_x, con_y, console.buffer)
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

class SparsePresenter:
    """
    Presenter which finds differences between frames and only writes the changes to the terminal.
    """

    def __init__(self) -> None:
        self._last_buffer = numpy.full(fill_value=0, shape=(0, 0))
        self._fallback = NaivePresenter()

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

        if console.buffer.shape != self._last_buffer.shape:
            self._fallback.present(
                console=console,
                term_dim=term_dim,
                out_file=out_file,
                clear_colour=clear_colour,
                align=align
            )

        else:
            con_dim, buf_get = _get_console_info(console)
            draw_dim = tuple(min(con_dim[i], term_dim[i]) for i in range(2))
            pad_top = int((term_dim[1] - draw_dim[1]) * align[0]) + 1
            pad_left = int((term_dim[0] - draw_dim[0]) * align[0]) + 1
            diff = console.buffer != self._last_buffer
            for con_x, con_y in numpy.ndindex(draw_dim): # type: ignore
                if buf_get(con_x, con_y, diff):
                    out_file.write(b"[%i;%iH" % (con_y + pad_top, con_x + pad_left))
                    c, fg, bg = buf_get(con_x, con_y, console.buffer)
                    set_colours_true(fg, bg, out_file)
                    out_file.write(c)

        self._last_buffer = numpy.copy(console.buffer) # type: ignore

        out_file.flush()
