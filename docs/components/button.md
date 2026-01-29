# Button

Clickable button with hover and press states.

## Usage

```python
from arepy_ui import Button, Color, Unit

# Basic button
button = Button("Click me", on_click=lambda: print("Clicked!"))

# Styled button
button = Button(
    "Save",
    on_click=lambda: save_game(),
    width=Unit.px(120),
    height=Unit.px(40),
    bg_color=Color(0, 122, 204),
    text_color=Color(255, 255, 255),
    border_radius=8.0,
    font_size=14.0,
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Button label |
| `on_click` | `Callable` | required | Click callback |
| `width` | `Unit` | `Unit.px(120)` | Button width |
| `height` | `Unit` | `Unit.px(40)` | Button height |
| `bg_color` | `Color` | `Color(0, 122, 204)` | Background color |
| `text_color` | `Color` | `Color(255, 255, 255)` | Text color |
| `border_radius` | `float` | `8.0` | Corner radius |
| `font_size` | `float` | `12.0` | Text size |
| `style` | `Style` | `None` | Additional styling |

## Hover Effect

Buttons automatically lighten on hover. The hover color is calculated from `bg_color`:

```python
# Hover color is bg_color + 20 for each RGB channel
hover_color = Color(
    min(bg_color.r + 20, 255),
    min(bg_color.g + 20, 255),
    min(bg_color.b + 20, 255),
    bg_color.a,
)
```

## Examples

### Icon Button

```python
# Button with just an icon (using a small image or unicode)
Button("⚙", on_click=open_settings, width=Unit.px(40), height=Unit.px(40))
```

### Full Width Button

```python
Button(
    "Submit",
    on_click=submit,
    width=Unit.percent(100),
    style=Style(margin=Spacing.symmetric(10, 0)),
)
```

### Danger Button

```python
Button(
    "Delete",
    on_click=delete_item,
    bg_color=Color(220, 50, 50),
)
```
