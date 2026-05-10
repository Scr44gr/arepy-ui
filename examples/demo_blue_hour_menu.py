from __future__ import annotations

"""Minimal Slot Island title screen demo."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import raylib as rl
from arepy import (
    ArepyEngine,
    ArepyShader,
    Renderer2D,
    ShaderUniformType,
    SystemPipeline,
    TextureFilter,
)
from arepy.engine.renderer import Rect
from arepy.engine.time import Time

from arepy_ui import (
    AlignItems,
    Checkbox,
    Color,
    CursorType,
    Easing,
    FlexDirection,
    FontLoadRequest,
    JustifyContent,
    Node,
    PositionType,
    ResizeMode,
    Slider,
    Spacing,
    Style,
    Text,
    UIConfig,
    UIManager,
    Unit,
    draw_text,
    load_fonts,
)
from arepy_ui.runtime import get_runtime


WHITE = Color(255, 255, 255, 255)
BLACK = Color(8, 8, 8, 255)
SOFT_BLACK = Color(48, 48, 48, 255)
DIM_BLACK = Color(96, 96, 96, 255)
LIGHT_GRAY = Color(232, 232, 232, 255)
MID_GRAY = Color(196, 196, 196, 255)
HAZE_GRAY = Color(244, 244, 244, 255)
PARCHMENT = WHITE
PARCHMENT_SOFT = LIGHT_GRAY
PARCHMENT_GLOW = WHITE
INK = BLACK
INK_SOFT = SOFT_BLACK
WINE = BLACK
WINE_DARK = BLACK
GOLD = BLACK
GOLD_SOFT = MID_GRAY
GOLD_LINE = MID_GRAY
SHADOW_WARM = Color(0, 0, 0, 48)

FONT_DISPLAY: str | None = None
FONT_BODY: str | None = None
FONT_META: str | None = None

ui_manager: UIManager | None = None
background_shader: ArepyShader | None = None

scene_clock = 0.0
current_view = "idle"
current_settings_view = "video"
active_menu_key = ""
loading_active = False
loading_complete = False
loading_elapsed = 0.0
loading_progress = 0.0
loading_stage_index = -1


class MainView(str, Enum):
    IDLE = "idle"
    SETTINGS = "settings"
    CREDITS = "credits"
    LOADING = "loading"


class SettingsView(str, Enum):
    VIDEO = "video"
    SOUND = "sound"
    INTERFACE = "interface"


@dataclass(frozen=True, slots=True)
class ChangelogEntry:
    version: str
    title: str
    detail: str


CHANGELOG = [
    ChangelogEntry(
        version="0.1.7a",
        title="Cozy casino pass",
        detail="The menu now leans into warm parchment, burgundy felt, and old-gold accents instead of harsh black-white blocks.",
    ),
    ChangelogEntry(
        version="0.1.6",
        title="House flow tightened",
        detail="Play, credits, settings, and loading each own their panel, so the right side only shows what matters now.",
    ),
    ChangelogEntry(
        version="0.1.5",
        title="Sky parlor backdrop",
        detail="The title screen keeps the blue-purple cloud sky, but the interface now reads like a fantasy casino room floating under it.",
    ),
]


LOADING_PHASES = [
    (
        0.0,
        0.16,
        "Shuffling the first deck",
        "The summoned hero is being seated at the opening table.",
    ),
    (
        0.9,
        0.42,
        "Lighting the velvet hall",
        "Lantern glow, cloud drift, and shoreline paths are settling into place.",
    ),
    (
        1.9,
        0.72,
        "Stacking the island wagers",
        "Occupied routes, docks, and first-region markers are being laid out.",
    ),
    (
        3.1,
        1.0,
        "Opening the house gate",
        "The first shore is ready for a lucky hand.",
    ),
]


menu_buttons: dict[str, "MenuButton"] = {}
settings_tab_buttons: dict[SettingsView, "SettingsTabButton"] = {}
view_panels: dict[MainView, Node] = {}
settings_panels: dict[SettingsView, Node] = {}
intro_nodes: list[Node] = []
back_buttons: list["BackButton"] = []

loading_bar: "LoadingBar | None" = None
loading_percent_text: Text | None = None
loading_status_text: Text | None = None
loading_hint_text: Text | None = None
loading_steps_text: Text | None = None
title_text: Node | None = None
changelog_title: Text | None = None
menu_shell: Node | None = None
detail_shell: Node | None = None
detail_card: Node | None = None


FRAGMENT_SHADER = """
#version 330

in vec4 fragColor;
out vec4 finalColor;

uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 5; i++) {
        value += amplitude * noise(p);
        p = p * 2.03 + vec2(11.2, 7.6);
        amplitude *= 0.5;
    }
    return value;
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    uv.y = 1.0 - uv.y;

    vec3 top = vec3(0.54, 0.76, 1.00);
    vec3 mid = vec3(0.71, 0.81, 1.00);
    vec3 bottom = vec3(0.86, 0.78, 0.98);
    vec3 color = mix(top, mid, smoothstep(0.0, 0.45, uv.y));
    color = mix(color, bottom, smoothstep(0.35, 1.0, uv.y));

    float sun = smoothstep(0.18, 0.0, distance(uv, vec2(0.78, 0.18)));
    color += vec3(0.12, 0.08, 0.02) * sun;

    float cloud = fbm(vec2(uv.x * 2.7 + u_time * 0.020, uv.y * 4.0 - u_time * 0.008));
    float detail = fbm(vec2(uv.x * 5.8 - u_time * 0.016, uv.y * 7.2 + 4.6));
    float wave = 0.03 * sin(uv.x * 5.4 + u_time * 0.12);
    float mask = smoothstep(0.56 - wave, 0.84 - wave, cloud + detail * 0.32);
    color = mix(color, vec3(0.97, 0.98, 1.0), mask * 0.58);

    float lower = fbm(vec2(uv.x * 3.0 + 2.4, uv.y * 6.5 - u_time * 0.011));
    float lower_mask = smoothstep(0.58, 0.88, lower) * smoothstep(1.0, 0.30, uv.y);
    color = mix(color, vec3(0.92, 0.89, 0.99), lower_mask * 0.22);

    float vignette = uv.x * (1.0 - uv.x) * uv.y * (1.0 - uv.y);
    color *= 0.96 + vignette * 0.12;

    finalColor = vec4(color, 1.0);
}
"""


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def lerp(start: float, end: float, progress: float) -> float:
    return start + (end - start) * progress


def ease_to(current: float, target: float, speed: float, dt: float) -> float:
    return current + (target - current) * min(1.0, speed * dt)


def with_opacity(color: Color, opacity: float) -> Color:
    return Color(color.r, color.g, color.b, int(color.a * clamp(opacity)))


def mix_color(start: Color, end: Color, progress: float) -> Color:
    t = clamp(progress)
    return Color(
        int(round(lerp(start.r, end.r, t))),
        int(round(lerp(start.g, end.g, t))),
        int(round(lerp(start.b, end.b, t))),
        int(round(lerp(start.a, end.a, t))),
    )


def demo_font_path(group: str, filename: str) -> str:
    return str(
        Path(__file__).resolve().parent
        / "fonts"
        / "dead-revolver"
        / group
        / "TTF"
        / filename
    )


def setup_demo_fonts() -> None:
    global FONT_DISPLAY, FONT_BODY, FONT_META

    requests = [
        FontLoadRequest(
            name="slot-display",
            path=demo_font_path("Display", "DeadRevolverDisplay.ttf"),
            base_size=104,
            texture_filter=TextureFilter.NEAREST,
            glyphs="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /:-",
        ),
        FontLoadRequest(
            name="slot-body",
            path=demo_font_path("Game", "DeadRevolverGameCompact.ttf"),
            base_size=54,
            set_as_default=True,
            texture_filter=TextureFilter.NEAREST,
        ),
        FontLoadRequest(
            name="slot-meta",
            path=demo_font_path("Digital", "DeadRevolverDigital.ttf"),
            base_size=34,
            texture_filter=TextureFilter.NEAREST,
        ),
    ]
    load_fonts(requests)
    FONT_DISPLAY = "slot-display"
    FONT_BODY = "slot-body"
    FONT_META = "slot-meta"


def font_for(role: str) -> str | None:
    if role == "display":
        return FONT_DISPLAY
    if role == "meta":
        return FONT_META
    return FONT_BODY


def ui_text(text: str, size: float, color: Color, role: str = "body") -> Text:
    return Text(text, size=size, color=color, font_name=font_for(role))


def create_separator(height: float = 1.0, color: Color = GOLD_LINE) -> Node:
    return Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(height),
            background_color=color,
        )
    )


def create_stage_panel() -> Node:
    panel = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(0),
            padding=Spacing.all(10),
            gap=16,
        )
    )
    panel.style.visible = False
    panel.style.opacity = 0.0
    return panel


def draw_diagonal_fill(
    renderer: Renderer2D,
    x: float,
    y: float,
    width: float,
    height: float,
    cut: float,
    color: Color,
) -> None:
    total_height = max(1, int(round(height)))
    if total_height <= 0 or width <= 0:
        return

    step_height = 3
    rows = max(1, (total_height + step_height - 1) // step_height)
    for row_index in range(rows):
        row_y = y + row_index * step_height
        current_height = min(step_height, total_height - row_index * step_height)
        progress = (row_index + 1) / rows
        row_width = max(1, int(round(width - cut * progress)))
        renderer.draw_rectangle(
            Rect(int(x), int(row_y), row_width, int(current_height)),
            color,
        )


class OutlinedTitle(Node):
    def __init__(self, label: str):
        super().__init__(
            style=Style(
                width=Unit.percent(100),
                height=Unit.px(152),
            )
        )
        self.label = label
        self.pickable = False

    def render(self) -> None:
        if not self.style.visible or self.style.opacity <= 0.0:
            return

        opacity = clamp(self.style.opacity)
        x = self.computed_x + 8
        y = self.computed_y + 18
        outline_color = with_opacity(BLACK, opacity)
        fill_color = with_opacity(WHITE, opacity)
        shadow_color = with_opacity(GOLD_SOFT, opacity * 0.85)
        offsets = [
            (-3, 0),
            (3, 0),
            (0, -3),
            (0, 3),
            (-2, -2),
            (2, -2),
            (-2, 2),
            (2, 2),
        ]

        draw_text(
            self.label,
            x + 7,
            y + 7,
            72,
            shadow_color,
            font_for("display"),
            1.0,
        )

        for offset_x, offset_y in offsets:
            draw_text(
                self.label,
                x + offset_x,
                y + offset_y,
                72,
                outline_color,
                font_for("display"),
                1.0,
            )

        draw_text(
            self.label,
            x,
            y,
            72,
            fill_color,
            font_for("display"),
            1.0,
        )


class MenuButton(Node):
    def __init__(self, key: str, label: str, on_press):
        super().__init__(
            style=Style(
                width=Unit.percent(100),
                height=Unit.px(84),
                cursor=CursorType.POINTING_HAND,
            )
        )
        self.key = key
        self.label = label
        self._on_press = on_press
        self.hover_progress = 0.0
        self.hover_target = 0.0
        self.select_progress = 0.0
        self.select_target = 0.0
        self.flash_progress = 0.0
        self.slide_x = -44.0
        self.base_height = 84.0
        self.hover_height = 122.0
        self.current_height = self.base_height
        self.on_hover_enter = self._handle_hover_enter
        self.on_hover_exit = self._handle_hover_exit
        self.on_click = self._handle_click

    def _handle_hover_enter(self) -> None:
        self.hover_target = 1.0

    def _handle_hover_exit(self) -> None:
        self.hover_target = 0.0

    def _handle_click(self) -> None:
        self.flash_progress = 1.0
        self._on_press(self.key)

    def set_selected(self, selected: bool) -> None:
        self.select_target = 1.0 if selected else 0.0

    def tick(self, dt: float) -> None:
        self.hover_progress = ease_to(self.hover_progress, self.hover_target, 16.0, dt)
        self.select_progress = ease_to(
            self.select_progress, self.select_target, 12.0, dt
        )
        self.flash_progress = max(0.0, self.flash_progress - dt * 2.6)

        target_height = self.base_height + (self.hover_height - self.base_height) * self.hover_target
        next_height = ease_to(self.current_height, target_height, 12.0, dt)
        if abs(next_height - self.current_height) > 0.1:
            self.current_height = next_height
            self.style.height = Unit.px(self.current_height)

    def render(self) -> None:
        if not self.style.visible or self.style.opacity <= 0.0:
            return

        runtime = get_runtime()
        x = self.computed_x + self.slide_x
        y = self.computed_y
        width = self.computed_width
        height = self.computed_height
        opacity = clamp(self.style.opacity)
        active = clamp(self.select_progress + self.hover_progress * 0.9)
        growth = 34.0 * active
        draw_y = y
        draw_width = width + growth
        draw_height = height
        diagonal_cut = 30.0 + 20.0 * active
        shadow_color = with_opacity(SHADOW_WARM, opacity * (0.22 + active * 0.16))
        fill_color = with_opacity(mix_color(PARCHMENT, WINE, active), opacity)
        text_color = with_opacity(mix_color(WINE_DARK, PARCHMENT_GLOW, active), opacity)
        accent_color = with_opacity(mix_color(GOLD_LINE, GOLD_SOFT, active * 0.7), opacity)

        draw_diagonal_fill(
            runtime.renderer,
            x + 7,
            draw_y + 8,
            draw_width,
            draw_height,
            diagonal_cut,
            shadow_color,
        )

        draw_diagonal_fill(
            runtime.renderer,
            x,
            draw_y,
            draw_width,
            draw_height,
            diagonal_cut,
            fill_color,
        )

        if self.flash_progress > 0.0:
            draw_diagonal_fill(
                runtime.renderer,
                x,
                draw_y,
                draw_width,
                draw_height,
                diagonal_cut,
                with_opacity(
                    mix_color(BLACK, WHITE, 0.8), opacity * self.flash_progress * 0.12
                ),
            )

        runtime.renderer.draw_rectangle(
            Rect(int(x + 16), int(draw_y + draw_height - 8), int(54 + active * 44), 4),
            accent_color,
        )
        runtime.renderer.draw_rectangle(
            Rect(int(x + 14), int(draw_y + 12), int(12 + active * 3), int(draw_height - 24)),
            with_opacity(mix_color(GOLD_SOFT, GOLD, active), opacity * (0.22 + active * 0.22)),
        )

        draw_text(
            self.label.upper(),
            x + 26 + active * 12,
            draw_y + (draw_height * 0.5) - 21 - active * 2,
            30 + active * 3.0,
            text_color,
            font_for("body"),
            1.4,
        )


class SettingsTabButton(Node):
    def __init__(self, tab: SettingsView, label: str, on_press):
        super().__init__(
            style=Style(
                width=Unit.percent(31.8),
                height=Unit.px(56),
                cursor=CursorType.POINTING_HAND,
            )
        )
        self.tab = tab
        self.label = label
        self._on_press = on_press
        self.hover_progress = 0.0
        self.hover_target = 0.0
        self.select_progress = 0.0
        self.select_target = 0.0
        self.on_hover_enter = self._handle_hover_enter
        self.on_hover_exit = self._handle_hover_exit
        self.on_click = self._handle_click

    def _handle_hover_enter(self) -> None:
        self.hover_target = 1.0

    def _handle_hover_exit(self) -> None:
        self.hover_target = 0.0

    def _handle_click(self) -> None:
        self._on_press(self.tab)

    def set_selected(self, selected: bool) -> None:
        self.select_target = 1.0 if selected else 0.0

    def tick(self, dt: float) -> None:
        self.hover_progress = ease_to(self.hover_progress, self.hover_target, 18.0, dt)
        self.select_progress = ease_to(
            self.select_progress, self.select_target, 12.0, dt
        )

    def render(self) -> None:
        if not self.style.visible or self.style.opacity <= 0.0:
            return

        runtime = get_runtime()
        x = self.computed_x
        y = self.computed_y
        width = self.computed_width
        height = self.computed_height
        opacity = clamp(self.style.opacity)
        active = clamp(self.select_progress + self.hover_progress * 0.65)
        fill_color = with_opacity(mix_color(PARCHMENT_SOFT, WINE_DARK, active), opacity)
        text_color = with_opacity(mix_color(INK, PARCHMENT_GLOW, active), opacity)

        runtime.renderer.draw_rectangle(
            Rect(int(x), int(y), int(width), int(height)),
            fill_color,
        )
        runtime.renderer.draw_rectangle(
            Rect(int(x), int(y + height - 2), int(width), 2),
            with_opacity(mix_color(GOLD_LINE, GOLD, active), opacity),
        )
        draw_text(
            self.label.upper(),
            x + 14,
            y + 14,
            18,
            text_color,
            font_for("meta"),
            1.3,
        )


class BackButton(Node):
    def __init__(self, label: str, on_press):
        super().__init__(
            style=Style(
                width=Unit.px(132),
                height=Unit.px(52),
                cursor=CursorType.POINTING_HAND,
            )
        )
        self.label = label
        self._on_press = on_press
        self.hover_progress = 0.0
        self.hover_target = 0.0
        self.on_hover_enter = self._handle_hover_enter
        self.on_hover_exit = self._handle_hover_exit
        self.on_click = self._handle_click

    def _handle_hover_enter(self) -> None:
        self.hover_target = 1.0

    def _handle_hover_exit(self) -> None:
        self.hover_target = 0.0

    def _handle_click(self) -> None:
        self._on_press()

    def tick(self, dt: float) -> None:
        self.hover_progress = ease_to(self.hover_progress, self.hover_target, 18.0, dt)

    def render(self) -> None:
        if not self.style.visible or self.style.opacity <= 0.0:
            return

        runtime = get_runtime()
        x = self.computed_x
        y = self.computed_y
        width = self.computed_width
        height = self.computed_height
        opacity = clamp(self.style.opacity)
        active = self.hover_progress
        fill_color = with_opacity(mix_color(WHITE, BLACK, active), opacity)
        text_color = with_opacity(mix_color(BLACK, WHITE, active), opacity)

        runtime.renderer.draw_rectangle(
            Rect(int(x), int(y), int(width), int(height)),
            fill_color,
        )
        runtime.renderer.draw_rectangle_lines_ex(
            Rect(int(x), int(y), int(width), int(height)),
            2,
            with_opacity(BLACK, opacity),
        )
        draw_text(
            self.label.upper(),
            x + 18,
            y + 14,
            18,
            text_color,
            font_for("meta"),
            1.3,
        )


class LoadingBar(Node):
    def __init__(self):
        super().__init__(
            style=Style(
                width=Unit.percent(100),
                height=Unit.px(14),
            )
        )
        self.progress = 0.0
        self.display_progress = 0.0

    def tick(self, dt: float) -> None:
        self.display_progress = ease_to(self.display_progress, self.progress, 8.5, dt)

    def render(self) -> None:
        if not self.style.visible or self.style.opacity <= 0.0:
            return

        runtime = get_runtime()
        x = self.computed_x
        y = self.computed_y
        width = self.computed_width
        height = self.computed_height
        opacity = clamp(self.style.opacity)

        runtime.renderer.draw_rectangle(
            Rect(int(x), int(y), int(width), int(height)),
            with_opacity(PARCHMENT_SOFT, opacity),
        )
        fill_width = max(0, int(width * clamp(self.display_progress)))
        if fill_width > 0:
            runtime.renderer.draw_rectangle(
                Rect(int(x), int(y), fill_width, int(height)),
                with_opacity(WINE, opacity),
            )
            runtime.renderer.draw_rectangle(
                Rect(int(max(x, x + fill_width - 18)), int(y), min(18, fill_width), int(height)),
                with_opacity(GOLD_SOFT, opacity * 0.55),
            )
        runtime.renderer.draw_rectangle(
            Rect(int(x), int(y), int(width), 1),
            with_opacity(GOLD_LINE, opacity),
        )
        runtime.renderer.draw_rectangle(
            Rect(int(x), int(y + height - 1), int(width), 1),
            with_opacity(GOLD_LINE, opacity),
        )


def create_slider_setting(
    title: str,
    value: float,
    *,
    min_value: float = 0.0,
    max_value: float = 100.0,
    suffix: str = "%",
) -> Node:
    container = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            gap=8,
        )
    )
    container.add_child(create_separator())

    row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.SPACE_BETWEEN,
            align_items=AlignItems.CENTER,
            gap=12,
        )
    )
    row.add_child(ui_text(title.upper(), 18, INK, role="body"))
    value_text = ui_text(f"{int(value)}{suffix}", 16, SOFT_BLACK, role="meta")
    row.add_child(value_text)

    slider = Slider(
        min_value=min_value,
        max_value=max_value,
        value=value,
        width=Unit.percent(100),
        height=Unit.px(28),
        track_color=PARCHMENT_SOFT,
        fill_color=WINE,
        thumb_color=GOLD,
        thumb_size=16.0,
        track_height=10.0,
        on_change=lambda new_value, text=value_text: setattr(
            text, "text", f"{int(new_value)}{suffix}"
        ),
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(28),
        ),
    )

    container.add_child(row)
    container.add_child(slider)
    return container


def create_toggle_setting(title: str, checked: bool) -> Node:
    container = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            gap=8,
        )
    )
    container.add_child(create_separator())

    row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.SPACE_BETWEEN,
            align_items=AlignItems.CENTER,
            gap=12,
        )
    )
    row.add_child(ui_text(title.upper(), 18, INK, role="body"))

    control = Node(
        style=Style(
            width=Unit.auto(),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=10,
            align_items=AlignItems.CENTER,
        )
    )
    state_text = ui_text("ON" if checked else "OFF", 16, SOFT_BLACK, role="meta")
    checkbox = Checkbox(
        checked=checked,
        color=WINE,
        unchecked_color=PARCHMENT_SOFT,
        size=24.0,
        on_change=lambda enabled, text=state_text: setattr(
            text, "text", "ON" if enabled else "OFF"
        ),
    )
    control.add_child(state_text)
    control.add_child(checkbox)
    row.add_child(control)

    container.add_child(row)
    return container


def create_credit_row(label: str, value: str) -> Node:
    row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            gap=6,
        )
    )
    row.add_child(create_separator())
    row.add_child(ui_text(label.upper(), 14, DIM_BLACK, role="meta"))
    row.add_child(ui_text(value, 18, INK, role="body"))
    return row


def create_changelog_entry(entry: ChangelogEntry) -> Node:
    row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            gap=6,
        )
    )
    row.add_child(create_separator())
    row.add_child(ui_text(entry.version, 10, GOLD_LINE, role="meta"))
    row.add_child(ui_text(entry.title.upper(), 11, WINE_DARK, role="body"))
    row.add_child(ui_text(entry.detail, 11, INK_SOFT, role="body"))
    return row


def create_panel_header(title: str, subtitle: str) -> Node:
    header = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            gap=14,
        )
    )

    top_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
        )
    )
    back_button = BackButton("Back", return_to_menu)
    back_buttons.append(back_button)
    top_row.add_child(back_button)

    header.add_child(top_row)
    header.add_child(ui_text(title, 46, BLACK, role="display"))
    header.add_child(ui_text(subtitle, 16, SOFT_BLACK, role="body"))
    header.add_child(create_separator(2.0, BLACK))
    return header


def build_loading_steps(active_index: int, complete: bool = False) -> str:
    lines = []
    for index, (_start, _target, label, _hint) in enumerate(LOADING_PHASES):
        if complete or index < active_index:
            prefix = "[OK]"
        elif index == active_index:
            prefix = "[>>]"
        else:
            prefix = "[  ]"
        lines.append(f"{prefix} {label}")
    return "\n".join(lines)


def finalize_view_hide(view: MainView) -> None:
    panel = view_panels.get(view)
    if panel is None or current_view == view.value:
        return
    panel.style.visible = False
    panel.style.left = Unit.px(0)
    panel.style.opacity = 0.0


def finalize_menu_hide() -> None:
    if menu_shell is None or current_view == MainView.IDLE.value:
        return
    menu_shell.style.visible = False
    menu_shell.style.left = Unit.px(0)
    menu_shell.style.opacity = 0.0


def finalize_detail_hide() -> None:
    if detail_shell is None or current_view != MainView.IDLE.value:
        return
    detail_shell.style.visible = False
    detail_shell.style.left = Unit.px(0)
    detail_shell.style.opacity = 0.0
    if detail_card is not None:
        detail_card.style.margin.top = Unit.px(0)


def finalize_settings_hide(view: SettingsView) -> None:
    panel = settings_panels.get(view)
    if panel is None or current_settings_view == view.value:
        return
    panel.style.visible = False
    panel.style.left = Unit.px(0)
    panel.style.opacity = 0.0


def switch_view(view: MainView, *, instant: bool = False, force: bool = False) -> None:
    global current_view

    if current_view == view.value and not force:
        return

    old_view = MainView(current_view)
    old_panel = view_panels.get(old_view)
    new_panel = view_panels.get(view)
    current_view = view.value

    show_menu = view == MainView.IDLE
    show_detail = view != MainView.IDLE

    if new_panel is None and show_detail:
        return

    if instant or ui_manager is None:
        if menu_shell is not None:
            menu_shell.style.visible = show_menu
            menu_shell.style.opacity = 1.0 if show_menu else 0.0
            menu_shell.style.left = Unit.px(0)
        if detail_shell is not None:
            detail_shell.style.visible = show_detail
            detail_shell.style.opacity = 1.0 if show_detail else 0.0
            detail_shell.style.left = Unit.px(0)
        if detail_card is not None:
            detail_card.style.margin.top = Unit.px(0)
        for panel_view, panel in view_panels.items():
            is_active = show_detail and panel_view == view
            panel.style.visible = is_active
            panel.style.opacity = 1.0 if is_active else 0.0
            panel.style.left = Unit.px(0)
        return

    if old_panel is not None and old_panel is not new_panel:
        ui_manager.animator.create().to(
            old_panel.style,
            "opacity",
            0.0,
            0.16,
            Easing.EASE_OUT_CUBIC,
        ).call(lambda closing=old_view: finalize_view_hide(closing)).start()
        ui_manager.animator.create().to(
            old_panel.style,
            "left",
            Unit.px(16),
            0.16,
            Easing.EASE_OUT_CUBIC,
        ).start()

    if show_menu:
        if detail_shell is not None:
            ui_manager.animator.create().to(
                detail_shell.style,
                "opacity",
                0.0,
                0.18,
                Easing.EASE_OUT_CUBIC,
            ).call(finalize_detail_hide).start()
        if detail_card is not None:
            ui_manager.animator.create().to(
                detail_card.style,
                "margin.top",
                Unit.px(18),
                0.18,
                Easing.EASE_OUT_CUBIC,
            ).start()
        if menu_shell is not None:
            menu_shell.style.visible = True
            menu_shell.style.opacity = 0.0
            menu_shell.style.left = Unit.px(-18)
            ui_manager.animator.create().to(
                menu_shell.style,
                "opacity",
                1.0,
                0.26,
                Easing.EASE_OUT_CUBIC,
            ).start()
            ui_manager.animator.create().to(
                menu_shell.style,
                "left",
                Unit.px(0),
                0.34,
                Easing.EASE_OUT_EXPO,
            ).start()
        return

    if menu_shell is not None:
        ui_manager.animator.create().to(
            menu_shell.style,
            "opacity",
            0.0,
            0.16,
            Easing.EASE_OUT_CUBIC,
        ).call(finalize_menu_hide).start()
        ui_manager.animator.create().to(
            menu_shell.style,
            "left",
            Unit.px(-22),
            0.18,
            Easing.EASE_OUT_CUBIC,
        ).start()

    if detail_shell is not None:
        detail_shell.style.visible = True
        if old_view == MainView.IDLE:
            detail_shell.style.opacity = 0.0
            detail_shell.style.left = Unit.px(0)
            ui_manager.animator.create().to(
                detail_shell.style,
                "opacity",
                1.0,
                0.22,
                Easing.EASE_OUT_CUBIC,
            ).start()

    if detail_card is not None and old_view == MainView.IDLE:
        detail_card.style.margin.top = Unit.px(20)
        ui_manager.animator.create().to(
            detail_card.style,
            "margin.top",
            Unit.px(0),
            0.30,
            Easing.EASE_OUT_EXPO,
        ).start()

    if new_panel is not None:
        new_panel.style.visible = True
        new_panel.style.opacity = 0.0
        new_panel.style.left = Unit.px(-18)
        ui_manager.animator.create().to(
            new_panel.style,
            "opacity",
            1.0,
            0.24,
            Easing.EASE_OUT_CUBIC,
        ).start()
        ui_manager.animator.create().to(
            new_panel.style,
            "left",
            Unit.px(0),
            0.30,
            Easing.EASE_OUT_EXPO,
        ).start()


def return_to_menu() -> None:
    stop_loading_sequence()
    set_active_menu(None)
    switch_view(MainView.IDLE)


def switch_settings_view(
    view: SettingsView,
    *,
    instant: bool = False,
    force: bool = False,
) -> None:
    global current_settings_view

    if current_settings_view == view.value and not force:
        return

    old_view = SettingsView(current_settings_view)
    old_panel = settings_panels.get(old_view)
    new_panel = settings_panels.get(view)
    current_settings_view = view.value

    for tab, button in settings_tab_buttons.items():
        button.set_selected(tab == view)

    if new_panel is None:
        return

    if instant or ui_manager is None:
        for panel_view, panel in settings_panels.items():
            panel.style.visible = panel_view == view
            panel.style.opacity = 1.0 if panel_view == view else 0.0
            panel.style.left = Unit.px(0)
        return

    if old_panel is not None and old_panel is not new_panel:
        ui_manager.animator.create().to(
            old_panel.style,
            "opacity",
            0.0,
            0.14,
            Easing.EASE_OUT_CUBIC,
        ).call(lambda closing=old_view: finalize_settings_hide(closing)).start()
        ui_manager.animator.create().to(
            old_panel.style,
            "left",
            Unit.px(14),
            0.14,
            Easing.EASE_OUT_CUBIC,
        ).start()

    new_panel.style.visible = True
    new_panel.style.opacity = 0.0
    new_panel.style.left = Unit.px(-14)
    ui_manager.animator.create().to(
        new_panel.style,
        "opacity",
        1.0,
        0.20,
        Easing.EASE_OUT_CUBIC,
    ).start()
    ui_manager.animator.create().to(
        new_panel.style,
        "left",
        Unit.px(0),
        0.26,
        Easing.EASE_OUT_EXPO,
    ).start()


def set_active_menu(key: str | None) -> None:
    global active_menu_key

    active_menu_key = key or ""
    for button_key, button in menu_buttons.items():
        button.set_selected(button_key == active_menu_key)


def stop_loading_sequence() -> None:
    global loading_active, loading_complete, loading_elapsed, loading_progress, loading_stage_index

    loading_active = False
    loading_complete = False
    loading_elapsed = 0.0
    loading_progress = 0.0
    loading_stage_index = -1
    if loading_bar is not None:
        loading_bar.progress = 0.0
        loading_bar.display_progress = 0.0
    if loading_percent_text is not None:
        loading_percent_text.text = "000%"
    if loading_status_text is not None:
        loading_status_text.text = "PRESS PLAY"
    if loading_hint_text is not None:
        loading_hint_text.text = "The loading panel only appears after you hit Play."
    if loading_steps_text is not None:
        loading_steps_text.text = build_loading_steps(-1, False)


def apply_loading_stage(index: int) -> None:
    global loading_stage_index

    if index == loading_stage_index:
        return

    loading_stage_index = index
    _start, _target, label, hint = LOADING_PHASES[index]
    if loading_status_text is not None:
        loading_status_text.text = label.upper()
    if loading_hint_text is not None:
        loading_hint_text.text = hint
    if loading_steps_text is not None:
        loading_steps_text.text = build_loading_steps(index, False)

    if ui_manager is not None and loading_status_text is not None:
        loading_status_text.style.opacity = 0.25
        ui_manager.animator.create().to(
            loading_status_text.style,
            "opacity",
            1.0,
            0.22,
            Easing.EASE_OUT_CUBIC,
        ).start()


def finalize_loading_sequence() -> None:
    global loading_complete

    if loading_complete:
        return

    loading_complete = True
    if loading_percent_text is not None:
        loading_percent_text.text = "100%"
    if loading_status_text is not None:
        loading_status_text.text = "SHORELINE READY"
    if loading_hint_text is not None:
        loading_hint_text.text = "The demo stops on the title screen after the handoff so the transition stays visible."
    if loading_steps_text is not None:
        loading_steps_text.text = build_loading_steps(len(LOADING_PHASES) - 1, True)


def begin_loading_sequence() -> None:
    global loading_active, loading_complete, loading_elapsed, loading_progress, loading_stage_index

    set_active_menu("play")
    stop_loading_sequence()
    switch_view(MainView.LOADING)
    loading_active = True
    loading_complete = False
    loading_elapsed = 0.0
    loading_progress = 0.0
    loading_stage_index = -1


def handle_menu_action(key: str) -> None:
    if key == "play":
        begin_loading_sequence()
        return

    if key == "settings":
        stop_loading_sequence()
        set_active_menu(key)
        switch_view(MainView.SETTINGS)
        return

    if key == "credits":
        stop_loading_sequence()
        set_active_menu(key)
        switch_view(MainView.CREDITS)
        return

    set_active_menu(key)
    rl.CloseWindow()


def tick_scene(time: Time) -> None:
    global scene_clock, loading_elapsed, loading_progress

    dt = time.delta_seconds
    scene_clock += dt

    for button in menu_buttons.values():
        button.tick(dt)
    for button in settings_tab_buttons.values():
        button.tick(dt)
    for button in back_buttons:
        button.tick(dt)
    if loading_bar is not None:
        loading_bar.tick(dt)

    if loading_active:
        loading_elapsed += dt

        active_index = 0
        target_progress = 0.0
        for index, (start_time, target, _label, _hint) in enumerate(LOADING_PHASES):
            if loading_elapsed >= start_time:
                active_index = index
                target_progress = target

        apply_loading_stage(active_index)
        loading_progress = ease_to(loading_progress, target_progress, 1.7, dt)
        if active_index == len(LOADING_PHASES) - 1 and loading_elapsed >= 4.1:
            loading_progress = ease_to(loading_progress, 1.0, 2.6, dt)

        if loading_bar is not None:
            loading_bar.progress = loading_progress
        if loading_percent_text is not None:
            loading_percent_text.text = f"{int(round(loading_progress * 100)):03d}%"

        if loading_elapsed >= 4.4 and loading_progress >= 0.995:
            finalize_loading_sequence()


def draw_cloud_overlays(renderer: Renderer2D, width: int, height: int) -> None:
    for index in range(5):
        offset = ((scene_clock * (15.0 + index * 1.4)) + index * 240.0) % (
            width + 360.0
        ) - 220.0
        y = int(height * (0.14 + index * 0.10))
        renderer.draw_rectangle(
            Rect(int(offset), y, int(260 + index * 110), int(22 + index * 8)),
            Color(250, 251, 255, 132 - index * 18),
        )


def render_background_system(renderer: Renderer2D) -> None:
    runtime = get_runtime()
    width, height = runtime.display.get_window_size()
    renderer.clear(WHITE)

    if background_shader is not None:
        renderer.set_shader_value(
            background_shader,
            ShaderUniformType.VEC2,
            "u_resolution",
            (float(width), float(height)),
        )
        renderer.set_shader_value(
            background_shader,
            ShaderUniformType.FLOAT,
            "u_time",
            float(scene_clock),
        )
        renderer.begin_shader_mode(background_shader)
        renderer.draw_rectangle(Rect(0, 0, width, height), WHITE)
        renderer.end_shader_mode()

    draw_cloud_overlays(renderer, width, height)


def create_idle_panel() -> Node:
    panel = create_stage_panel()
    panel.style.visible = True
    panel.style.opacity = 1.0
    return panel


def create_settings_page_video() -> Node:
    page = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(0),
            gap=12,
        )
    )
    page.add_child(create_slider_setting("Sky bloom", 92))
    page.add_child(create_slider_setting("Cloud drift", 64))
    page.add_child(create_slider_setting("Lantern sheen", 76))
    return page


def create_settings_page_sound() -> Node:
    page = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(0),
            gap=12,
        )
    )
    page.add_child(create_slider_setting("Hall volume", 84))
    page.add_child(create_slider_setting("String bed", 72))
    page.add_child(create_slider_setting("Chip clink", 68))
    return page


def create_settings_page_interface() -> Node:
    page = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(0),
            gap=12,
        )
    )
    page.add_child(create_toggle_setting("Compact HUD", True))
    page.add_child(create_toggle_setting("Win popups", True))
    page.add_child(create_toggle_setting("Larger prompts", False))
    return page


def create_settings_panel() -> Node:
    panel = create_stage_panel()
    panel.add_child(
        create_panel_header(
            "SETTINGS",
            "Adjust the presentation before dealing the first hand.",
        )
    )

    tabs_row = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            flex_direction=FlexDirection.ROW,
            gap=12,
        )
    )

    settings_tab_buttons.clear()
    for tab, label in (
        (SettingsView.VIDEO, "Video"),
        (SettingsView.SOUND, "Sound"),
        (SettingsView.INTERFACE, "Interface"),
    ):
        button = SettingsTabButton(tab, label, switch_settings_view)
        settings_tab_buttons[tab] = button
        tabs_row.add_child(button)
    panel.add_child(tabs_row)

    pages_stage = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.px(300),
        )
    )

    settings_panels.clear()
    settings_panels[SettingsView.VIDEO] = create_settings_page_video()
    settings_panels[SettingsView.SOUND] = create_settings_page_sound()
    settings_panels[SettingsView.INTERFACE] = create_settings_page_interface()

    for tab, page in settings_panels.items():
        page.style.visible = tab == SettingsView.VIDEO
        page.style.opacity = 1.0 if tab == SettingsView.VIDEO else 0.0
        pages_stage.add_child(page)

    panel.add_child(pages_stage)
    return panel


def create_credits_panel() -> Node:
    panel = create_stage_panel()
    panel.add_child(
        create_panel_header(
            "CREDITS",
            "The people and pieces behind this title screen pass.",
        )
    )
    panel.add_child(
        create_credit_row(
            "Concept",
            "Slot Island // a slot addict is summoned into another world to reclaim floating islands.",
        )
    )
    panel.add_child(
        create_credit_row(
            "Interface",
            "A left-rail menu with felt-and-parchment colors, cleaner view switching, and stronger hover feel.",
        )
    )
    panel.add_child(
        create_credit_row(
            "Atmosphere",
            "A blue-purple cloud shader now carries the whole title screen without floating island sprites.",
        )
    )
    panel.add_child(
        create_credit_row(
            "Fonts",
            "Dead Revolver display, game compact, and digital variants from the provided pack.",
        )
    )
    return panel


def create_loading_panel() -> Node:
    global loading_bar, loading_percent_text, loading_status_text, loading_hint_text, loading_steps_text

    panel = create_stage_panel()
    panel.add_child(
        create_panel_header(
            "LOADING",
            "A dedicated transition view before the first playable shore.",
        )
    )

    loading_percent_text = ui_text("000%", 44, BLACK, role="display")
    panel.add_child(loading_percent_text)

    loading_bar = LoadingBar()
    panel.add_child(loading_bar)

    loading_status_text = ui_text("PRESS PLAY", 18, BLACK, role="meta")
    loading_hint_text = ui_text(
        "The loading panel only appears after you hit Play.",
        16,
        INK_SOFT,
        role="body",
    )
    loading_steps_text = ui_text(
        build_loading_steps(-1, False), 16, INK_SOFT, role="body"
    )
    panel.add_child(loading_status_text)
    panel.add_child(loading_hint_text)
    panel.add_child(create_separator())
    panel.add_child(loading_steps_text)
    return panel


def create_changelog_panel() -> Node:
    global changelog_title

    panel = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.auto(),
            gap=10,
        )
    )
    changelog_title = ui_text("EARLY ACCESS LEDGER", 12, GOLD_LINE, role="meta")
    panel.add_child(changelog_title)
    for entry in CHANGELOG:
        panel.add_child(create_changelog_entry(entry))
    return panel


def create_ui() -> Node:
    global title_text, menu_shell, detail_shell, detail_card

    menu_buttons.clear()
    settings_tab_buttons.clear()
    view_panels.clear()
    settings_panels.clear()
    intro_nodes.clear()
    back_buttons.clear()

    root = Node(
        style=Style(
            width=Unit.vw(100),
            height=Unit.vh(100),
            padding=Spacing.all(0),
            gap=0,
        )
    )

    menu_shell = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(0),
        )
    )

    title_text = OutlinedTitle("SLOT ISLAND")
    title_text.style.position = PositionType.ABSOLUTE
    title_text.style.top = Unit.px(52)
    title_text.style.left = Unit.px(108)
    title_text.style.width = Unit.px(560)
    menu_shell.add_child(title_text)

    menu_stack = Node(
        style=Style(
            width=Unit.px(500),
            height=Unit.auto(),
            position=PositionType.ABSOLUTE,
            top=Unit.px(238),
            left=Unit.px(0),
            gap=0,
        )
    )
    for key, label in (
        ("play", "Play"),
        ("settings", "Settings"),
        ("credits", "Credits"),
        ("quit", "Quit"),
    ):
        button = MenuButton(key, label, handle_menu_action)
        menu_buttons[key] = button
        menu_stack.add_child(button)
    menu_shell.add_child(menu_stack)

    detail_shell = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            position=PositionType.ABSOLUTE,
            top=Unit.px(0),
            left=Unit.px(0),
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            padding=Spacing.symmetric(54, 88),
        )
    )
    detail_shell.style.visible = False
    detail_shell.style.opacity = 0.0

    detail_card = Node(
        style=Style(
            width=Unit.percent(58),
            height=Unit.px(612),
            background_color=WHITE,
            border_color=BLACK,
            border_width=3.0,
            padding=Spacing.all(30),
        )
    )

    content_stage = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
        )
    )
    view_panels[MainView.IDLE] = create_idle_panel()
    view_panels[MainView.SETTINGS] = create_settings_panel()
    view_panels[MainView.CREDITS] = create_credits_panel()
    view_panels[MainView.LOADING] = create_loading_panel()

    for panel in view_panels.values():
        content_stage.add_child(panel)
    detail_card.add_child(content_stage)
    detail_shell.add_child(detail_card)

    intro_nodes.append(title_text)
    root.add_child(menu_shell)
    root.add_child(detail_shell)
    return root


def start_intro() -> None:
    if ui_manager is None:
        return

    for index, node in enumerate(intro_nodes):
        node.style.opacity = 0.0
        node.style.margin.top = Unit.px(18)
        delay = index * 0.05
        ui_manager.animator.create().wait(delay).to(
            node.style,
            "opacity",
            1.0,
            0.32,
            Easing.EASE_OUT_CUBIC,
        ).start()
        ui_manager.animator.create().wait(delay).to(
            node.style,
            "margin.top",
            Unit.px(0),
            0.40,
            Easing.EASE_OUT_EXPO,
        ).start()

    for index, button in enumerate(menu_buttons.values()):
        button.style.opacity = 0.0
        button.slide_x = -54.0
        delay = 0.10 + index * 0.05
        ui_manager.animator.create().wait(delay).to(
            button.style,
            "opacity",
            1.0,
            0.20,
            Easing.EASE_OUT_CUBIC,
        ).start()
        ui_manager.animator.create().wait(delay).to(
            button,
            "slide_x",
            0.0,
            0.32,
            Easing.EASE_OUT_EXPO,
        ).start()


def main() -> None:
    global ui_manager, background_shader
    global scene_clock, current_view, current_settings_view, active_menu_key
    global loading_active, loading_complete, loading_elapsed, loading_progress, loading_stage_index

    scene_clock = 0.0
    current_view = MainView.IDLE.value
    current_settings_view = SettingsView.VIDEO.value
    active_menu_key = ""
    loading_active = False
    loading_complete = False
    loading_elapsed = 0.0
    loading_progress = 0.0
    loading_stage_index = -1

    rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE | rl.FLAG_MSAA_4X_HINT)

    game = ArepyEngine(
        title="Slot Island // Title Screen",
        width=1366,
        height=768,
    )
    world = game.create_world("slot_island_title")

    ui_manager = UIManager.install(
        world,
        config=UIConfig(
            resize_mode=ResizeMode.RESPONSIVE,
            font_texture_filter=TextureFilter.NEAREST,
        ),
    )

    setup_demo_fonts()
    ui_manager.set_font_texture_filter(TextureFilter.NEAREST)
    ui_manager.set_root(create_ui())

    switch_view(MainView.IDLE, instant=True, force=True)
    switch_settings_view(SettingsView.VIDEO, instant=True, force=True)
    stop_loading_sequence()
    set_active_menu(None)

    renderer = world.get_resource(Renderer2D)
    background_shader = renderer.compile_shader(fragment_source=FRAGMENT_SHADER)

    world.add_system(SystemPipeline.UPDATE, tick_scene)
    world.add_system(SystemPipeline.RENDER, render_background_system)
    world.on_startup(start_intro)

    @world.on_shutdown
    def cleanup_shader() -> None:
        if background_shader is not None:
            renderer.unload_shader(background_shader)

    game.set_current_world("slot_island_title")
    game.run()


if __name__ == "__main__":
    main()
