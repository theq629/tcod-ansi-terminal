"""
ANSI terminal support for Python TCOD.
"""

import sys
import os
import atexit
from typing import *
import tcod
from . import _platform
from . import event
from . import context

__all__ = (
    'event',
    'context',
)
