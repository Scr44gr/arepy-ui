# API Reference

This section is the source-aligned reference for the API pages currently maintained in the docs.

## API Documents

- [docs/reference/api/index.md](index.md) - entry point and navigation notes for the API reference.
- [docs/reference/api/uimanager.md](uimanager.md) - `UIManager`, `UIConfig`, and overlay helpers.
- [docs/reference/api/debugger.md](debugger.md) - `UIDebugger` and debug-overlay behavior.
- [docs/reference/api/animations.md](animations.md) - animation, timers, timeline, and transition primitives.

## Source of Truth

These pages are backed by the library source through `mkdocstrings`, so signatures and docstrings come from the code instead of hand-maintained tables.

## Common Imports

```python
from arepy_ui import (
    AlignItems,
    Animation,
    Animator,
    Button,
    Color,
    Easing,
    FadeTransition,
    FlexDirection,
    JustifyContent,
    KeyFrame,
    Node,
    ScrollView,
    Spacing,
    Style,
    Timer,
    Timers,
    Text,
    Timeline,
    UIConfig,
    UIManager,
    Unit,
)

from arepy_ui.markup import load_aui, load_aui_string, load_globals, get_theme, set_theme
```

## Minimal Lifecycle

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

game = ArepyEngine(title="My UI", width=1280, height=720)
game.on_startup = lambda: setup(game)
world = game.create_world("main")
world.add_system(SystemPipeline.UPDATE, ui_update_system)
world.add_system(SystemPipeline.RENDER_UI, ui_render_system)
game.set_current_world("main")
game.run()
```

## Related Sections

- [reference/components/index.md](../components/index.md)
- [reference/styling/index.md](../styling/index.md)
- [reference/markup/index.md](../markup/index.md)
