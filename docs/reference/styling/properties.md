# Style Properties

Complete reference for all Style properties.

## Overview

The `Style` class controls layout, appearance, and positioning of nodes.

## Import

```python
from arepy_ui import Style, Color, Unit, FlexDirection, JustifyContent, AlignItems, Spacing
```

## Size Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `width` | `Unit` | `auto` | Element width |
| `height` | `Unit` | `auto` | Element height |
| `min_width` | `Unit` | `None` | Minimum width |
| `min_height` | `Unit` | `None` | Minimum height |
| `max_width` | `Unit` | `None` | Maximum width |
| `max_height` | `Unit` | `None` | Maximum height |

```python
Style(
    width=Unit.px(200),         # Fixed 200 pixels
    height=Unit.percent(100),   # 100% of parent
    min_width=Unit.px(100),     # At least 100px
    max_width=Unit.px(500),     # At most 500px
)
```

## Flex Layout

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `flex_direction` | `FlexDirection` | `COLUMN` | Main axis direction |
| `justify_content` | `JustifyContent` | `FLEX_START` | Main axis alignment |
| `align_items` | `AlignItems` | `STRETCH` | Cross axis alignment |
| `align_self` | `AlignItems` | `None` | Override parent's align_items |
| `flex` | `float` | `0` | Flex grow factor |
| `flex_grow` | `float` | `0` | How much to grow |
| `flex_shrink` | `float` | `1` | How much to shrink |
| `flex_wrap` | `FlexWrap` | `NO_WRAP` | Wrap behavior |
| `gap` | `float` | `0` | Space between children |

```python
Style(
    flex_direction=FlexDirection.ROW,
    justify_content=JustifyContent.SPACE_BETWEEN,
    align_items=AlignItems.CENTER,
    gap=10,
)
```

## Spacing

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `padding` | `Spacing` | `None` | Inner spacing |
| `margin` | `Spacing` | `None` | Outer spacing |

```python
from arepy_ui.core.style import Spacing

Style(
    padding=Spacing.all(16),  # All sides
    margin=Spacing(
        top=Unit.px(10),
        right=Unit.px(20),
        bottom=Unit.px(10),
        left=Unit.px(20),
    ),
)
```

## Background

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `background_color` | `Color` | `None` | Background fill color |
| `background_image` | `str` | `None` | Path to background image |

```python
Style(
    background_color=Color(30, 30, 40, 255),  # RGBA
)
```

## Border

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `border_width` | `float` | `0` | Border thickness |
| `border_color` | `Color` | `None` | Border color |
| `border_radius` | `float` | `0` | Corner radius |

```python
Style(
    border_width=2.0,
    border_color=Color(100, 100, 120),
    border_radius=8.0,
)
```

## Positioning

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `position` | `str` | `"relative"` | Positioning type |
| `top` | `Unit` | `None` | Top offset |
| `right` | `Unit` | `None` | Right offset |
| `bottom` | `Unit` | `None` | Bottom offset |
| `left` | `Unit` | `None` | Left offset |
| `z_index` | `int` | `0` | Stack order |

```python
# Absolute positioned overlay
Style(
    position="absolute",
    top=Unit.px(0),
    left=Unit.px(0),
    right=Unit.px(0),
    bottom=Unit.px(0),
    z_index=100,
)
```

## Visibility

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `visible` | `bool` | `True` | Whether visible |
| `opacity` | `float` | `1.0` | Transparency (0-1) |

```python
Style(
    visible=False,  # Hidden
    opacity=0.5,    # 50% transparent
)
```

## Overflow

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `overflow` | `Overflow` | `VISIBLE` | Content overflow handling |

```python
from arepy_ui.core.types import Overflow

Style(
    overflow=Overflow.HIDDEN,  # Clip overflow
    overflow=Overflow.SCROLL,  # Enable scrolling
)
```

## Complete Example

```python
card_style = Style(
    # Size
    width=Unit.px(300),
    height=Unit.auto(),
    min_height=Unit.px(100),
    
    # Layout
    flex_direction=FlexDirection.COLUMN,
    justify_content=JustifyContent.FLEX_START,
    align_items=AlignItems.STRETCH,
    gap=12,
    
    # Spacing
    padding=Spacing.all(20),
    margin=Spacing(bottom=Unit.px(16)),
    
    # Appearance
    background_color=Color(40, 40, 55),
    border_radius=12.0,
    border_width=1.0,
    border_color=Color(60, 60, 75),
    
    # Effects
    opacity=1.0,
)
```

## See Also

- [Units](units.md) - Size units reference
- [Spacing](spacing.md) - Padding and margin
- [Flexbox](flexbox.md) - Layout guide
- [Positioning](positioning.md) - Absolute/relative positioning
