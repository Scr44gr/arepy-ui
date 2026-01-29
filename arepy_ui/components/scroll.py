from typing import Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, Unit, Vector2
from ..runtime import MouseButton, get_runtime


class ScrollView(Node):
    """Scrollable container with proper scroll offset handling."""

    SCROLLBAR_WIDTH = 8
    SCROLLBAR_PADDING = 2
    MIN_THUMB_HEIGHT = 20

    def __init__(
        self,
        width: Unit,
        height: Unit,
        content: Node,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(width=width, height=height)
        super().__init__(style=style or default_style, **kwargs)

        self.content = content
        self.add_child(content)

        # scroll_y: 0 = top, negative = scrolled down
        self.scroll_y = 0.0
        self.scroll_speed = 40.0

        # Drag state for scrollbar
        self.is_dragging = False
        self.drag_start_mouse_y = 0.0
        self.drag_start_scroll_y = 0.0

    def _get_scroll_metrics(self):
        """Get scroll-related measurements."""
        content_h = self.content.computed_height
        view_h = self.computed_height
        max_scroll = max(0.0, content_h - view_h)
        return content_h, view_h, max_scroll

    def _clamp_scroll(self):
        """Clamp scroll to valid range."""
        content_h, view_h, max_scroll = self._get_scroll_metrics()
        if content_h <= view_h:
            self.scroll_y = 0.0
        else:
            self.scroll_y = max(-max_scroll, min(0.0, self.scroll_y))

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
        is_inside = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        content_h, view_h, max_scroll = self._get_scroll_metrics()

        # Handle scrollbar dragging
        if self.is_dragging:
            if runtime.input.is_mouse_button_down(MouseButton.LEFT):
                if max_scroll > 0:
                    ratio = view_h / content_h
                    thumb_h = max(self.MIN_THUMB_HEIGHT, view_h * ratio)
                    track_space = view_h - thumb_h

                    if track_space > 0:
                        delta_mouse = mouse_pos.y - self.drag_start_mouse_y
                        new_scroll = (
                            self.drag_start_scroll_y
                            - (delta_mouse / track_space) * max_scroll
                        )
                        self.scroll_y = max(-max_scroll, min(0.0, new_scroll))
                return True
            else:
                self.is_dragging = False

        # Check scrollbar click
        if is_inside and max_scroll > 0 and is_click:
            bar_width = self.SCROLLBAR_WIDTH
            track_x = (
                self.computed_x
                + self.computed_width
                - bar_width
                - self.SCROLLBAR_PADDING
            )

            ratio = view_h / content_h
            thumb_h = max(self.MIN_THUMB_HEIGHT, view_h * ratio)
            scroll_ratio = -self.scroll_y / max_scroll if max_scroll > 0 else 0
            thumb_y = self.computed_y + scroll_ratio * (view_h - thumb_h)

            thumb_rect = Rect(track_x - 4, thumb_y, bar_width + 8, int(thumb_h))
            if check_collision_point_rec((mouse_pos.x, mouse_pos.y), thumb_rect):
                self.is_dragging = True
                self.drag_start_mouse_y = mouse_pos.y
                self.drag_start_scroll_y = self.scroll_y
                return True

            track_rect = Rect(track_x - 4, self.computed_y, bar_width + 8, int(view_h))
            if check_collision_point_rec((mouse_pos.x, mouse_pos.y), track_rect):
                click_ratio = (mouse_pos.y - self.computed_y) / view_h
                self.scroll_y = max(-max_scroll, min(0.0, -click_ratio * max_scroll))
                return True

        if not is_inside:
            return False

        # Pass input to children with adjusted mouse position for scroll
        adjusted_mouse = Vector2(mouse_pos.x, mouse_pos.y - self.scroll_y)
        child_consumed = self.content.handle_input(
            adjusted_mouse, is_click, wheel_scroll
        )
        if child_consumed:
            return True

        # Mouse wheel scroll
        wheel = (
            wheel_scroll if wheel_scroll != 0 else runtime.input.get_mouse_wheel_delta()
        )
        if wheel != 0 and max_scroll > 0:
            old_scroll = self.scroll_y
            self.scroll_y += wheel * self.scroll_speed
            self.scroll_y = max(-max_scroll, min(0.0, self.scroll_y))
            if self.scroll_y != old_scroll:
                return True

        return False

    def calculate_layout(self, parent_x, parent_y, parent_width, parent_height):
        if not self.style.visible:
            self.computed_width = 0
            self.computed_height = 0
            return

        # Standard layout calculation
        super().calculate_layout(parent_x, parent_y, parent_width, parent_height)

        # Clamp scroll to valid range after layout
        self._clamp_scroll()

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        self._clamp_scroll()

        # Begin scissor mode to clip content
        runtime.renderer.begin_scissor_mode(
            int(self.computed_x),
            int(self.computed_y),
            int(self.computed_width),
            int(self.computed_height),
        )

        # Apply scroll offset to content for rendering
        if self.scroll_y != 0:
            self.content.translate(0, self.scroll_y)

        self.content.render()

        # Undo scroll offset after rendering
        if self.scroll_y != 0:
            self.content.translate(0, -self.scroll_y)

        runtime.renderer.end_scissor_mode()

        # Draw scrollbar
        content_h, view_h, max_scroll = self._get_scroll_metrics()

        if max_scroll <= 0:
            return

        bar_width = self.SCROLLBAR_WIDTH
        track_x = (
            self.computed_x + self.computed_width - bar_width - self.SCROLLBAR_PADDING
        )

        # Track background
        runtime.renderer.draw_rectangle(
            Rect(int(track_x), int(self.computed_y), bar_width, int(view_h)),
            Color(40, 40, 40, 100),
        )

        # Thumb
        ratio = view_h / content_h
        thumb_h = max(self.MIN_THUMB_HEIGHT, view_h * ratio)
        scroll_ratio = -self.scroll_y / max_scroll if max_scroll > 0 else 0
        thumb_y = self.computed_y + scroll_ratio * (view_h - thumb_h)

        thumb_color = (
            Color(180, 180, 180, 200) if self.is_dragging else Color(120, 120, 120, 150)
        )
        runtime.renderer.draw_rectangle_rounded(
            Rect(int(track_x), int(thumb_y), bar_width, int(thumb_h)),
            0.5,
            4,
            thumb_color,
        )
