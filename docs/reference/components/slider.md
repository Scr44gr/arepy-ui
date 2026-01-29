# Slider

Horizontal or vertical slider for numeric values.

## Usage

```python
from arepy_ui import Slider, SliderOrientation, Unit

# Basic slider
slider = Slider(
    value=50,
    min_value=0,
    max_value=100,
    on_change=lambda v: print(f"Value: {v}"),
)

# Vertical slider
slider = Slider(
    value=0.5,
    min_value=0,
    max_value=1,
    orientation=SliderOrientation.VERTICAL,
    height=Unit.px(150),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `float` | `0` | Initial value |
| `min_value` | `float` | `0` | Minimum value |
| `max_value` | `float` | `100` | Maximum value |
| `on_change` | `Callable[[float], None]` | `None` | Called when value changes |
| `orientation` | `SliderOrientation` | `HORIZONTAL` | Slider direction |
| `width` | `Unit` | `Unit.px(200)` | Slider width |
| `height` | `Unit` | `Unit.px(20)` | Slider height |
| `style` | `Style` | `None` | Additional styling |

## Properties

```python
slider = Slider(value=50, min_value=0, max_value=100)

# Get current value
current = slider.value

# Set value programmatically
slider.value = 75
```

## Orientation

```python
from arepy_ui import SliderOrientation

# Horizontal (default)
Slider(orientation=SliderOrientation.HORIZONTAL, width=Unit.px(200))

# Vertical
Slider(orientation=SliderOrientation.VERTICAL, height=Unit.px(150))
```

## Examples

### Volume Control

```python
Node(
    style=Style(flex_direction=FlexDirection.ROW, align_items=AlignItems.CENTER, gap=10),
    children=[
        Text("Volume", size=14),
        Slider(
            value=audio.volume,
            min_value=0,
            max_value=100,
            on_change=lambda v: audio.set_volume(v),
            width=Unit.px(150),
        ),
        Text(f"{int(audio.volume)}%", size=12),
    ],
)
```

### Color Picker (RGB)

```python
Node(
    style=Style(flex_direction=FlexDirection.COLUMN, gap=5),
    children=[
        Slider(value=255, max_value=255, on_change=lambda v: set_r(v)),
        Slider(value=128, max_value=255, on_change=lambda v: set_g(v)),
        Slider(value=0, max_value=255, on_change=lambda v: set_b(v)),
    ],
)
```
