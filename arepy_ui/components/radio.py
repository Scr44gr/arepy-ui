"""Radio component - Single selection from options."""

from typing import Any, Callable, List, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Spacing, Style
from ..core.types import AlignItems, Color, FlexDirection, Unit
from ..runtime import Key, get_runtime


class RadioOption:
    """Represents a single radio option."""

    def __init__(self, label: str, value: Any, disabled: bool = False):
        self.label = label
        self.value = value
        self.disabled = disabled


class RadioGroup(Node):
    """
    Radio button group component.

    Features:
    - Single selection from multiple options
    - Keyboard navigation
    - Horizontal or vertical layout
    - Disabled options
    - Animated selection indicator
    """

    def __init__(
        self,
        options: Optional[List[RadioOption]] = None,
        selected_value: Any = None,
        width: Unit = Unit.auto(),
        height: Unit = Unit.auto(),
        style: Optional[Style] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        direction: FlexDirection = FlexDirection.COLUMN,
        gap: int = 12,
        font_size: int = 14,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            flex_direction=direction,
            gap=gap,
            align_items=AlignItems.START,
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

        self.options = options or []
        self.on_change = on_change
        self.font_size = font_size

        # Selection state
        self._selected_index = -1
        if selected_value is not None:
            for i, opt in enumerate(self.options):
                if opt.value == selected_value:
                    self._selected_index = i
                    break

        # Focus state
        self._focused_index = 0
        self.is_focused = False

        # Visual config
        self.radio_size = 18
        self.radio_inner_size = 10
        self.label_gap = 8

        # Colors
        self.radio_border_color = Color(100, 100, 120, 255)
        self.radio_border_color_focused = Color(100, 140, 200, 255)
        self.radio_fill_color = Color(80, 140, 220, 255)
        self.radio_disabled_color = Color(60, 60, 70, 255)
        self.label_color = Color(220, 220, 230, 255)
        self.label_disabled_color = Color(100, 100, 110, 255)

        # Animation
        self._animation_states: List[float] = [0.0] * len(self.options)
        if self._selected_index >= 0:
            self._animation_states[self._selected_index] = 1.0
        self._animation_speed = 10.0

    @property
    def selected_value(self) -> Any:
        """Get the selected value."""
        if 0 <= self._selected_index < len(self.options):
            return self.options[self._selected_index].value
        return None

    @selected_value.setter
    def selected_value(self, value: Any):
        """Set the selected value."""
        for i, opt in enumerate(self.options):
            if opt.value == value:
                self._select(i)
                return
        self._selected_index = -1

    def _select(self, index: int):
        """Select an option by index."""
        if 0 <= index < len(self.options) and not self.options[index].disabled:
            if self._selected_index != index:
                self._selected_index = index
                if self.on_change:
                    self.on_change(self.options[index].value)

    def _get_option_rect(self, index: int) -> Rect:
        """Get the bounding rect for an option."""
        runtime = get_runtime()
        direction = self.style.flex_direction or FlexDirection.COLUMN
        gap = self.style.gap or 12

        opt = self.options[index]
        label_width = runtime.renderer.measure_text(opt.label, self.font_size)
        option_width = self.radio_size + self.label_gap + label_width
        option_height = max(self.radio_size, self.font_size)

        if direction == FlexDirection.COLUMN:
            y_offset = sum(
                max(self.radio_size, self.font_size) + gap for _ in range(index)
            )
            return Rect(
                int(self.computed_x),
                int(self.computed_y + y_offset),
                int(option_width),
                int(option_height),
            )
        else:
            x_offset = 0
            for i in range(index):
                o = self.options[i]
                lw = runtime.renderer.measure_text(o.label, self.font_size)
                x_offset += self.radio_size + self.label_gap + lw + gap
            return Rect(
                int(self.computed_x + x_offset),
                int(self.computed_y),
                int(option_width),
                int(option_height),
            )

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()

        # Check if any option is clicked/hovered
        clicked_option = -1
        for i in range(len(self.options)):
            rect = self._get_option_rect(i)
            if check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect):
                if is_click and not self.options[i].disabled:
                    clicked_option = i
                    self.is_focused = True
                    self._focused_index = i
                break

        if clicked_option >= 0:
            self._select(clicked_option)
            return True

        # Focus loss on click outside
        if is_click:
            total_rect = Rect(
                int(self.computed_x),
                int(self.computed_y),
                int(self.computed_width),
                int(self.computed_height),
            )
            if not check_collision_point_rec((mouse_pos.x, mouse_pos.y), total_rect):
                self.is_focused = False

        # Keyboard navigation
        if self.is_focused and len(self.options) > 0:
            direction = self.style.flex_direction or FlexDirection.COLUMN

            prev_key = Key.UP if direction == FlexDirection.COLUMN else Key.LEFT
            next_key = Key.DOWN if direction == FlexDirection.COLUMN else Key.RIGHT

            if runtime.input.is_key_pressed(prev_key):
                new_focus = self._focused_index - 1
                while new_focus >= 0 and self.options[new_focus].disabled:
                    new_focus -= 1
                if new_focus >= 0:
                    self._focused_index = new_focus
                    self._select(new_focus)

            elif runtime.input.is_key_pressed(next_key):
                new_focus = self._focused_index + 1
                while (
                    new_focus < len(self.options) and self.options[new_focus].disabled
                ):
                    new_focus += 1
                if new_focus < len(self.options):
                    self._focused_index = new_focus
                    self._select(new_focus)

            elif runtime.input.is_key_pressed(
                Key.SPACE
            ) or runtime.input.is_key_pressed(Key.ENTER):
                self._select(self._focused_index)
                return True

        return False

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        dt = runtime.renderer.get_delta_time()

        # Update animations
        for i in range(len(self.options)):
            target = 1.0 if i == self._selected_index else 0.0
            if self._animation_states[i] != target:
                direction = 1 if target > self._animation_states[i] else -1
                self._animation_states[i] += direction * dt * self._animation_speed
                self._animation_states[i] = max(
                    0.0, min(1.0, self._animation_states[i])
                )

        # Draw each option
        for i, opt in enumerate(self.options):
            rect = self._get_option_rect(i)

            radio_x = rect.x
            radio_y = rect.y + (rect.height - self.radio_size) / 2
            radio_center_x = radio_x + self.radio_size / 2
            radio_center_y = radio_y + self.radio_size / 2

            # Radio outer circle
            if opt.disabled:
                border_color = self.radio_disabled_color
            elif i == self._focused_index and self.is_focused:
                border_color = self.radio_border_color_focused
            else:
                border_color = self.radio_border_color

            runtime.renderer.draw_circle_lines(
                (int(radio_center_x), int(radio_center_y)),
                int(self.radio_size / 2),
                border_color,
            )

            # Radio inner circle (animated)
            if self._animation_states[i] > 0:
                inner_radius = (self.radio_inner_size / 2) * self._animation_states[i]
                fill_color = (
                    self.radio_disabled_color if opt.disabled else self.radio_fill_color
                )
                runtime.renderer.draw_circle(
                    (int(radio_center_x), int(radio_center_y)),
                    int(inner_radius),
                    fill_color,
                )

            # Label
            label_x = radio_x + self.radio_size + self.label_gap
            label_y = rect.y + (rect.height - self.font_size) / 2
            label_color = (
                self.label_disabled_color if opt.disabled else self.label_color
            )
            runtime.renderer.draw_text(
                opt.label,
                (int(label_x), int(label_y)),
                self.font_size,
                label_color,
            )

        # Render children
        for child in self.children:
            child.render()
