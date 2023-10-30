Usage
=====

Use :py:meth:`tcod_ansi_terminal.context.new()` to get a context object which
manages an ANSI terminal and can :py:meth:`present()
<tcod_ansi_terminal.context.TerminalContext.present>` Python TCOD consoles to
it. Use :py:meth:`tcod_ansi_terminal.event.wait()` to get events.

Targeting terminals
-------------------

Not all features will be supported in all terminals, so if you want broad
compatibly you should not assume that any particular feature will be available.

The context will request the terminal size asked for (if any), but the calling
code must treat this as a request, and not assume that the request will be
honoured or that the size will remain the same during the run. Use the
context's
:py:meth:`~tcod_ansi_terminal.context.TerminalCompatibleContext.recommended_console_size()`
to get the actual size, or
:py:meth:`~tcod_ansi_terminal.context.TerminalCompatibleContext.new_console()`
to get a correctly sized console, and use the ``WindowResized`` event (or
re-checking the size) to catch resizes.

The terminal context :py:class:`~tcod_ansi_terminal.context.TerminalContext` may
support operations that are not part of the regular TCOD interface, currently
just cursor controls.

Targeting either terminals or regular tcod
------------------------------------------

If you want to support both regular TCOD and terminals in your program,
parameterize your core code using these interfaces:

- For rendering, the
  :py:class:`tcod_ansi_terminal.context.TerminalCompatibleContext` protocol.
- For input, the
  :py:class:`tcod_ansi_terminal.event.TerminalCompatibleEventWait` protocol.

The included example covers handling both a terminal or regular TCOD.

Presenters
----------

:py:mod:`tcod_ansi_terminal.context` provides two presenters which manage how a
TCOD console is written to a terminal on a context
:py:meth:`~tcod_ansi_terminal.context.TerminalCompatibleContext.present()`
call.  :py:clasS:`~tcod_ansi_terminal.context.NaivePresenter` always writes the
entire console. :py:class:`~tcod_ansi_terminal.context.SparsePresenter` writes
only the character cells which changed since the last
:py:meth:`~tcod_ansi_terminal.context.TerminalCompatibleContext.present()`
call.  If the calling code tends to update only small parts of the console
between frames, :py:class:`~tcod_ansi_terminal.context.SparsePresenter` will
likely be much faster.
