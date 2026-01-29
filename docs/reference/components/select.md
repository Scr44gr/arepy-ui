# Select

Dropdown menu for selecting from a list of options.

## Usage

```python
from arepy_ui import Select, Unit

select = Select(
    options=["Easy", "Normal", "Hard"],
    selected_index=1,
    on_change=lambda idx, val: print(f"Selected: {val}"),
    width=Unit.px(150),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `options` | `list[str]` | required | List of options |
| `selected_index` | `int` | `0` | Initially selected index |
| `on_change` | `Callable[[int, str], None]` | `None` | Called on selection change |
| `width` | `Unit` | `Unit.px(150)` | Dropdown width |
| `height` | `Unit` | `Unit.px(40)` | Dropdown height |
| `bg_color` | `Color` | `Color(50, 52, 60)` | Background color |
| `hover_color` | `Color` | Auto-calculated | Color when hovered (bg + 10) |
| `pressed_color` | `Color` | Auto-calculated | Color when pressed (bg - 15) |
| `style` | `Style` | `None` | Additional styling |

## Interactive States

Select has visual feedback for hover and pressed states:

```python
Select(
    options=["Option 1", "Option 2"],
    bg_color=Color(40, 42, 50),
    hover_color=Color(60, 62, 70),
    pressed_color=Color(30, 32, 40),
)
```

**ACSS Styling with pseudo-selectors:**

```css
.my-select {
    background: #282a32;
}

.my-select:hover {
    background: #3c3e46;
}

.my-select:active {
    background: #1e2028;
}
```

## Properties

```python
select = Select(options=["A", "B", "C"])

# Get selected index
idx = select.selected_index

# Get selected value
value = select.options[select.selected_index]

# Change selection
select.selected_index = 2
```

## Events

The `on_change` callback receives both the index and value:

```python
def handle_change(index: int, value: str):
    print(f"Index: {index}, Value: {value}")

Select(
    options=["One", "Two", "Three"],
    on_change=handle_change,
)
```

## Examples

### Difficulty Selector

```python
Select(
    options=["Easy", "Normal", "Hard", "Nightmare"],
    selected_index=1,
    on_change=lambda i, v: game.set_difficulty(v),
)
```

### Resolution Picker

```python
Select(
    options=["1280x720", "1920x1080", "2560x1440"],
    selected_index=1,
    on_change=lambda i, v: set_resolution(v),
    width=Unit.px(180),
)
```

### Language Selector

```python
Select(
    options=["English", "Español", "日本語", "Deutsch"],
    selected_index=0,
    on_change=lambda i, v: set_language(i),
)
```
