"""
ColorPicker Demo - Demonstrates the ColorPicker component.

Features shown:
- Basic color picker with hue/saturation/value
- Alpha channel support
- Color preview with hex value
- Callback on color change
"""

import raylib as rl
from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline
from arepy.ecs.world import World
from arepy.engine.renderer import Color as ArepyColor

from arepy_ui import ResizeMode, UIConfig, UIManager
from arepy_ui.components import (
    AlignItems,
    Color,
    ColorPicker,
    FlexDirection,
    Node,
    Spacing,
    Style,
    Text,
    Unit,
)

# Global state
ui_manager: UIManager = None  # type: ignore
preview_box: Node = None  # type: ignore
color_text: Text = None  # type: ignore


def on_color_change(color: Color):
    """Update the preview when color changes."""
    global preview_box, color_text

    # Update the text
    hex_val = f"#{color.r:02X}{color.g:02X}{color.b:02X}"
    if color.a < 255:
        hex_val += f"{color.a:02X}"
    color_text.text = f"Selected: {hex_val}"

    # Update preview box
    preview_box.style.background_color = color


def create_ui() -> Node:
    """Create the demo UI."""
    global preview_box, color_text

    color_text = Text(
        "Selected: #FF0000", size=14, color=Color(255, 255, 255, 255), id="color-text"
    )

    preview_box = Node(
        id="preview-box",
        style=Style(
            width=Unit.px(100),
            height=Unit.px(100),
            background_color=Color(255, 0, 0, 255),
            border_radius=8.0,
        ),
    )

    picker = ColorPicker(
        color=Color(255, 0, 0, 255),
        width=Unit.px(280),
        height=Unit.px(220),
        show_alpha=True,
        show_preview=True,
        on_change=on_color_change,
        id="picker",
    )

    picker_no_alpha = ColorPicker(
        color=Color(0, 150, 255, 255),
        width=Unit.px(200),
        height=Unit.px(180),
        show_alpha=False,
        show_preview=True,
        id="picker-no-alpha",
    )

    return Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            background_color=Color(30, 30, 35, 255),
            padding=Spacing.all(20),
            flex_direction=FlexDirection.COLUMN,
            gap=20.0,
        ),
        children=[
            Text(
                "ColorPicker Demo",
                size=24,
                color=Color(255, 255, 255, 255),
            ),
            # Main content row
            Node(
                style=Style(
                    flex_direction=FlexDirection.ROW,
                    gap=40.0,
                    align_items=AlignItems.START,
                ),
                children=[
                    # Left: Full picker with alpha
                    Node(
                        style=Style(
                            flex_direction=FlexDirection.COLUMN,
                            gap=10.0,
                        ),
                        children=[
                            Text(
                                "With Alpha Channel",
                                size=14,
                                color=Color(180, 180, 180, 255),
                            ),
                            picker,
                        ],
                    ),
                    # Center: Preview area
                    Node(
                        style=Style(
                            flex_direction=FlexDirection.COLUMN,
                            gap=10.0,
                            align_items=AlignItems.CENTER,
                        ),
                        children=[
                            Text(
                                "Live Preview",
                                size=14,
                                color=Color(180, 180, 180, 255),
                            ),
                            preview_box,
                            color_text,
                        ],
                    ),
                    # Right: Picker without alpha
                    Node(
                        style=Style(
                            flex_direction=FlexDirection.COLUMN,
                            gap=10.0,
                        ),
                        children=[
                            Text(
                                "Without Alpha",
                                size=14,
                                color=Color(180, 180, 180, 255),
                            ),
                            picker_no_alpha,
                        ],
                    ),
                ],
            ),
            # Instructions
            Node(
                style=Style(
                    flex_direction=FlexDirection.COLUMN,
                    gap=5.0,
                    padding=Spacing.symmetric(10, 0),
                ),
                children=[
                    Text(
                        "Instructions:",
                        size=14,
                        color=Color(150, 150, 150, 255),
                    ),
                    Text(
                        "• Drag in the large square to select saturation (X) and brightness (Y)",
                        size=12,
                        color=Color(120, 120, 120, 255),
                    ),
                    Text(
                        "• Drag the narrow bar to select hue",
                        size=12,
                        color=Color(120, 120, 120, 255),
                    ),
                    Text(
                        "• Drag the rightmost bar to adjust alpha (transparency)",
                        size=12,
                        color=Color(120, 120, 120, 255),
                    ),
                ],
            ),
        ],
    )


def ui_update_system(renderer: Renderer2D, input: Input, display: Display):
    """UPDATE system - handles input and layout."""
    global ui_manager
    dt = renderer.get_delta_time()
    wheel_scroll = input.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel_scroll)


def ui_render_system(renderer: Renderer2D):
    """RENDER system - draws the UI."""
    global ui_manager
    renderer.clear(ArepyColor(30, 30, 35, 255))
    ui_manager.render()


def setup_system(game: ArepyEngine):
    """Initial setup system."""
    global ui_manager

    config = UIConfig(
        resize_mode=ResizeMode.RESPONSIVE,
        layout_debounce_ms=0,
    )

    ui_manager = UIManager.from_engine(game, config=config)
    ui_manager.set_root(create_ui())

    print("ColorPicker Demo")
    print("================")
    print("- Drag to select colors")
    print("- Left picker has alpha, right one doesn't")


def main():
    rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE | rl.FLAG_MSAA_4X_HINT)

    game = ArepyEngine(
        title="ColorPicker Demo",
        width=800,
        height=600,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore

    world: World = game.create_world("colorpicker_demo")
    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("colorpicker_demo")
    game.run()


if __name__ == "__main__":
    main()
