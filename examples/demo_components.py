from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline
from arepy.ecs.world import World

from arepy_ui import (
    AlignItems,
    Button,
    Checkbox,
    Color,
    FlexDirection,
    JustifyContent,
    Node,
    ResizeMode,
    ScrollView,
    Select,
    Slider,
    Spacing,
    Style,
    Tabs,
    Text,
    TextInput,
    UIConfig,
    UIManager,
    Unit,
)
from arepy_ui.components import (
    Divider,
    DividerOrientation,
    ListItem,
    ListView,
    ProgressBar,
    RadioGroup,
    RadioOption,
    TextArea,
    Toggle,
)
from typing import Any, Dict

from arepy_ui.debug import UIDebugger

# Estado global
app_state: Dict[str, Any] = {
    "toggle_dark_mode": True,
    "radio_size": "M",
    "progress": 35.0,
    "selected_items": [],
    "code": "def hello():\n    print('Hello World!')\n\nhello()",
}

ui_manager: UIManager = None  # type: ignore
ui_debugger: UIDebugger = None  # type: ignore
progress_bar: ProgressBar = None  # type: ignore
progress_label: Text = None  # type: ignore


def create_section(title: str, children_nodes: list) -> Node:
    """Helper para crear una sección con título."""
    section = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=12,
            padding=Spacing.all(16),
            background_color=Color(40, 40, 50, 255),
            border_radius=8.0,
        )
    )

    title_text = Text(title, size=16, color=Color(180, 200, 255, 255))
    section.add_child(title_text)

    for child in children_nodes:
        section.add_child(child)

    return section


