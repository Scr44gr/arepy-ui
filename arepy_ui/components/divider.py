"""Divider component - Visual separator line."""

from enum import Enum
from typing import Optional

from arepy.engine.renderer import Rect

from ..core.node import Node
from ..core.style import Spacing, Style
from ..core.types import Color, Unit
from ..runtime import get_runtime


class DividerOrientation(Enum):
    """Divider orientation."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Divider(Node):
    """
    Divider/Separator component.

    A simple visual line to separate content sections.

    Features:
    - Horizontal or vertical orientation
    - Customizable thickness and color
    - Optional margins
    - Optional label (for horizontal dividers)
    """

    def __init__(
        self,
        orientation: DividerOrientation = DividerOrientation.HORIZONTAL,
        thickness: int = 1,
        color: Optional[Color] = None,
        width: Optional[Unit] = None,
        height: Optional[Unit] = None,
        style: Optional[Style] = None,
        label: str = "",
        label_position: str = "center",  # "left", "center", "right"
        **kwargs,
    ):
        # Default dimensions based on orientation
        if orientation == DividerOrientation.HORIZONTAL:
            default_width = width or Unit.percent(100)
            default_height = height or Unit.px(thickness)
        else:
            default_width = width or Unit.px(thickness)
            default_height = height or Unit.percent(100)

        default_style = Style(
            width=default_width,
            height=default_height,
            margin=(
                Spacing.symmetric(vertical=8, horizontal=0)
                if orientation == DividerOrientation.HORIZONTAL
                else Spacing.symmetric(vertical=0, horizontal=8)
            ),
        )

        if style:
            for attr in vars(style):
                val = getattr(style, attr)
                if val is not None:
                    setattr(default_style, attr, val)
            style = default_style
        else:
            style = default_style

        super().__init__(style=style, **kwargs)

        self.orientation = orientation
        self.thickness = thickness
        self.divider_color = color or Color(60, 60, 70, 255)
        self.label = label
        self.label_position = label_position

        # Label config
        self.label_color = Color(120, 120, 130, 255)
        self.font_size = 12
        self.label_padding = 12

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        # No interaction for divider
        return False

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()

        if self.orientation == DividerOrientation.HORIZONTAL:
            self._render_horizontal(runtime)
        else:
            self._render_vertical(runtime)

        # Render children
        for child in self.children:
            child.render()

    def _render_horizontal(self, runtime):
        """Render horizontal divider."""
        line_y = self.computed_y + self.computed_height / 2

        if self.label:
            # Divider with label
            label_width = runtime.renderer.measure_text(self.label, self.font_size)
            total_label_width = label_width + self.label_padding * 2

            # Calculate label position
            if self.label_position == "left":
                label_x = self.computed_x + self.label_padding
            elif self.label_position == "right":
                label_x = (
                    self.computed_x
                    + self.computed_width
                    - label_width
                    - self.label_padding
                )
            else:  # center
                label_x = self.computed_x + (self.computed_width - label_width) / 2

            # Draw left line
            left_line_end = label_x - self.label_padding
            if left_line_end > self.computed_x:
                runtime.renderer.draw_rectangle(
                    Rect(
                        int(self.computed_x),
                        int(line_y - self.thickness / 2),
                        int(left_line_end - self.computed_x),
                        self.thickness,
                    ),
                    self.divider_color,
                )

            # Draw label
            label_y = self.computed_y + (self.computed_height - self.font_size) / 2
            runtime.renderer.draw_text(
                self.label,
                (int(label_x), int(label_y)),
                self.font_size,
                self.label_color,
            )

            # Draw right line
            right_line_start = label_x + label_width + self.label_padding
            if right_line_start < self.computed_x + self.computed_width:
                runtime.renderer.draw_rectangle(
                    Rect(
                        int(right_line_start),
                        int(line_y - self.thickness / 2),
                        int(self.computed_x + self.computed_width - right_line_start),
                        self.thickness,
                    ),
                    self.divider_color,
                )
        else:
            # Simple line
            runtime.renderer.draw_rectangle(
                Rect(
                    int(self.computed_x),
                    int(line_y - self.thickness / 2),
                    int(self.computed_width),
                    self.thickness,
                ),
                self.divider_color,
            )

    def _render_vertical(self, runtime):
        """Render vertical divider."""
        line_x = self.computed_x + self.computed_width / 2

        runtime.renderer.draw_rectangle(
            Rect(
                int(line_x - self.thickness / 2),
                int(self.computed_y),
                self.thickness,
                int(self.computed_height),
            ),
            self.divider_color,
        )
