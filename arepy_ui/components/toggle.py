"""Toggle/Switch component - Visual toggle switch."""

from typing import Callable, Optional

from arepy import CursorType
from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, Unit
from ..runtime import get_runtime


class Toggle(Node):
    """
    Toggle switch component.

    A visual alternative to checkbox with smooth animation.

    Features:
    - Smooth animated toggle
    - Customizable colors
    - Disabled state
    - Label support
    """

    def __init__(
        self,
        checked: bool = False,
        width: Unit = Unit.px(50),
        height: Unit = Unit.px(26),
        style: Optional[Style] = None,
        on_change: Optional[Callable[[bool], None]] = None,
        label: str = "",
        disabled: bool = False,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            cursor=CursorType.POINTING_HAND if not disabled else CursorType.DEFAULT,
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

        self.checked = checked
        self.on_change = on_change
        self.label = label
        self.disabled = disabled

        # Animation state
        self._animation_progress = 1.0 if checked else 0.0
        self._animation_speed = 8.0

        # Colors
        self.track_color_off = Color(70, 70, 80, 255)
        self.track_color_on = Color(80, 140, 220, 255)
        self.track_color_disabled = Color(50, 50, 55, 255)
        self.thumb_color = Color(255, 255, 255, 255)
        self.thumb_color_disabled = Color(150, 150, 150, 255)
        self.label_color = Color(220, 220, 230, 255)
        self.label_color_disabled = Color(100, 100, 110, 255)

        # Sizes
        self.thumb_padding = 3
        self.label_gap = 10
        self.font_size = 14

    def toggle(self):
        """Toggle the switch."""
        if not self.disabled:
            self.checked = not self.checked
            if self.on_change:
                self.on_change(self.checked)

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible or self.disabled:
            return False

        # Calculate hitbox (including label)
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
        is_inside = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        if is_click and is_inside:
            self.toggle()
            return True

        return False

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        dt = runtime.renderer.get_delta_time()

        # Animate progress
        target = 1.0 if self.checked else 0.0
        if self._animation_progress != target:
            direction = 1 if target > self._animation_progress else -1
            self._animation_progress += direction * dt * self._animation_speed
            self._animation_progress = max(0.0, min(1.0, self._animation_progress))

        # Track dimensions
        track_width = self.computed_width
        track_height = self.computed_height
        track_x = self.computed_x
        track_y = self.computed_y

        # Track color (interpolate)
        if self.disabled:
            track_color = self.track_color_disabled
        else:
            t = self._animation_progress
            track_color = Color(
                int(
                    self.track_color_off.r
                    + (self.track_color_on.r - self.track_color_off.r) * t
                ),
                int(
                    self.track_color_off.g
                    + (self.track_color_on.g - self.track_color_off.g) * t
                ),
                int(
                    self.track_color_off.b
                    + (self.track_color_on.b - self.track_color_off.b) * t
                ),
                255,
            )

        # Draw track (rounded rectangle)
        track_rect = Rect(
            int(track_x), int(track_y), int(track_width), int(track_height)
        )
        roundness = 1.0  # Fully rounded ends
        runtime.renderer.draw_rectangle_rounded(track_rect, roundness, 10, track_color)

        # Thumb dimensions
        thumb_size = track_height - self.thumb_padding * 2
        thumb_x_start = track_x + self.thumb_padding
        thumb_x_end = track_x + track_width - thumb_size - self.thumb_padding
        thumb_x = (
            thumb_x_start + (thumb_x_end - thumb_x_start) * self._animation_progress
        )
        thumb_y = track_y + self.thumb_padding

        # Draw thumb (circle)
        thumb_color = self.thumb_color_disabled if self.disabled else self.thumb_color
        thumb_center_x = thumb_x + thumb_size / 2
        thumb_center_y = thumb_y + thumb_size / 2
        runtime.renderer.draw_circle(
            (int(thumb_center_x), int(thumb_center_y)),
            int(thumb_size / 2),
            thumb_color,
        )

        # Draw label
        if self.label:
            label_x = track_x + track_width + self.label_gap
            label_y = track_y + (track_height - self.font_size) / 2
            label_color = (
                self.label_color_disabled if self.disabled else self.label_color
            )
            runtime.renderer.draw_text(
                self.label,
                (int(label_x), int(label_y)),
                self.font_size,
                label_color,
            )

        # Render children
        for child in self.children:
            child.render()
