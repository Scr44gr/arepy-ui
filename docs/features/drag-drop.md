# Drag & Drop

Built-in drag and drop system for creating interactive UIs.

## Basic Usage

```python
from arepy_ui import Draggable, DropZone, Text

# Create a draggable item
item = Draggable(
    drag_data={"id": "sword", "damage": 10},
    content=Text("Sword"),
)

# Create a drop zone
def on_drop(data):
    print(f"Dropped: {data}")

zone = DropZone(
    on_drop=on_drop,
    children=[Text("Drop here")],
)
```

## Draggable

Makes a node draggable.

```python
Draggable(
    drag_data={"key": "value"},  # Data passed to drop zone
    content=node,                # Visual content (single node)
    style=Style(...),            # Styling
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drag_data` | `Any` | `None` | Data to pass when dropped |
| `content` | `Node` | `None` | Content node |
| `style` | `Style` | `None` | Styling |

## DropZone

Receives dropped items.

```python
DropZone(
    on_drop=callback,    # Called when item dropped
    on_hover=callback,   # Called when dragging over
    children=[...],      # Visual content
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `on_drop` | `Callable` | `None` | Drop callback |
| `on_hover` | `Callable` | `None` | Hover callback |
| `children` | `list[Node]` | `[]` | Content nodes |
| `data` | `Any` | `None` | Arbitrary data (e.g., slot ID) |

## Callbacks

### on_drop

Called when an item is dropped on the zone. It receives the `Draggable` instance and its data.

```python
def on_drop(draggable, data):
    # draggable: The Draggable component instance
    # data: The drag_data from the Draggable
    print(f"Received: {data}")
    return True # Return True to accept the drop
```

### on_hover

Called while dragging over the zone:

```python
def on_hover(data, is_over: bool):
    if is_over:
        zone.style.border_color = Color(0, 255, 0)
    else:
        zone.style.border_color = Color(100, 100, 100)
```

## State Helpers

```python
from arepy_ui import is_dragging, get_drag_state

# Check if currently dragging
if is_dragging():
    print("Dragging something")

# Get current drag state
state = get_drag_state()
if state:
    print(f"Dragging: {state.data}")
```

## Examples

### Inventory Slots

```python
def create_slot(slot_id: int, item=None):
    def on_drop(data):
        inventory.move_item(data["item_id"], slot_id)
    
    zone = DropZone(
        on_drop=on_drop,
        style=Style(
            width=Unit.px(50),
            height=Unit.px(50),
            background_color=Color(60, 60, 60),
            border_radius=5,
        ),
    )
    
    if item:
        zone.add_child(
            Draggable(
                drag_data={"item_id": item.id, "from_slot": slot_id},
                content=Image(item.icon, width=Unit.px(40)),
            )
        )
    
    return zone
```

### Card Game

```python
# Hand cards
hand = Node(
    style=Style(flex_direction=FlexDirection.ROW, gap=10),
    children=[
        Draggable(
            drag_data={"card": card},
            content=create_card_visual(card),
        )
        for card in player.hand
    ],
)

# Play area
play_area = DropZone(
    on_drop=lambda data: play_card(data["card"]),
    style=Style(width=Unit.px(400), height=Unit.px(200)),
    children=[Text("Play cards here")],
)
```

### Sortable List

```python
def create_sortable_item(item, index):
    return DropZone(
        on_drop=lambda data: reorder(data["index"], index),
        children=[
            Draggable(
                drag_data={"index": index, "item": item},
                content=Text(item.name),
            )
        ],
    )
```
