# Event Handling

Make your UI interactive with event handlers!

## Button Events

The most common interaction - clicking a button:

```python
def on_click():
    print("Button clicked!")

Button("Click me", on_click=on_click)
```

### With Parameters

Use a lambda to pass data:

```python
def select_item(item_id):
    print(f"Selected: {item_id}")

# Create buttons for items
for item in items:
    Button(
        item.name,
        on_click=lambda id=item.id: select_item(id)
    )
```

## Slider Events

Sliders fire `on_change` when the value changes:

```python
def on_volume_change(value):
    print(f"Volume: {value}%")
    audio.set_volume(value / 100)

Slider(
    value=50,
    min_value=0,
    max_value=100,
    on_change=on_volume_change,
)
```

## TextInput Events

Text inputs fire events when text changes:

```python
def on_text_change(text):
    print(f"Text: {text}")

def on_submit(text):
    print(f"Submitted: {text}")

TextInput(
    placeholder="Enter your name...",
    on_change=on_text_change,
    on_submit=on_submit,  # When Enter is pressed
)
```

## Checkbox Events

```python
def on_toggle(checked):
    if checked:
        print("Sound enabled")
    else:
        print("Sound disabled")

Checkbox(
    label="Enable sound",
    checked=True,
    on_change=on_toggle,
)
```

## Select (Dropdown) Events

```python
def on_select(index, option):
    print(f"Selected: {option}")

Select(
    options=["Easy", "Medium", "Hard"],
    selected=0,
    on_change=on_select,
)
```

## ColorPicker Events

```python
def on_color_change(color):
    print(f"Color: rgba({color.r}, {color.g}, {color.b}, {color.a})")
    player.set_color(color)

ColorPicker(
    color=Color(255, 0, 0),
    on_change=on_color_change,
)
```

## Drag & Drop Events

```python
from arepy_ui.components import Draggable, DropZone

def on_drag_start(data):
    print(f"Started dragging: {data}")

def on_drop(data):
    print(f"Dropped: {data}")

# Draggable item
Draggable(
    data={"item_id": 123},
    on_drag_start=on_drag_start,
    children=[Text("Drag me!")],
)

# Drop target
DropZone(
    on_drop=on_drop,
    children=[Text("Drop here!")],
)
```

## Pattern: Updating UI State

A common pattern is updating UI elements based on events:

```python
# Keep references to update later
counter_text: Text = None
count = 0

def increment():
    global count
    count += 1
    counter_text.text = f"Count: {count}"

def create_ui():
    global counter_text
    
    counter_text = Text(f"Count: {count}", font_size=24)
    
    return Node(
        children=[
            counter_text,
            Button("+1", on_click=increment),
        ]
    )
```

## Pattern: State Object

For complex UIs, use a state object:

```python
class GameState:
    def __init__(self):
        self.score = 0
        self.health = 100
        self.score_text = None
        self.health_bar = None
    
    def add_score(self, points):
        self.score += points
        if self.score_text:
            self.score_text.text = f"Score: {self.score}"
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health_bar:
            self.health_bar.value = self.health

state = GameState()
```

## Event Handler Reference

| Component | Event | Callback Signature |
|-----------|-------|-------------------|
| `Button` | `on_click` | `() -> None` |
| `Slider` | `on_change` | `(value: float) -> None` |
| `TextInput` | `on_change` | `(text: str) -> None` |
| `TextInput` | `on_submit` | `(text: str) -> None` |
| `Checkbox` | `on_change` | `(checked: bool) -> None` |
| `Select` | `on_change` | `(index: int, option: str) -> None` |
| `ColorPicker` | `on_change` | `(color: Color) -> None` |
| `Draggable` | `on_drag_start` | `(data: Any) -> None` |
| `DropZone` | `on_drop` | `(data: Any) -> None` |

## Tips

!!! tip "Avoid Heavy Work in Handlers"
    Event handlers run on the main thread. Keep them fast!
    ```python
    # ❌ Bad
    def on_click():
        save_to_disk()  # Slow!
    
    # ✅ Better
    def on_click():
        pending_saves.append(data)  # Queue for later
    ```

!!! tip "Use Default Arguments for Closures"
    ```python
    # ❌ Bug: All buttons use the same i
    for i in range(3):
        Button(f"Button {i}", on_click=lambda: print(i))
    
    # ✅ Correct: Capture i's value
    for i in range(3):
        Button(f"Button {i}", on_click=lambda x=i: print(x))
    ```

## Next Steps

- [Building a Game Menu](../tutorials/game-menu.md) - Apply what you've learned
- [Components Reference](../../reference/components/index.md) - All component events
