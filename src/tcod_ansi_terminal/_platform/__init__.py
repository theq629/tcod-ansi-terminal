"""
Platform-specific functionality.
"""

from typing import BinaryIO
import sys
from ._abstract_platform import Platform

__all__ = (
    'Platform',
    'make_platform',
)

try:
    from ._windows import WindowsPlatform

    def make_platform(in_file: BinaryIO) -> Platform:
        return WindowsPlatform(in_file)

except ImportError:
    from ._unix import UnixPlatform

    def make_platform(in_file: BinaryIO) -> Platform:
        return UnixPlatform(in_file)
