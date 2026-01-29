# UI Debugger

The UIDebugger is a visual debugging tool that helps you inspect and understand your UI layout in real-time.

<!-- TODO: Add screenshot of debugger in action -->
![UIDebugger Overview](../assets/debugger-overview.png)
*The UIDebugger showing component bounds and hover information*

## Overview

The debugger provides:

- **Component bounds** - Visual borders around each component
- **Hover inspection** - Detailed info panel when hovering over components
- **Component tree** - Hierarchical view of your UI structure
- **Padding visualization** - See padding areas highlighted
- **Keyboard shortcuts** - Quick toggles for different views

## Quick Start

```python
from arepy_ui.debug import UIDebugger

# Create debugger instance
ui_debugger = UIDebugger()

def update(dt: float):
    ui_manager.update(dt)
    
    # Toggle debugger with F3
    if input.is_key_pressed(Key.F3):
        ui_debugger.toggle()

def render():
    ui_manager.render()
    
    # Render debug overlay on top
    ui_debugger.render(ui_manager.root)
```

## Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `F3` | Toggle Debug | Enable/disable the entire debugger |
| `F4` | Toggle Bounds | Show/hide component boundary boxes |
| `F5` | Toggle Padding | Show/hide padding visualization |
| `F6` | Toggle Tree | Show/hide component tree panel |

<!-- TODO: Add GIF showing keyboard shortcuts in action -->
![Debugger Shortcuts](../assets/debugger-shortcuts.gif)
*Using keyboard shortcuts to toggle debugger features*

## Toolbar

When enabled, the debugger displays a toolbar at the top of the screen:

```
[F3] Debug  [F4] Bounds  [F5] Padding  [F6] Tree     Hovering: Button #submit
```

- Active features are highlighted in color
- Inactive features are dimmed
- Current hovered component is shown on the right

<!-- TODO: Add screenshot of toolbar -->
![Debugger Toolbar](../assets/debugger-toolbar.png)
*The debugger toolbar showing active features*

## Component Bounds

When **Bounds** is enabled (F4), each component gets a colored border:

- Different component types have different colors
- Hovered components are highlighted with a yellow glow
- Nested components show their hierarchy visually

<!-- TODO: Add screenshot of bounds visualization -->
![Bounds Visualization](../assets/debugger-bounds.png)
*Component bounds with different colors per type*

### Component Colors

| Component | Color |
|-----------|-------|
| Node | Gray |
| Text | Blue |
| Button | Green |
| TextInput | Cyan |
| Slider | Orange |
| Checkbox | Purple |
| Image | Pink |
| ScrollView | Teal |
| ColorPicker | Gold |

## Hover Info Panel

When you hover over a component, a detailed info panel appears showing:

<!-- TODO: Add screenshot of info panel -->
![Info Panel](../assets/debugger-info-panel.png)
*Detailed component information on hover*

### Layout Section

```
Position: (100, 200)
Size: 250 × 45
```

Shows the computed position and dimensions in pixels.

### Style Section

```
width: 100%
height: 45px
flex: row
gap: 10
padding: 8 16
```

Shows the applied style properties.

### Props Section

Component-specific properties:

| Component | Properties Shown |
|-----------|-----------------|
| `Text` | text content, size |
| `Button` | label |
| `TextInput` | value, placeholder |
| `Slider` | value, range |
| `Checkbox` | checked state |
| `Image` | source path |
| `Video` | state, duration |
| `ColorPicker` | current color (RGBA) |
| `Select` | options count, selected index |

### Tree Section

```
Parent: Node
Children: 3
```

Shows the component's position in the hierarchy.

## Component Tree

When **Tree** is enabled (F6), a panel appears on the right showing the full component hierarchy:

<!-- TODO: Add screenshot of tree view -->
![Component Tree](../assets/debugger-tree.png)
*The component tree panel*

- Components are indented by depth
- Each component shows its type and ID
- Colored markers indicate component type
- Hovered component is highlighted in yellow

```
◆ Node #root
  ├── Text #title
  ├── Node #content
  │   ├── Button #submit
  │   └── Button #cancel
  └── Text #footer
```

## Padding Visualization

When **Padding** is enabled (F5), padding areas are highlighted in green:

<!-- TODO: Add screenshot of padding visualization -->
![Padding Visualization](../assets/debugger-padding.png)
*Padding areas shown in green overlay*

This helps you understand:
- Where padding is applied
- The actual size of padding on each side
- How padding affects layout

## Complete Example

```python
from arepy import ArepyEngine, Input, Key, SystemPipeline
from arepy_ui import UIManager, UIConfig, Node, Button, Text, Style
from arepy_ui.debug import UIDebugger

ui_manager: UIManager = None
ui_debugger: UIDebugger = None

def setup(game: ArepyEngine):
    global ui_manager, ui_debugger
    
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    ui_debugger = UIDebugger()
    
    ui_manager.set_root(
        Node(
            id="root",
            style=Style(padding=Spacing.all(20), gap=10),
            children=[
                Text("Debug Demo", id="title", size=24),
                Button("Click me", id="btn"),
            ],
        )
    )
    game.add_resource(ui_manager)
    game.add_resource(ui_debugger)

def update(dt: float, input: Input):
    ui_manager.update(dt)
    
    # Debugger keyboard shortcuts
    if input.is_key_pressed(Key.F3):
        ui_debugger.toggle()
    if input.is_key_pressed(Key.F4):
        ui_debugger.toggle_bounds()
    if input.is_key_pressed(Key.F5):
        ui_debugger.toggle_padding()
    if input.is_key_pressed(Key.F6):
        ui_debugger.toggle_tree()

def render():
    ui_manager.render()
    ui_debugger.render(ui_manager.root)

if __name__ == "__main__":
    game = ArepyEngine(title="Debugger Demo", width=800, height=600)
    world = game.create_world("main")
    world.add_startup_system(setup)
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER, render)
    game.set_current_world("main")
    game.run()
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
