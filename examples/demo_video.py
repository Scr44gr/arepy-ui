from pathlib import Path

import raylib as rl
from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline, TextureFilter
from arepy.ecs.world import World

from arepy_ui import (
    AlignItems,
    Button,
    Color,
    FlexDirection,
    FontLoadRequest,
    JustifyContent,
    Node,
    PositionType,
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
    load_fonts,
)
from arepy_ui.components import Divider

ui_manager: UIManager = None  # type: ignore

FONT_BODY: str | None = None
FONT_BRAND: str | None = None
FONT_META: str | None = None

BG = Color(15, 15, 15, 255)
SURFACE = Color(24, 24, 24, 255)
SURFACE_SOFT = Color(34, 34, 34, 255)
SURFACE_ELEVATED = Color(39, 39, 39, 255)
SURFACE_BORDER = Color(58, 58, 58, 255)
TEXT_PRIMARY = Color(241, 241, 241, 255)
TEXT_SECONDARY = Color(170, 170, 170, 255)
TEXT_TERTIARY = Color(120, 120, 120, 255)
ACCENT_RED = Color(255, 0, 0, 255)
CHIP_ACTIVE = Color(241, 241, 241, 255)
CHIP_ACTIVE_TEXT = Color(15, 15, 15, 255)


def noop():
    pass


def _first_existing_path(candidates: list[str]) -> str | None:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def setup_demo_fonts() -> None:
    global FONT_BODY, FONT_BRAND, FONT_META

    font_base_sizes = {
        "yt-body": 20,
        "yt-brand": 32,
        "yt-meta": 14,
    }

    font_sources = {
        "yt-body": [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ],
        "yt-brand": [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/bahnschrift.ttf",
            "C:/Windows/Fonts/seguisb.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ],
        "yt-meta": [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/verdana.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ],
    }

    requests: list[FontLoadRequest] = []
    loaded_names: dict[str, str] = {}

    for name, candidates in font_sources.items():
        path = _first_existing_path(candidates)
        if not path:
            continue
        requests.append(
            FontLoadRequest(
                name=name,
                path=path,
                base_size=font_base_sizes.get(name, 20),
                set_as_default=name == "yt-body",
                texture_filter=TextureFilter.TRILINEAR,
            )
        )
        loaded_names[name] = name

    if requests:
        load_fonts(requests)

    FONT_BODY = loaded_names.get("yt-body")
    FONT_BRAND = loaded_names.get("yt-brand") or FONT_BODY
    FONT_META = loaded_names.get("yt-meta") or FONT_BODY


def font_for(role: str) -> str | None:
    if role == "brand":
        return FONT_BRAND
    if role == "meta":
        return FONT_META
    return FONT_BODY


def ui_text(text: str, size: float, color: Color, role: str = "body") -> Text:
    return Text(text, size=size, color=color, font_name=font_for(role))


def create_chip(label: str, active: bool = False) -> Node:
    chip = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            background_color=CHIP_ACTIVE if active else SURFACE_SOFT,
            border_radius=8.0,
            padding=Spacing.symmetric(vertical=8, horizontal=12),
        )
    )
    chip.add_child(
        ui_text(
            label,
            12,
            CHIP_ACTIVE_TEXT if active else TEXT_PRIMARY,
            role="body",
        )
    )
    return chip


def create_icon_avatar(label: str, color: Color) -> Node:
    avatar = Node(
        style=Style(
            width=Unit.px(36),
            height=Unit.px(36),
            background_color=color,
            border_radius=18.0,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
        )
    )
    avatar.add_child(ui_text(label, 13, TEXT_PRIMARY, role="brand"))
    return avatar


def create_action_button(
    label: str,
    width: int,
    background: Color = SURFACE_SOFT,
    text_color: Color = TEXT_PRIMARY,
) -> Button:
    return Button(
        label,
        noop,
        Unit.px(width),
        Unit.px(36),
        background,
        text_color=text_color,
        border_radius=18.0,
        font_size=12,
        font_name=font_for("body"),
    )


