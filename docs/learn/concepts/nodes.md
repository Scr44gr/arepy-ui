# Understanding Nodes

The **Node** is the foundation of everything in arepy-ui. Understanding Nodes is key to building great UIs.

## What is a Node?

A Node is a container that can:
- Have a **style** (size, color, layout)
- Contain **children** (other Nodes)
- Respond to **events** (clicks, hovers)

Think of it like a `<div>` in HTML or a `View` in React Native.

```python
from arepy_ui import Node, Style, Unit, Spacing, FlexDirection, Text, Color

# A simple Node
box = Node(
    style=Style(
        width=Unit.px(200),
        height=Unit.px(100),
        background_color=Color(255, 0, 0),  # Red box
    )
)
```

## The Node Tree

UIs are built as a **tree** of Nodes:

```
Root Node
├── Header Node
│   └── Title (Text)
├── Content Node
│   ├── Button
│   └── Button
└── Footer Node
    └── Copyright (Text)
```

In code:

```python
root = Node(
    children=[
        Node(id="header", children=[
            Text("My App"),
        ]),
        Node(id="content", children=[
            Button("Click me"),
            Button("Or me"),
        ]),
        Node(id="footer", children=[
            Text("© 2024"),
        ]),
    ]
)
```

## Everything is a Node

All components in arepy-ui inherit from Node:

| Component | What it is |
|-----------|------------|
| `Node` | Base container |
| `Text` | Node that displays text |
| `Button` | Node that's clickable |
| `Image` | Node that shows an image |
| `Slider` | Node with a draggable handle |

This means **every component** can have:
- Children
- Styles
- Event handlers

```python
# A Button can have children!
button = Button(
    "Save",
    children=[
        Image(source="icons/save.png"),  # Icon inside button
    ]
)
```

## Node Properties

### Common Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique identifier |
| `style` | `Style` | Visual styling |
| `children` | `list` | Child nodes |
| `visible` | `bool` | Show/hide node |

### Finding Nodes

```python
# Find by ID
header = root.find_by_id("header")

# Access children
first_child = root.children[0]

# Access parent
parent = some_node.parent
```

## Computed Layout

After the layout engine runs, each Node has computed values:

```python
node = Node(style=Style(width=Unit.percent(50)))

# After layout:
print(node.computed_x)       # 0.0
print(node.computed_y)       # 0.0
print(node.computed_width)   # 400.0 (50% of 800px screen)
print(node.computed_height)  # 600.0
```

## Example: Card Component

Let's build a reusable card:

```python
def Card(title: str, content: str) -> Node:
    """A reusable card component."""
    return Node(
        style=Style(
            background_color=Color(40, 40, 50),
            padding=Spacing.all(16),
            border_radius=8.0,
            flex_direction=FlexDirection.COLUMN,
            gap=8,
        ),
        children=[
            Text(title, font_size=18, color=Color(255, 255, 255)),
            Text(content, font_size=14, color=Color(180, 180, 180)),
        ],
    )

# Use it!
root = Node(
    children=[
        Card("Welcome", "This is a card component."),
        Card("Features", "You can reuse it anywhere!"),
    ]
)
```

## Best Practices

!!! tip "Give Nodes IDs"
    Use `id` for nodes you need to reference later:
    ```python
    Node(id="score-display", children=[...])
    ```

!!! tip "Use Functions for Reusable UI"
    Create functions that return Nodes for reusable components:
    ```python
    def MenuItem(text: str, on_click) -> Button:
        return Button(text, on_click=on_click, style=menu_style)
    ```

!!! tip "Keep Trees Shallow"
    Deep nesting can hurt performance. Flatten when possible.

## Next Steps

- [Styles & Layout](styles.md) - Learn the flexbox layout system
- [Event Handling](events.md) - Make your UI interactive
