# Positioning

Control how nodes are positioned in the layout.

## Position Types

### Relative (Default)

Node participates in normal flow.

```python
from arepy_ui import PositionType

Style(position=PositionType.RELATIVE)
```

### Absolute

Node is removed from flow and positioned relative to its parent.

```python
Style(
    position=PositionType.ABSOLUTE,
    top=Unit.px(10),
    left=Unit.px(10),
)
```

## Position Properties

```python
Style(
    position=PositionType.ABSOLUTE,
    top=Unit.px(10),     # Distance from top
    right=Unit.px(10),   # Distance from right
    bottom=Unit.px(10),  # Distance from bottom
    left=Unit.px(10),    # Distance from left
)
```

## Examples

### Corner Badge

```python
Node(
    style=Style(width=Unit.px(100), height=Unit.px(100)),
    children=[
        # Badge in top-right corner
        Node(
            style=Style(
                position=PositionType.ABSOLUTE,
                top=Unit.px(-5),
                right=Unit.px(-5),
                width=Unit.px(20),
                height=Unit.px(20),
                background_color=Color(255, 0, 0),
                border_radius=10,
            ),
        ),
    ],
)
```

### Overlay

```python
Node(
    style=Style(width=Unit.percent(100), height=Unit.percent(100)),
    children=[
        # Full-screen overlay
        Node(
            style=Style(
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                left=Unit.px(0),
                right=Unit.px(0),
                bottom=Unit.px(0),
                background_color=Color(0, 0, 0, 150),
            ),
        ),
    ],
)
```

### Fixed HUD Element

```python
# Health bar in top-left
Node(
    style=Style(
        position=PositionType.ABSOLUTE,
        top=Unit.px(20),
        left=Unit.px(20),
    ),
    children=[ProgressBar(value=0.8, ...)],
)
```

### Tooltip

```python
Node(
    style=Style(
        position=PositionType.ABSOLUTE,
        top=Unit.px(mouse_y + 10),
        left=Unit.px(mouse_x + 10),
        padding=Spacing.all(5),
        background_color=Color(30, 30, 30, 230),
    ),
    children=[Text("Tooltip text", size=12)],
)
```
