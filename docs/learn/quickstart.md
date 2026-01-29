# Quick Start

This guide will help you create your first UI with arepy-ui.

## Basic Setup

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig, Node, Text, Button, Style, Color, Unit

ui_manager: UIManager = None

def create_ui() -> Node:
    """Create the UI tree."""
    return Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            background_color=Color(30, 30, 30),
        ),
        children=[
            Text("Hello, arepy-ui!", size=24, color=Color(255, 255, 255)),
            Button("Click me", on_click=lambda: print("Clicked!")),
        ],
    )

def setup(game: ArepyEngine):
    """Initialize the UI manager."""
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    ui_manager.set_root(create_ui())
    game.add_resource(ui_manager)

def update(dt: float):
    """Update UI state."""
    ui_manager.update(dt)

def render():
    """Render the UI."""
    ui_manager.render()

if __name__ == "__main__":
    game = ArepyEngine(title="UI Example", width=800, height=600)
    world = game.create_world("main")
    world.add_startup_system(setup)
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER, render)
    game.set_current_world("main")
    game.run()
```

## Understanding the Code

### 1. UIManager

The `UIManager` is the central controller for your UI. Use `from_engine()` to create it:

```python
ui_manager = UIManager.from_engine(game, config=UIConfig())
```

This automatically configures the runtime with the engine's renderer, input, and display.

### 2. Nodes

Everything in arepy-ui is a `Node`. Nodes form a tree structure:

```python
root = Node(
    style=Style(...),
    children=[
        child1,
        child2,
    ],
)
```

### 3. Styles

Styles define how nodes look and are laid out:

```python
Style(
    width=Unit.px(200),
    height=Unit.px(100),
    background_color=Color(255, 0, 0),
    padding=Spacing.all(10),
)
```

### 4. Game Loop

The UI needs to be updated and rendered each frame:

```python
def update(dt: float):
    ui_manager.update(dt)

def render():
    ui_manager.render()
```

## Next Steps

- Learn about [Layout](../layout/flexbox.md)
- Explore [Components](../components/index.md)
- Check out the [Examples](../examples.md)
