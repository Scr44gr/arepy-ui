import raylib as rl
from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline
from arepy.ecs.world import World

from arepy_ui import (
    AlignItems,
    Button,
    Color,
    FlexDirection,
    JustifyContent,
    Node,
    ResizeMode,
    ScrollView,
    Spacing,
    Style,
    Text,
    TextInput,
    UIConfig,
    UIManager,
    Unit,
    Video,
    configure_runtime,
)
from arepy_ui.components import Divider
from arepy_ui.debug import UIDebugger

ui_manager: UIManager = None  # type: ignore
ui_debugger: UIDebugger = None  # type: ignore


def create_video_card(
    title: str, channel: str, views: str, duration: str = "10:30"
) -> Node:
    card = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=12,
            padding=Spacing.all(8),
            border_radius=8.0,
        )
    )

    thumb = Node(
        style=Style(
            width=Unit.px(168),
            height=Unit.px(94),
            background_color=Color(50, 50, 55, 255),
            border_radius=8.0,
        )
    )

    duration_badge = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            background_color=Color(0, 0, 0, 220),
            padding=Spacing.symmetric(horizontal=6, vertical=2),
            border_radius=4.0,
        )
    )
    duration_badge.add_child(Text(duration, size=11, color=Color(255, 255, 255, 255)))
    thumb.add_child(duration_badge)
    card.add_child(thumb)

    # Info
    info = Node(
        style=Style(
            width=Unit.percent(55),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=4,
        )
    )

    display_title = title[:45] + "..." if len(title) > 45 else title
    info.add_child(Text(display_title, size=14, color=Color(255, 255, 255, 255)))
    info.add_child(Text(channel, size=12, color=Color(150, 150, 150, 255)))
    info.add_child(Text(views, size=12, color=Color(150, 150, 150, 255)))

    card.add_child(info)
    return card


def create_comment(author: str, text: str, likes: str, time_ago: str) -> Node:
    """Crea un comentario."""
    comment = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=12,
            padding=Spacing.symmetric(vertical=12, horizontal=0),
        )
    )

    # Avatar
    avatar = Node(
        style=Style(
            width=Unit.px(40),
            height=Unit.px(40),
            background_color=Color(80, 80, 120, 255),
            border_radius=20.0,
        )
    )
    comment.add_child(avatar)

    # Contenido
    content = Node(
        style=Style(
            width=Unit.percent(90),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=4,
        )
    )

    # Header del comentario
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=8,
            align_items=AlignItems.CENTER,
        )
    )
    header.add_child(Text(author, size=13, color=Color(255, 255, 255, 255)))
    header.add_child(Text(time_ago, size=12, color=Color(120, 120, 120, 255)))
    content.add_child(header)

    content.add_child(Text(text, size=13, color=Color(220, 220, 220, 255)))

    # Likes
    likes_row = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=16,
            align_items=AlignItems.CENTER,
        )
    )
    likes_row.add_child(Text(f" {likes}", size=12, color=Color(150, 150, 150, 255)))
    likes_row.add_child(Text("Reply", size=12, color=Color(150, 150, 150, 255)))
    content.add_child(likes_row)

    comment.add_child(content)
    return comment


