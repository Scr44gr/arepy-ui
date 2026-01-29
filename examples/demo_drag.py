"""
Demo: Drag and Drop - Kanban Board
===================================
Ejemplo de sistema drag & drop con arepy-ui.
Muestra un tablero estilo Kanban donde puedes arrastrar cards entre columnas.
Las cards se reposicionan automaticamente al soltarlas en una columna.
"""

import raylib as rl
from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline
from arepy.ecs.world import World

from arepy_ui import (
    AlignItems,
    Color,
    Draggable,
    DropZone,
    FlexDirection,
    JustifyContent,
    Node,
    ResizeMode,
    Spacing,
    Style,
    Text,
    UIConfig,
    UIManager,
    Unit,
)

ui_manager: UIManager = None  # type: ignore


def create_task_card(task: dict) -> Draggable:
    """Crear una tarjeta arrastrable."""
    r, g, b = task["color"]

    card_content = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            background_color=Color(45, 45, 50, 255),
            border_radius=8.0,
            padding=Spacing.all(12),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
        )
    )

    # Color indicator
    color_bar = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(4),
            background_color=Color(r, g, b, 255),
            border_radius=2.0,
        )
    )
    card_content.add_child(color_bar)

    # Title
    card_content.add_child(
        Text(task["title"], size=14, color=Color(240, 240, 240, 255))
    )

    # Task ID
    card_content.add_child(
        Text(f"#{task['id']}", size=11, color=Color(120, 120, 130, 255))
    )

    # Crear el Draggable
    draggable = Draggable(
        content=card_content,
        data=task,
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
        ),
        drag_opacity=0.9,
        on_drag_start=lambda t=task: print(f"  -> Dragging: {t['title']}"),
        on_drag_end=lambda dropped, target, t=task: print(
            f"  <- Dropped '{t['title']}' in '{getattr(target, 'column_id', 'nowhere') if target else 'nowhere'}'"
            if dropped
            else f"  <- Returned '{t['title']}' to original position"
        ),
    )

    return draggable


def create_column(title: str, column_id: str, initial_tasks: list) -> Node:

    column = Node(
        style=Style(
            width=Unit.percent(30),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            gap=0,
        )
    )

    # Header
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(48),
            background_color=Color(35, 35, 40, 255),
            border_radius=8.0,
            padding=Spacing.symmetric(horizontal=16, vertical=0),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            justify_content=JustifyContent.SPACE_BETWEEN,
        )
    )

    header.add_child(Text(title, size=16, color=Color(255, 255, 255, 255)))
    column.add_child(header)

    drop_zone = DropZone(
        style=Style(
            width=Unit.percent(100),
            height=Unit.vh(70),
            background_color=Color(25, 25, 30, 255),
            border_radius=8.0,
            padding=Spacing.all(8),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
        ),
        on_drop=lambda drag, data, col=column_id: on_task_dropped(drag, data, col),
        on_drag_enter=lambda col=column_id: print(f"  [ENTER] {col}"),
        on_drag_leave=lambda col=column_id: print(f"  [LEAVE] {col}"),
        highlight_color=Color(40, 50, 40, 255),
        auto_adopt=True,
        data=column_id,
    )

    for task in initial_tasks:
        drop_zone.add_child(create_task_card(task))

    column.add_child(drop_zone)
    return column


def on_task_dropped(draggable, data: dict, column_id: str) -> bool:
    print(f"[DROP] Task '{data['title']}' moved to '{column_id}'")
    return True


def create_ui() -> Node:

    tasks = {
        "todo": [
            {"id": 1, "title": "Design UI mockups", "color": (100, 150, 255)},
            {"id": 2, "title": "Write documentation", "color": (255, 150, 100)},
            {"id": 3, "title": "Review pull requests", "color": (150, 255, 100)},
        ],
        "in_progress": [
            {"id": 4, "title": "Implement drag & drop", "color": (255, 200, 100)},
        ],
        "done": [
            {"id": 5, "title": "Setup project", "color": (200, 150, 255)},
            {"id": 6, "title": "Create components", "color": (100, 255, 200)},
        ],
    }

    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=Color(18, 18, 22, 255),
            flex_direction=FlexDirection.COLUMN,
            padding=Spacing.all(24),
        )
    )

    # Header
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=4,
            padding=Spacing.symmetric(vertical=16, horizontal=0),
        )
    )

    header.add_child(Text("Kanban Board", size=28, color=Color(255, 255, 255, 255)))
    header.add_child(
        Text(
            "Drag cards between columns - they will automatically reposition",
            size=14,
            color=Color(120, 120, 130, 255),
        )
    )
    root.add_child(header)

    # Columns container
    columns = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.vh(78),
            flex_direction=FlexDirection.ROW,
            gap=24,
            padding=Spacing.symmetric(vertical=16, horizontal=0),
        )
    )

    columns.add_child(create_column("To Do", "todo", tasks["todo"]))
    columns.add_child(create_column("In Progress", "in_progress", tasks["in_progress"]))
    columns.add_child(create_column("Done", "done", tasks["done"]))

    root.add_child(columns)

    return root


def ui_update_system(renderer: Renderer2D, input: Input, display: Display):
    global ui_manager
    dt = renderer.get_delta_time()
    wheel = input.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel)


def ui_render_system(renderer: Renderer2D):
    global ui_manager
    ui_manager.render()


def setup_system(game: ArepyEngine):
    global ui_manager

    ui_manager = UIManager.from_engine(
        game, config=UIConfig(resize_mode=ResizeMode.RESPONSIVE)
    )

    root = create_ui()
    ui_manager.set_root(root)


def main():
    rl.SetConfigFlags(rl.FLAG_MSAA_4X_HINT | rl.FLAG_WINDOW_RESIZABLE)

    game = ArepyEngine(
        title="arepy-ui Drag & Drop Demo",
        width=1200,
        height=700,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore

    world: World = game.create_world("drag_demo")
    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("drag_demo")
    game.run()


if __name__ == "__main__":
    main()
