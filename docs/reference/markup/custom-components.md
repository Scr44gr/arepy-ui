# Custom Components

Register custom components for use in AUI markup.

## Overview

You can extend AUI by registering regular arepy-ui component classes and mapping them to custom tags.

The current builder support is intentionally small:

- Register a component class with `register_component(...)`
- Use the registered tag in `.aui`
- Let the builder pass the resolved `style` and optional `id`
- Let child nodes declared in markup be appended after construction

Arbitrary markup attributes are not exposed as a generic `props` dictionary in the current runtime.

## Registering a Component

```python
from arepy_ui import Color, Node, Style, Unit, register_component

class HealthBar(Node):
    def __init__(
        self,
        value: float = 100.0,
        max_value: float = 100.0,
        bar_color: Color = Color(0, 255, 0, 255),
        style: Style | None = None,
        **kwargs,
    ):
        merged_style = style or Style(
            width=Unit.px(220),
            height=Unit.px(18),
            background_color=Color(40, 40, 50, 255),
            border_radius=6.0,
        )
        super().__init__(style=merged_style, **kwargs)
        self.value = value
        self.max_value = max_value
        self.bar_color = bar_color

    def render(self):
        super().render()
        # Draw the filled bar here.


register_component(
    HealthBar,
    tags=["healthbar", "health-bar"],
    color=(255, 100, 100),
    category="custom",
    )
```

## Using in AUI

After registration, use the component in markup:

```html
<column class="hud">
    <healthbar id="player-health" />
</column>
```

## What Markup Passes Today

For registered custom tags, the builder currently does this:

- resolves ACSS and inline styles into the `style` kwarg
- forwards the element `id` when present
- instantiates the registered class
- appends declared child elements after the instance is created

That means this works well for components that behave like normal `Node` subclasses and can be configured by style plus any values you set in Python after loading.

```python
result = load_aui("hud.aui")
if result.success and result.root is not None:
    health_bar = result.root.find_by_id("player-health")
    if isinstance(health_bar, HealthBar):
        health_bar.value = 75
        health_bar.max_value = 100
```

## Child Content

Child markup is still useful, because the builder attaches child nodes after the custom component instance is created:

```html
<container class="panel">
    <healthbar id="boss-health">
        <text>Boss</text>
    </healthbar>
</container>
```

```python
class Panel(Node):
    pass


register_component(Panel, tags=["panel"])
```

## Current Limitation

Do not rely on arbitrary markup attributes being converted into constructor kwargs for custom tags. Examples like `value="75"`, `max-value="100"`, or a generic `props` dictionary are not aligned with the current builder implementation.

If you need data-driven custom components today, use one of these approaches:

- configure the component after `load_aui()` by finding it with `id`
- express styling through ACSS and inline styles
- use built-in tags whose attributes are explicitly supported by the markup builder

## Registration API

```python
from arepy_ui import get_registry, register_component

register_component(
    HealthBar,
    name="HealthBar",
    tags=["healthbar", "health-bar"],
    color=(255, 100, 100),
    category="custom",
)

registry = get_registry()
print(registry.get_valid_tags())
```

## Tips

!!! tip "Naming Convention"
    Use kebab-case for custom component names: `my-component`, `status-bar`.

!!! tip "Constructor Contract"
    Keep custom components compatible with normal arepy-ui construction: accept `style`, optional `id`, and `**kwargs`.

!!! tip "Reusable Components"
    Create a `components.py` file to register all your custom components at startup.

```python
# components.py
from arepy_ui import register_component

def register_all():
    register_component(HealthBar, tags=["healthbar", "health-bar"])

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
