"""
Demo de Animaciones con arepy-ui.

Este ejemplo demuestra:
- Diferentes tipos de easing (Linear, Quad, Cubic, Bounce, Elastic, etc.)
- Animación de propiedades (opacity, position, size, color)
- Animaciones encadenadas
- Control de animaciones (play, reset)
"""

import raylib as rl
from arepy import ArepyEngine

from arepy_ui import (
    AlignItems,
    Button,
    Color,
    Easing,
    FlexDirection,
    JustifyContent,
    Node,
    Spacing,
    Style,
    Text,
    UIManager,
    Unit,
)

# Estado global
ui_manager: UIManager = None  # type: ignore

# Nodos animables
animated_boxes: list[Node] = []


def create_animated_box(color: Color, label: str) -> tuple[Node, Node]:
    """Crea una caja animable con etiqueta."""
    container = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(50),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=10,
        )
    )

    # Etiqueta del easing
    label_text = Text(label, size=10, color=Color(200, 200, 200, 255))
    label_text.style.width = Unit.px(100)
    container.add_child(label_text)

    # Caja animable
    box = Node(
        style=Style(
            width=Unit.px(40),
            height=Unit.px(40),
            background_color=color,
            border_radius=8.0,
        )
    )
    container.add_child(box)

    return container, box


def run_all_animations():
    """Ejecuta todas las animaciones de demostración."""
    global animated_boxes, ui_manager

    # Limpiar animaciones previas
    ui_manager.animator.clear()

    easings = [
        Easing.LINEAR,
        Easing.EASE_IN_QUAD,
        Easing.EASE_OUT_QUAD,
        Easing.EASE_IN_OUT_QUAD,
        Easing.EASE_IN_CUBIC,
        Easing.EASE_OUT_CUBIC,
        Easing.EASE_OUT_BOUNCE,
        Easing.EASE_OUT_BACK,
        Easing.EASE_OUT_EXPO,
    ]

    # Resetear primero
    for box in animated_boxes:
        box.style.margin = Spacing(
            top=Unit.px(0),
            right=Unit.px(0),
            bottom=Unit.px(0),
            left=Unit.px(0),
        )

    for i, box in enumerate(animated_boxes):
        if i < len(easings):
            delay = i * 0.05
            ui_manager.animator.create().wait(delay).to(
                box.style,
                "margin.left",
                300,
                2.0,
                easings[i],
            ).start()
            ui_manager.animator.create().wait(delay).to(
                box.style,
                "opacity",
                0.55,
                0.16,
                Easing.EASE_OUT_QUAD,
            ).to(
                box.style,
                "opacity",
                1.0,
                0.20,
                Easing.EASE_OUT_QUAD,
            ).start()


def reset_animations():
    """Resetea todas las cajas a su posición inicial."""
    global animated_boxes, ui_manager

    # Limpiar animaciones activas
    ui_manager.animator.clear()

    # Resetear posiciones (usar Unit.px para crear el objeto correcto)
    for box in animated_boxes:
        box.style.margin = Spacing(
            top=Unit.px(0),
            right=Unit.px(0),
            bottom=Unit.px(0),
            left=Unit.px(0),
        )
        box.style.opacity = 1.0


def create_ui() -> Node:
    """Crea la interfaz de demostración de animaciones."""
    global animated_boxes

    # Root
    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=Color(25, 25, 35, 255),
            flex_direction=FlexDirection.COLUMN,
            padding=Spacing.all(20),
            gap=10,
        )
    )

    # Título
    title = Text(
        "Animation Easing Demo",
        size=24,
        color=Color(255, 255, 255, 255),
    )
    root.add_child(title)

    subtitle = Text(
        "Compara diferentes funciones de easing",
        size=12,
        color=Color(150, 150, 170, 255),
    )
    root.add_child(subtitle)

    # Separador
    separator = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(1),
            background_color=Color(60, 60, 80, 255),
        )
    )
    root.add_child(separator)

    # Contenedor de animaciones
    anim_container = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=5,
            padding=Spacing.symmetric(10, 0),
        )
    )

    # Crear cajas para cada tipo de easing
    easing_data = [
        ("LINEAR", Color(100, 200, 255, 255)),
        ("EASE_IN_QUAD", Color(255, 100, 100, 255)),
        ("EASE_OUT_QUAD", Color(100, 255, 100, 255)),
        ("EASE_IN_OUT_QUAD", Color(255, 255, 100, 255)),
        ("EASE_IN_CUBIC", Color(255, 150, 50, 255)),
        ("EASE_OUT_CUBIC", Color(150, 100, 255, 255)),
        ("EASE_OUT_BOUNCE", Color(255, 100, 200, 255)),
        ("EASE_OUT_BACK", Color(100, 255, 200, 255)),
        ("EASE_OUT_EXPO", Color(200, 200, 100, 255)),
    ]

    animated_boxes.clear()
    for label, color in easing_data:
        container, box = create_animated_box(color, label)
        anim_container.add_child(container)
        animated_boxes.append(box)

    root.add_child(anim_container)

    # Separador
    separator2 = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(1),
            background_color=Color(60, 60, 80, 255),
        )
    )
    root.add_child(separator2)

    # Botones de control
    button_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=15,
            justify_content=JustifyContent.CENTER,
            padding=Spacing.symmetric(15, 0),
        )
    )

    play_btn = Button(
        text="Play",
        on_click=run_all_animations,
        width=Unit.px(120),
        height=Unit.px(45),
        bg_color=Color(80, 180, 80, 255),
        font_size=14,
    )
    button_row.add_child(play_btn)

    reset_btn = Button(
        text="Reset",
        on_click=reset_animations,
        width=Unit.px(120),
        height=Unit.px(45),
        bg_color=Color(180, 80, 80, 255),
        font_size=14,
    )
    button_row.add_child(reset_btn)

    root.add_child(button_row)

    # Instrucciones
    instructions = Text(
        "Presiona Play para ver las animaciones, Reset para reiniciar",
        size=10,
        color=Color(120, 120, 140, 255),
    )
    instructions.style.margin = Spacing.symmetric(10, 0)
    root.add_child(instructions)

    return root


def main():
    # Ventana resizable
    rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE)

    game = ArepyEngine(
        title="Arepy-UI Animation Demo",
        width=800,
        height=700,
    )

    world = game.create_world("animation_demo")

    global ui_manager
    ui_manager = UIManager.install(world, root=create_ui())

    game.set_current_world("animation_demo")
    game.run()


if __name__ == "__main__":
    main()
