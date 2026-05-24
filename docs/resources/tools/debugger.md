# UI Debugger

The debugger is built into `UIManager` and is intended for development-time inspection of layout, hover state, padding, and tree structure.

## Recommended Setup

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

ui_manager.enable_debug_overlay(True)
debugger = ui_manager.get_debugger()
debugger.show_info = True


## Current Behavior

- `F3` toggles the overlay by default.
- Bounds follow visual scroll offsets correctly.
- Hover inspection uses the clipped visible area.
- Toolbar labels reflect configured hotkeys.
- Overlay text is ASCII-safe.

## Reference

For the runtime API, see [reference/api/debugger.md](../../reference/api/debugger.md).
    # Register as a game resource so systems can receive it via DI
    game.add_resource(ui_manager)


def update(ui_manager: UIManager, renderer: Renderer2D):
    ui_manager.update(renderer.get_delta_time())


def render(ui_manager: UIManager):
    ui_manager.render()


if __name__ == "__main__":
    game = ArepyEngine(title="Debugger Demo", width=800, height=600)
    setup(game)

    world = game.create_world("main")
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER_UI, render)
    game.set_current_world("main")
    game.run()
```

```

```

```

## API Reference

### UIDebugger

| Method | Description |
|--------|-------------|
| `toggle()` | Toggle the entire debugger on/off |
| `toggle_bounds()` | Toggle bounds visualization |
| `toggle_padding()` | Toggle padding visualization |
| `toggle_tree()` | Toggle component tree panel |
| `render(root)` | Render debug overlay for the UI tree |

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Whether debugger is active |
| `show_bounds` | `bool` | `True` | Show component boundaries |
| `show_padding` | `bool` | `False` | Show padding areas |
| `show_info` | `bool` | `True` | Show hover info panel |
| `show_tree` | `bool` | `False` | Show component tree |
| `hovered_node` | `Node` | `None` | Currently hovered component |

## Tips

!!! tip "Development Only"
    Remove or disable the debugger in production builds for better performance.

!!! tip "Use Component IDs"
    Give your components meaningful IDs to make them easier to identify in the debugger:
    ```python
    Button("Submit", id="submit-btn")
    ```

!!! tip "Inspect Layout Issues"
    Use the debugger to understand why layouts aren't working as expected. The hover panel shows computed vs. styled values.
