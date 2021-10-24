"""
Presenters which handle presenting a console on a terminal.
"""

from typing import Any, Callable, Iterable, NamedTuple, Tuple, BinaryIO
try:
    from typing import Protocol # pylint: disable=ungrouped-imports
except ImportError:
    from typing_extensions import Protocol # type: ignore
from numpy.typing import NDArray
import numpy
from tcod import Console
from ._console_utils import get_console_order
from ._ansi import make_set_colours_true

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

class _DrawPlan(NamedTuple):
    draw_dim: Tuple[int, int]
    pad_left: int
    pad_top: int
    buf_get: Callable[[int, int, NDArray[Any]], Any]

def _get_draw_plan(
    console: Console,
    term_dim: Tuple[int, int],
    align: Tuple[float, float]
) -> _DrawPlan:
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

    draw_dim = (min(con_dim[0], term_dim[0]), min(con_dim[1], term_dim[1]))
    pad_left = int((term_dim[0] - draw_dim[0]) * align[0])
    pad_top = int((term_dim[1] - draw_dim[1]) * align[1])

    return _DrawPlan(draw_dim, pad_left, pad_top, buf_get)

def _draw_naive(
    *,
    draw_dim: Tuple[int, int],
    pad_left: int,
    pad_right: int,
    pad_top: int,
    pad_bottom: int,
    pad_bg: Tuple[int, int, int, int],
    buf_get: Callable[[int, int, NDArray[Any]], Any],
    console: Console
) -> Iterable[bytes]:
    term_y = 1

    yield make_set_colours_true(_PAD_FG, pad_bg)
    for _ in range(pad_top):
        yield b"[%i;1H" % (term_y)
        yield b"[2K"
        term_y += 1

    for con_y in range(draw_dim[1]):
        yield b"[%i;%iH" % (term_y, pad_left + 1)
        yield make_set_colours_true(_PAD_FG, pad_bg)
        yield b"[1K"
        for con_x in range(draw_dim[0]):
            c, fg, bg = buf_get(con_x, con_y, console.buffer)
            yield make_set_colours_true(fg, bg)
            yield c
        if pad_right > 0:
            yield make_set_colours_true(_PAD_FG, pad_bg)
            yield b"[0K"
        term_y += 1

    yield make_set_colours_true(_PAD_FG, pad_bg)
    for _ in range(pad_bottom):
        yield b"[%i;1H" % (term_y)
        yield b"[2K"
        term_y += 1

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

        draw_dim, pad_left, pad_top, buf_get = _get_draw_plan(console, term_dim, align)

        out_file.write(b''.join(_draw_naive(
            draw_dim=draw_dim,
            pad_left=pad_left,
            pad_top=pad_top,
            pad_right=term_dim[0] - draw_dim[0] - pad_left,
            pad_bottom=term_dim[1] - draw_dim[1] - pad_top,
            pad_bg=clear_colour + (0,),
            buf_get=buf_get,
            console=console
        )))
        out_file.flush()

def _draw_sparse_changes(
    *,
    draw_dim: Tuple[int, int],
    pad_left: int,
    pad_top: int,
    buf_get: Callable[[int, int, NDArray[Any]], Any],
    to_draw: NDArray[Any],
    console: Console
) -> Iterable[bytes]:
    for con_x, con_y in numpy.ndindex(draw_dim): # type: ignore
        if buf_get(con_x, con_y, to_draw):
            yield b"[%i;%iH" % (con_y + pad_top, con_x + pad_left)
            c, fg, bg = buf_get(con_x, con_y, console.buffer)
            yield make_set_colours_true(fg, bg)
            yield c

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
            draw_dim, pad_left, pad_top, buf_get = _get_draw_plan(console, term_dim, align)
            diff = console.buffer != self._last_buffer
            out_file.write(b''.join(_draw_sparse_changes(
                draw_dim=draw_dim,
                pad_left=pad_left + 1,
                pad_top=pad_top + 1,
                buf_get=buf_get,
                to_draw=diff,
                console=console
            )))

        self._last_buffer = numpy.copy(console.buffer) # type: ignore

        out_file.flush()
