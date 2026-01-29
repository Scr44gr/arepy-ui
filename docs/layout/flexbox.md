# Flexbox Layout

arepy-ui uses a flexbox-based layout system similar to CSS flexbox.

## Flex Direction

Controls the main axis direction.

```python
from arepy_ui import Style, FlexDirection

# Horizontal row (default)
Style(flex_direction=FlexDirection.ROW)

# Vertical column
Style(flex_direction=FlexDirection.COLUMN)

# Reversed
Style(flex_direction=FlexDirection.ROW_REVERSE)
Style(flex_direction=FlexDirection.COLUMN_REVERSE)
```

## Justify Content

Aligns children along the **main axis**.

```python
from arepy_ui import JustifyContent

Style(justify_content=JustifyContent.FLEX_START)    # Start (default)
Style(justify_content=JustifyContent.FLEX_END)      # End
Style(justify_content=JustifyContent.CENTER)        # Center
Style(justify_content=JustifyContent.SPACE_BETWEEN) # Space between items
Style(justify_content=JustifyContent.SPACE_AROUND)  # Space around items
Style(justify_content=JustifyContent.SPACE_EVENLY)  # Equal space
```

## Align Items

Aligns children along the **cross axis**.

```python
from arepy_ui import AlignItems

Style(align_items=AlignItems.FLEX_START)  # Start
Style(align_items=AlignItems.FLEX_END)    # End
Style(align_items=AlignItems.CENTER)      # Center
Style(align_items=AlignItems.STRETCH)     # Stretch to fill (default)
```

## Gap

Space between children.

```python
Style(gap=10)  # 10px gap between all children
```

## Flex Grow / Shrink

Control how children grow or shrink.

```python
# Child grows to fill available space
child.style.flex_grow = 1

# Child shrinks if needed
child.style.flex_shrink = 1
```

## Examples

### Centered Content

```python
Node(
    style=Style(
        width=Unit.percent(100),
        height=Unit.percent(100),
        justify_content=JustifyContent.CENTER,
        align_items=AlignItems.CENTER,
    ),
    children=[Text("Centered!")],
)
```

### Horizontal Menu

```python
Node(
    style=Style(
        flex_direction=FlexDirection.ROW,
        justify_content=JustifyContent.SPACE_BETWEEN,
        padding=Spacing.symmetric(0, 20),
    ),
    children=[
        Button("Home", ...),
        Button("Play", ...),
        Button("Settings", ...),
    ],
)
```

### Sidebar Layout

```python
Node(
    style=Style(
        flex_direction=FlexDirection.ROW,
        width=Unit.percent(100),
        height=Unit.percent(100),
    ),
    children=[
        # Sidebar (fixed width)
        Node(
            style=Style(width=Unit.px(200), background_color=Color(40, 40, 40)),
            children=[...],
        ),
        # Main content (fills remaining space)
        Node(
            style=Style(flex_grow=1),
            children=[...],
        ),
    ],
)
```

### Card Grid

```python
Node(
    style=Style(
        flex_direction=FlexDirection.ROW,
        flex_wrap=True,  # Wrap to next line
        gap=10,
    ),
    children=[create_card(item) for item in items],
)
```
