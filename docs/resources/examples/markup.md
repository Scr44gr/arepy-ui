# Markup Demo

Using AUI/ACSS markup files.

<!-- TODO: Add markup demo screenshot -->
![Markup Demo](../../assets/examples/markup-demo.png)

## Overview

This example shows how to build UI with declarative markup instead of Python code.

## Run the Demo

```bash
uv run examples/demo_markup.py
```

## Files

### menu.aui

```html
<column class="screen">
    <!-- Header -->
    <row class="header">
        <text class="logo">🎮</text>
        <text class="title">{game_title}</text>
    </row>
    
    <!-- Menu -->
    <column class="menu">
        <button class="btn" on-click="new_game">New Game</button>
        <button class="btn" on-click="continue_game">Continue</button>
        <button class="btn" on-click="options">Options</button>
        <button class="btn btn-danger" on-click="quit">Quit</button>
    </column>
    
    <!-- Footer -->
    <text class="version">v{version}</text>
</column>
```

### menu.acss

```css
:root {
    --bg: #1a1a2e;
    --primary: #6450c8;
    --danger: #c83c3c;
    --text: #ffffff;
    --text-dim: #888899;
}

.screen {
    width: 100%;
    height: 100%;
    background: var(--bg);
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 40px;
}

.header {
    flex-direction: row;
    align-items: center;
    gap: 12px;
}

.logo {
    font-size: 48px;
}

.title {
    font-size: 36px;
    color: var(--text);
}

.menu {
    flex-direction: column;
    gap: 12px;
}

.btn {
    width: 200px;
    height: 50px;
    background: var(--primary);
    border-radius: 8px;
    justify-content: center;
    align-items: center;
}

.btn-danger {
    background: var(--danger);
}

.version {
    font-size: 12px;
    color: var(--text-dim);
    position: absolute;
    bottom: 20px;
    right: 20px;
}
```

### main.py

```python
"""Markup demo."""
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager
from arepy_ui.markup import load_aui, load_globals

ui_manager: UIManager = None

def new_game():
    print("Starting new game...")

def continue_game():
    print("Continuing...")

def options():
    print("Opening options...")

def quit():
    print("Quitting...")

def setup(game: ArepyEngine):
    global ui_manager
    
    # Load global styles
    load_globals("assets/ui/globals.acss")
    
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    # Load AUI with handlers
    result = load_aui("assets/ui/menu.aui", handlers={
        # Event handlers
        "new_game": new_game,
        "continue_game": continue_game,
        "options": options,
        "quit": quit,
    })

    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
    game.add_resource(ui_manager)

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()

game = ArepyEngine(title="Markup Demo", width=800, height=600)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

## Key Concepts

### Dynamic Data

The current loader maps callbacks through `handlers=`. For dynamic values, build the text in Python or rebuild the UI tree when your state changes.

### Event Handlers

Reference functions by name:

```html
<button on-click="my_handler">Click</button>
```

```python
load_aui("file.aui", handlers={"my_handler": my_function})
```

### CSS Variables

Define in ACSS and use throughout:

```css
:root { --primary: #6450c8; }
.btn { background: var(--primary); }
```

## File Organization

```
assets/
└── ui/
    ├── globals.acss
    ├── menu.aui
    ├── menu.acss
    ├── options.aui
    └── options.acss
```

## See Also

- [AUI Syntax](../../reference/markup/aui.md) - Markup reference
- [ACSS Styling](../../reference/markup/acss.md) - Style reference
- [Global Styles](../../reference/markup/globals.md) - Variables and themes
