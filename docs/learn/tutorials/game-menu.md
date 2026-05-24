# Building a Game Menu

Learn how to build a professional-looking game menu with arepy-ui.

## What We'll Build

- Title screen with game logo
- Start, Options, and Quit buttons
- Options panel with volume slider
- Smooth transitions between panels

## Step 1: Project Setup

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig, Node, Text, Button, Slider, Style, Color, Unit, FlexDirection, JustifyContent, AlignItems, Spacing

ui_manager: UIManager = None
current_panel = "main"  # Track which panel is shown

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    show_main_menu()
    game.add_resource(ui_manager)

def show_main_menu():
    global current_panel
    current_panel = "main"
    ui_manager.set_root(create_main_menu())

def show_options():
    global current_panel
    current_panel = "options"
    ui_manager.set_root(create_options_menu())

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()
```

## Step 2: Define Styles

Keep your styles organized:

```python
# Color palette
COLORS = {
    "bg": Color(15, 15, 25),
    "panel": Color(25, 25, 40),
    "primary": Color(100, 80, 200),
    "primary_hover": Color(120, 100, 220),
    "danger": Color(200, 60, 60),
    "text": Color(255, 255, 255),
    "text_dim": Color(150, 150, 160),
}

# Reusable button style
def button_style(color=None):
    return Style(
        width=Unit.px(220),
        height=Unit.px(50),
        background_color=color or COLORS["primary"],
        border_radius=8.0,
    )
```

## Step 3: Main Menu

```python
def create_main_menu() -> Node:
    return Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            gap=40,
            background_color=COLORS["bg"],
        ),
        children=[
            # Title
            Text("SPACE SHOOTER", size=56, color=COLORS["text"]),
            Text("The Ultimate Adventure", size=18, color=COLORS["text_dim"]),
            
            # Buttons
            Node(
                style=Style(
                    flex_direction=FlexDirection.COLUMN,
                    gap=12,
                    margin=Spacing(top=Unit.px(30)),
                ),
                children=[
                    Button("New Game", on_click=start_game, style=button_style()),
                    Button("Options", on_click=show_options, style=button_style()),
                    Button("Quit", on_click=quit_game, style=button_style(COLORS["danger"])),
                ],
            ),
            
            # Footer
            Text("v1.0.0", size=12, color=COLORS["text_dim"]),
        ],
    )

def start_game():
    print("Starting game...")

def quit_game():
    print("Quitting...")
```

## Step 4: Options Menu

```python
volume = 80  # Global volume state

def create_options_menu() -> Node:
    return Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            gap=30,
            background_color=COLORS["bg"],
        ),
        children=[
            Text("OPTIONS", size=42, color=COLORS["text"]),
            
            # Options panel
            Node(
                style=Style(
                    width=Unit.px(400),
                    background_color=COLORS["panel"],
                    padding=Spacing.all(24),
                    border_radius=12.0,
                    flex_direction=FlexDirection.COLUMN,
                    gap=20,
                ),
                children=[
                    # Volume control
                    Node(
                        style=Style(
                            flex_direction=FlexDirection.ROW,
                            justify_content=JustifyContent.SPACE_BETWEEN,
                            align_items=AlignItems.CENTER,
                        ),
                        children=[
                            Text("Volume", size=16, color=COLORS["text"]),
                            Slider(
                                value=volume,
                                min_value=0,
                                max_value=100,
                                on_change=on_volume_change,
                                style=Style(width=Unit.px(200)),
                            ),
                        ],
                    ),
                    
                    # More options here...
                ],
            ),
            
            # Back button
            Button("Back", on_click=show_main_menu, style=button_style()),
        ],
    )

def on_volume_change(value):
    global volume
    volume = value
    print(f"Volume: {value}%")
```

## Step 5: Wire It Into the Engine

Once you have `create_main_menu()` and `create_options_menu()`, hook the manager into your Arepy world:

```python
game = ArepyEngine(title="Space Shooter", width=1280, height=720)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

This tutorial is intentionally assembled from small pieces. Use it as a pattern for your own project rather than as a reference to a missing demo file.

## Using AUI Markup

You can also build this menu with markup files:

**menu.aui**
```html
<column class="screen">
    <text class="title">SPACE SHOOTER</text>
    <text class="subtitle">The Ultimate Adventure</text>
    
    <column class="buttons">
        <button class="btn" on-click="start_game">New Game</button>
        <button class="btn" on-click="show_options">Options</button>
        <button class="btn btn-danger" on-click="quit_game">Quit</button>
    </column>
    
    <text class="version">v1.0.0</text>
</column>
```

**menu.acss**
```css
:root {
    --bg: #0f0f19;
    --primary: #6450c8;
    --danger: #c83c3c;
    --text: #ffffff;
    --text-dim: #9696a0;
}

.screen {
    width: 100%;
    height: 100%;
    background: var(--bg);
    justify-content: center;
    align-items: center;
    gap: 40px;
}

.title {
    font-size: 56px;
    color: var(--text);
}

.subtitle {
    font-size: 18px;
    color: var(--text-dim);
}

.buttons {
    gap: 12px;
    margin-top: 30px;
}

.btn {
    width: 220px;
    height: 50px;
    background: var(--primary);
    border-radius: 8px;
}

.btn-danger {
    background: var(--danger);
}

.version {
    font-size: 12px;
    color: var(--text-dim);
}
```

**main.py**
```python
from arepy_ui.markup import load_aui

handlers = {
    "start_game": start_game,
    "show_options": show_options,
    "quit_game": quit_game,
}

def show_main_menu():
    result = load_aui("menu.aui", handlers=handlers)
    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
```

## Tips

!!! tip "Organize Styles"
    Keep colors and styles in variables/dictionaries for easy theming.

!!! tip "Use Functions for Panels"
    Create a function for each screen (main menu, options, etc.) and call `set_root()` to switch.

!!! tip "Test with Debugger"
    Press F3 to enable the UI debugger and inspect your layout.

## Next Steps

- [Creating an Inventory](inventory.md) - Build a drag & drop inventory
- [Theme Switching](theming.md) - Add light/dark mode
