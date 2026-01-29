"""Slider component for range value selection."""

from typing import Callable, Optional

from arepy.engine.renderer import Rect

from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, CursorType, Unit
from ..runtime import MOUSE_BUTTON_LEFT, get_runtime


class Slider(Node):
    """
    Slider component for selecting values in a range.

    Usage:
        # Basic slider
        slider = Slider(
            min_value=0,
            max_value=100,
            value=50,
            on_change=lambda v: print(f"Value: {v}"),
        )

        # Vertical slider
        slider = Slider(orientation=SliderOrientation.VERTICAL)

        # Custom colors
        slider = Slider(
            track_color=Color(60, 60, 60, 255),
            fill_color=Color(0, 200, 100, 255),
            thumb_color=Color(255, 255, 255, 255),
        )
    """

    def __init__(
        self,
        min_value: float = 0.0,
        max_value: float = 1.0,
        value: float = 0.0,
        step: Optional[float] = None,
        orientation: Optional["SliderOrientation"] = None,
        width: Unit = Unit.px(200),
        height: Unit = Unit.px(24),
        track_color: Color = Color(80, 80, 80, 255),
        fill_color: Color = Color(0, 122, 204, 255),
        thumb_color: Color = Color(255, 255, 255, 255),
        thumb_size: float = 16.0,
        track_height: float = 6.0,
        on_change: Optional[Callable[[float], None]] = None,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            cursor=CursorType.POINTING_HAND,
        )

        super().__init__(style=style or default_style, **kwargs)

        self.min_value = min_value
        self.max_value = max_value
        self._value = max(min_value, min(max_value, value))
        self.step = step
        self.orientation = orientation or SliderOrientation.HORIZONTAL

        self.track_color = track_color
        self.fill_color = fill_color
        self.thumb_color = thumb_color
        self.thumb_size = thumb_size
        self.track_height = track_height

        self.on_change = on_change
        self._is_dragging = False
        self._is_hovered = False

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float):
        clamped = max(self.min_value, min(self.max_value, new_value))

        # Apply step if defined
        if self.step is not None and self.step > 0:
            steps = round((clamped - self.min_value) / self.step)
            clamped = self.min_value + steps * self.step
            clamped = max(self.min_value, min(self.max_value, clamped))

        if clamped != self._value:
            self._value = clamped
            if self.on_change:
                self.on_change(self._value)

    @property
    def normalized_value(self) -> float:
        """Get value as 0-1 range."""
        if self.max_value == self.min_value:
            return 0.0
        return (self._value - self.min_value) / (self.max_value - self.min_value)

    @normalized_value.setter
    def normalized_value(self, norm: float):
        """Set value from 0-1 range."""
        self.value = self.min_value + norm * (self.max_value - self.min_value)

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        mx, my = mouse_pos.x, mouse_pos.y

        # Check bounds
        in_bounds = (
            self.computed_x <= mx < self.computed_x + self.computed_width
            and self.computed_y <= my < self.computed_y + self.computed_height
        )

        self._is_hovered = in_bounds

        # Handle drag start
        if is_click and in_bounds:
            self._is_dragging = True

        # Handle drag end
        if not runtime.input.is_mouse_button_down(MOUSE_BUTTON_LEFT):
            self._is_dragging = False

        # Update value while dragging
        if self._is_dragging:
            if self.orientation == SliderOrientation.HORIZONTAL:
                relative = (mx - self.computed_x) / self.computed_width
            else:
                # Vertical: top = max, bottom = min
                relative = 1.0 - (my - self.computed_y) / self.computed_height

            self.normalized_value = max(0.0, min(1.0, relative))
            return True

        return in_bounds and is_click

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()

        is_horizontal = self.orientation == SliderOrientation.HORIZONTAL

        if is_horizontal:
            # Track background
            track_y = self.computed_y + (self.computed_height - self.track_height) / 2
            track_rect = Rect(
                self.computed_x,
                track_y,
                int(self.computed_width),
                int(self.track_height),
            )
            runtime.renderer.draw_rectangle_rounded(
                track_rect, 0.5, 8, self.track_color
            )

            # Fill
            fill_width = self.computed_width * self.normalized_value
            if fill_width > 0:
                fill_rect = Rect(
                    self.computed_x,
                    track_y,
                    int(fill_width),
                    int(self.track_height),
                )
                runtime.renderer.draw_rectangle_rounded(
                    fill_rect, 0.5, 8, self.fill_color
                )

            # Thumb
            thumb_x = self.computed_x + fill_width - self.thumb_size / 2
            thumb_y = self.computed_y + (self.computed_height - self.thumb_size) / 2
            thumb_color = self.thumb_color

            # Drag/hover effect - darken when dragging, lighten when hovering
            if self._is_dragging:
                thumb_color = Color(
                    max(0, thumb_color.r - 30),
                    max(0, thumb_color.g - 30),
                    max(0, thumb_color.b - 30),
                    thumb_color.a,
                )
            elif self._is_hovered:
                thumb_color = Color(
                    min(255, thumb_color.r + 20),
                    min(255, thumb_color.g + 20),
                    min(255, thumb_color.b + 20),
                    thumb_color.a,
                )

            runtime.renderer.draw_circle(
                (
                    int(thumb_x + self.thumb_size / 2),
                    int(thumb_y + self.thumb_size / 2),
                ),
                self.thumb_size / 2,
                thumb_color,
            )
        else:
            # Vertical slider
            track_x = self.computed_x + (self.computed_width - self.track_height) / 2
            track_rect = Rect(
                track_x,
                self.computed_y,
                int(self.track_height),
                int(self.computed_height),
            )
            runtime.renderer.draw_rectangle_rounded(
                track_rect, 0.5, 8, self.track_color
            )

            # Fill (from bottom)
            fill_height = self.computed_height * self.normalized_value
            if fill_height > 0:
                fill_rect = Rect(
                    track_x,
                    self.computed_y + self.computed_height - fill_height,
                    int(self.track_height),
                    int(fill_height),
                )
                runtime.renderer.draw_rectangle_rounded(
                    fill_rect, 0.5, 8, self.fill_color
                )

            # Thumb
            thumb_x = self.computed_x + (self.computed_width - self.thumb_size) / 2
            thumb_y = (
                self.computed_y
                + self.computed_height
                - fill_height
                - self.thumb_size / 2
            )
            thumb_color = self.thumb_color

            # Drag/hover effect - darken when dragging, lighten when hovering
            if self._is_dragging:
                thumb_color = Color(
                    max(0, thumb_color.r - 30),
                    max(0, thumb_color.g - 30),
                    max(0, thumb_color.b - 30),
                    thumb_color.a,
                )
            elif self._is_hovered:
                thumb_color = Color(
                    min(255, thumb_color.r + 20),
                    min(255, thumb_color.g + 20),
                    min(255, thumb_color.b + 20),
                    thumb_color.a,
                )

            runtime.renderer.draw_circle(
                (
                    int(thumb_x + self.thumb_size / 2),
                    int(thumb_y + self.thumb_size / 2),
                ),
                self.thumb_size / 2,
                thumb_color,
            )


class SliderOrientation:
    """Slider orientation."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
