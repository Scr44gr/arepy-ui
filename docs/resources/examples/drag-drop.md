# Drag & Drop Example

Complete drag and drop implementation.

## Overview

This example shows how to build a complete drag and drop system.

## Run the Demo

```bash
uv run examples/demo_drag.py
```

## Source Code

```python
"""Drag and drop demo."""
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIConfig, UIManager, Node, Text, Style, Color, Unit
from arepy_ui.components import Draggable, DropZone
from arepy_ui.core.types import FlexDirection, JustifyContent, AlignItems
from arepy_ui.core.style import Spacing

ui_manager: UIManager = None

# Items in each column
left_items = ["🍎 Apple", "🍊 Orange", "🍋 Lemon"]
right_items = []

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    create_ui()
    game.add_resource(ui_manager)

def create_ui():
    ui_manager.set_root(
        Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                flex_direction=FlexDirection.COLUMN,
                padding=Spacing.all(20),
                gap=20,
                background_color=Color(25, 25, 35),
            ),
            children=[
                Text("Drag & Drop Demo", size=28, color=Color(255, 255, 255)),
                Text("Drag items between columns", size=14, color=Color(150, 150, 160)),
                
                # Two columns
                Node(
                    style=Style(
                        width=Unit.percent(100),
                        flex_direction=FlexDirection.ROW,
                        gap=40,
                    ),
                    children=[
                        Column("Left", left_items, "left"),
                        Column("Right", right_items, "right"),
                    ],
                ),
            ],
        )
    )

def Column(title: str, items: list, column_id: str) -> Node:
    return DropZone(
        on_drop=lambda data: on_drop(column_id, data),
        style=Style(
            width=Unit.px(200),
            min_height=Unit.px(300),
            background_color=Color(40, 40, 55),
            border_radius=12.0,
            padding=Spacing.all(16),
            flex_direction=FlexDirection.COLUMN,
            gap=12,
        ),
        children=[
            Text(title, size=18, color=Color(200, 200, 220)),
            *[DraggableItem(item, column_id) for item in items],
            # Empty placeholder if no items
            Text("Drop here", size=12, color=Color(100, 100, 120))
            if not items else None,
        ],
    )

def DraggableItem(text: str, source: str) -> Node:
    return Draggable(
        data={"text": text, "source": source},
        content=Node(
            style=Style(
                width=Unit.percent(100),
                padding=Spacing.symmetric(8, 12),
                background_color=Color(70, 70, 90),
                border_radius=6.0,
            ),
            children=[
                Text(text, size=14, color=Color(220, 220, 230)),
            ],
        ),
    )

def on_drop(target: str, data: dict):
    global left_items, right_items
    
    text = data["text"]
    source = data["source"]
    
    # Don't drop on same column
    if source == target:
        return
    
    # Move item
    if source == "left":
        left_items.remove(text)
        right_items.append(text)
    else:
        right_items.remove(text)
        left_items.append(text)
    
    # Rebuild UI
    create_ui()

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()

game = ArepyEngine(title="Drag & Drop", width=600, height=500)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

## Key Concepts

### Draggable

Wraps content to make it draggable:

```python
Draggable(
    data={"id": 1, "type": "item"},  # Passed to DropZone
    content=node,  # Single node to make draggable
)
```

### DropZone

Receives dropped items:

```python
DropZone(
    on_drop=lambda data: handle_drop(data),
    children=[...],
)
```

### Data Flow

1. User starts dragging a `Draggable`
2. User drops on a `DropZone`
3. `on_drop` is called with the `data` from `Draggable`
4. Handler updates state and rebuilds UI

## See Also

- [Draggable Reference](../../reference/components/draggable.md)
- [DropZone Reference](../../reference/components/dropzone.md)
- [Inventory Tutorial](../../learn/tutorials/inventory.md)
