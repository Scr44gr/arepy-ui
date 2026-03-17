# Inventory System Example

Complete grid-based inventory with drag and drop.

<!-- TODO: Add inventory GIF -->
![Inventory Demo](../../assets/examples/inventory-demo.gif)

## Overview

A full inventory system with:

- Grid-based slots
- Drag and drop items
- Item stacking
- Visual feedback

## Run the Demo

```bash
uv run examples/demo_inventory.py
```

## Source Code

See the [Inventory Tutorial](../../learn/tutorials/inventory.md) for a step-by-step guide to building this.

## Quick Implementation

```python
"""Inventory system demo."""
from dataclasses import dataclass
from typing import Optional
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, Node, Text, Style, Color, Unit
from arepy_ui.components import Draggable, DropZone
from arepy_ui.core.types import FlexDirection, JustifyContent, AlignItems
from arepy_ui.core.style import Spacing

ui_manager: UIManager = None

@dataclass
class Item:
    id: str
    name: str
    icon: str
    stack: int = 1

# 24-slot inventory
inventory: list[Optional[Item]] = [None] * 24

# Add some items
inventory[0] = Item("sword", "Sword", "🗡️")
inventory[1] = Item("shield", "Shield", "🛡️")
inventory[2] = Item("potion", "Potion", "🧪", stack=5)
inventory[5] = Item("gold", "Gold", "💰", stack=42)

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    create_inventory()
    game.add_resource(ui_manager)

def create_inventory():
    rows = []
    for row_start in range(0, 24, 8):
        row_items = inventory[row_start:row_start + 8]
        row = Node(
            style=Style(flex_direction=FlexDirection.ROW, gap=4),
            children=[
                Slot(row_start + i, item) 
                for i, item in enumerate(row_items)
            ],
        )
        rows.append(row)
    
    ui_manager.set_root(
        Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                justify_content=JustifyContent.CENTER,
                align_items=AlignItems.CENTER,
                background_color=Color(20, 20, 30),
            ),
            children=[
                Node(
                    style=Style(
                        background_color=Color(35, 35, 50),
                        padding=Spacing.all(16),
                        border_radius=12.0,
                        flex_direction=FlexDirection.COLUMN,
                        gap=4,
                    ),
                    children=[
                        Text("Inventory", size=18, color=Color(200, 200, 220)),
                        *rows,
                    ],
                ),
            ],
        )
    )

def Slot(index: int, item: Optional[Item]) -> Node:
    slot_style = Style(
        width=Unit.px(48),
        height=Unit.px(48),
        background_color=Color(50, 50, 65),
        border_radius=4.0,
        justify_content=JustifyContent.CENTER,
        align_items=AlignItems.CENTER,
    )
    
    def on_drop(data):
        source = data["slot"]
        if source != index:
            # Swap items
            inventory[index], inventory[source] = inventory[source], inventory[index]
            create_inventory()
    
    if item is None:
        return DropZone(on_drop=on_drop, style=slot_style)
    
    return DropZone(
        on_drop=on_drop,
        style=slot_style,
        children=[
            Draggable(
                data={"slot": index, "item": item},
                children=[
                    Node(
                        style=Style(
                            width=Unit.px(40),
                            height=Unit.px(40),
                            justify_content=JustifyContent.CENTER,
                            align_items=AlignItems.CENTER,
                        ),
                        children=[
                            Text(item.icon, size=24),
                            Text(str(item.stack), size=10, 
                                 color=Color(255, 255, 255),
                                 style=Style(
                                     position="absolute",
                                     right=Unit.px(2),
                                     bottom=Unit.px(2),
                                 )
                            ) if item.stack > 1 else None,
                        ],
                    ),
                ],
            ),
        ],
    )

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()

game = ArepyEngine(title="Inventory", width=600, height=400)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

## Features

### Item Swapping

Items can be swapped between slots:

```python
def on_drop(data):
    source = data["slot"]
    inventory[index], inventory[source] = inventory[source], inventory[index]
```

### Stack Display

Shows stack count for stackable items:

```python
Text(str(item.stack), size=10) if item.stack > 1 else None
```

### Visual Slots

Empty slots act as drop targets too.

## See Also

- [Inventory Tutorial](../../learn/tutorials/inventory.md) - Full walkthrough
- [Drag & Drop Reference](../../reference/components/draggable.md)
