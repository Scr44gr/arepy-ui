<p align="center">
  <img src="assets/arepy-ui-hero-logo.png" alt="arepy-ui" width="400">
</p>

<p align="center">
    <em>Modern, fast, declarative UI library for the Arepy game engine.</em>
</p>

---

UI library for [Arepy](https://github.com/Scr44gr/arepy) game engine. Build game interfaces with a flexbox-based layout system.

## Features

- :material-view-grid: **Flexbox Layout** - Familiar CSS-like layout system
- :material-puzzle: **Component Library** - Ready-to-use UI components
- :material-file-document: **Declarative Markup** - HTML-like `.aui` and CSS-like `.acss` files
- :material-palette: **Theme Support** - CSS variables with light/dark variants
- :material-cursor-move: **Drag & Drop** - Built-in drag and drop support
- :material-animation: **Animations** - Sequenced animator and timers with easing functions
- :material-text: **Custom Fonts** - TTF/OTF font support
- :material-monitor: **Responsive** - Multiple resize modes

## Quick Example

=== "Python"

    ```python
    from arepy import ArepyEngine, Renderer2D, SystemPipeline

    from arepy_ui import (
        AlignItems,
        Button,
        JustifyContent,
        Node,
        Style,
        Text,
        UIConfig,
        UIManager,
        Unit,
    )


    def setup(game: ArepyEngine):
        ui_manager = UIManager.from_engine(game, config=UIConfig())
        ui_manager.set_root(
            Node(
                style=Style(
                    width=Unit.percent(100),
                    height=Unit.percent(100),
                    align_items=AlignItems.CENTER,
                    justify_content=JustifyContent.CENTER,
                ),
                children=[
                    Text("Hello!", size=24),
                    Button("Click me", on_click=lambda: print("Clicked!")),
                ],
            )
        )
        game.add_resource(ui_manager)


    def update(ui_manager: UIManager, renderer: Renderer2D):
        ui_manager.update(renderer.get_delta_time())


    def render(ui_manager: UIManager):
        ui_manager.render()


    if __name__ == "__main__":
        game = ArepyEngine(title="My Game", width=800, height=600)
        setup(game)

        world = game.create_world("main")
        world.add_system(SystemPipeline.UPDATE, update)
        world.add_system(SystemPipeline.RENDER_UI, render)
        game.set_current_world("main")
        game.run()
    ```

=== "AUI Markup"

    **ui.aui**
    ```html
        <column class="main">
            <text class="title">Hello!</text>
            <button on-click="greet">Click me</button>
        </column>
    ```
    **ui.acss**
    ```css
        .main {
            width: 100%;
            height: 100%;
            justify-content: center;
            align-items: center;
            gap: 20px;
        }

        .title { font-size: 24px; }
    ```

    **main.py**
    ```python
    from arepy_ui.markup import load_aui

    handlers = {"greet": lambda: print("Clicked!")}
    result = load_aui("ui.aui", handlers=handlers)

    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
    else:
        for error in result.errors:
            print(error)
    ```

## Components

| Component | Description |
|-----------|-------------|
| [`Text`](reference/components/text.md) | Text rendering with custom fonts |
| [`Button`](reference/components/button.md) | Clickable button with hover states |
| [`TextInput`](reference/components/textinput.md) | Text field with cursor and selection |
| [`Checkbox`](reference/components/checkbox.md) | Toggle with label |
| [`Slider`](reference/components/slider.md) | Horizontal or vertical value slider |
| [`Select`](reference/components/select.md) | Dropdown menu |
| [`Tabs`](reference/components/tabs.md) | Tabbed container |
| [`Image`](reference/components/image.md) | Texture display with fit modes |
| [`ScrollView`](reference/components/scrollview.md) | Scrollable container |
| [`ProgressBar`](reference/components/progressbar.md) | Progress indicator |
| [`Canvas`](reference/components/canvas.md) | Custom drawing |
| [`Video`](reference/components/video.md) | Video playback |
| [`ColorPicker`](reference/components/colorpicker.md) | HSV color selection |

## Layout System

Flexbox-based layout with familiar CSS properties:

```python
Node(
    style=Style(
        flex_direction=FlexDirection.ROW,
        justify_content=JustifyContent.CENTER,
        align_items=AlignItems.CENTER,
        gap=10,
        padding=Spacing.all(20),
    ),
    children=[...]
)
```

## Theme Support

Define themes with CSS variables:

```css
:root {
    --bg: #1a1a2e;
    --accent: #6c5ce7;
}

:root.light {
    --bg: #ffffff;
    --accent: #5849c2;
}
```

Switch at runtime:

```python
from arepy_ui.markup import set_theme
set_theme("light")
```

Theme variants can be switched at runtime with `set_theme(...)` after loading global styles.

## UI Debugger

Built-in visual debugger for inspecting layouts (press F3):

| Key | Action |
|-----|--------|
| `F3` | Toggle debugger |
| `F4` | Toggle component bounds |
| `F5` | Toggle padding visualization |
| `F6` | Toggle component tree |

[:octicons-arrow-right-24: Debugger Documentation](resources/tools/debugger.md)

## Examples

Examples available in the repository:

- `uv run examples/demo_components.py`
- `uv run examples/demo_drag.py`
- `uv run examples/colorpicker_demo.py`
- `uv run examples/demo_video.py`

```bash
uv run examples/demo_components.py
uv run examples/demo_drag.py
uv run examples/colorpicker_demo.py
```

## Getting Started

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install arepy-ui with pip

    [:octicons-arrow-right-24: Installation](learn/getting-started.md)

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Build your first UI in 5 minutes

    [:octicons-arrow-right-24: Quick Start](learn/getting-started.md)

-   :material-puzzle:{ .lg .middle } **Components**

    ---

    Explore available UI components

    [:octicons-arrow-right-24: Components](reference/components/index.md)

-   :material-file-document:{ .lg .middle } **AUI Markup**

    ---

    Declarative UI with markup files

    [:octicons-arrow-right-24: AUI Markup](reference/markup/index.md)

</div>
