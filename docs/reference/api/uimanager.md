# UIManager API

`UIManager` is the runtime entry point for layout, input, rendering, overlays, modals, tooltips, font scaling, and the integrated debugger.

## Typical Usage

```python
from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline
from arepy_ui import UIConfig, UIManager

ui_manager: UIManager | None = None

def setup(game: ArepyEngine) -> None:
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    ui_manager.set_root(create_ui())

def ui_update_system(renderer: Renderer2D, input: Input, display: Display) -> None:
    assert ui_manager is not None
    ui_manager.update(renderer.get_delta_time())

def ui_render_system(renderer: Renderer2D) -> None:
    assert ui_manager is not None
    ui_manager.render()
```

## Notes

- `from_engine()` is the recommended constructor because it configures renderer, input, display, asset store, and audio device.
- `find_by_id()` belongs to `Node`, so use `ui_manager.root.find_by_id(...)` when the root exists.
- Debug overlay management is built in through `get_debugger()`, `enable_debug_overlay()`, `toggle_debug_overlay()`, and the `UIConfig` debug keys.

## Reference

::: arepy_ui.manager.UIManager

## Related Types

::: arepy_ui.config.UIConfig

::: arepy_ui.manager.register_overlay

::: arepy_ui.manager.clear_overlays