def create_ui() -> Node:
    """Crea el layout completo responsive."""
    global progress_bar, progress_label

    # Root - 100% de la ventana
    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=Color(25, 25, 35, 255),
            flex_direction=FlexDirection.COLUMN,
            padding=Spacing.all(20),
            gap=20,
        )
    )

    # Header
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.SPACE_BETWEEN,
            align_items=AlignItems.CENTER,
            padding=Spacing.symmetric(vertical=10, horizontal=20),
            background_color=Color(35, 35, 50, 255),
            border_radius=8.0,
        )
    )

    title = Text("arepy-ui Components Demo", size=24, color=Color(255, 255, 255, 255))
    header.add_child(title)

    version_badge = Node(
        style=Style(
            padding=Spacing.symmetric(vertical=4, horizontal=12),
            background_color=Color(80, 140, 220, 255),
            border_radius=12.0,
        )
    )
    version_badge.add_child(Text("v1.0", size=12, color=Color(255, 255, 255, 255)))
    header.add_child(version_badge)

    root.add_child(header)

    main_content = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.vh(80),
            flex_direction=FlexDirection.ROW,
            gap=20,
        )
    )

    # ====== COLUMNA IZQUIERDA ======
    left_column = Node(
        style=Style(
            width=Unit.percent(50),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            gap=16,
        )
    )

    left_scroll_content = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=16,
        )
    )

    toggle = Toggle(
        checked=bool(app_state["toggle_dark_mode"]),
        label="Dark Mode",
        on_change=lambda v: print(f"Dark mode: {v}"),
    )
    left_scroll_content.add_child(create_section("Toggle / Switch", [toggle]))

    radio_options = [
        RadioOption("Small (S)", "S"),
        RadioOption("Medium (M)", "M"),
        RadioOption("Large (L)", "L"),
        RadioOption("Extra Large (XL)", "XL"),
    ]
    radio_group = RadioGroup(
        options=radio_options,
        selected_value=app_state["radio_size"],
        direction=FlexDirection.ROW,
        gap=20,
        on_change=lambda v: print(f"Size: {v}"),
    )
    left_scroll_content.add_child(create_section("Radio Group", [radio_group]))

    progress_container = Node(
        style=Style(
            width=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            gap=12,
        )
    )

    progress_bar = ProgressBar(
        value=float(app_state["progress"]),
        width=Unit.percent(100),
        height=Unit.px(12),
        show_label=True,
    )
    progress_container.add_child(progress_bar)

    loading_label = Text("Loading...", size=12, color=Color(150, 150, 160, 255))
    progress_container.add_child(loading_label)
    loading_bar = ProgressBar(
        width=Unit.percent(100),
        height=Unit.px(6),
        indeterminate=True,
    )
    progress_container.add_child(loading_bar)

    progress_buttons = Node(
        style=Style(
            flex_direction=FlexDirection.ROW,
            gap=10,
        )
    )

    def decrease_progress():
        app_state["progress"] = max(0, float(app_state["progress"]) - 10)
        progress_bar.value = float(app_state["progress"])

    def increase_progress():
        app_state["progress"] = min(100, float(app_state["progress"]) + 10)
        progress_bar.value = float(app_state["progress"])

    progress_buttons.add_child(
        Button(
            text="-10%",
            on_click=decrease_progress,
            width=Unit.px(70),
            height=Unit.px(32),
            bg_color=Color(180, 80, 80, 255),
        )
    )
    progress_buttons.add_child(
        Button(
            text="+10%",
            on_click=increase_progress,
            width=Unit.px(70),
            height=Unit.px(32),
            bg_color=Color(80, 180, 80, 255),
        )
    )
    progress_container.add_child(progress_buttons)

    left_scroll_content.add_child(create_section("Progress Bar", [progress_container]))

    # --- Sección Divider ---
    divider_demo = Node(
        style=Style(
            width=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            gap=16,
        )
    )

    divider_demo.add_child(
        Text("Simple divider:", size=12, color=Color(150, 150, 160, 255))
    )
    divider_demo.add_child(Divider())

    divider_demo.add_child(
        Text("Divider with label:", size=12, color=Color(150, 150, 160, 255))
    )
    divider_demo.add_child(Divider(label="OR", label_position="center"))

    row_with_vertical = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(60),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            justify_content=JustifyContent.CENTER,
            gap=20,
        )
    )
    row_with_vertical.add_child(Text("Left", size=14, color=Color(200, 200, 210, 255)))
    row_with_vertical.add_child(
        Divider(
            orientation=DividerOrientation.VERTICAL,
            height=Unit.px(40),
        )
    )
    row_with_vertical.add_child(Text("Right", size=14, color=Color(200, 200, 210, 255)))
    divider_demo.add_child(row_with_vertical)

    left_scroll_content.add_child(create_section("Divider", [divider_demo]))

    inputs_demo = Node(
        style=Style(
            width=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            gap=12,
        )
    )

    inputs_demo.add_child(
        TextInput(
            placeholder="Enter your name...",
            width=Unit.percent(100),
        )
    )

    checkbox_row = Node(
        style=Style(
            flex_direction=FlexDirection.ROW,
            gap=10,
            align_items=AlignItems.CENTER,
        )
    )
    checkbox_row.add_child(Checkbox(checked=False))
    checkbox_row.add_child(
        Text("Accept terms and conditions", size=14, color=Color(200, 200, 210, 255))
    )
    inputs_demo.add_child(checkbox_row)

    slider_row = Node(
        style=Style(
            width=Unit.percent(100),
            flex_direction=FlexDirection.ROW,
            gap=10,
            align_items=AlignItems.CENTER,
        )
    )
    slider_row.add_child(Text("Volume:", size=14, color=Color(200, 200, 210, 255)))
    slider_row.add_child(
        Slider(
            min_value=0,
            max_value=100,
            value=50,
            width=Unit.px(150),
        )
    )
    inputs_demo.add_child(slider_row)

    left_scroll_content.add_child(create_section("Classic Inputs", [inputs_demo]))

    left_scroll = ScrollView(
        width=Unit.percent(100),
        height=Unit.percent(100),
        content=left_scroll_content,
    )
    left_column.add_child(left_scroll)

    main_content.add_child(left_column)

    right_column = Node(
        style=Style(
            width=Unit.percent(50),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            gap=16,
        )
    )

    right_scroll_content = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=16,
        )
    )

    # --- Sección ListView ---
    list_items = [
        ListItem("Python", "python"),
        ListItem("JavaScript", "js"),
        ListItem("TypeScript", "ts"),
        ListItem("Rust", "rust"),
        ListItem("Go", "go"),
        ListItem("C++", "cpp", disabled=True),
        ListItem("Java", "java"),
        ListItem("C#", "csharp"),
    ]

    list_view = ListView(
        items=list_items,
        width=Unit.percent(100),
        height=Unit.px(180),
        multi_select=True,
        on_select=lambda vals: print(f"Selected: {vals}"),
    )
    right_scroll_content.add_child(
        create_section("ListView (multi-select)", [list_view])
    )

    textarea = TextArea(
        placeholder="Write your code here...",
        width=Unit.percent(100),
        height=Unit.px(200),
        show_line_numbers=True,
        font_size=13,
    )
    textarea.value = str(app_state["code"])
    right_scroll_content.add_child(create_section("TextArea (code editor)", [textarea]))

    tabs_demo = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
        )
    )

    tab1_content = Node(
        style=Style(
            padding=Spacing.all(16),
            background_color=Color(50, 50, 60, 255),
        )
    )
    tab1_content.add_child(
        Text("Content of Tab 1", size=14, color=Color(200, 200, 210, 255))
    )

    tab2_content = Node(
        style=Style(
            padding=Spacing.all(16),
            background_color=Color(50, 50, 60, 255),
        )
    )
    tab2_content.add_child(
        Text("Content of Tab 2", size=14, color=Color(200, 200, 210, 255))
    )

    tab3_content = Node(
        style=Style(
            padding=Spacing.all(16),
            background_color=Color(50, 50, 60, 255),
        )
    )
    tab3_content.add_child(
        Text("Content of Tab 3", size=14, color=Color(200, 200, 210, 255))
    )

    tabs = Tabs(
        tabs=[
            ("Home", tab1_content),
            ("Settings", tab2_content),
            ("About", tab3_content),
        ],
        width=Unit.percent(100),
    )
    tabs_demo.add_child(tabs)
    right_scroll_content.add_child(create_section("Tabs", [tabs_demo]))

    # --- Sección Select ---
    select_demo = Select(
        options=["Choose an option...", "Option A", "Option B", "Option C", "Option D"],
        width=Unit.percent(100),
    )
    right_scroll_content.add_child(create_section("Select / Dropdown", [select_demo]))

    right_scroll = ScrollView(
        width=Unit.percent(100),
        height=Unit.percent(100),
        content=right_scroll_content,
    )
    right_column.add_child(right_scroll)

    main_content.add_child(right_column)
    root.add_child(main_content)

    # Footer
    footer = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.CENTER,
            padding=Spacing.all(10),
        )
    )
    footer.add_child(
        Text(
            "Press F3 for debug overlay | Resize window to test responsiveness",
            size=11,
            color=Color(100, 100, 120, 255),
        )
    )
    root.add_child(footer)

    return root


