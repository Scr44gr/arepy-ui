# Creating an Inventory System

Build a complete inventory system with drag and drop!

<!-- TODO: Add inventory screenshot -->
![Inventory System](../../assets/examples/inventory-demo.gif)

## What We'll Build

- A grid-based inventory
- Draggable items
- Drop zones (slots)
- Item stacking

## Step 1: Item Data

First, define what an item looks like:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Item:
    id: str
    name: str
    icon: str  # Path to icon image
    stackable: bool = False
    stack_size: int = 1
    max_stack: int = 64

# Example items
ITEMS = {
    "sword": Item("sword", "Iron Sword", "icons/sword.png"),
    "potion": Item("potion", "Health Potion", "icons/potion.png", stackable=True, max_stack=10),
    "gold": Item("gold", "Gold Coin", "icons/gold.png", stackable=True, max_stack=99),
}
```

## Step 2: Inventory Slot Component

Create a reusable slot:

```python
from arepy_ui import Node, Text, Image, Style, Color, Unit, FlexDirection, JustifyContent, AlignItems
from arepy_ui.components import DropZone, Draggable

SLOT_SIZE = 64

def InventorySlot(
    slot_index: int,
    item: Optional[Item] = None,
    on_drop = None,
) -> Node:
    """A single inventory slot."""
    
    slot_style = Style(
        width=Unit.px(SLOT_SIZE),
        height=Unit.px(SLOT_SIZE),
        background_color=Color(40, 40, 50),
        border_radius=4.0,
        border_width=2.0,
        border_color=Color(60, 60, 70),
        justify_content=JustifyContent.CENTER,
        align_items=AlignItems.CENTER,
    )
    
    def handle_drop(data):
        if on_drop:
            on_drop(slot_index, data)
    
    # Empty slot
    if item is None:
        return DropZone(
            on_drop=handle_drop,
            style=slot_style,
        )
    
    # Slot with item
    return DropZone(
        on_drop=handle_drop,
        style=slot_style,
        children=[
            Draggable(
                data={"slot": slot_index, "item": item},
                content=Node(
                    style=Style(
                        width=Unit.px(SLOT_SIZE - 8),
                        height=Unit.px(SLOT_SIZE - 8),
                    ),
                    children=[
                        Image(source=item.icon, style=Style(
                            width=Unit.percent(100),
                            height=Unit.percent(100),
                        )),
                        # Stack count
                        Text(
                            str(item.stack_size) if item.stackable else "",
                            size=10,
                            color=Color(255, 255, 255),
                            style=Style(
                                position="absolute",
                                right=Unit.px(2),
                                bottom=Unit.px(2),
                            ),
                        ) if item.stackable and item.stack_size > 1 else None,
                    ],
                ),
            ),
        ],
    )
```

## Step 3: Inventory Grid

```python
def InventoryGrid(
    slots: list,  # List of Optional[Item]
    columns: int = 8,
    on_drop = None,
) -> Node:
    """A grid of inventory slots."""
    
    rows = []
    for row_start in range(0, len(slots), columns):
        row_slots = slots[row_start:row_start + columns]
        row = Node(
            style=Style(
                flex_direction=FlexDirection.ROW,
                gap=4,
            ),
            children=[
                InventorySlot(row_start + i, item, on_drop)
                for i, item in enumerate(row_slots)
            ],
        )
        rows.append(row)
    
    return Node(
        style=Style(
            background_color=Color(30, 30, 40),
            padding=Spacing.all(12),
            border_radius=8.0,
            flex_direction=FlexDirection.COLUMN,
            gap=4,
        ),
        children=[
            Text("Inventory", size=16, color=Color(200, 200, 200)),
            *rows,
        ],
    )
```

## Step 4: Inventory Logic

```python
class Inventory:
    def __init__(self, size: int = 24):
        self.slots: list[Optional[Item]] = [None] * size
    
    def add_item(self, item: Item) -> bool:
        """Add item to first available slot."""
        # Try to stack first
        if item.stackable:
            for i, slot in enumerate(self.slots):
                if slot and slot.id == item.id and slot.stack_size < slot.max_stack:
                    slot.stack_size += item.stack_size
                    return True
        
        # Find empty slot
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item
                return True
        
        return False  # Inventory full
    
    def move_item(self, from_slot: int, to_slot: int):
        """Move item between slots."""
        from_item = self.slots[from_slot]
        to_item = self.slots[to_slot]
        
        # Swap
        self.slots[to_slot] = from_item
        self.slots[from_slot] = to_item
    
    def remove_item(self, slot: int) -> Optional[Item]:
        """Remove and return item from slot."""
        item = self.slots[slot]
        self.slots[slot] = None
        return item
```

## Step 5: Put It Together

```python
inventory = Inventory(24)

# Add some test items
inventory.add_item(Item("sword", "Iron Sword", "icons/sword.png"))
inventory.add_item(Item("potion", "Health Potion", "icons/potion.png", True, 5, 10))

def on_item_drop(target_slot: int, data: dict):
    source_slot = data["slot"]
    inventory.move_item(source_slot, target_slot)
    refresh_ui()

def refresh_ui():
    ui_manager.set_root(create_inventory_ui())

def create_inventory_ui() -> Node:
    return Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            background_color=Color(20, 20, 30),
        ),
        children=[
            InventoryGrid(inventory.slots, columns=8, on_drop=on_item_drop),
        ],
    )
```

## Tips

!!! tip "Visual Feedback"
    Highlight slots when dragging over them using the DropZone's hover state.

!!! tip "Item Tooltips"
    Show item details on hover using a positioned Text node.

!!! tip "Animations"
    Add subtle animations when items are picked up and dropped.

## Next Steps

- [Theme Switching](theming.md) - Add visual themes
- [Drag & Drop Reference](../../reference/components/draggable.md) - Full API docs
