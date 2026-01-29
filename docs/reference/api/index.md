# API Reference

Core classes and functions for arepy-ui.

<div class="grid cards" markdown>

-   :material-cogs:{ .lg .middle } **UIManager**

    ---

    The main UI controller class.

    [:octicons-arrow-right-24: UIManager](uimanager.md)

-   :material-bug:{ .lg .middle } **UIDebugger**

    ---

    Visual debugging tools.

    [:octicons-arrow-right-24: Debugger](debugger.md)

-   :material-animation:{ .lg .middle } **Animations**

    ---

    Transitions and keyframe animations.

    [:octicons-arrow-right-24: Animations](animations.md)

</div>

## Quick Reference

### Main Classes

| Class | Description |
|-------|-------------|
| `UIManager` | Main UI controller |
| `Node` | Base container element |
| `Style` | Layout and appearance |
| `Color` | RGBA color |
| `Unit` | Size units (px, %) |
| `Spacing` | Padding/margin |

### Import Patterns

```python
# Core imports
from arepy_ui import (
    UIManager,
    Node,
    Style,
    Color,
    Unit,
)

# Components
from arepy_ui import (
    Text,
    Button,
    TextInput,
    Checkbox,
    Slider,
    Select,
    Image,
    Video,
    Canvas,
    ProgressBar,
    ScrollView,
    Tabs,
)

# Types
from arepy_ui.core.types import (
    FlexDirection,
    JustifyContent,
    AlignItems,
    AlignSelf,
    FlexWrap,
    Overflow,
)

# Styling
from arepy_ui.core.style import Spacing

# Markup
from arepy_ui.markup import (
    load_aui,
    load_acss,
    load_globals,
    set_theme,
    get_theme,
    register_component,
)

# Animations
from arepy_ui.core.animation import (
    Animation,
    Transition,
    Easing,
    Keyframe,
)

# Drag & Drop
from arepy_ui.components import (
    Draggable,
    DropZone,
)
```

### Lifecycle

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig

ui_manager: UIManager = None

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    ui_manager.set_root(create_ui())
    game.add_resource(ui_manager)

def update():
    ui_manager.update()

def draw():
    ui_manager.render()

game = ArepyEngine(title="My Game", width=800, height=600)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

### Error Handling

```python
from arepy_ui.markup import load_aui

try:
    root = load_aui("menu.aui")
except FileNotFoundError:
    print("AUI file not found")
except SyntaxError as e:
    print(f"AUI parse error: {e}")
```

## Type Enums

### FlexDirection

```python
FlexDirection.ROW           # Left to right
FlexDirection.COLUMN        # Top to bottom
FlexDirection.ROW_REVERSE   # Right to left
FlexDirection.COLUMN_REVERSE # Bottom to top
```

### JustifyContent

```python
JustifyContent.FLEX_START    # Start
JustifyContent.FLEX_END      # End
JustifyContent.CENTER        # Center
JustifyContent.SPACE_BETWEEN # Even, no edge gap
JustifyContent.SPACE_AROUND  # Even with edge gap
JustifyContent.SPACE_EVENLY  # Equal everywhere
```

### AlignItems

```python
AlignItems.FLEX_START  # Top/Left
AlignItems.FLEX_END    # Bottom/Right
AlignItems.CENTER      # Center
AlignItems.STRETCH     # Fill
```

### Overflow

```python
Overflow.VISIBLE  # Show overflow
Overflow.HIDDEN   # Clip overflow
Overflow.SCROLL   # Scrollable
```
