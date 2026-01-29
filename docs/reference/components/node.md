# Node

The fundamental building block of arepy-ui.

## Overview

`Node` is the core container element in arepy-ui. Every UI element is either a Node or contains Nodes. Think of it as a `<div>` in HTML.

## Import

```python
from arepy_ui import Node
```

## Basic Usage

```python
from arepy_ui import Node, Style, Color, Unit

# Simple node
node = Node(
    style=Style(
        width=Unit.px(200),
        height=Unit.px(100),
        background_color=Color(50, 50, 60),
    ),
)

# Node with children
container = Node(
    style=Style(
        width=Unit.percent(100),
        height=Unit.percent(100),
    ),
    children=[
        Text("Hello!"),
        Button("Click me"),
    ],
)
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `str` | `None` | Unique identifier for the node |
| `style` | `Style` | `Style()` | Layout and appearance properties |
| `children` | `list[Node]` | `[]` | Child nodes |
| `class_name` | `str` | `None` | CSS class for markup integration |
| `on_click` | `Callable` | `None` | Click event handler |
| `on_hover` | `Callable` | `None` | Hover event handler |

## Style Properties

See [Style Properties](../styling/properties.md) for all available options.

Common properties:

```python
Style(
    # Size
    width=Unit.px(200),
    height=Unit.percent(100),
    
    # Layout
    flex_direction=FlexDirection.ROW,
    justify_content=JustifyContent.CENTER,
    align_items=AlignItems.CENTER,
    gap=10,
    
    # Appearance
    background_color=Color(30, 30, 40),
    border_radius=8.0,
    border_width=1.0,
    border_color=Color(60, 60, 70),
    
    # Spacing
    padding=Spacing.all(16),
    margin=Spacing(top=Unit.px(10)),
)
```

## Nesting

Nodes can be deeply nested:

```python
# Header - Content - Footer layout
Node(
    style=Style(
        flex_direction=FlexDirection.COLUMN,
        height=Unit.percent(100),
    ),
    children=[
        # Header
        Node(
            style=Style(height=Unit.px(60)),
            children=[Text("Header")],
        ),
        # Content (grows to fill space)
        Node(
            style=Style(flex=1),
            children=[Text("Main content")],
        ),
        # Footer
        Node(
            style=Style(height=Unit.px(40)),
            children=[Text("Footer")],
        ),
    ],
)
```

## Finding Nodes

Use `id` to find nodes in the tree:

```python
root = Node(
    id="root",
    children=[
        Node(id="sidebar"),
        Node(id="content"),
    ],
)

# Find by ID (from root node)
sidebar = ui_manager.root.find_by_id("sidebar") if ui_manager.root else None
```

## AUI Markup

In AUI markup, generic containers are:

```html
<node class="container">...</node>
<column class="stack">...</column>
<row class="horizontal">...</row>
```

The `<column>` and `<row>` elements are shortcuts for Node with `flex_direction` preset.

## Tips

!!! tip "Use Semantic IDs"
    Give nodes meaningful IDs for easier debugging and lookup.

!!! tip "Avoid Deep Nesting"
    Keep your hierarchy shallow when possible for better performance.

## See Also

- [Understanding Nodes](../../learn/concepts/nodes.md) - Concept explanation
- [Style Properties](../styling/properties.md) - All style options
- [Flexbox Layout](../styling/flexbox.md) - Layout guide
