# tcod-ansi-terminal

Minimal true colour ANSI terminal support for Python TCOD (`tcod`).

This doesn't try to support everything or be very compatible, just to cover
basic functionality on common terminals with true colour support. Note that
TCOD itself [may eventually get terminal
support](https://github.com/libtcod/libtcod/issues/78), so check it before
committing to using this.

This is currently all in Python code and may not be very performant.

There is an example included in [`example/`](example/). It also serves for
basic testing of features.

## Compatibility

Operating systems:
- Linux, MacOS X, probably other Unixes: somewhat tested, works
- Windows: totally untested, almost certainly doesn't work yet

Terminal emulators (without exploring their options much):
- xterm: working (all supported features)
- urxvt: mostly working (poor colour handling)
- gnome-terminal: working (doesn't honour pixel size or position requests;
  reserves some function keys)
- konsole: mostly working (may read initial size wrong if size was requested;
  doesn't honour any size or position requests; doesn't honour title; reserves
  some function keys)
- kitty: working (doesn't honour any size or position requests)
- alacritty: working (doesn't honour any size of position requests)
- MacOS X default terminal: not working (no true colour support; some other
  features don't work)
- iterm2: working (does not respect any position or size requests, insert key
  seemingly not supported; reserves some function keys)

Only uses true colour mode, and won't support consoles that don't handle it.

## Features

Supported TCOD features (at least for some terminals):
- Basic letter, digit, punctuation, and enter keys (anything received as an
  unescaped character; this set is safest for compatibility with untested
  terminals).
- Shift modifier for letter keys (but not digits etc.).
- Arrow, function, home, end, insert, delete, page up, page down keys.
- Keysyms for the above keys.
- Key down and key up events in immediate succession for the above keys, based
  on terminal input.
- Text input events for letter etc. keys.
- Terminal size checks for `recommended_console_size()` and `new_console()`.
- Window position, pixel size, and character size as requests. The choice to
  honour them or not is up to the terminal and/or window manager.
- Window resize events for terminal resizes.
- Mouse motion, button, and wheel events.
- Window focus gained and lost events.
- Window title.
- Quit event on hangup and other exit signals. If in a windowing system, this
  might get produced when the window is closed but isn't guaranteed.

Other features:
- The terminal will be reset cleanly on exit.
- The cursor position can be set.
- Cursor visibility can be set.

Unsupported TCOD features:
- Shift modifier for non-letter key.
- Modifiers other than shift.
- Key scancodes (are all `K_UNKNOWN`).
- Correct timing for key down/up events.
- `tcod.event.get()`.
- Basically any other input/output feature that isn't mentioned above,
  especially things in `tcod.context` and `tcod.event`.

Features that are not supported but could be later:
- Some support for other colour modes.
- Screenshots (with separate interface) to text files.

## Usage

Use `tcod_ansi_terminal.context.new()` to get a context object which manages an
ANSI terminal and can `present()` Python TCOD consoles to it. Use
`tcod_ansi_terminal.event.wait()` to get events.

### Targeting terminals

Not all features will be supported in all terminals, so if you want broad
compatibly you should not assume that any particular feature will be available.

The context will request the terminal size asked for (if any), but the calling
code must treat this as a request, and not assume that the request will be
honoured or that the size will remain the same during the run. Use the
context's `recommended_console_size()` to get the actual size, or
`new_console()` to get a correctly sized console, and use the `WindowResized`
event (or re-checking the size) to catch resizes.

The terminal context `tcod_ansi_terminal.context.TerminalContext` may support
operations that are not part of the regular TCOD interface, currently just
cursor controls.

### Targeting either terminals or regular tcod

If you want to support both regular TCOD and terminals in your program,
parameterize your core code using these interfaces:
- For rendering, the `tcod_ansi_terminal.context.TerminalCompatibleContext` protocol.
- For input, the `tcod_ansi_terminal.event.TerminalCompatibleEventWait` protocol.

The included example covers handling both a terminal or regular TCOD.

### Presenters

`tcod_ansi_terminal.context` provides two presenters which manage how a TCOD
console is written to a terminal on a context `present()` call.
`NaivePresenter` always writes the entire console. `SparsePresenter` writes only
the character cells which changed since the last `present()` call. If the
calling code tends to update only small parts of the console between frames,
`SparsePresenter` will likely be much faster.
