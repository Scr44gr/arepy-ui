from typing import Callable, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, Unit
from ..runtime import MOUSE_BUTTON_LEFT, get_runtime


class Checkbox(Node):
    """Modern checkbox with animation-ready design."""

    def __init__(
        self,
        checked: bool = False,
        on_change: Optional[Callable[[bool], None]] = None,
        label: str = "",
        size: float = 22.0,
        color: Color = Color(0, 150, 255, 255),
        hover_color: Optional[Color] = None,
        pressed_color: Optional[Color] = None,
        unchecked_color: Color = Color(50, 52, 60, 255),
        label_color: Optional[Color] = None,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=Unit.px(size),
            height=Unit.px(size),
        )

        super().__init__(style=style or default_style, **kwargs)

        self.checked = checked
        self.on_change = on_change
        self.label = label
        self.check_color = color
        self.hover_color = hover_color or Color(
            min(255, color.r + 30),
            min(255, color.g + 30),
            min(255, color.b + 30),
            color.a,
        )
        self.pressed_color = pressed_color or Color(
            max(0, color.r - 40),
            max(0, color.g - 40),
            max(0, color.b - 40),
            color.a,
        )
        self.unchecked_color = unchecked_color
        self.label_color = label_color or Color(220, 220, 230, 255)
        self.size = size
        self.is_hovered = False
        self._is_pressed = False
        self.label_gap = 10
        self.font_size = 14

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        label_width = 0
        if self.label:
            label_width = (
                runtime.renderer.measure_text(self.label, self.font_size)
                + self.label_gap
            )

        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width + label_width),
            int(self.computed_height),
        )
        is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)
        is_mouse_down = runtime.input.is_mouse_button_down(MOUSE_BUTTON_LEFT)

        self.is_hovered = is_over

        # Track pressed state
        if is_over and is_mouse_down:
            self._is_pressed = True
        elif not is_mouse_down:
            self._is_pressed = False

        if is_click and is_over:
            self.checked = not self.checked
            if self.on_change:
                self.on_change(self.checked)
            return True

        return is_over

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        x = self.computed_x
        y = self.computed_y
        size = self.size

        # Background
        rect = Rect(x, y, int(size), int(size))
        WHITE = Color(255, 255, 255, 255)

        if self.checked:
            # Filled background when checked
            if self._is_pressed:
                bg_color = self.pressed_color
            elif self.is_hovered:
                bg_color = self.hover_color
            else:
                bg_color = self.check_color
            runtime.renderer.draw_rectangle_rounded(rect, 0.25, 6, bg_color)

            # Draw checkmark
            check_padding = size * 0.25
            cx = x + check_padding
            cy = y + size * 0.5

            # Checkmark path
            runtime.renderer.draw_line_ex(
                (cx, cy), (cx + size * 0.15, cy + size * 0.2), 2.5, WHITE
            )
            runtime.renderer.draw_line_ex(
                (cx + size * 0.15, cy + size * 0.2),
                (cx + size * 0.45, cy - size * 0.2),
                2.5,
                WHITE,
            )
        else:
            # Empty box - use unchecked_color with hover/pressed variants
            if self._is_pressed:
                bg_color = Color(
                    max(0, self.unchecked_color.r - 10),
                    max(0, self.unchecked_color.g - 10),
                    max(0, self.unchecked_color.b - 10),
                    self.unchecked_color.a,
                )
            elif self.is_hovered:
                bg_color = Color(
                    min(255, self.unchecked_color.r + 10),
                    min(255, self.unchecked_color.g + 10),
                    min(255, self.unchecked_color.b + 10),
                    self.unchecked_color.a,
                )
            else:
                bg_color = self.unchecked_color

            runtime.renderer.draw_rectangle_rounded(rect, 0.25, 6, bg_color)

            # Border
            border_color = (
                Color(80, 82, 90, 255)
                if not self.is_hovered
                else Color(100, 102, 110, 255)
            )
            runtime.renderer.draw_rectangle_rounded_lines(rect, 0.25, 6, border_color)

        # Draw label
        if self.label:
            label_x = x + size + self.label_gap
            label_y = y + (size - self.font_size) / 2
            runtime.renderer.draw_text(
                self.label,
                (int(label_x), int(label_y)),
                self.font_size,
                self.label_color,
            )
