# UIManager API

The main class for managing UI state and rendering.

## Overview

`UIManager` is the central controller for arepy-ui. It handles the UI tree, rendering, input events, and updates.

## Import

```python
from arepy_ui import UIManager, UIConfig
```

## Creating UIManager

```python
from arepy import ArepyEngine
from arepy_ui import UIManager, UIConfig

def setup(game: ArepyEngine):
    # Create from engine (recommended)
    ui_manager = UIManager.from_engine(game, config=UIConfig())
```

## Methods

### set_root

Set the root node of the UI tree.

```python
ui_manager.set_root(root_node)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `root` | `Node` | The root node of the UI tree |

### update

Process input and update UI state. Call once per frame.

```python
def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())
```

### render

Render the UI tree. Call in your draw function.

```python
def draw():
    ui_manager.render()
```

### root

Access the root node of the UI tree.

```python
# Get the root node
root = ui_manager.root

# Set a new root
ui_manager.set_root(new_root)
```

**Type:** `Optional[Node]`

### find_by_id

Find a node by its ID (must be called on the root node).

```python
if ui_manager.root:
    node = ui_manager.root.find_by_id("my-node-id")
    if node:
        print(f"Found: {node}")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Node identifier |

**Returns:** `Optional[Node]`

### Modals

Show and manage modal dialogs:

```python
# Show a modal
modal = Node(style=Style(width=Unit.px(300), height=Unit.px(200)))
ui_manager.show_modal(modal, backdrop=True, close_on_backdrop=True)

# Close the topmost modal
ui_manager.close_modal()

# Close all modals
ui_manager.close_all_modals()

# Check if a modal is open
if ui_manager.has_modal:
    print("Modal is open")
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `root` | `Optional[Node]` | Root node of the UI tree |
| `screen_width` | `int` | Current screen width |
| `screen_height` | `int` | Current screen height |
| `is_dirty` | `bool` | Whether layout needs recalculation |
| `is_input_captured` | `bool` | Whether UI has captured input |
| `has_modal` | `bool` | Whether any modal is currently open |
| `config` | `UIConfig` | UI configuration settings |
| `animator` | `Animator` | Animation controller |

## Complete Example

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig, Node, Text, Button, Style, Color, Unit

ui_manager: UIManager = None

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    create_menu()
    game.add_resource(ui_manager)

def create_menu():
    root = Node(
        id="root",
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            background_color=Color(30, 30, 40),
        ),
        children=[
            Text("Hello!", size=32, color=Color(255, 255, 255)),
            Button("Click me", on_click=on_click),
        ],
    )
    ui_manager.set_root(root)

def on_click():
    # Find and update a node
    if ui_manager.root:
        root = ui_manager.root.find_by_id("root")
        print("Button clicked!")

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()

# Run
game = ArepyEngine(title="Demo", width=800, height=600)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

## Hot Reload Pattern

Rebuild UI when needed:

```python
def refresh_ui():
    """Rebuild the UI from current state."""
    ui_manager.set_root(create_ui_from_state())

def on_setting_change(value):
    settings.volume = value
    refresh_ui()  # Rebuild with new state
```

## With Markup

```python
from arepy_ui.markup import load_aui, load_globals
from arepy_ui import UIManager, UIConfig

def setup(game: ArepyEngine):
    global ui_manager
    
    # Load global styles
    load_globals("assets/ui/globals.acss")
    
    # Create manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    # Load from markup
    result = load_aui("menu.aui", handlers={
        "start_game": start_game,
        "open_settings": open_settings,
    })
    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
    game.add_resource(ui_manager)
```

!!! note "ParseResult"
    `load_aui()` returns a `ParseResult`, not a raw `Node`. Check `result.success`, inspect `result.errors`, and use `result.root` when parsing succeeds.

## Tips

!!! tip "Global Instance"
    Keep UIManager as a global or class variable for easy access.

!!! tip "Single Root"
    Call `set_root()` with your complete UI tree. Don't add nodes individually.

!!! tip "State Management"
    Rebuild the UI when state changes rather than mutating nodes directly.

## See Also

- [Getting Started](../../learn/getting-started.md) - Setup guide
- [UIDebugger](debugger.md) - Debug tools
- [Nodes](../components/node.md) - Building UI trees
