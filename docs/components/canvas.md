# Canvas

Container for custom drawing using the renderer.

## Usage

```python
from arepy_ui import Canvas, Unit, Color

def draw(renderer, x, y, width, height):
    # Custom drawing code
    renderer.draw_circle(x + width/2, y + height/2, 50, Color(255, 0, 0))

canvas = Canvas(
    on_render=draw,
    width=Unit.px(200),
    height=Unit.px(200),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `on_render` | `Callable` | required | Drawing callback |
| `width` | `Unit` | `Unit.px(100)` | Canvas width |
| `height` | `Unit` | `Unit.px(100)` | Canvas height |
| `style` | `Style` | `None` | Additional styling |

## Render Callback

The `on_render` callback receives:

- `renderer` - The 2D renderer for drawing
- `x` - Computed X position of the canvas
- `y` - Computed Y position of the canvas
- `width` - Computed width of the canvas
- `height` - Computed height of the canvas

```python
def on_render(renderer, x: float, y: float, width: float, height: float):
    # Use renderer methods to draw
    pass
```

## Examples

### Mini Map

```python
def draw_minimap(renderer, x, y, w, h):
    # Background
    renderer.draw_rectangle(Rect(x, y, w, h), Color(20, 20, 20, 200))
    
    # Player dot
    px = x + w/2
    py = y + h/2
    renderer.draw_circle(px, py, 3, Color(0, 255, 0))
    
    # Enemies
    for enemy in enemies:
        ex = x + (enemy.x / world_width) * w
        ey = y + (enemy.y / world_height) * h
        renderer.draw_circle(ex, ey, 2, Color(255, 0, 0))

Canvas(on_render=draw_minimap, width=Unit.px(150), height=Unit.px(150))
```

### Graph

```python
def draw_graph(renderer, x, y, w, h):
    # Axes
    renderer.draw_line(x, y + h, x + w, y + h, Color(255, 255, 255))
    renderer.draw_line(x, y, x, y + h, Color(255, 255, 255))
    
    # Data points
    for i, value in enumerate(data):
        px = x + (i / len(data)) * w
        py = y + h - (value * h)
        renderer.draw_circle(px, py, 3, Color(0, 200, 255))

Canvas(on_render=draw_graph, width=Unit.px(300), height=Unit.px(150))
```

### Custom Shape

```python
def draw_hexagon(renderer, x, y, w, h):
    cx, cy = x + w/2, y + h/2
    radius = min(w, h) / 2 - 5
    
    import math
    points = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 6
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        points.append((px, py))
    
    # Draw lines between points
    for i in range(6):
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        renderer.draw_line(p1[0], p1[1], p2[0], p2[1], Color(255, 200, 0))

Canvas(on_render=draw_hexagon, width=Unit.px(100), height=Unit.px(100))
```
