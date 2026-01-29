# ColorPicker

Interactive color selection component using the HSV (Hue, Saturation, Value) color model.

## Overview

The ColorPicker provides a complete color selection experience with:

- **Saturation/Value gradient** - Square picker for saturation (X-axis) and value (Y-axis)
- **Hue slider** - Vertical bar to select the base hue (0-360°)
- **Alpha slider** - Optional transparency control
- **Preview** - Live preview of the selected color

## Usage

=== "Python"

    ```python
    from arepy_ui.components import ColorPicker, Color, Unit

    def on_color_change(color: Color):
        print(f"Selected: #{color.r:02X}{color.g:02X}{color.b:02X}")

    picker = ColorPicker(
        color=Color(255, 0, 0, 255),
        width=Unit.px(280),
        height=Unit.px(220),
        show_alpha=True,
        show_preview=True,
        on_change=on_color_change,
    )
    ```

=== "AUI"

    ```html
    <colorpicker 
        id="my-picker" 
        color="#ff0000" 
        width="280px" 
        height="220px"
        show-alpha="true"
        show-preview="true"
        on-change="on_color_change" 
    />
    ```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `color` | `Color` | `Color(255, 0, 0, 255)` | Initial color (red by default) |
| `width` | `Unit` | `Unit.px(250)` | Total width of the picker |
| `height` | `Unit` | `Unit.px(200)` | Height of the SV gradient area |
| `show_alpha` | `bool` | `True` | Whether to show the alpha slider |
| `show_preview` | `bool` | `True` | Whether to show the color preview |
| `on_change` | `Callable[[Color], None]` | `None` | Callback when color changes |
| `style` | `Style` | `None` | Additional styling |

## Properties

```python
picker = ColorPicker(color=Color(100, 150, 200, 255))

# Get current color
current_color = picker.color  # Color(100, 150, 200, 255)

# Get hex color string
hex_value = picker.hex_color  # "#6496C8" or "#6496C8FF" if alpha < 255

# Set color programmatically
picker.color = Color(255, 128, 0, 255)
```

## Examples

### Basic Color Picker

```python
from arepy_ui.components import ColorPicker, Color, Unit, Node, Text, Style
from arepy_ui.core.types import FlexDirection

color_display = Text("Color: #FF0000", size=14)

def update_display(color: Color):
    hex_val = f"#{color.r:02X}{color.g:02X}{color.b:02X}"
    color_display.text = f"Color: {hex_val}"

ui = Node(
    style=Style(
        flex_direction=FlexDirection.COLUMN,
        gap=20,
    ),
    children=[
        ColorPicker(
            color=Color(255, 0, 0, 255),
            on_change=update_display,
        ),
        color_display,
    ],
)
```

### Color Picker with Preview Box

```python
from arepy_ui.components import ColorPicker, Color, Unit, Node, Style

preview_box = Node(
    style=Style(
        width=Unit.px(100),
        height=Unit.px(100),
        background_color=Color(255, 0, 0, 255),
        border_radius=8.0,
    ),
)

def on_change(color: Color):
    preview_box.style.background_color = color

picker = ColorPicker(
    color=Color(255, 0, 0, 255),
    show_alpha=True,
    on_change=on_change,
)
```

### Without Alpha Channel

```python
picker = ColorPicker(
    color=Color(0, 150, 255, 255),
    width=Unit.px(200),
    height=Unit.px(180),
    show_alpha=False,  # Hide alpha slider
    show_preview=True,
)
```

### Minimal Picker

```python
picker = ColorPicker(
    color=Color(128, 128, 128, 255),
    width=Unit.px(180),
    height=Unit.px(150),
    show_alpha=False,
    show_preview=False,  # No preview bar
)
```

## Color Model

The ColorPicker uses the **HSV** (Hue, Saturation, Value) color model internally:

- **Hue** (0-360°): The base color on the color wheel
- **Saturation** (0-100%): Color intensity (left = gray, right = vivid)
- **Value** (0-100%): Brightness (bottom = black, top = bright)

This model is more intuitive for color selection than RGB because:

1. Moving horizontally changes saturation only
2. Moving vertically changes brightness only
3. The hue bar changes the base color independently

## Performance

The ColorPicker uses **streaming textures** for efficient gradient rendering:

- Gradients are generated using Cython-optimized functions when available
- Textures are updated only when the hue changes
- Double-buffered uploads prevent visual tearing

To enable Cython acceleration:

```bash
pip install arepy-ui[markup]
python -m arepy_ui.markup.build_ext
```

## Styling

The ColorPicker accepts standard Node styles:

```python
picker = ColorPicker(
    color=Color(255, 0, 0, 255),
    style=Style(
        margin=Spacing.all(20),
        border_radius=8.0,
    ),
)
```

## AUI Markup

In `.aui` files, the colorpicker tag maps to the ColorPicker component:

```html
<container class="color-section">
    <text class="label">Choose a color:</text>
    <colorpicker 
        id="theme-color"
        color="#6c5ce7"
        width="250px"
        height="200px"
        show-alpha="true"
        on-change="on_theme_change"
    />
</container>
```

**Handler mapping:**

```python
def on_theme_change(color):
    app.theme_color = color

handlers = {
    "on_theme_change": on_theme_change,
}

root = load_aui("ui/settings.aui", handlers=handlers)
```
