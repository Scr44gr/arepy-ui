from typing import Callable, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Spacing, Style, merge_style_fields
from ..core.types import AlignItems, Color, CursorType, JustifyContent, Unit
from ..runtime import MOUSE_BUTTON_LEFT, get_runtime
from .text import Text


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

        merge_style_fields(
            default_style,
            style,
            ("margin", "position", "top", "left"),
        )

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
        self.add_child(self.text_node)

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

        self.on_hover_enter = self._on_enter
        self.on_hover_exit = self._on_exit

    def _on_enter(self):
        if not self._is_pressed:
            self.style.background_color = self.hover_color

    def _on_exit(self):
        self._is_pressed = False
        self.style.background_color = self.base_color

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )
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
