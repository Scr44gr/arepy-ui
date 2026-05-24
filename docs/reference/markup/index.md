# Markup Reference

AUI/ACSS declarative markup system for arepy-ui.

<div class="grid cards" markdown>

-   :material-code-tags:{ .lg .middle } **AUI Syntax**

    ---

    HTML-like markup for UI structure.

    [:octicons-arrow-right-24: AUI Guide](aui.md)

-   :material-palette:{ .lg .middle } **ACSS Styling**

    ---

    CSS-like stylesheets for AUI files.

    [:octicons-arrow-right-24: ACSS Guide](acss.md)

-   :material-brush-variant:{ .lg .middle } **Global Styles**

    ---

    Variables and theme management.

    [:octicons-arrow-right-24: Globals Guide](globals.md)

-   :material-puzzle:{ .lg .middle } **Custom Components**

    ---

    Extend AUI with your own elements.

    [:octicons-arrow-right-24: Custom Components](custom-components.md)

</div>

## Quick Start

Create two files:

=== "menu.aui"

    ```html
    <column class="screen">
        <text class="title">My Game</text>
        <button class="btn" on-click="start">Play</button>
    </column>
    ```

=== "menu.acss"

    ```css
    .screen {
        width: 100%;
        height: 100%;
        background: #1a1a2e;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }

    .title {
        font-size: 48px;
        color: white;
    }

    .btn {
        width: 200px;
        height: 50px;
        background: #6450c8;
        border-radius: 8px;
    }
    ```

=== "main.py"

    ```python
    from arepy_ui.markup import load_aui
    from arepy_ui import UIManager, UIConfig

    def start():
        print("Game started!")

    def setup(game):
        ui_manager = UIManager.from_engine(game, config=UIConfig())
        result = load_aui("menu.aui", handlers={"start": start})
        if result.success and result.root is not None:
            ui_manager.set_root(result.root)
        game.add_resource(ui_manager)
    ```

## When to Use Markup

| Use Markup When... | Use Python API When... |
|--------------------|------------------------|
| Building static layouts | Creating dynamic UIs |
| Designers need to edit | Complex logic per element |
| Quick prototyping | Programmatic generation |
| Separating structure/style | Fine-grained control |

## File Organization

```
assets/
└── ui/
    ├── globals.acss        # Shared variables
    ├── main-menu.aui       # Main menu structure
    ├── main-menu.acss      # Main menu styles
    ├── options.aui         # Options screen
    ├── options.acss        # Options styles
    ├── hud.aui             # In-game HUD
    └── hud.acss            # HUD styles
```

## API Overview

```python
from arepy_ui.markup import (
    load_aui,           # Load AUI file
    load_aui_string,    # Load AUI from string
    load_globals,       # Load global styles
    set_theme,          # Switch theme
    get_theme,          # Get current theme
)

from arepy_ui import register_component  # Add custom element
```
