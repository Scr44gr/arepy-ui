

from arepy import ArepyEngine
from typing import Any, Dict

from arepy import Display, Input, Renderer2D, SystemPipeline
from arepy.ecs.world import World

from arepy_ui import (
    AlignItems,
    Button,
    Canvas,
    Checkbox,
    Color,
    FlexDirection,
    Image,
    ImageFit,
    JustifyContent,
    Node,
    PositionType,
    ResizeMode,
    Slider,
    Spacing,
    Style,
    Text,
    TextInput,
    UIConfig,
    UIManager,
    Unit,
)
from arepy_ui.debug import UIDebugger

# Estado global de la aplicación
app_state: Dict[str, Any] = {
    "counter": 0,
    "checkbox_value": False,
    "input_text": "",
    "slider_value": 50.0,
    "canvas_color": (100, 150, 200),
}

# UIManager global
ui_manager: UIManager = None  # type: ignore
counter_label: Text = None  # type: ignore
fps_text: Text = None  # type: ignore
size_text: Text = None  # type: ignore
slider_label: Text = None  # type: ignore
ui_debugger: UIDebugger = None  # type: ignore


def on_window_resize(width: int, height: int):
    """Callback cuando la ventana cambia de tamaño."""
    global size_text
    print(f"Window resized to: {width}x{height}")
    if size_text:
        size_text.text = f"{width}x{height}"


