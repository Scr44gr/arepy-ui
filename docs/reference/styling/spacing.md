# Spacing

Spacing controls padding (inner space) and margin (outer space).

## Spacing Class

```python
from arepy_ui import Spacing

# All sides equal
Spacing.all(10)  # 10px on all sides

# Symmetric (vertical, horizontal)
Spacing.symmetric(10, 20)  # 10px top/bottom, 20px left/right

# Individual sides (top, right, bottom, left)
Spacing(10, 20, 10, 20)

# Named properties
spacing = Spacing(top=10, right=20, bottom=10, left=20)
```

## Padding

Inner space between the node's border and its content.

```python
Style(padding=Spacing.all(10))
Style(padding=Spacing.symmetric(5, 15))
Style(padding=Spacing(10, 20, 10, 20))
```

## Margin

Outer space between the node and its siblings.

```python
Style(margin=Spacing.all(5))
Style(margin=Spacing.symmetric(10, 0))  # Vertical only
Style(margin=Spacing(0, 0, 10, 0))      # Bottom only
```

## Examples

### Padded Container

```python
Node(
    style=Style(
        padding=Spacing.all(20),
        background_color=Color(40, 40, 40),
    ),
    children=[...],
)
```

### Spaced Items

```python
Node(
    style=Style(flex_direction=FlexDirection.COLUMN),
    children=[
        Text("Item 1", style=Style(margin=Spacing(0, 0, 10, 0))),
        Text("Item 2", style=Style(margin=Spacing(0, 0, 10, 0))),
        Text("Item 3"),
    ],
)
```

### Centered with Margin

```python
Node(
    style=Style(
        width=Unit.px(300),
        margin=Spacing.symmetric(0, auto),  # Center horizontally
    ),
)
```

### Button with Padding

```python
Button(
    "Click",
    style=Style(padding=Spacing.symmetric(10, 20)),
)
```