def create_ui(video_path: str) -> Node:
    """Layout principal estilo YouTube - 100% responsive."""

    # Root
    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=Color(15, 15, 15, 255),
            flex_direction=FlexDirection.COLUMN,
        )
    )

    # ========== HEADER ==========
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(56),
            background_color=Color(15, 15, 15, 255),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            justify_content=JustifyContent.SPACE_BETWEEN,
            padding=Spacing.symmetric(horizontal=24, vertical=0),
        )
    )

    # Logo
    logo = Text(" YouTube", size=20, color=Color(255, 255, 255, 255))
    header.add_child(logo)

    # Search
    search_container = Node(
        style=Style(
            width=Unit.percent(40),
            height=Unit.px(40),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.CENTER,
        )
    )
    search_input = TextInput(
        placeholder="Search...",
        width=Unit.percent(100),
        height=Unit.px(40),
    )
    search_container.add_child(search_input)
    header.add_child(search_container)

    # User
    user_avatar = Node(
        style=Style(
            width=Unit.px(32),
            height=Unit.px(32),
            background_color=Color(100, 120, 200, 255),
            border_radius=16.0,
        )
    )
    header.add_child(user_avatar)

    root.add_child(header)

    # Divider bajo header
    root.add_child(Divider(color=Color(40, 40, 40, 255), thickness=1))

    # ========== MAIN CONTENT ==========
    main_wrapper = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.vh(92),  # Resto de la ventana
            flex_direction=FlexDirection.ROW,
            padding=Spacing.all(24),
            gap=24,
        )
    )

    # ===== COLUMNA PRINCIPAL (70%) =====
    main_column = Node(
        style=Style(
            width=Unit.percent(68),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
        )
    )

    main_scroll_content = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=16,
        )
    )

    # Video Player
    video = Video(
        source=video_path,
        width=Unit.percent(100),
        height=Unit.vh(50),
        autoplay=True,
        loop=True,
    )
    main_scroll_content.add_child(video)

    # T�tulo del video
    main_scroll_content.add_child(
        Text(
            "Building a YouTube-like Video Player with arepy-ui",
            size=22,
            color=Color(255, 255, 255, 255),
        )
    )

    # Stats row
    stats_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.SPACE_BETWEEN,
            align_items=AlignItems.CENTER,
        )
    )

    stats_row.add_child(
        Text("1,234,567 views  Dec 5, 2025", size=13, color=Color(150, 150, 150, 255))
    )

    # Action buttons
    actions = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=8,
        )
    )

    def noop():
        pass

    actions.add_child(
        Button(
            " 123K",
            noop,
            Unit.px(90),
            Unit.px(36),
            Color(40, 40, 40, 255),
            font_size=12,
        )
    )
    actions.add_child(
        Button("", noop, Unit.px(50), Unit.px(36), Color(40, 40, 40, 255), font_size=12)
    )
    actions.add_child(
        Button(
            "Share",
            noop,
            Unit.px(70),
            Unit.px(36),
            Color(40, 40, 40, 255),
            font_size=12,
        )
    )
    actions.add_child(
        Button(
            "Save", noop, Unit.px(60), Unit.px(36), Color(40, 40, 40, 255), font_size=12
        )
    )

    stats_row.add_child(actions)
    main_scroll_content.add_child(stats_row)

    # Divider
    main_scroll_content.add_child(Divider(color=Color(50, 50, 50, 255)))

    # Channel info
    channel_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=16,
            align_items=AlignItems.CENTER,
            padding=Spacing.symmetric(vertical=16, horizontal=0),
        )
    )

    channel_avatar = Node(
        style=Style(
            width=Unit.px(48),
            height=Unit.px(48),
            background_color=Color(200, 80, 80, 255),
            border_radius=24.0,
        )
    )
    channel_row.add_child(channel_avatar)

    channel_info = Node(
        style=Style(
            width=Unit.percent(60),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=2,
        )
    )
    channel_info.add_child(Text("Arepy UI", size=16, color=Color(255, 255, 255, 255)))
    channel_info.add_child(
        Text("15.2K subscribers", size=12, color=Color(150, 150, 150, 255))
    )
    channel_row.add_child(channel_info)

    channel_row.add_child(
        Button(
            "Subscribe",
            noop,
            Unit.px(110),
            Unit.px(38),
            Color(255, 0, 0, 255),
            font_size=14,
        )
    )

    main_scroll_content.add_child(channel_row)

    # Description box
    desc_box = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            background_color=Color(30, 30, 35, 255),
            border_radius=12.0,
            padding=Spacing.all(16),
            flex_direction=FlexDirection.COLUMN,
            gap=8,
        )
    )
    desc_box.add_child(
        Text(
            "This demo showcases the Video component of arepy-ui with full playback controls, "
            "responsive layout using vh/vw units, ScrollView for long content, and a clean "
            "YouTube-inspired design. All built with Python!",
            size=14,
            color=Color(200, 200, 200, 255),
        )
    )
    desc_box.add_child(Text("Show more", size=13, color=Color(150, 150, 150, 255)))
    main_scroll_content.add_child(desc_box)

    # Comments section
    main_scroll_content.add_child(Divider(color=Color(50, 50, 50, 255)))

    comments_header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=24,
            padding=Spacing.symmetric(vertical=16, horizontal=0),
        )
    )
    comments_header.add_child(
        Text("128 Comments", size=16, color=Color(255, 255, 255, 255))
    )
    comments_header.add_child(Text("Sort by", size=13, color=Color(150, 150, 150, 255)))
    main_scroll_content.add_child(comments_header)

    # Comments
    comments_data = [
        (
            "@pythondev",
            "This is exactly what I needed! Great work on the UI framework.",
            "245",
            "2 hours ago",
        ),
        (
            "@gamedev_pro",
            "The video controls are smooth. How did you handle the frame timing?",
            "89",
            "5 hours ago",
        ),
        (
            "@ui_enthusiast",
            "Love the attention to detail on the scrollbars and hover effects!",
            "156",
            "1 day ago",
        ),
        (
            "@coding_wizard",
            "Finally a good UI library for Python games. Subscribed!",
            "312",
            "2 days ago",
        ),
        (
            "@learner2025",
            "Could you make a tutorial series on building this from scratch?",
            "67",
            "3 days ago",
        ),
    ]

    for author, text, likes, time_ago in comments_data:
        main_scroll_content.add_child(create_comment(author, text, likes, time_ago))

    main_scroll = ScrollView(
        width=Unit.percent(100),
        height=Unit.percent(100),
        content=main_scroll_content,
    )
    main_column.add_child(main_scroll)
    main_wrapper.add_child(main_column)

    sidebar = Node(
        style=Style(
            width=Unit.percent(30),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
        )
    )

    sidebar_scroll_content = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=12,
        )
    )

    sidebar_scroll_content.add_child(
        Text("Related Videos", size=14, color=Color(150, 150, 150, 255))
    )

    # Videos relacionados
    related = [
        (
            "Python Game Development - Complete Course 2025",
            "GameDev Academy",
            "892K views  2 weeks",
            "2:15:30",
        ),
        (
            "Building UIs with Flexbox - Deep Dive",
            "CSS Master",
            "234K views  1 month",
            "45:12",
        ),
        (
            "Raylib - Performance Comparison",
            "Code Compare",
            "156K views  3 days",
            "18:45",
        ),
        (
            "Create a Music Player in Python",
            "PyTutorials",
            "67K views  1 week",
            "32:20",
        ),
        (
            "Advanced Python Patterns for Games",
            "Pro Coder",
            "445K views  2 months",
            "1:05:00",
        ),
        ("UI Animation Techniques", "Motion Design", "123K views  5 days", "28:15"),
        ("Python Performance Tips 2025", "Speed Demon", "89K views  1 day", "22:40"),
        (
            "Building a Video Editor in Python",
            "Creative Code",
            "234K views  2 weeks",
            "1:45:00",
        ),
        ("The Future of Python GUIs", "Tech Talk", "178K views  4 days", "35:50"),
        ("Responsive Design Principles", "UI/UX Pro", "92K views  1 week", "41:30"),
    ]

    for title, channel, views, duration in related:
        sidebar_scroll_content.add_child(
            create_video_card(title, channel, views, duration)
        )

    sidebar_scroll = ScrollView(
        width=Unit.percent(100),
        height=Unit.percent(100),
        content=sidebar_scroll_content,
    )
    sidebar.add_child(sidebar_scroll)
    main_wrapper.add_child(sidebar)

    root.add_child(main_wrapper)
    return root


