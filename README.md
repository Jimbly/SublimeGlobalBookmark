Jimbly's Global Bookmark
========================

Global bookmark plugin for Sublime Text 2/3

Features:
* Navigate between bookmarks in multiple files
* Save bookmarks between sessions

Default Keybinds (from Visual Studio):
* Ctrl+K, Ctrl+K: toggle ("global_bookmark_toggle")
* Ctrl+K, Ctrl+N: next ("global_bookmark_next")
* Ctrl+K, Ctrl+L: clear all ("global_bookmark_clear")

To replace Sublime's default bookmark keys, if you're used to those, place this in your keybinds file:
```
  { "keys": ["f2"], "command": "global_bookmark_next" },
  { "keys": ["ctrl+f2"], "command": "global_bookmark_toggle" },
  { "keys": ["ctrl+shift+f2"], "command": "global_bookmark_clear" },
```
