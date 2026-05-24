"""ProgressBar component - Visual progress indicator."""

from typing import Optional

from arepy.engine.renderer import Rect

from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, Unit
from ..runtime import get_runtime


class ProgressBar(Node):
    """
    Progress bar component.

    A visual indicator of progress or loading state.
    No user interaction - use Slider for interactive progress.

    Features:
    - Determinate mode (0-100%)
    - Indeterminate mode (animated loading)
    - Customizable colors
    - Optional label/percentage display
    - Animated transitions
    """

    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 100.0,
        width: Unit = Unit.px(200),
        height: Unit = Unit.px(8),
        style: Optional[Style] = None,
        show_label: bool = False,
        indeterminate: bool = False,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=Color(40, 40, 50, 255),
            border_radius=4.0,
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

        self._value = max(0.0, min(value, max_value))
        self.max_value = max_value
        self.show_label = show_label
        self.indeterminate = indeterminate

        # Animation state
        self._display_value = self._value
        self._animation_speed = 5.0
        self._indeterminate_offset = 0.0
        self._indeterminate_speed = 1.5

        # Colors
        self.fill_color = Color(80, 140, 220, 255)
        self.label_color = Color(220, 220, 230, 255)

        # Label config
        self.font_size = 12
        self.label_gap = 8

    @property
    def value(self) -> float:
        """Get current value."""
        return self._value

    @value.setter
    def value(self, val: float):
        """Set current value."""
        self._value = max(0.0, min(val, self.max_value))

    @property
    def percentage(self) -> float:
        """Get progress as percentage (0-100)."""
        if self.max_value <= 0:
            return 0.0
        return (self._value / self.max_value) * 100

    def set_percentage(self, percent: float):
        """Set progress by percentage."""
        self._value = (percent / 100.0) * self.max_value

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        # No interaction for progress bar
        return False

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        dt = runtime.renderer.get_delta_time()

        # Calculate label dimensions
        label_width = 0
        if self.show_label:
            label_text = f"{int(self.percentage)}%"
            label_width = (
                runtime.renderer.measure_text(label_text, self.font_size)
                + self.label_gap
            )

        # Bar dimensions
        bar_width = self.computed_width
        bar_height = self.computed_height
        bar_x = self.computed_x
        bar_y = self.computed_y

        # If showing label, adjust bar to make room
        if self.show_label:
            bar_width -= label_width

        # Background track
        track_rect = Rect(int(bar_x), int(bar_y), int(bar_width), int(bar_height))

        if self.style.background_color:
            min_dim = min(bar_width, bar_height)
            if self.style.border_radius > 0 and min_dim > 0:
                runtime.renderer.draw_rectangle_rounded(
                    track_rect,
                    self.style.border_radius / min_dim,
                    10,
                    self.style.background_color,
                )
            else:
                runtime.renderer.draw_rectangle(track_rect, self.style.background_color)

        if self.indeterminate:
            # Indeterminate animation
            self._indeterminate_offset += dt * self._indeterminate_speed
            if self._indeterminate_offset > 1.0:
                self._indeterminate_offset -= 1.0

            # Moving block
            block_width = bar_width * 0.3
            # Ease in/out for smooth movement
            t = self._indeterminate_offset
            # Smooth oscillation
            eased_t = 0.5 - 0.5 * __import__("math").cos(t * 3.14159 * 2)
            block_x = bar_x + (bar_width - block_width) * eased_t

            # Clip to bar bounds
            runtime.renderer.begin_scissor_mode(
                int(bar_x), int(bar_y), int(bar_width), int(bar_height)
            )

            fill_rect = Rect(
                int(block_x), int(bar_y), int(block_width), int(bar_height)
            )
            min_dim = min(bar_width, bar_height)
            if self.style.border_radius > 0 and min_dim > 0:
                runtime.renderer.draw_rectangle_rounded(
                    fill_rect,
                    self.style.border_radius / min_dim,
                    10,
                    self.fill_color,
                )
            else:
                runtime.renderer.draw_rectangle(fill_rect, self.fill_color)

            runtime.renderer.end_scissor_mode()
        else:
            # Determinate mode - animate to target value
            if self._display_value != self._value:
                diff = self._value - self._display_value
                self._display_value += diff * dt * self._animation_speed
                if abs(diff) < 0.01:
                    self._display_value = self._value

            # Fill bar
            fill_percentage = (
                self._display_value / self.max_value if self.max_value > 0 else 0
            )
            fill_width = bar_width * fill_percentage

            if fill_width > 0:
                # Clip to bar bounds for proper rounded corners
                runtime.renderer.begin_scissor_mode(
                    int(bar_x), int(bar_y), int(fill_width), int(bar_height)
                )

                fill_rect = Rect(
                    int(bar_x), int(bar_y), int(bar_width), int(bar_height)
                )
                min_dim = min(bar_width, bar_height)
                if self.style.border_radius > 0 and min_dim > 0:
                    runtime.renderer.draw_rectangle_rounded(
                        fill_rect,
                        self.style.border_radius / min_dim,
                        10,
                        self.fill_color,
                    )
                else:
                    runtime.renderer.draw_rectangle(fill_rect, self.fill_color)

                runtime.renderer.end_scissor_mode()

        # Label
        if self.show_label:
            label_text = f"{int(self.percentage)}%"
            label_x = bar_x + bar_width + self.label_gap
            label_y = bar_y + (bar_height - self.font_size) / 2
            runtime.renderer.draw_text(
                label_text,
                (int(label_x), int(label_y)),
                self.font_size,
                self.label_color,
            )

        # Render children
        for child in self.children:
            child.render()
