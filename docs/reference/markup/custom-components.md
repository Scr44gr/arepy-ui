# Custom Components

Register custom components for use in AUI markup.

## Overview

You can extend AUI with your own components that can be used like built-in elements.

## Registering a Component

```python
from arepy_ui.markup import register_component
from arepy_ui import Node, Text, Style, Color, Unit

def IconButton(props: dict) -> Node:
    """Custom icon button component."""
    icon = props.get("icon", "⭐")
    label = props.get("label", "Button")
    on_click = props.get("on_click")
    
    return Node(
        style=Style(
            flex_direction=FlexDirection.ROW,
            gap=8,
            padding=Spacing.xy(h=16, v=8),
            background_color=Color(80, 80, 100),
            border_radius=8.0,
        ),
        on_click=on_click,
        children=[
            Text(icon, size=20),
            Text(label, size=14, color=Color(255, 255, 255)),
        ],
    )

# Register the component
register_component("icon-button", IconButton)
```

## Using in AUI

After registration, use the component in markup:

```html
<!-- menu.aui -->
<column class="menu">
    <icon-button icon="🎮" label="Play" on-click="start_game" />
    <icon-button icon="⚙️" label="Settings" on-click="open_settings" />
    <icon-button icon="🚪" label="Quit" on-click="quit_game" />
</column>
```

## Component Props

All attributes become props:

```html
<my-component
    title="Hello"
    count="42"
    enabled="true"
    on-click="handler"
/>
```

```python
def MyComponent(props: dict) -> Node:
    title = props.get("title", "Default")
    count = int(props.get("count", 0))
    enabled = props.get("enabled") == "true"
    on_click = props.get("on_click")  # Function reference
    
    return Node(...)
```

## Component with Children

Access children through `props["children"]`:

```python
def Card(props: dict) -> Node:
    """Card container with title."""
    title = props.get("title", "Card")
    children = props.get("children", [])
    
    return Node(
        style=Style(
            background_color=Color(40, 40, 55),
            border_radius=12.0,
            padding=Spacing.all(16),
            flex_direction=FlexDirection.COLUMN,
            gap=12,
        ),
        children=[
            Text(title, size=18, color=Color(255, 255, 255)),
            *children,  # Insert child elements
        ],
    )

register_component("card", Card)
```

Usage:

```html
<card title="Player Stats">
    <text>Health: 100</text>
    <text>Mana: 50</text>
</card>
```

## Complete Example: StatusBar

```python
from arepy_ui.markup import register_component
from arepy_ui import Node, Text, Style, Color, Unit
from arepy_ui.components import ProgressBar
from arepy_ui.core.types import FlexDirection, AlignItems

def StatusBar(props: dict) -> Node:
    """Health/mana bar with icon and value."""
    icon = props.get("icon", "❤️")
    value = float(props.get("value", 100))
    max_value = float(props.get("max", 100))
    color = props.get("color", "#ff4444")
    
    # Parse hex color
    hex_val = color.lstrip("#")
    r, g, b = [int(hex_val[i:i+2], 16) for i in (0, 2, 4)]
    bar_color = Color(r, g, b)
    
    return Node(
        style=Style(
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=8,
            width=Unit.px(200),
        ),
        children=[
            Text(icon, size=20),
            ProgressBar(
                value=value,
                max_value=max_value,
                style=Style(
                    flex=1,
                    height=Unit.px(12),
                ),
                fill_color=bar_color,
            ),
            Text(f"{int(value)}", size=12, color=Color(200, 200, 200)),
        ],
    )

register_component("status-bar", StatusBar)
```

Usage in AUI:

```html
<column class="hud">
    <status-bar icon="❤️" value="{health}" max="100" color="#ff4444" />
    <status-bar icon="💧" value="{mana}" max="80" color="#4488ff" />
    <status-bar icon="⚡" value="{stamina}" max="100" color="#44ff44" />
</column>
```

## Registration API

```python
from arepy_ui.markup import (
    register_component,
    unregister_component,
    get_registered_components,
)

# Register
register_component("my-widget", MyWidgetFunction)

# Unregister
unregister_component("my-widget")

# List all registered
components = get_registered_components()
print(components)  # ["icon-button", "card", "status-bar", ...]
```

## Tips

!!! tip "Naming Convention"
    Use kebab-case for custom component names: `my-component`, `status-bar`.

!!! tip "Props Validation"
    Add defaults and type conversion in your component function.

!!! tip "Reusable Components"
    Create a `components.py` file to register all your custom components at startup.

```python
# components.py
from arepy_ui.markup import register_component

def register_all():
    register_component("icon-button", IconButton)
    register_component("card", Card)
    register_component("status-bar", StatusBar)

# main.py
from components import register_all

def setup(game):
    register_all()
    load_globals("assets/ui/globals.acss")
    # ...
```

## See Also

- [AUI Syntax](aui.md) - Markup structure
- [ACSS Styling](acss.md) - Style custom components
