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
| `height` | `Unit` | `Unit.px(32)` | Dropdown height |
| `style` | `Style` | `None` | Additional styling |

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
