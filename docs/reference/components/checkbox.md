# Checkbox

Toggle component with optional label.

## Usage

```python
from arepy_ui import Checkbox

# Basic checkbox
checkbox = Checkbox(
    label="Enable sound",
    checked=True,
    on_change=lambda checked: set_sound(checked),
)

# Without label
checkbox = Checkbox(
    checked=False,
    on_change=lambda c: print(f"Checked: {c}"),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | `""` | Label text |
| `checked` | `bool` | `False` | Initial state |
| `on_change` | `Callable[[bool], None]` | `None` | Called when toggled |
| `size` | `float` | `22` | Checkbox size |
| `color` | `Color` | `Color(0, 150, 255)` | Check color when checked |
| `hover_color` | `Color` | Auto-calculated | Color when hovered (color + 30) |
| `pressed_color` | `Color` | Auto-calculated | Color when pressed (color - 40) |
| `unchecked_color` | `Color` | `Color(50, 52, 60)` | Background when unchecked |
| `style` | `Style` | `None` | Additional styling |

## Interactive States

Checkbox has visual feedback for hover and pressed states:

```python
Checkbox(
    checked=True,
    color=Color(0, 200, 100),          # Custom check color
    hover_color=Color(50, 230, 130),   # Custom hover
    pressed_color=Color(0, 150, 70),   # Custom pressed
)
```

**ACSS Styling with pseudo-selectors:**

```css
.my-checkbox {
    background: #00c864;
}

.my-checkbox:hover {
    background: #32e682;
}

.my-checkbox:active {
    background: #009646;
}
```

## Properties

```python
checkbox = Checkbox(label="Option")

# Get current state
is_checked = checkbox.checked

# Set state programmatically
checkbox.checked = True
```

## Examples

### Settings List

```python
Node(
    style=Style(flex_direction=FlexDirection.COLUMN, gap=10),
    children=[
        Checkbox(label="Enable music", checked=True, on_change=set_music),
        Checkbox(label="Enable sound effects", checked=True, on_change=set_sfx),
        Checkbox(label="Show FPS", checked=False, on_change=set_fps_display),
        Checkbox(label="Fullscreen", checked=False, on_change=set_fullscreen),
    ],
)
```

### Terms Agreement

```python
agree_checkbox = Checkbox(
    label="I agree to the terms and conditions",
    on_change=lambda c: submit_button.set_enabled(c),
)
```
