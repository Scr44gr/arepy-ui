# Component Demo

Interactive demo showcasing all arepy-ui components.

## Overview

This example demonstrates all available components in action.

## Run the Demo

```bash
uv run examples/demo_components.py
```

## Source Code

```python
"""Component showcase demo."""
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import (
    UIManager, Node, Text, Button, TextInput, 
    Checkbox, Slider, Select, Image, ProgressBar,
    Style, Color, Unit,
)
from arepy_ui.core.types import FlexDirection, JustifyContent, AlignItems
from arepy_ui.core.style import Spacing

ui_manager: UIManager = None

# Component states
checkbox_value = False
slider_value = 50
select_value = "option1"
text_input_value = ""
progress = 75

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    create_demo()
    game.add_resource(ui_manager)

def create_demo():
    ui_manager.set_root(
        Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                flex_direction=FlexDirection.COLUMN,
                padding=Spacing.all(20),
                gap=20,
                background_color=Color(25, 25, 35),
            ),
            children=[
                # Title
                Text("Component Showcase", size=32, color=Color(255, 255, 255)),
                
                # Button row
                section("Buttons", [
                    Button("Primary", on_click=lambda: print("Primary clicked")),
                    Button("Secondary", style=Style(background_color=Color(80, 80, 100))),
                    Button("Danger", style=Style(background_color=Color(200, 60, 60))),
                ]),
                
                # Text Input
                section("Text Input", [
                    TextInput(
                        value=text_input_value,
                        placeholder="Enter text...",
                        on_change=on_text_change,
                        style=Style(width=Unit.px(300)),
                    ),
                ]),
                
                # Checkbox
                section("Checkbox", [
                    Checkbox(
                        label="Enable feature",
                        checked=checkbox_value,
                        on_change=on_checkbox_change,
                    ),
                ]),
                
                # Slider
                section("Slider", [
                    Text(f"Value: {slider_value}", color=Color(200, 200, 200)),
                    Slider(
                        value=slider_value,
                        min_value=0,
                        max_value=100,
                        on_change=on_slider_change,
                        style=Style(width=Unit.px(200)),
                    ),
                ]),
                
                # Select
                section("Select", [
                    Select(
                        value=select_value,
                        options=[
                            ("option1", "Option 1"),
                            ("option2", "Option 2"),
                            ("option3", "Option 3"),
                        ],
                        on_change=on_select_change,
                    ),
                ]),
                
                # Progress Bar
                section("Progress Bar", [
                    ProgressBar(
                        value=progress,
                        max_value=100,
                        style=Style(width=Unit.px(300), height=Unit.px(16)),
                    ),
                ]),
            ],
        )
    )

def section(title: str, children: list) -> Node:
    return Node(
        style=Style(
            flex_direction=FlexDirection.COLUMN,
            gap=8,
        ),
        children=[
            Text(title, size=16, color=Color(150, 150, 180)),
            Node(
                style=Style(flex_direction=FlexDirection.ROW, gap=12),
                children=children,
            ),
        ],
    )

def on_text_change(value):
    global text_input_value
    text_input_value = value
    print(f"Text: {value}")

def on_checkbox_change(value):
    global checkbox_value
    checkbox_value = value
    create_demo()

def on_slider_change(value):
    global slider_value
    slider_value = int(value)
    create_demo()

def on_select_change(value):
    global select_value
    select_value = value
    print(f"Selected: {value}")

def update(game: ArepyEngine):
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()

game = ArepyEngine(title="Components Demo", width=800, height=600)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

## Components Used

| Component | Description |
|-----------|-------------|
| `Text` | Display text |
| `Button` | Clickable button |
| `TextInput` | Text entry field |
| `Checkbox` | Toggle checkbox |
| `Slider` | Value slider |
| `Select` | Dropdown select |
| `ProgressBar` | Progress indicator |

## See Also

- [Component Reference](../../reference/index.md) - All component docs
- [Drag & Drop Demo](drag-drop.md) - Drag & drop example
