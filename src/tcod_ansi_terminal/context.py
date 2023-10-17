"""
TCOD-compatible contexts that will write to a terminal.
"""

from typing import Optional
import sys
import os
from ._abstract_context import TerminalCompatibleContext
from ._internal_context import TerminalContext, make_terminal_context
from ._presenters import Presenter, NaivePresenter, SparsePresenter

__all__ = (
    'TerminalCompatibleContext',
    'TerminalContext',
    'new',
    'Presenter',
    'NaivePresenter',
    'SparsePresenter',
)

def new(
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    columns: Optional[int] = None,
    rows: Optional[int] = None,
    title: Optional[str] = None
) -> TerminalContext:
    """
    Corresponds to `tcod.context.new()` but produces a terminal context.

    The position and dimension settings `x`, `y`, `width`, `height`, `columns`
    and `rows` are requests, which may or may not be granted; the caller should
    use the returned context's `recommended_console_size()` or `new_console()`
    to get the actual dimensions.

    This does not read `sys.argv` or take `argv` as input.
    """
    in_file = sys.stdin.buffer
    out_file = os.fdopen(sys.stdout.fileno(), 'wb', 1024)
    return make_terminal_context(
        in_file=in_file,
        out_file=out_file,
        requested_window_pos=(x, y) if x is not None and y is not None else None,
        requested_pixels_dim=(width, height) if width is not None and height is not None else None,
        requested_chars_dim=(columns, rows) if columns is not None and rows is not None else None,
        title=title,
    )
