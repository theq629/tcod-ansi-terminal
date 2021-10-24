"""
TCOD-compatible contexts that will write to a terminal.
"""

from typing import Optional
import sys
import os
from ._abstract_context import MinimalContext
from ._internal_context import TerminalContext, make_terminal_context
from ._presenters import Presenter, NaivePresenter, SparsePresenter

__all__ = (
    'MinimalContext',
    'TerminalContext',
    'new',
    'Presenter',
    'NaivePresenter',
    'SparsePresenter',
)

def new(
    *,
    columns: Optional[int] = None,
    rows: Optional[int] = None,
    title: Optional[str] = None
) -> TerminalContext:
    """
    Corresponds to `tcod.context.new()` but produces a terminal context.

    The dimension settings `columns` and `rows` are a request, which may or may not be granted; the
    caller should use the returned context's `recommended_console_size()` or `new_console()` to get
    the actual dimensions.

    This does not read `sys.argv` or take `argv` as input.
    """
    in_file = sys.stdin.buffer
    out_file = os.fdopen(sys.stdout.fileno(), 'wb', 1024)
    return make_terminal_context(in_file, out_file, columns, rows, title)
