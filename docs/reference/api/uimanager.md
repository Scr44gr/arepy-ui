# UIManager API

`UIManager` is the runtime entry point for layout, input, rendering, overlays, modals, tooltips, font scaling, and the integrated debugger.

## Typical Usage

```python
from arepy import ArepyEngine
from arepy_ui import UIConfig, UIManager

game = ArepyEngine(title="UI Demo", width=1280, height=720)
world = game.create_world("main")

ui_manager = UIManager.install(
    world,
    config=UIConfig(),
    root=create_ui(),
)
```

## Notes

- `install()` is the recommended entry point when your UI lives inside an arepy `World`.
- `from_world()` configures runtime services from the world's shared resources when you want manual control.
- `from_engine()` remains available for non-world or legacy setup paths.
- `find_by_id()` belongs to `Node`, so use `ui_manager.root.find_by_id(...)` when the root exists.
- Debug overlay management is built in through `get_debugger()`, `enable_debug_overlay()`, `toggle_debug_overlay()`, and the `UIConfig` debug keys.

## Reference

::: arepy_ui.manager.UIManager

## Related Types

::: arepy_ui.config.UIConfig

::: arepy_ui.manager.register_overlay

::: arepy_ui.manager.clear_overlays
