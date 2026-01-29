# ProgressBar

Visual progress indicator.

## Usage

```python
from arepy_ui.components.progressbar import ProgressBar
from arepy_ui import Color, Unit

# Basic progress bar
bar = ProgressBar(
    value=0.75,  # 75%
    width=Unit.px(200),
    height=Unit.px(20),
)

# Styled progress bar
bar = ProgressBar(
    value=0.5,
    width=Unit.px(300),
    height=Unit.px(25),
    fill_color=Color(0, 200, 0),
    background_color=Color(50, 50, 50),
    border_radius=5.0,
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `float` | `0` | Progress value (0.0 to 1.0) |
| `width` | `Unit` | `Unit.px(200)` | Bar width |
| `height` | `Unit` | `Unit.px(20)` | Bar height |
| `fill_color` | `Color` | `Color(0, 150, 255)` | Fill color |
| `background_color` | `Color` | `Color(60, 60, 60)` | Background color |
| `border_radius` | `float` | `0` | Corner radius |
| `style` | `Style` | `None` | Additional styling |

## Properties

```python
bar = ProgressBar(value=0.5)

# Update value
bar.value = 0.75

# Animate progress (manual)
bar.value = min(bar.value + 0.01, 1.0)
```

## Examples

### Health Bar

```python
def create_health_bar(current: int, max_hp: int):
    return ProgressBar(
        value=current / max_hp,
        width=Unit.px(150),
        height=Unit.px(15),
        fill_color=Color(220, 50, 50),
        border_radius=3,
    )
```

### Loading Screen

```python
loading_bar = ProgressBar(
    value=0,
    width=Unit.percent(80),
    height=Unit.px(30),
    fill_color=Color(100, 200, 100),
    border_radius=5,
)

# In update loop
def update_loading(progress: float):
    loading_bar.value = progress
```

### XP Bar

```python
Node(
    style=Style(flex_direction=FlexDirection.COLUMN, gap=2),
    children=[
        Text(f"Level {player.level}", size=12),
        ProgressBar(
            value=player.xp / player.xp_to_next_level,
            width=Unit.px(200),
            height=Unit.px(10),
            fill_color=Color(255, 215, 0),  # Gold
            border_radius=5,
        ),
    ],
)
```
