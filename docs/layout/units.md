# Units

Units define sizes and positions in the layout system.

## Available Units

### Pixels

Fixed size in pixels.

```python
from arepy_ui import Unit

Unit.px(100)   # 100 pixels
Unit.px(50.5)  # Decimal values supported
```

### Percent

Percentage of parent size.

```python
Unit.percent(50)   # 50% of parent
Unit.percent(100)  # Full parent size
```

### Viewport

Percentage of screen/window size.

```python
Unit.vw(100)  # 100% of window width
Unit.vh(50)   # 50% of window height
```

### Auto

Automatic sizing based on content or available space.

```python
Unit.auto()  # Size to content or fill available space
```

## Usage

```python
from arepy_ui import Style, Unit

Style(
    width=Unit.px(200),
    height=Unit.percent(100),
)
```

## Examples

### Fixed Size Box

```python
Node(
    style=Style(
        width=Unit.px(300),
        height=Unit.px(200),
    ),
)
```

### Full Screen

```python
Node(
    style=Style(
        width=Unit.percent(100),
        height=Unit.percent(100),
    ),
)
```

### Responsive Width

```python
Node(
    style=Style(
        width=Unit.percent(80),  # 80% of parent
        max_width=Unit.px(600),  # But max 600px
    ),
)
```

### Auto Height

```python
Node(
    style=Style(
        width=Unit.px(200),
        height=Unit.auto(),  # Height based on content
    ),
    children=[...],
)
```
