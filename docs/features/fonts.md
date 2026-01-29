# Custom Fonts

Load and use custom TrueType fonts.

## Loading Fonts

```python
from arepy_ui import load_font

# Load a font
load_font("pixel", "assets/fonts/pixel.ttf", base_size=32)

# Load and set as default
load_font("main", "assets/fonts/main.ttf", base_size=32, set_as_default=True)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | required | Unique font name |
| `path` | `str` | required | Path to .ttf/.otf file |
| `base_size` | `int` | `32` | Base size for quality |
| `set_as_default` | `bool` | `False` | Use as default font |

## Using Fonts

```python
from arepy_ui import Text

# Use by name
Text("Hello", font_size=16, font_name="pixel")

# Default font (if set)
Text("Hello", font_size=16)  # Uses default font
```

## Font Manager

For more control, use the FontManager directly:

```python
from arepy_ui import FontManager, get_font_manager

# Get the singleton
fm = get_font_manager()

# Load font
fm.load_font("title", "fonts/title.ttf", base_size=48)

# Get font info
font_info = fm.get_font_info("title")
print(f"Base size: {font_info.base_size}")

# Get raw font object
font = fm.get_font("title")
```

## Text Measurement

```python
from arepy_ui import measure_text, measure_text_ex

# Simple measurement
width = measure_text("Hello World", font_size=16)

# Detailed measurement
metrics = measure_text_ex("Hello World", font_size=16, font_name="pixel")
print(f"Width: {metrics.width}, Height: {metrics.height}")
```

## Drawing Text Directly

```python
from arepy_ui import draw_text, draw_text_centered

# Draw at position
draw_text("Hello", x=100, y=100, size=16, color=Color(255, 255, 255))

# Draw centered at position
draw_text_centered("Title", x=400, y=50, size=24, color=Color(255, 255, 255))
```

## Examples

### Multiple Fonts

```python
# Load fonts at startup
def setup(game):
    load_font("title", "fonts/title.ttf", base_size=48)
    load_font("body", "fonts/body.ttf", base_size=24, set_as_default=True)
    load_font("mono", "fonts/mono.ttf", base_size=16)

# Use in UI
Node(children=[
    Text("GAME TITLE", font_size=48, font_name="title"),
    Text("Regular text with body font", font_size=16),  # Uses default
    Text("Code: print('hello')", font_size=14, font_name="mono"),
])
```

### Pixel Font for Retro Look

```python
load_font("pixel", "fonts/pixel.ttf", base_size=16)

# Use at base size or multiples for crisp pixels
Text("SCORE: 1000", font_size=16, font_name="pixel")
Text("LEVEL 1", font_size=32, font_name="pixel")  # 2x size
```

!!! tip "Base Size"
    For best quality, set `base_size` to the largest size you'll use. The font will scale down cleanly but may look blurry when scaled up significantly.
