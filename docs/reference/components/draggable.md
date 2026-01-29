# Draggable

Make elements draggable for drag & drop interactions.

## Overview

The `Draggable` component wraps content and makes it draggable. Works with `DropZone` to create drag & drop systems.

## Import

```python
from arepy_ui.components import Draggable
```

## Basic Usage

```python
from arepy_ui.components import Draggable
from arepy_ui import Node, Text, Style

draggable_item = Draggable(
    data={"id": "item_1", "name": "Sword"},
    children=[
        Node(
            style=Style(
                width=Unit.px(64),
                height=Unit.px(64),
                background_color=Color(80, 80, 100),
            ),
            children=[Text("🗡️")],
        ),
    ],
)
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `dict` | `{}` | Data passed to DropZone on drop |
| `children` | `list[Node]` | `[]` | Content to make draggable |
| `style` | `Style` | `None` | Container style |
| `disabled` | `bool` | `False` | Disable dragging |
| `on_drag_start` | `Callable` | `None` | Called when drag starts |
| `on_drag_end` | `Callable` | `None` | Called when drag ends |

## With DropZone

```python
from arepy_ui.components import Draggable, DropZone

# Draggable item
item = Draggable(
    data={"slot": 0, "item": "sword"},
    children=[ItemIcon("sword")],
)

# Drop target
slot = DropZone(
    on_drop=lambda data: print(f"Dropped: {data}"),
    style=Style(
        width=Unit.px(64),
        height=Unit.px(64),
        background_color=Color(40, 40, 50),
    ),
)
```

## Drag Events

```python
def on_start():
    print("Started dragging!")

def on_end():
    print("Stopped dragging!")

draggable = Draggable(
    data={"id": 1},
    on_drag_start=on_start,
    on_drag_end=on_end,
    children=[...],
)
```

## Styling While Dragging

The dragged element follows the cursor. Apply styles for visual feedback:

```python
# Visual clone appears while dragging
draggable = Draggable(
    data=item_data,
    children=[
        Node(
            style=Style(
                width=Unit.px(64),
                height=Unit.px(64),
                background_color=Color(100, 100, 120),
                border_radius=8.0,
                opacity=0.8,  # Semi-transparent while dragging
            ),
            children=[...],
        ),
    ],
)
```

## Complete Example

```python
# Inventory slot with draggable item
def InventorySlot(slot_index: int, item: Optional[Item]) -> Node:
    def handle_drop(data):
        source = data["slot"]
        inventory.move_item(source, slot_index)
    
    slot_style = Style(
        width=Unit.px(64),
        height=Unit.px(64),
        background_color=Color(40, 40, 50),
        border_radius=4.0,
    )
    
    if item is None:
        return DropZone(on_drop=handle_drop, style=slot_style)
    
    return DropZone(
        on_drop=handle_drop,
        style=slot_style,
        children=[
            Draggable(
                data={"slot": slot_index, "item": item},
                children=[ItemIcon(item.icon)],
            ),
        ],
    )
```

## AUI Markup

```html
<draggable data-id="item1" data-type="weapon">
    <node class="item-icon">⚔️</node>
</draggable>
```

## Tips

!!! tip "Pass Sufficient Data"
    Include all information needed by the DropZone in the `data` prop.

!!! tip "Visual Feedback"
    Change appearance on drag start/end for better UX.

## See Also

- [DropZone](dropzone.md) - Drop target component
- [Inventory Tutorial](../../learn/tutorials/inventory.md) - Complete drag & drop example
