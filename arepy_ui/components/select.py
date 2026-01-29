from typing import Callable, List, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Spacing, Style
from ..core.types import AlignItems, Color, Unit
from ..manager import register_overlay
from ..runtime import MOUSE_BUTTON_LEFT, get_runtime


class Select(Node):
    """Dropdown select component with overlay rendering."""

    def __init__(
        self,
        options: List[str],
        on_change: Optional[Callable[[int, str], None]] = None,
        width: Unit = Unit.px(150),
        height: Unit = Unit.px(40),
        bg_color: Color = Color(50, 52, 60, 255),
        hover_color: Optional[Color] = None,
        pressed_color: Optional[Color] = None,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=bg_color,
            border_width=1.0,
            border_color=Color(70, 72, 80, 255),
            border_radius=6.0,
            padding=Spacing.symmetric(8, 12),
            align_items=AlignItems.CENTER,
        )
        super().__init__(style=style or default_style, **kwargs)

        self.options = options
        self.on_change = on_change
        self.selected_index = 0
        self.is_open = False
        self.font_size = 16
        self.is_hovered = False
        self._is_pressed = False
        self._hovered_option = -1

        # Configurable colors
        self.base_color = bg_color
        self.hover_color = hover_color or Color(
            min(255, bg_color.r + 10),
            min(255, bg_color.g + 10),
            min(255, bg_color.b + 10),
            bg_color.a,
        )
        self.pressed_color = pressed_color or Color(
            max(0, bg_color.r - 15),
            max(0, bg_color.g - 15),
            max(0, bg_color.b - 15),
            bg_color.a,
        )

        # Store visual position at render time for dropdown
        self._render_x = 0.0
        self._render_y = 0.0

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        main_rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )
        is_over_main = check_collision_point_rec((mouse_pos.x, mouse_pos.y), main_rect)
        is_mouse_down = runtime.input.is_mouse_button_down(MOUSE_BUTTON_LEFT)

        self.is_hovered = is_over_main
        self._hovered_option = -1

        # Track pressed state
        if is_over_main and is_mouse_down and not self.is_open:
            self._is_pressed = True
        elif not is_mouse_down:
            self._is_pressed = False

        # If dropdown is open, check options using stored render position
        if self.is_open:
            actual_mouse = runtime.input.get_mouse_position()

            dropdown_y = self._render_y + self.computed_height + 4
            option_height = 36

            for i, option in enumerate(self.options):
                option_rect = Rect(
                    self._render_x,
                    dropdown_y + i * option_height,
                    int(self.computed_width),
                    option_height,
                )

                if check_collision_point_rec(
                    (actual_mouse[0], actual_mouse[1]), option_rect
                ):
                    self._hovered_option = i
                    if is_click:
                        self.selected_index = i
                        self.is_open = False
                        if self.on_change:
                            self.on_change(i, option)
                        return True
                    return True

            # Click outside closes dropdown
            if is_click:
                self.is_open = False
                if is_over_main:
                    return True
                return False

        # Main box click
        if is_click and is_over_main:
            self.is_open = not self.is_open
            return True

        return is_over_main

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()

        # Store current visual position for dropdown
        self._render_x = self.computed_x
        self._render_y = self.computed_y

        main_rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )

        # Background
        if self._is_pressed:
            bg_color = self.pressed_color
        elif self.is_hovered or self.is_open:
            bg_color = self.hover_color
        else:
            bg_color = self.base_color

        runtime.renderer.draw_rectangle_rounded(main_rect, 0.3, 6, bg_color)

        # Border
        border_color = (
            Color(0, 150, 255, 255)
            if self.is_open
            else (self.style.border_color or Color(70, 72, 80, 255))
        )
        runtime.renderer.draw_rectangle_rounded_lines(main_rect, 0.3, 6, border_color)

        # Selected text
        text = self.options[self.selected_index] if self.options else ""
        text_x = self.computed_x + 12
        text_y = self.computed_y + (self.computed_height - self.font_size) / 2
        runtime.renderer.draw_text(
            text, (int(text_x), int(text_y)), self.font_size, Color(220, 220, 220, 255)
        )

        # Arrow
        arrow_x = self.computed_x + self.computed_width - 24
        arrow_y = self.computed_y + self.computed_height / 2

        ARROW_COLOR = Color(150, 150, 150, 255)
        if self.is_open:
            runtime.renderer.draw_line_ex(
                (arrow_x, arrow_y + 2), (arrow_x + 5, arrow_y - 3), 2, ARROW_COLOR
            )
            runtime.renderer.draw_line_ex(
                (arrow_x + 5, arrow_y - 3), (arrow_x + 10, arrow_y + 2), 2, ARROW_COLOR
            )
        else:
            runtime.renderer.draw_line_ex(
                (arrow_x, arrow_y - 2), (arrow_x + 5, arrow_y + 3), 2, ARROW_COLOR
            )
            runtime.renderer.draw_line_ex(
                (arrow_x + 5, arrow_y + 3), (arrow_x + 10, arrow_y - 2), 2, ARROW_COLOR
            )

        # Register dropdown as overlay
        if self.is_open:
            register_overlay(self._render_dropdown)

    def _render_dropdown(self):
        """Render dropdown as overlay."""
        runtime = get_runtime()
        dropdown_y = self._render_y + self.computed_height + 4
        option_height = 36
        dropdown_height = len(self.options) * option_height
        padding = 4

        # Shadow
        shadow_rect = Rect(
            self._render_x + 3,
            dropdown_y + 3,
            int(self.computed_width),
            int(dropdown_height + padding * 2),
        )
        runtime.renderer.draw_rectangle_rounded(shadow_rect, 0.2, 6, Color(0, 0, 0, 60))

        # Dropdown background
        dropdown_rect = Rect(
            self._render_x,
            dropdown_y,
            int(self.computed_width),
            int(dropdown_height + padding * 2),
        )
        runtime.renderer.draw_rectangle_rounded(
            dropdown_rect, 0.2, 6, Color(45, 47, 55, 255)
        )
        runtime.renderer.draw_rectangle_rounded_lines(
            dropdown_rect, 0.2, 6, Color(70, 72, 80, 255)
        )

        # Options
        for i, option in enumerate(self.options):
            option_y = dropdown_y + padding + i * option_height
            option_rect = Rect(
                self._render_x + 4,
                option_y,
                int(self.computed_width - 8),
                int(option_height),
            )

            # Highlight
            if i == self._hovered_option:
                runtime.renderer.draw_rectangle_rounded(
                    option_rect, 0.3, 4, Color(60, 100, 180, 255)
                )
            elif i == self.selected_index:
                runtime.renderer.draw_rectangle_rounded(
                    option_rect, 0.3, 4, Color(50, 52, 60, 255)
                )

            # Option text
            text_y = option_y + (option_height - self.font_size) / 2
            runtime.renderer.draw_text(
                option,
                (int(self._render_x + 12), int(text_y)),
                self.font_size,
                Color(220, 220, 220, 255),
            )
