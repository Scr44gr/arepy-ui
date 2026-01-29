# Image

Display textures with support for different fit modes.

## Usage

```python
from arepy_ui import Image, ImageFit, Color, Unit

# Basic image
img = Image("assets/icon.png", width=Unit.px(64), height=Unit.px(64))

# With tint color
img = Image("assets/heart.png", tint=Color(255, 0, 0))

# With fit mode
img = Image("assets/background.png", fit=ImageFit.COVER)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `str` | required | Path to image file |
| `width` | `Unit` | `Unit.auto()` | Image width |
| `height` | `Unit` | `Unit.auto()` | Image height |
| `tint` | `Color` | `Color(255, 255, 255)` | Tint color |
| `fit` | `ImageFit` | `ImageFit.FILL` | How image fits container |
| `border_radius` | `float` | `0` | Corner radius |
| `style` | `Style` | `None` | Additional styling |

## Fit Modes

```python
from arepy_ui import ImageFit

# Fill: stretch to fill (may distort)
Image("bg.png", fit=ImageFit.FILL)

# Contain: fit inside, maintain aspect ratio
Image("bg.png", fit=ImageFit.CONTAIN)

# Cover: fill container, maintain aspect ratio (may crop)
Image("bg.png", fit=ImageFit.COVER)
```

## Examples

### Avatar

```python
Image(
    "assets/avatar.png",
    width=Unit.px(64),
    height=Unit.px(64),
    border_radius=32,  # Circular
)
```

### Tinted Icon

```python
# Red heart
Image("assets/heart.png", tint=Color(255, 0, 0), width=Unit.px(32))

# Grayed out (disabled look)
Image("assets/icon.png", tint=Color(128, 128, 128), width=Unit.px(32))
```

### Background

```python
Node(
    style=Style(width=Unit.percent(100), height=Unit.percent(100)),
    children=[
        Image(
            "assets/background.jpg",
            width=Unit.percent(100),
            height=Unit.percent(100),
            fit=ImageFit.COVER,
        ),
        # UI content on top...
    ],
)
```

!!! note "Asset Store Required"
    Image loading requires the asset store to be configured. This is done automatically when using `UIManager.from_engine()`.