def create_ui() -> Node:
    """Crea y retorna el layout completo de la UI."""
    global counter_label, fps_text, size_text

    # Nodo raíz - ocupa toda la pantalla
    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=Color(30, 30, 40, 255),
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            padding=Spacing.all(20),
        )
    )

    # Panel central con bordes redondeados
    main_panel = Node(
        style=Style(
            width=Unit.px(400),
            height=Unit.auto(),
            background_color=Color(50, 50, 65, 255),
            border_radius=16.0,
            padding=Spacing.all(30),
            flex_direction=FlexDirection.COLUMN,
            gap=20,
            align_items=AlignItems.CENTER,
        )
    )

    # Título
    title = Text(
        "Arepy-UI Demo",
        size=28,
        color=Color(255, 255, 255, 255),
    )
    main_panel.add_child(title)

    # Avatar/Imagen circular con border_radius
    avatar = Image(
        source="examples/satoru.jpg",
        width=Unit.px(80),
        height=Unit.px(80),
        fit=ImageFit.COVER,  # type: ignore
        border_radius=40.0,  # 50% = circular
    )
    main_panel.add_child(avatar)

    # Subtítulo
    subtitle = Text(
        "Ejemplo de componentes y layout con arepy-ui",
        size=14,
        color=Color(180, 180, 200, 255),
    )
    main_panel.add_child(subtitle)

    # Separador visual
    separator = Node(
        style=Style(
            width=Unit.percent(80),
            height=Unit.px(2),
            background_color=Color(80, 80, 100, 255),
            border_radius=1.0,
        )
    )
    main_panel.add_child(separator)

    # ========================================
    # Sección: Contador
    # ========================================
    counter_section = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=10,
            align_items=AlignItems.CENTER,
        )
    )

    counter_label = Text(
        "Contador: 0",
        size=20,
        color=Color(255, 255, 255, 255),
    )
    counter_section.add_child(counter_label)

    # Fila de botones
    button_row = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=15,
        )
    )

    def on_decrement():
        app_state["counter"] = int(app_state["counter"]) - 1
        counter_label.text = f"Contador: {app_state['counter']}"

    def on_increment():
        app_state["counter"] = int(app_state["counter"]) + 1
        counter_label.text = f"Contador: {app_state['counter']}"

    btn_minus = Button(
        text="-",
        on_click=on_decrement,
        width=Unit.px(50),
        height=Unit.px(40),
        bg_color=Color(200, 80, 80, 255),
        font_size=18,
    )
    button_row.add_child(btn_minus)

    btn_plus = Button(
        text="+",
        on_click=on_increment,
        width=Unit.px(50),
        height=Unit.px(40),
        bg_color=Color(80, 180, 80, 255),
        font_size=18,
    )
    button_row.add_child(btn_plus)

    counter_section.add_child(button_row)
    main_panel.add_child(counter_section)

    # ========================================
    # Sección: Checkbox
    # ========================================
    checkbox_section = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=10,
            align_items=AlignItems.CENTER,
            justify_content=JustifyContent.CENTER,
        )
    )

    def on_checkbox_change(value: bool):
        app_state["checkbox_value"] = value
        print(f"Checkbox: {value}")

    checkbox = Checkbox(
        checked=bool(app_state["checkbox_value"]),
        on_change=on_checkbox_change,
        size=24,
    )
    checkbox_section.add_child(checkbox)

    checkbox_label = Text(
        "Habilitar notificaciones",
        size=14,
        color=Color(200, 200, 220, 255),
    )
    checkbox_section.add_child(checkbox_label)

    main_panel.add_child(checkbox_section)

    # ========================================
    # Sección: Input de texto
    # ========================================
    input_section = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
            align_items=AlignItems.CENTER,
        )
    )

    input_label = Text(
        "Tu nombre:",
        size=14,
        color=Color(180, 180, 200, 255),
    )
    input_section.add_child(input_label)

    def on_text_change(new_text: str):
        app_state["input_text"] = new_text

    text_input = TextInput(
        placeholder="Escribe aquí...",
        on_change=on_text_change,
        width=Unit.px(280),
        height=Unit.px(36),
    )
    input_section.add_child(text_input)

    main_panel.add_child(input_section)

    # ========================================
    # Sección: Slider
    # ========================================
    slider_section = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
            align_items=AlignItems.CENTER,
        )
    )

    slider_label = Text(
        f"Volumen: {int(float(app_state['slider_value']))}%",
        size=14,
        color=Color(180, 180, 200, 255),
    )
    slider_section.add_child(slider_label)

    def on_slider_change(value: float):
        app_state["slider_value"] = value
        if slider_label:
            slider_label.text = f"Volumen: {int(value)}%"

    volume_slider = Slider(
        min_value=0,
        max_value=100,
        value=float(app_state["slider_value"]),
        on_change=on_slider_change,
        width=Unit.px(280),
        height=Unit.px(24),
        track_color=Color(60, 60, 80, 255),
        fill_color=Color(70, 130, 220, 255),
        thumb_color=Color(255, 255, 255, 255),
    )
    slider_section.add_child(volume_slider)

    main_panel.add_child(slider_section)

    # ========================================
    # Sección: Canvas (Custom Rendering)
    # ========================================
    canvas_section = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
            align_items=AlignItems.CENTER,
        )
    )

    canvas_title = Text(
        "Canvas Demo",
        size=14,
        color=Color(180, 180, 200, 255),
    )
    canvas_section.add_child(canvas_title)

    def on_canvas_render(renderer, rect, state):
        """Custom canvas rendering - dibuja círculos animados."""
        import math

        from arepy import Color as AColor
        from arepy.engine.renderer import Rect as ArepyRect

        time = state.get("time", 0)
        cx, cy = rect.x + rect.width / 2, rect.y + rect.height / 2

        # Dibujar fondo
        bg_rect = ArepyRect(int(rect.x), int(rect.y), int(rect.width), int(rect.height))
        renderer.draw_rectangle(bg_rect, AColor(40, 40, 55, 255))

        # Dibujar círculos orbitando
        for i in range(5):
            angle = time * 2 + (i * math.pi * 2 / 5)
            radius = 30
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            color = AColor(
                int(127 + 127 * math.sin(time + i)),
                int(127 + 127 * math.cos(time + i * 0.5)),
                200,
                255,
            )
            renderer.draw_circle((int(x), int(y)), 8, color)

        # Actualizar tiempo
        state["time"] = time + 0.016

    custom_canvas = Canvas(
        on_render=on_canvas_render,
        width=Unit.px(280),
        height=Unit.px(80),
        state={"time": 0},
    )
    canvas_section.add_child(custom_canvas)

    main_panel.add_child(canvas_section)

    # ========================================
    # Botón de acción principal
    # ========================================
    def on_submit():
        name = app_state["input_text"] or "Anónimo"
        print(f"¡Hola, {name}! Contador: {app_state['counter']}")

    submit_btn = Button(
        text="Enviar",
        on_click=on_submit,
        width=Unit.px(200),
        height=Unit.px(45),
        bg_color=Color(70, 130, 220, 255),
        font_size=16,
    )
    main_panel.add_child(submit_btn)

    # ========================================
    # Botón para abrir Modal
    # ========================================
    def create_modal_content():
        """Crea el contenido del modal."""
        modal_panel = Node(
            style=Style(
                width=Unit.px(350),
                height=Unit.auto(),
                background_color=Color(60, 60, 80, 255),
                border_radius=12.0,
                padding=Spacing.all(25),
                flex_direction=FlexDirection.COLUMN,
                gap=15,
                align_items=AlignItems.CENTER,
            )
        )

        modal_title = Text(
            "¡Modal de Ejemplo!",
            size=22,
            color=Color(255, 255, 255, 255),
        )
        modal_panel.add_child(modal_title)

        modal_text = Text(
            "Este es un modal creado con el sistema de modales.\nPuedes cerrarlo con el botón o haciendo clic fuera.",
            size=14,
            color=Color(200, 200, 220, 255),
        )
        modal_panel.add_child(modal_text)

        def close_modal():
            if ui_manager:
                ui_manager.close_modal(modal_panel)

        close_btn = Button(
            text="Cerrar",
            on_click=close_modal,
            width=Unit.px(120),
            height=Unit.px(40),
            bg_color=Color(180, 80, 80, 255),
            font_size=14,
        )
        modal_panel.add_child(close_btn)

        return modal_panel

    def on_show_modal():
        if ui_manager:
            modal = create_modal_content()
            ui_manager.show_modal(modal, backdrop=True)

    modal_btn = Button(
        text="Abrir Modal",
        on_click=on_show_modal,
        width=Unit.px(200),
        height=Unit.px(40),
        bg_color=Color(150, 100, 180, 255),
        font_size=14,
    )
    main_panel.add_child(modal_btn)

    # Añadir panel al root
    root.add_child(main_panel)

    # ========================================
    # HUD en esquina (posición absoluta)
    # ========================================
    hud_container = Node(
        style=Style(
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(10),
            flex_direction=FlexDirection.COLUMN,
            gap=5,
            align_items=AlignItems.START,
        )
    )

    # FPS
    hud_fps = Node(
        style=Style(
            background_color=Color(0, 0, 0, 150),
            padding=Spacing.symmetric(5, 10),
            border_radius=4.0,
        )
    )
    fps_text = Text("FPS: 60", size=12, color=Color(100, 255, 100, 255))
    hud_fps.add_child(fps_text)
    hud_container.add_child(hud_fps)

    # Window Size
    hud_size = Node(
        style=Style(
            background_color=Color(0, 0, 0, 150),
            padding=Spacing.symmetric(5, 10),
            border_radius=4.0,
        )
    )
    size_text = Text("800x600", size=12, color=Color(100, 200, 255, 255))
    hud_size.add_child(size_text)
    hud_container.add_child(hud_size)

    root.add_child(hud_container)

    return root


