# UI Debugger

`UIDebugger` is the visual inspector used by `UIManager`. It draws bounds, hover details, padding overlays, and a tree view over the active UI.

## Recommended Usage

Use the debugger through `UIManager` instead of wiring a second overlay manually.

```python
from arepy.engine.input import Key
from arepy_ui import UIConfig, UIManager

ui_manager = UIManager.from_engine(
    game,
    config=UIConfig(
        debug_enabled=False,
        debug_toggle_key=Key.F3,
        debug_bounds_key=Key.F4,
        debug_padding_key=Key.F5,
        debug_tree_key=Key.F6,
    ),
)

debugger = ui_manager.get_debugger()
ui_manager.enable_debug_overlay(True)
ui_manager.set_debug_hotkeys(toggle=Key.F2, bounds=Key.F3, padding=Key.F4, tree=Key.F5)
```

## Current Behavior

- Bounds are computed from the visual frame, so overlays follow `ScrollView` offsets correctly.
- Hover inspection uses the clipped visible area, which avoids selecting content outside the viewport.
- Toolbar labels reflect configured hotkeys instead of assuming fixed keys.
- The overlay text stays ASCII-safe.

## Reference

::: arepy_ui.debug.UIDebugger
