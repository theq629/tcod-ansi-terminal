tcod-ansi-terminal
==================

Minimal true colour ANSI terminal support for Python TCOD.

This doesn't try to support everything or be very compatible, just to cover basic functionality on
common terminals with true colour support.

Slightly tested on Linux and OSX, totally untested and would need more work on Windows.

Basics
------

Use `tcod_ansi_terminal.context.new()` to get a context object which manages an ANSI terminal and
can `present()` Python TCOD consoles to it. Use `tcod_ansi_terminal.event.wait()` to get events.
