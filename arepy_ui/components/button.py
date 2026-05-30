import math
from typing import Callable, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core import fonts as font_utils
from ..core.node import Node
from ..core.style import Spacing, Style, merge_style_fields
from ..core.types import AlignItems, Color, CursorType, JustifyContent, Unit
from ..runtime import MOUSE_BUTTON_LEFT, get_runtime
from .text import Text


_BUTTON_MERGE_FIELDS = ("margin", "position", "top", "left")
_VISUAL_TRANSFORM_EPSILON = 0.001


class Button(Node):
    def __init__(
        self,
        text: str,
        on_click: Callable[[], None],
        width: Unit = Unit.px(120),
        height: Unit = Unit.px(40),
        bg_color: Color = Color(0, 122, 204, 255),
        text_color: Color = Color(255, 255, 255, 255),
        border_radius: float = 8.0,
        font_size: float = 12.0,
        hover_color: Optional[Color] = None,
        pressed_color: Optional[Color] = None,
        pressed_scale: float = 0.98,
        style: Optional[Style] = None,
        font_name: Optional[str] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=bg_color,
            border_radius=border_radius,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            padding=Spacing.symmetric(8, 16),
            cursor=CursorType.POINTING_HAND,
        )

        if style is not None:
            merge_style_fields(default_style, style, _BUTTON_MERGE_FIELDS)

        super().__init__(style=default_style, **kwargs)

        self.on_click = on_click

        # Add Text Child with specified font size
        self.text_node = Text(
            text,
            size=font_size,
            color=text_color,
            font_name=font_name,
        )
        self.text_node.pickable = False  # Text should not block button click
        self.text_node.parent = self
        self.children.append(self.text_node)

        # Button states
        self.base_color = bg_color
        self.hover_color = hover_color or Color(
            min(bg_color.r + 20, 255),
            min(bg_color.g + 20, 255),
            min(bg_color.b + 20, 255),
            bg_color.a,
        )
        self.pressed_color = pressed_color or Color(
            max(bg_color.r - 30, 0),
            max(bg_color.g - 30, 0),
            max(bg_color.b - 30, 0),
            bg_color.a,
        )
        self.pressed_scale = pressed_scale
        self._is_pressed = False

        # Optional render-time transform state. These do not affect layout.
        self.visual_scale_x = 1.0
        self.visual_scale_y = 1.0
        self.visual_rotation_degrees = 0.0
        self.text_spacing = 1.0
        self.render_via_texture = False
        self._visual_texture = None
        self._visual_texture_skin_key = None

        self.on_hover_enter = self._on_enter
        self.on_hover_exit = self._on_exit

    def __del__(self):
        try:
            self._dispose_visual_texture()
        except Exception:
            pass

    def _visual_transform_active(self) -> bool:
        return (
            self.render_via_texture
            or abs(self.visual_scale_x - 1.0) > _VISUAL_TRANSFORM_EPSILON
            or abs(self.visual_scale_y - 1.0) > _VISUAL_TRANSFORM_EPSILON
            or abs(self.visual_rotation_degrees) > _VISUAL_TRANSFORM_EPSILON
            or abs(self.text_spacing - 1.0) > _VISUAL_TRANSFORM_EPSILON
        )

    def _should_render_via_texture(self) -> bool:
        return (
            self._visual_transform_active()
            and len(self.children) == 1
            and self.children[0] is self.text_node
        )

    def _get_visual_rect(self) -> Rect:
        scaled_width = max(1, int(round(self.computed_width * self.visual_scale_x)))
        scaled_height = max(1, int(round(self.computed_height * self.visual_scale_y)))
        visual_x = self.computed_x + (self.computed_width - scaled_width) / 2
        visual_y = self.computed_y + (self.computed_height - scaled_height) / 2
        return Rect(visual_x, visual_y, scaled_width, scaled_height)

    def _get_visual_bounds(self) -> Rect:
        visual_rect = self._get_visual_rect()
        if abs(self.visual_rotation_degrees) <= _VISUAL_TRANSFORM_EPSILON:
            return visual_rect

        radians = math.radians(self.visual_rotation_degrees)
        sin_rotation = abs(math.sin(radians))
        cos_rotation = abs(math.cos(radians))
        bound_width = max(
            1,
            int(
                math.ceil(
                    visual_rect.width * cos_rotation
                    + visual_rect.height * sin_rotation
                )
            ),
        )
        bound_height = max(
            1,
            int(
                math.ceil(
                    visual_rect.width * sin_rotation
                    + visual_rect.height * cos_rotation
                )
            ),
        )
        center_x = self.computed_x + self.computed_width / 2
        center_y = self.computed_y + self.computed_height / 2
        return Rect(
            center_x - bound_width / 2,
            center_y - bound_height / 2,
            bound_width,
            bound_height,
        )

    def _get_hit_rect(self) -> Rect:
        if self._visual_transform_active():
            return self._get_visual_bounds()
        return Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )

    def _dispose_visual_texture(self, runtime=None) -> None:
        if self._visual_texture is None:
            return

        try:
            active_runtime = runtime or get_runtime()
            active_runtime.renderer.unload_texture(self._visual_texture)
        except Exception:
            pass

        self._visual_texture = None
        self._visual_texture_skin_key = None

    def _color_key(self, color: Optional[Color]) -> Optional[tuple[int, int, int, int]]:
        if color is None:
            return None
        return (int(color.r), int(color.g), int(color.b), int(color.a))

    def _apply_opacity(self, color: Color, opacity: float) -> Color:
        alpha = max(0, min(255, int(round(color.a * opacity))))
        return Color(color.r, color.g, color.b, alpha)

    def _render_button_frame(self, runtime, rect: Rect, opacity: float) -> None:
        fill_color = (
            self._apply_opacity(self.style.background_color, opacity)
            if self.style.background_color
            else None
        )
        border_color = (
            self._apply_opacity(self.style.border_color, opacity)
            if self.style.border_width > 0 and self.style.border_color
            else None
        )

        if self.style.border_radius > 0 and border_color is not None and fill_color is not None:
            min_dim = min(rect.width, rect.height)
            roundness = self.style.border_radius / min_dim if min_dim > 0 else 0
            runtime.renderer.draw_rectangle_rounded(rect, roundness, 10, border_color)

            inset = min(
                float(self.style.border_width),
                max(0.0, rect.width / 2),
                max(0.0, rect.height / 2),
            )
            inner_width = max(0, int(round(rect.width - inset * 2)))
            inner_height = max(0, int(round(rect.height - inset * 2)))
            if inner_width > 0 and inner_height > 0:
                inner_rect = Rect(rect.x + inset, rect.y + inset, inner_width, inner_height)
                inner_radius = max(0.0, self.style.border_radius - inset)
                inner_roundness = (
                    inner_radius / min(inner_width, inner_height)
                    if min(inner_width, inner_height) > 0
                    else 0
                )
                runtime.renderer.draw_rectangle_rounded(
                    inner_rect,
                    inner_roundness,
                    10,
                    fill_color,
                )
            return

        if fill_color is not None:
            if self.style.border_radius > 0:
                min_dim = min(rect.width, rect.height)
                roundness = self.style.border_radius / min_dim if min_dim > 0 else 0
                runtime.renderer.draw_rectangle_rounded(rect, roundness, 10, fill_color)
            elif abs(self.visual_rotation_degrees) > _VISUAL_TRANSFORM_EPSILON:
                runtime.renderer.draw_rectangle_ex(
                    rect,
                    self.visual_rotation_degrees,
                    fill_color,
                )
            else:
                runtime.renderer.draw_rectangle(rect, fill_color)

        if border_color is not None:
            if self.style.border_radius > 0:
                min_dim = min(rect.width, rect.height)
                roundness = self.style.border_radius / min_dim if min_dim > 0 else 0
                runtime.renderer.draw_rectangle_rounded_lines(
                    rect,
                    roundness,
                    10,
                    border_color,
                )
            else:
                runtime.renderer.draw_rectangle_lines_ex(
                    rect,
                    self.style.border_width,
                    border_color,
                )

    def _get_visual_texture_skin_key(
        self,
        texture_width: int,
        texture_height: int,
    ) -> tuple:
        local_text_x = round(self.text_node.computed_x - self.computed_x, 3)
        local_text_y = round(self.text_node.computed_y - self.computed_y, 3)
        return (
            texture_width,
            texture_height,
            self._color_key(self.style.background_color),
            self._color_key(self.style.border_color),
            round(self.style.border_width, 3),
            round(self.style.border_radius, 3),
            self.text_node.text,
            self._color_key(self.text_node.color),
            round(self.text_node.font_size, 3),
            self.text_node.font_name,
            round(self.text_spacing, 3),
            local_text_x,
            local_text_y,
        )

    def _ensure_visual_texture(self, runtime) -> None:
        texture_width = max(1, int(round(self.computed_width)))
        texture_height = max(1, int(round(self.computed_height)))
        texture_size = (texture_width, texture_height)

        if (
            self._visual_texture is None
            or self._visual_texture.get_size() != texture_size
        ):
            self._dispose_visual_texture(runtime)
            self._visual_texture = runtime.renderer.create_render_texture(
                texture_width,
                texture_height,
            )
            self._visual_texture_skin_key = None

        skin_key = self._get_visual_texture_skin_key(texture_width, texture_height)
        if self._visual_texture_skin_key == skin_key:
            return

        runtime.renderer.bind_render_texture(self._visual_texture)
        runtime.renderer.clear(Color(0, 0, 0, 0))

        local_rect = Rect(0, 0, texture_width, texture_height)
        self._render_button_frame(runtime, local_rect, 1.0)
        font_utils.get_font_manager().draw_text(
            self.text_node.text,
            self.text_node.computed_x - self.computed_x,
            self.text_node.computed_y - self.computed_y,
            self.text_node.font_size,
            self.text_node.color,
            self.text_node.font_name,
            self.text_spacing,
        )

        runtime.renderer.unbind_render_texture()
        self._visual_texture_skin_key = skin_key

    def _on_enter(self):
        if not self._is_pressed:
            self.style.background_color = self.hover_color

    def _on_exit(self):
        self._is_pressed = False
        self.style.background_color = self.base_color

    def render(self):
        if not self.style.visible or self.style.opacity <= 0:
            return

        runtime = get_runtime()
        screen_w, screen_h = runtime.display.get_window_size()
        visual_bounds = self._get_hit_rect()

        if (
            visual_bounds.x > screen_w
            or visual_bounds.x + visual_bounds.width < 0
            or visual_bounds.y > screen_h
            or visual_bounds.y + visual_bounds.height < 0
        ):
            return

        if self._should_render_via_texture():
            self._ensure_visual_texture(runtime)
            if self._visual_texture is not None:
                texture_width, texture_height = self._visual_texture.get_size()
                visual_rect = self._get_visual_rect()
                draw_rect = Rect(
                    self.computed_x + self.computed_width / 2,
                    self.computed_y + self.computed_height / 2,
                    visual_rect.width,
                    visual_rect.height,
                )
                runtime.renderer.draw_texture_ex(
                    self._visual_texture,
                    Rect(0, 0, texture_width, -texture_height),
                    draw_rect,
                    (visual_rect.width / 2, visual_rect.height / 2),
                    self.visual_rotation_degrees,
                    Color(255, 255, 255, int(round(255 * self.style.opacity))),
                )

            for child in self.children:
                if child is not self.text_node:
                    child.render()
            return

        visual_rect = self._get_visual_rect()
        self._render_button_frame(runtime, visual_rect, self.style.opacity)
        for child in self.children:
            child.render()

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        rect = self._get_hit_rect()
        is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)
        is_mouse_down = runtime.input.is_mouse_button_down(MOUSE_BUTTON_LEFT)

        # Update hover state
        if is_over:
            if not self.is_hovered:
                self.is_hovered = True
                if self.on_hover_enter:
                    self.on_hover_enter()

            # Handle pressed state
            if is_mouse_down:
                if not self._is_pressed:
                    self._is_pressed = True
                    self.style.background_color = self.pressed_color
            else:
                if self._is_pressed:
                    self._is_pressed = False
                    self.style.background_color = self.hover_color

            # Handle click
            if is_click and self.on_click:
                self.on_click()
                return True
        else:
            if self.is_hovered:
                self.is_hovered = False
                self._is_pressed = False
                if self.on_hover_exit:
                    self.on_hover_exit()

        return False
