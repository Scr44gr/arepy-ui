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


def create_item(item: dict) -> Draggable:
    """Crear un item arrastrable del inventario."""
    r, g, b = item["color"]

    # Contenido del item
    item_content = Node(
        style=Style(
            width=Unit.px(80),
            height=Unit.px(80),
            background_color=Color(r, g, b, 200),
            border_radius=8.0,
            border_width=2.0,
            border_color=Color(r, g, b, 255),
            flex_direction=FlexDirection.COLUMN,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            gap=4,
        )
    )

    # Icono (emoji como texto)
    item_content.add_child(Text(item["icon"], size=28, color=Color(255, 255, 255, 255)))

    # Cantidad
    if item.get("quantity", 1) > 1:
        item_content.add_child(
            Text(f"x{item['quantity']}", size=12, color=Color(200, 200, 200, 255))
        )

    # Crear el Draggable
    draggable = Draggable(
        content=item_content,
        data=item,
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
        ),
        drag_opacity=0.85,
        on_drag_start=lambda i=item: print(f"Picked up: {i['name']}"),
        on_drag_end=lambda dropped, target, i=item: print(
            f"  -> {i['name']} dropped" if dropped else f"  -> {i['name']} returned"
        ),
    )

    return draggable


def create_inventory_slot(
    slot_id: str, title: str, items: list, direction: FlexDirection = FlexDirection.ROW
) -> Node:
    """Crear una sección del inventario con ordenamiento."""

    container = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
        )
    )

    # Título
    container.add_child(Text(title, size=14, color=Color(180, 180, 180, 255)))

    # DropZone con ordenamiento habilitado
    drop_zone = DropZone(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(96),
            background_color=Color(30, 30, 35, 255),
            border_radius=8.0,
            border_width=2.0,
            border_color=Color(50, 50, 60, 255),
            padding=Spacing.all(8),
            flex_direction=direction,
            gap=8,
        ),
        highlight_color=Color(50, 60, 50, 255),
        auto_adopt=True,
        sortable=True,  # Permite reordenar items
        drop_indicator_color=Color(100, 200, 100, 200),
        on_drop=lambda drag, data, sid=slot_id: print(
            f"[{sid}] Received: {data['name']}"
        ),
        data=slot_id,
    )

    # Agregar items iniciales
    for item in items:
        drop_zone.add_child(create_item(item))

    container.add_child(drop_zone)
    return container


def create_ui() -> Node:
    """Crear el UI del inventario."""

    # Items de ejemplo
    weapons = [
        {
            "id": 1,
            "name": "Sword",
            "icon": "⚔",
            "color": (180, 180, 200),
            "quantity": 1,
        },
        {"id": 2, "name": "Bow", "icon": "🏹", "color": (139, 90, 43), "quantity": 1},
        {
            "id": 3,
            "name": "Staff",
            "icon": "🪄",
            "color": (138, 43, 226),
            "quantity": 1,
        },
    ]

    potions = [
        {
            "id": 4,
            "name": "Health Potion",
            "icon": "❤",
            "color": (200, 50, 50),
            "quantity": 5,
        },
        {
            "id": 5,
            "name": "Mana Potion",
            "icon": "💙",
            "color": (50, 100, 200),
            "quantity": 3,
        },
        {
            "id": 6,
            "name": "Speed Potion",
            "icon": "⚡",
            "color": (200, 200, 50),
            "quantity": 2,
        },
    ]

    materials = [
        {"id": 7, "name": "Wood", "icon": "🪵", "color": (139, 90, 43), "quantity": 20},
        {
            "id": 8,
            "name": "Stone",
            "icon": "🪨",
            "color": (128, 128, 128),
            "quantity": 15,
        },
        {
            "id": 9,
            "name": "Iron",
            "icon": "⬜",
            "color": (200, 200, 200),
            "quantity": 8,
        },
        {"id": 10, "name": "Gold", "icon": "🟨", "color": (255, 215, 0), "quantity": 4},
    ]

    # Root
    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=Color(18, 18, 22, 255),
            flex_direction=FlexDirection.COLUMN,
            padding=Spacing.all(24),
            gap=16,
        )
    )

    # Título
    root.add_child(Text("🎒 Inventory", size=24, color=Color(255, 255, 255, 255)))
    root.add_child(
        Text(
            "Drag items to reorder or move between categories",
            size=14,
            color=Color(128, 128, 128, 255),
        )
    )

    # Contenedor de inventario
    inventory = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=24,
            padding=Spacing.all(16),
            background_color=Color(25, 25, 30, 255),
            border_radius=12.0,
        )
    )

    # Fila de armas (horizontal)
    inventory.add_child(
        create_inventory_slot("weapons", "⚔ Weapons", weapons, FlexDirection.ROW)
    )

    # Fila de pociones (horizontal)
    inventory.add_child(
        create_inventory_slot("potions", "🧪 Potions", potions, FlexDirection.ROW)
    )

    # Fila de materiales (horizontal)
    inventory.add_child(
        create_inventory_slot("materials", "📦 Materials", materials, FlexDirection.ROW)
    )

    # Hotbar (zona especial abajo)
    hotbar_container = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
            padding=Spacing.all(16),
            background_color=Color(35, 35, 40, 255),
            border_radius=12.0,
        )
    )
    hotbar_container.add_child(
        Text(
            "🎮 Hotbar (Drag items here for quick access)",
            size=14,
            color=Color(180, 180, 180, 255),
        )
    )

    hotbar = DropZone(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(96),
            background_color=Color(45, 45, 50, 255),
            border_radius=8.0,
            border_width=2.0,
            border_color=Color(60, 60, 70, 255),
            padding=Spacing.all(8),
            flex_direction=FlexDirection.ROW,
            gap=8,
        ),
        highlight_color=Color(60, 70, 60, 255),
        auto_adopt=True,
        sortable=True,
        drop_indicator_color=Color(255, 200, 100, 200),
        on_drop=lambda drag, data: print(f"[HOTBAR] Equipped: {data['name']}"),
        data="hotbar",
    )
    hotbar_container.add_child(hotbar)

    inventory.add_child(hotbar_container)
    root.add_child(inventory)

    return root


ui_manager: UIManager = None  # type: ignore


def ui_update_system(renderer: Renderer2D, input_sys: Input, display: Display):
    global ui_manager
    dt = renderer.get_delta_time()
    wheel = input_sys.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel)


def ui_render_system(renderer: Renderer2D):
    global ui_manager
    ui_manager.render()


def setup_system(game: ArepyEngine):
    global ui_manager

    config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)
    ui_manager = UIManager.from_engine(game, config=config)

    root = create_ui()
    ui_manager.set_root(root)

    print("=== Inventory Demo ===")
    print("Drag items to reorder within a category")
    print("Drag items between categories to move them")
    print("The blue line shows where the item will be placed")


def main():
    rl.SetConfigFlags(rl.FLAG_MSAA_4X_HINT | rl.FLAG_WINDOW_RESIZABLE)

    game = ArepyEngine(
        title="Inventory Demo - Drag & Drop with Sorting",
        width=1280,
        height=720,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore

    world: World = game.create_world("inventory_demo")
    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("inventory_demo")
    game.run()


if __name__ == "__main__":
    main()