def create_video_card(
    title: str, channel: str, views: str, duration: str = "10:30"
) -> Node:
    card = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=12,
            padding=Spacing.symmetric(vertical=8, horizontal=0),
        )
    )

    thumb = Node(
        style=Style(
            width=Unit.px(168),
            height=Unit.px(94),
            background_color=Color(56, 56, 56, 255),
            border_radius=10.0,
        )
    )

    thumb_label = Node(
        style=Style(
            position=PositionType.ABSOLUTE,
            top=Unit.px(8),
            left=Unit.px(8),
            width=Unit.auto(),
            height=Unit.auto(),
            background_color=Color(0, 0, 0, 190),
            border_radius=4.0,
            padding=Spacing.symmetric(vertical=3, horizontal=6),
        )
    )
    thumb_label.add_child(ui_text("AREPY", 10, TEXT_PRIMARY, role="meta"))
    thumb.add_child(thumb_label)

    duration_badge = Node(
        style=Style(
            position=PositionType.ABSOLUTE,
            right=Unit.px(8),
            bottom=Unit.px(8),
            width=Unit.auto(),
            height=Unit.auto(),
            background_color=Color(0, 0, 0, 220),
            border_radius=4.0,
            padding=Spacing.symmetric(vertical=3, horizontal=6),
        )
    )
    duration_badge.add_child(ui_text(duration, 10, TEXT_PRIMARY, role="meta"))
    thumb.add_child(duration_badge)
    card.add_child(thumb)

    info = Node(
        style=Style(
            width=Unit.percent(58),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=4,
        )
    )

    display_title = title[:48] + "..." if len(title) > 48 else title
    info.add_child(ui_text(display_title, 14, TEXT_PRIMARY, role="body"))
    info.add_child(ui_text(channel, 12, TEXT_SECONDARY, role="meta"))
    info.add_child(ui_text(views, 12, TEXT_TERTIARY, role="meta"))

    card.add_child(info)
    return card


def create_comment(author: str, text: str, likes: str, time_ago: str) -> Node:
    comment = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=12,
            padding=Spacing.symmetric(vertical=14, horizontal=0),
        )
    )

    avatar = create_icon_avatar(author[1:3].upper(), Color(67, 102, 190, 255))
    avatar.style.width = Unit.px(40)
    avatar.style.height = Unit.px(40)
    avatar.style.border_radius = 20.0
    comment.add_child(avatar)

    content = Node(
        style=Style(
            width=Unit.percent(90),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=6,
        )
    )

    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=8,
            align_items=AlignItems.CENTER,
        )
    )
    header.add_child(ui_text(author, 13, TEXT_PRIMARY, role="body"))
    header.add_child(ui_text(time_ago, 12, TEXT_TERTIARY, role="meta"))
    content.add_child(header)

    content.add_child(ui_text(text, 13, Color(225, 225, 225, 255), role="body"))

    likes_row = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=16,
            align_items=AlignItems.CENTER,
        )
    )
    likes_row.add_child(ui_text(f"LIKE {likes}", 11, TEXT_SECONDARY, role="meta"))
    likes_row.add_child(ui_text("REPLY", 11, TEXT_SECONDARY, role="meta"))
    content.add_child(likes_row)

    comment.add_child(content)
    return comment


def create_header() -> Node:
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(56),
            background_color=BG,
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            justify_content=JustifyContent.SPACE_BETWEEN,
            padding=Spacing.symmetric(vertical=0, horizontal=16),
        )
    )

    left_cluster = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=14,
        )
    )
    left_cluster.add_child(create_action_button("=", 36))

    logo_row = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=8,
        )
    )
    logo_badge = Node(
        style=Style(
            width=Unit.px(30),
            height=Unit.px(22),
            background_color=ACCENT_RED,
            border_radius=7.0,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
        )
    )
    logo_badge.add_child(ui_text(">", 13, TEXT_PRIMARY, role="brand"))
    logo_row.add_child(logo_badge)
    logo_row.add_child(ui_text("YouTube", 20, TEXT_PRIMARY, role="brand"))
    left_cluster.add_child(logo_row)
    header.add_child(left_cluster)

    search_row = Node(
        style=Style(
            width=Unit.percent(44),
            height=Unit.px(40),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=10,
        )
    )
    search_input = TextInput(
        placeholder="Search",
        width=Unit.percent(100),
        height=Unit.px(40),
        font_size=14,
        style=Style(
            background_color=Color(18, 18, 18, 255),
            border_color=SURFACE_BORDER,
            border_width=1.0,
            border_radius=20.0,
            padding=Spacing.symmetric(vertical=8, horizontal=16),
        ),
    )
    search_input.text_color = TEXT_PRIMARY
    search_input.placeholder_color = TEXT_TERTIARY
    search_input.default_border_color = SURFACE_BORDER
    search_input.focused_border_color = Color(62, 166, 255, 255)
    search_row.add_child(search_input)
    search_row.add_child(create_action_button("Search", 78, SURFACE_SOFT))
    search_row.add_child(create_action_button("Mic", 48, SURFACE_SOFT))
    header.add_child(search_row)

    right_cluster = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=12,
        )
    )
    right_cluster.add_child(create_action_button("Create", 76, SURFACE_SOFT))
    right_cluster.add_child(create_action_button("Bell", 56, SURFACE_SOFT))
    right_cluster.add_child(create_icon_avatar("AU", Color(151, 93, 186, 255)))
    header.add_child(right_cluster)
    return header


