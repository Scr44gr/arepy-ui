# Text

Renders text with customizable font, size, and color.

## Usage

```python
from arepy_ui import Text, Color

# Basic text
text = Text("Hello World", size=16)

# With color
text = Text("Red text", size=16, color=Color(255, 0, 0))

# With custom font
text = Text("Custom", size=20, font="my-font")

# Multiline
text = Text("Line 1\nLine 2\nLine 3", size=14)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | `str` | required | The text to display |
| `size` | `float` | `16` | Font size in pixels |
| `color` | `Color` | `Color(255, 255, 255)` | Text color |
| `font` | `str` | `None` | Font name (uses default if None) |
| `style` | `Style` | `None` | Additional styling |

## Properties

```python
text = Text("Hello")

# Update text content
text.text = "New text"

# Update color
text.color = Color(0, 255, 0)

# Update size (via font_size attribute)
text.font_size = 24
text._update_size()
```

## Styling

```python
Text(
    "Styled text",
    size=18,
    style=Style(
        margin=Spacing.all(10),
        padding=Spacing.symmetric(5, 10),
    ),
)
```

## Custom Fonts

First load the font, then use it by name:

```python
from arepy_ui import load_font, Text

# Load font once at startup
load_font("pixel", "assets/fonts/pixel.ttf", base_size=32)

# Use in text
Text("Pixel text", size=16, font_name="pixel")
```

See [Fonts](../features/fonts.md) for more details.
