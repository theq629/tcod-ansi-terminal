Compatibility
=============

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
