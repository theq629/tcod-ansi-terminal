# tcod-ansi-terminal

[![test](https://github.com/theq629/tcod-ansi-terminal/actions/workflows/test.yml/badge.svg)](https://github.com/theq629/tcod-ansi-terminal/actions/workflows/test.yml)
[![docs](https://readthedocs.org/projects/tcod-ansi-terminal/badge/?version=latest&style=flat)](https://tcod-ansi-terminal.readthedocs.io/en/latest/)
[![pypi](https://badge.fury.io/py/tcod-ansi-terminal.svg)](https://badge.fury.io/py/tcod-ansi-terminal)

Minimal true colour ANSI terminal support for Python TCOD (`tcod`).

Works on UNIXish systems, and in theory could work on Windows but that's mostly
unimplemented.

This doesn't try to support everything or be very compatible, just to cover
basic functionality on common terminals with true colour support. Note that
TCOD itself [may eventually get terminal
support](https://github.com/libtcod/libtcod/issues/78), so check it before
committing to using this. This is currently all in Python code and may not be
very performant.
