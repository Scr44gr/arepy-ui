# Getting Started

Get arepy-ui running in 5 minutes.

## Installation

```bash
pip install arepy-ui
```

Or with uv:

```bash
uv add arepy-ui
```

## Requirements

- Python 3.11+
- [ArepyEngine](https://github.com/arepyui/arepy)

## Quick Start

Create `main.py`:

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig, Node, Text, Button, Style, Color, Unit, JustifyContent, AlignItems

ui_manager: UIManager = None

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    # Create simple UI
    root = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            background_color=Color(30, 30, 40),
        ),
        children=[
            Text("Hello, arepy-ui!", size=32, color=Color(255, 255, 255)),
            Button("Click me!", on_click=lambda: print("Clicked!")),
        ],
    )
    
    ui_manager.set_root(root)
    game.add_resource(ui_manager)

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw(game: ArepyEngine):
    ui_manager.render()

# Run game
game = ArepyEngine(title="My Game", width=800, height=600)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

Run it:

```bash
uv run main.py
```

<!-- TODO: Add screenshot of hello world -->
![Hello World](../assets/examples/hello-world.png)

## What's Next?

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Build Your First UI**

    ---

    Step-by-step tutorial to build a complete interface.

    [:octicons-arrow-right-24: First UI Tutorial](first-ui.md)

-   :material-book-open-variant:{ .lg .middle } **Core Concepts**

    ---

    Learn Nodes, Styles, and Events.

    [:octicons-arrow-right-24: Concepts](concepts/index.md)

-   :material-view-dashboard:{ .lg .middle } **Component Reference**

    ---

    Explore all available components.

    [:octicons-arrow-right-24: Components](../reference/index.md)

</div>

## Using Markup (AUI)

Prefer declarative UI? Use AUI markup files:

**menu.aui**
```html
<column class="screen">
    <text class="title">Hello, arepy-ui!</text>
    <button class="btn" on-click="say_hello">Click me!</button>
</column>
```

**menu.acss**
```css
.screen {
    width: 100%;
    height: 100%;
    justify-content: center;
    align-items: center;
    background: #1e1e28;
}

.title {
    font-size: 32px;
    color: white;
}

.btn {
    width: 120px;
    height: 40px;
    background: #4080ff;
    border-radius: 8px;
}
```

**main.py**
```python
from arepy_ui.markup import load_aui
from arepy_ui import UIManager, UIConfig

def say_hello():
    print("Hello!")

def setup(game: ArepyEngine):
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    # Load from files
    result = load_aui("menu.aui", handlers={
        "say_hello": say_hello,
    })

    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
    game.add_resource(ui_manager)
```

If parsing fails, inspect `result.errors` before replacing the current UI tree.

[:octicons-arrow-right-24: Learn more about AUI Markup](../reference/markup/aui.md)
