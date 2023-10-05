"""
Utilities for TCOD consoles.
"""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal # type: ignore
from tcod.console import Console

def get_console_order(console: Console) -> Literal['C', 'F']:
    # pylint: disable=protected-access
    return console._order