def ui_update_system(renderer: Renderer2D, input: Input, display: Display):
    global ui_manager
    dt = renderer.get_delta_time()
    wheel = input.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel)


def ui_render_system(renderer: Renderer2D):
    global ui_manager, ui_debugger
    ui_manager.render()
    if ui_debugger:
        ui_debugger.render(ui_manager.root)


def setup_system(game: ArepyEngine):
    global ui_manager, ui_debugger

    ui_manager = UIManager.from_engine(
        game,
        config=UIConfig(
            resize_mode=ResizeMode.RESPONSIVE,
        ),
    )
    ui_debugger = UIDebugger()

    video_path = "examples/assets/dispatch.mp4"
    root = create_ui(video_path)
    ui_manager.set_root(root)

    print("YouTube-style Video Player Demo")
    print("================================")
    print("- Resize window to test responsive layout")
    print("- Scroll in main content and sidebar")
    print("- Press F3 for debug overlay")


def main():
    rl.SetConfigFlags(rl.FLAG_MSAA_4X_HINT | rl.FLAG_WINDOW_RESIZABLE)

    game = ArepyEngine(
        title="arepy-ui Video Player",
        width=1280,
        height=720,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore

    world: World = game.create_world("video_demo")
    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("video_demo")
    game.run()


if __name__ == "__main__":
    main()
