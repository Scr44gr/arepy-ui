# Styles & Layout

arepy-ui uses a **flexbox** layout system, similar to CSS. If you know CSS, you'll feel right at home!

## The Style Object

Every Node has a `style` property:

```python
from arepy_ui import Node, Style, Unit, Color, FlexDirection, JustifyContent, AlignItems, Spacing

node = Node(
    style=Style(
        width=Unit.px(200),
        height=Unit.px(100),
        background_color=Color(100, 100, 200),
        padding=Spacing.all(16),
    )
)
```

## Size & Units

### Fixed Size (Pixels)

```python
Style(
    width=Unit.px(200),   # 200 pixels wide
    height=Unit.px(100),  # 100 pixels tall
)
```

### Percentage

```python
Style(
    width=Unit.percent(50),   # 50% of parent width
    height=Unit.percent(100), # 100% of parent height
)
```

### Auto

```python
Style(
    width=Unit.auto(),  # Size to content
)
```

## Flexbox Layout

### Flex Direction

Controls how children are arranged:

```python
# Horizontal (default)
Style(flex_direction=FlexDirection.ROW)

# Vertical
Style(flex_direction=FlexDirection.COLUMN)
```

```
ROW:                    COLUMN:
┌─────────────────┐     ┌─────────────────┐
│ [A] [B] [C]     │     │ [A]             │
└─────────────────┘     │ [B]             │
                        │ [C]             │
                        └─────────────────┘
```

### Justify Content (Main Axis)

Aligns children along the main axis:

```python
Style(justify_content=JustifyContent.CENTER)
```

| Value | Effect |
|-------|--------|
| `FLEX_START` | Pack at start |
| `CENTER` | Center items |
| `FLEX_END` | Pack at end |
| `SPACE_BETWEEN` | Even space between |
| `SPACE_AROUND` | Even space around |

```
FLEX_START:        CENTER:           FLEX_END:
[A][B][C]          [A][B][C]           [A][B][C]

SPACE_BETWEEN:     SPACE_AROUND:
[A]   [B]   [C]    [A]  [B]  [C]
```

### Align Items (Cross Axis)

Aligns children along the cross axis:

```python
Style(align_items=AlignItems.CENTER)
```

| Value | Effect |
|-------|--------|
| `FLEX_START` | Align to start |
| `CENTER` | Center items |
| `FLEX_END` | Align to end |
| `STRETCH` | Stretch to fill |

## Spacing

### Gap

Space between children:

```python
Style(gap=10)  # 10px between each child
```

### Padding

Space inside the node:

```python
# All sides
Style(padding=Spacing.all(16))

# Vertical and horizontal
Style(padding=Spacing.symmetric(vertical=10, horizontal=20))

# Individual sides
Style(padding=Spacing(top=10, right=20, bottom=10, left=20))
```

### Margin

Space outside the node:

```python
Style(margin=Spacing.all(10))
```

## Colors

```python
from arepy_ui.core.types import Color

# RGBA (0-255)
Color(255, 0, 0, 255)      # Red, fully opaque
Color(0, 0, 255, 128)      # Blue, 50% transparent

# Common colors
background_color=Color(30, 30, 40)     # Dark gray
```

## Borders

```python
Style(
    border_radius=8.0,              # Rounded corners
    border_width=2.0,               # Border thickness
    border_color=Color(100, 100, 100),  # Border color
)
```

## Complete Example

```python
# A centered card with flexbox layout
card = Node(
    style=Style(
        width=Unit.px(300),
        height=Unit.auto(),
        background_color=Color(40, 40, 55),
        padding=Spacing.all(20),
        border_radius=12.0,
        flex_direction=FlexDirection.COLUMN,
        gap=16,
    ),
    children=[
        Text("Card Title", size=24, color=Color(255, 255, 255)),
        Text("Some description text here.", size=14, color=Color(180, 180, 180)),
        Button("Action", style=Style(align_self=AlignSelf.FLEX_END)),
    ],
)

# Center the card on screen
root = Node(
    style=Style(
        width=Unit.percent(100),
        height=Unit.percent(100),
        justify_content=JustifyContent.CENTER,
        align_items=AlignItems.CENTER,
        background_color=Color(20, 20, 30),
    ),
    children=[card],
)
```

## Quick Reference

| Property | Values | Description |
|----------|--------|-------------|
| `width` | `Unit.px()`, `Unit.percent()`, `Unit.auto()` | Width |
| `height` | Same as width | Height |
| `flex_direction` | `ROW`, `COLUMN` | Child arrangement |
| `justify_content` | `FLEX_START`, `CENTER`, `FLEX_END`, `SPACE_BETWEEN` | Main axis alignment |
| `align_items` | `FLEX_START`, `CENTER`, `FLEX_END`, `STRETCH` | Cross axis alignment |
| `gap` | Number | Space between children |
| `padding` | `Spacing` | Inner space |
| `margin` | `Spacing` | Outer space |
| `background_color` | `Color` | Background |
| `border_radius` | Number | Corner rounding |

## Next Steps

- [Event Handling](events.md) - Make your UI interactive
- [Flexbox Reference](../../reference/styling/flexbox.md) - Complete layout guide