def ui_update_system(renderer: Renderer2D, input: Input, display: Display):
    """Sistema de UPDATE para la UI - maneja input y layout."""
    global ui_manager, fps_text, ui_debugger

    dt = renderer.get_delta_time()

    # Toggle debug con F12
    from arepy.engine.input import Key

    if input.is_key_pressed(Key.F3):
        ui_debugger.toggle()
        print(f"Debug: {'ON' if ui_debugger.enabled else 'OFF'}")

    # Actualizar UI (maneja input y layout)
    wheel_scroll = input.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel_scroll)


def ui_render_system():
    global ui_manager, ui_debugger

    # Renderizar UI
    ui_manager.render()

    # Renderizar debug overlay (si está habilitado)
    ui_debugger.render(ui_manager.root)


def setup_system(game: ArepyEngine):
    global ui_manager, ui_debugger

    config = UIConfig(
        resize_mode=ResizeMode.RESPONSIVE,
        on_resize=on_window_resize,
        layout_debounce_ms=0,
    )

    ui_manager = UIManager.from_engine(game, config=config)
    root = create_ui()
    ui_manager.set_root(root)

    width, height = game.display.get_window_size()
    on_window_resize(width, height)

    ui_debugger = UIDebugger()


def main():
    global ui_manager

    game = ArepyEngine(
        title="Arepy-UI Demo",
        width=800,
        height=600,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore
    world: World = game.create_world("ui_demo")

    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("ui_demo")
    game.run()


if __name__ == "__main__":
    main()
