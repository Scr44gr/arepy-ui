# DropZone

A drop target for draggable elements.

## Overview

`DropZone` defines areas where `Draggable` elements can be dropped. It receives the data from the dropped item via callback.

## Import

```python
from arepy_ui.components import DropZone
```

## Basic Usage

```python
from arepy_ui.components import DropZone
from arepy_ui import Style, Color, Unit

def handle_drop(data):
    print(f"Item dropped: {data}")

drop_area = DropZone(
    on_drop=handle_drop,
    style=Style(
        width=Unit.px(200),
        height=Unit.px(200),
        background_color=Color(50, 50, 60),
        border_width=2.0,
        border_color=Color(100, 100, 120),
    ),
)
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `on_drop` | `Callable[[dict], None]` | Required | Called when item is dropped |
| `style` | `Style` | `None` | Container style |
| `children` | `list[Node]` | `[]` | Content inside the zone |
| `on_hover_start` | `Callable` | `None` | Called when dragged item enters |
| `on_hover_end` | `Callable` | `None` | Called when dragged item leaves |
| `accept` | `list[str]` | `None` | Filter accepted item types |

## Drop Handler

The `on_drop` callback receives the data dict from the dropped `Draggable`:

```python
def on_drop(data: dict):
    item_id = data.get("id")
    item_type = data.get("type")
    source_slot = data.get("slot")
    
    print(f"Received {item_type} from slot {source_slot}")
```

## Filtering Accepted Items

Only accept certain types:

```python
# Only accept weapons
weapon_slot = DropZone(
    on_drop=equip_weapon,
    accept=["weapon"],
    style=slot_style,
)

# Draggable must have matching type
sword = Draggable(
    data={"type": "weapon", "name": "sword"},
    children=[...],
)

potion = Draggable(
    data={"type": "consumable", "name": "potion"},  # Won't be accepted
    children=[...],
)
```

## Hover Feedback

Show visual feedback when hovering:

```python
is_hovered = False

def on_hover_enter():
    global is_hovered
    is_hovered = True
    refresh_ui()

def on_hover_leave():
    global is_hovered
    is_hovered = False
    refresh_ui()

drop_zone = DropZone(
    on_drop=handle_drop,
    on_hover_start=on_hover_enter,
    on_hover_end=on_hover_leave,
    style=Style(
        background_color=Color(80, 80, 100) if is_hovered else Color(50, 50, 60),
        border_color=Color(150, 150, 200) if is_hovered else Color(80, 80, 100),
    ),
)
```

## With Content

DropZones can contain other elements:

```python
# Slot with existing item
DropZone(
    on_drop=handle_swap,
    style=slot_style,
    children=[
        # Existing item (also draggable for swapping)
        Draggable(
            data={"slot": 0, "item": current_item},
            children=[ItemIcon(current_item.icon)],
        ),
    ],
)
```

## Complete Example

```python
def create_equipment_panel():
    slots = {
        "head": equipped.get("head"),
        "chest": equipped.get("chest"),
        "weapon": equipped.get("weapon"),
    }
    
    def equip_item(slot_name: str):
        def handler(data):
            item = data["item"]
            if item.slot == slot_name:  # Validate slot type
                equipped[slot_name] = item
                refresh_ui()
        return handler
    
    return Node(
        style=Style(flex_direction=FlexDirection.COLUMN, gap=8),
        children=[
            EquipmentSlot("head", slots["head"], equip_item("head")),
            EquipmentSlot("chest", slots["chest"], equip_item("chest")),
            EquipmentSlot("weapon", slots["weapon"], equip_item("weapon")),
        ],
    )

def EquipmentSlot(slot_type: str, item: Optional[Item], on_drop) -> Node:
    return DropZone(
        on_drop=on_drop,
        accept=[slot_type],  # Only accept matching type
        style=Style(
            width=Unit.px(80),
            height=Unit.px(80),
            background_color=Color(40, 40, 55),
            border_radius=8.0,
        ),
        children=[
            ItemIcon(item.icon) if item else Text("🔲", size=24),
        ],
    )
```

## AUI Markup

```html
<dropzone on-drop="handle_drop" accept="weapon,armor">
    <node class="slot-content">
        <text>Drop here</text>
    </node>
</dropzone>
```

## Tips

!!! tip "Always Validate"
    Validate dropped items in your handler, not just with `accept`.

!!! tip "Visual States"
    Use hover callbacks to show when a drop is valid.

## See Also

- [Draggable](draggable.md) - Draggable element component
- [Inventory Tutorial](../../learn/tutorials/inventory.md) - Complete example
- [Drag & Drop Feature](../../features/drag-drop.md) - Full guide