def ui_update_system(renderer: Renderer2D, input: Input, display: Display):
    """Sistema UPDATE - maneja input y layout."""
    global ui_manager

    dt = renderer.get_delta_time()
    wheel_scroll = input.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel_scroll)


def ui_render_system(renderer: Renderer2D):
    """Sistema RENDER_UI - dibuja la interfaz."""
    global ui_manager, ui_debugger
    renderer.clear(Color(30, 30, 30, 255))
    ui_manager.render()
    ui_debugger.render(ui_manager.root)


def setup_system(game: ArepyEngine):
    """Sistema de configuración inicial."""
    global ui_manager, ui_debugger

    # Configurar UI responsive
    config = UIConfig(
        resize_mode=ResizeMode.RESPONSIVE,
        layout_debounce_ms=0,
    )

    ui_manager = UIManager.from_engine(game, config=config)
    ui_debugger = UIDebugger()
    root = create_ui()
    ui_manager.set_root(root)

    print("arepy-ui Components Demo")
    print("========================")
    print("- Resize the window to test responsiveness")
    print("- Use scroll on each column")
    print("- Try all the interactive components!")


def main():
    import raylib as rl

    rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE | rl.FLAG_MSAA_4X_HINT)

    game = ArepyEngine(
        title="arepy-ui Components Demo",
        width=1200,
        height=800,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore

    world: World = game.create_world("components_demo")
    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("components_demo")
    game.run()


if __name__ == "__main__":
    main()
