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
| `size` | `float` | `20` | Checkbox size |
| `style` | `Style` | `None` | Additional styling |

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
