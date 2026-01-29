from typing import Optional

from ..core.fonts import TextMetrics, draw_text, measure_text_ex
from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, Unit


class Text(Node):
    """Text node with cached measurement and custom font support."""

    def __init__(
        self,
        text: str,
        size: float = 20.0,
        color: Color = Color(0, 0, 0, 255),
        style: Optional[Style] = None,
        font_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(style=style or Style(), **kwargs)
        self._text = text
        self.font_size = size
        self.color = color
        self.font_name = font_name  # None uses default font
        self._cached_metrics: Optional[TextMetrics] = None
        self._update_size()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if value != self._text:
            self._text = value
            self._cached_metrics = None
            self._update_size()
            self.mark_dirty()

    def _update_size(self):
        """Update node size based on text content using measure_text_ex."""
        lines = self._text.split("\n")
        if len(lines) > 1:
            self._is_multiline = True
            # Measure first line to get line_height
            # We assume all lines have similar height characteristics
            metrics = measure_text_ex(lines[0], self.font_size, self.font_name)
            self._line_height = metrics.line_height

            max_width = 0
            for line in lines:
                m = measure_text_ex(line, self.font_size, self.font_name)
                max_width = max(max_width, m.width)

            self.style.width = Unit.px(max_width)
            self.style.height = Unit.px(len(lines) * self._line_height)
        else:
            self._is_multiline = False
            if self._cached_metrics is None:
                self._cached_metrics = measure_text_ex(
                    self._text, self.font_size, self.font_name
                )
            self.style.width = Unit.px(self._cached_metrics.width)
            # Use font_size as height for better vertical centering
            # measure_text_ex may return height with extra padding
            self.style.height = Unit.px(self.font_size)

    def render(self):
        if not self.style.visible or self.style.opacity <= 0:
            return

        # Ensure size is updated
        if not hasattr(self, "_is_multiline"):
            self._update_size()

        final_color = self.color
        if self.style.opacity < 1.0:
            final_color = Color(
                self.color.r,
                self.color.g,
                self.color.b,
                int(self.color.a * self.style.opacity),
            )

        if self._is_multiline:
            lines = self._text.split("\n")
            y = self.computed_y
            for line in lines:
                draw_text(
                    line,
                    self.computed_x,
                    y,
                    self.font_size,
                    final_color,
                    self.font_name,
                )
                y += self._line_height
        else:

            draw_text(
                self._text,
                self.computed_x,
                self.computed_y,
                self.font_size,
                final_color,
                self.font_name,
            )