def create_ui(video_path: str) -> Node:
    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            background_color=BG,
            flex_direction=FlexDirection.COLUMN,
        )
    )

    root.add_child(create_header())
    root.add_child(Divider(color=Color(42, 42, 42, 255), thickness=1))

    main_wrapper = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.vh(92),
            flex_direction=FlexDirection.ROW,
            padding=Spacing.all(24),
            gap=24,
        )
    )

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
            gap=18,
        )
    )

    video = Video(
        source=video_path,
        width=Unit.percent(100),
        height=Unit.vh(50),
        autoplay=True,
        loop=True,
    )
    main_scroll_content.add_child(video)

    main_scroll_content.add_child(
        ui_text(
            "Building a YouTube-like Video Player with arepy-ui",
            23,
            TEXT_PRIMARY,
            role="brand",
        )
    )

    stats_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.SPACE_BETWEEN,
            align_items=AlignItems.CENTER,
            gap=12,
        )
    )
    stats_row.add_child(
        ui_text("1,234,567 views  Dec 5, 2025", 13, TEXT_SECONDARY, role="meta")
    )

    actions = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=8,
        )
    )
    actions.add_child(create_action_button("Like 123K", 110, SURFACE_ELEVATED))
    actions.add_child(create_action_button("Dislike", 86, SURFACE_ELEVATED))
    actions.add_child(create_action_button("Share", 78, SURFACE_ELEVATED))
    actions.add_child(create_action_button("Save", 72, SURFACE_ELEVATED))
    stats_row.add_child(actions)
    main_scroll_content.add_child(stats_row)

    channel_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=16,
            align_items=AlignItems.CENTER,
            padding=Spacing.symmetric(vertical=8, horizontal=0),
        )
    )
    channel_row.add_child(create_icon_avatar("AI", Color(207, 84, 84, 255)))

    channel_info = Node(
        style=Style(
            width=Unit.percent(58),
            height=Unit.auto(),
            flex_direction=FlexDirection.COLUMN,
            gap=4,
        )
    )
    channel_info.add_child(ui_text("Arepy UI", 16, TEXT_PRIMARY, role="body"))
    channel_info.add_child(
        ui_text("15.2K subscribers  124 videos", 12, TEXT_SECONDARY, role="meta")
    )
    channel_row.add_child(channel_info)
    channel_row.add_child(
        create_action_button(
            "Subscribe",
            112,
            ACCENT_RED,
            TEXT_PRIMARY,
        )
    )
    channel_row.add_child(create_action_button("Join", 64, SURFACE_SOFT))
    main_scroll_content.add_child(channel_row)

    desc_box = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            background_color=SURFACE,
            border_radius=12.0,
            padding=Spacing.all(16),
            flex_direction=FlexDirection.COLUMN,
            gap=10,
        )
    )
    desc_box.add_child(
        ui_text(
            "124K views  5 days ago  #python  #gamedev  #ui",
            13,
            TEXT_PRIMARY,
            role="meta",
        )
    )
    desc_box.add_child(
        ui_text(
            "This demo showcases multiple fonts, a YouTube-inspired layout, custom video controls, "
            "responsive sidebars, and long-form content built entirely with arepy-ui components.",
            14,
            Color(215, 215, 215, 255),
            role="body",
        )
    )
    desc_box.add_child(ui_text("Show more", 13, TEXT_SECONDARY, role="meta"))
    main_scroll_content.add_child(desc_box)

    comments_header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=16,
            padding=Spacing.symmetric(vertical=8, horizontal=0),
        )
    )
    comments_header.add_child(ui_text("128 Comments", 18, TEXT_PRIMARY, role="body"))
    comments_header.add_child(ui_text("Sort by", 13, TEXT_SECONDARY, role="meta"))
    main_scroll_content.add_child(comments_header)

    add_comment_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            gap=12,
            padding=Spacing.symmetric(vertical=8, horizontal=0),
        )
    )
    add_comment_row.add_child(create_icon_avatar("AU", Color(151, 93, 186, 255)))
    comment_input = TextInput(
        placeholder="Add a comment...",
        width=Unit.percent(100),
        height=Unit.px(40),
        font_size=14,
        style=Style(
            background_color=BG,
            border_color=SURFACE_BORDER,
            border_width=0.0,
            border_radius=0.0,
            padding=Spacing.symmetric(vertical=10, horizontal=0),
        ),
    )
    comment_input.text_color = TEXT_PRIMARY
    comment_input.placeholder_color = TEXT_TERTIARY
    comment_input.default_border_color = BG
    comment_input.focused_border_color = BG
    add_comment_row.add_child(comment_input)
    main_scroll_content.add_child(add_comment_row)
    main_scroll_content.add_child(Divider(color=Color(50, 50, 50, 255)))

    comments_data = [
        (
            "@pythondev",
            "This is exactly what I needed. The new font hierarchy makes the demo feel much closer to a real video platform.",
            "245",
            "2 hours ago",
        ),
        (
            "@gamedev_pro",
            "The seek behavior is much better now. Audio and video recover way faster after scrubbing.",
            "89",
            "5 hours ago",
        ),
        (
            "@ui_enthusiast",
            "Love the cleaner header, action chips, and the updated related cards layout.",
            "156",
            "1 day ago",
        ),
        (
            "@coding_wizard",
            "Python UI demos rarely look this polished. Great progress.",
            "312",
            "2 days ago",
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
            gap=14,
        )
    )

    chips_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=8,
        )
    )
    chips_row.add_child(create_chip("All", active=True))
    chips_row.add_child(create_chip("Python"))
    chips_row.add_child(create_chip("UI"))
    chips_row.add_child(create_chip("Gamedev"))
    sidebar_scroll_content.add_child(chips_row)

    sidebar_scroll_content.add_child(
        ui_text("Up next", 14, TEXT_SECONDARY, role="meta")
    )

    related = [
        (
            "Python Game Development - Complete Course 2025",
            "GameDev Academy",
            "892K views  2 weeks ago",
            "2:15:30",
        ),
        (
            "Building UIs with Flexbox - Deep Dive",
            "CSS Master",
            "234K views  1 month ago",
            "45:12",
        ),
        (
            "Raylib Performance Comparison",
            "Code Compare",
            "156K views  3 days ago",
            "18:45",
        ),
        (
            "Create a Music Player in Python",
            "PyTutorials",
            "67K views  1 week ago",
            "32:20",
        ),
        (
            "Advanced Python Patterns for Games",
            "Pro Coder",
            "445K views  2 months ago",
            "1:05:00",
        ),
        ("UI Animation Techniques", "Motion Design", "123K views  5 days ago", "28:15"),
        (
            "Python Performance Tips 2025",
            "Speed Demon",
            "89K views  1 day ago",
            "22:40",
        ),
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
    global ui_manager
    ui_manager.render()


def setup_system(game: ArepyEngine):
    global ui_manager

    ui_manager = UIManager.from_engine(
        game,
        config=UIConfig(
            resize_mode=ResizeMode.RESPONSIVE,
            font_texture_filter=TextureFilter.NEAREST,
        ),
    )

    setup_demo_fonts()

    video_path = "examples/assets/dispatch.mp4"
    root = create_ui(video_path)
    ui_manager.set_root(root)

    print("YouTube-style Video Player Demo")
    print("================================")
    print("- Loads multiple font roles with platform fallbacks")
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
