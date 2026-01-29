"""Canvas component for custom rendering."""

from typing import Callable, Optional

from arepy.engine.renderer import Rect
from arepy.engine.renderer.renderer_2d import Renderer2D

from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, Unit
from ..runtime import get_runtime


class Canvas(Node):
    """
    Canvas component for custom drawing.

    Provides a callback where you can draw anything using the renderer.

    Usage:
        def draw_custom(renderer, rect, state):
            # rect contains x, y, width, height of the canvas
            # state is any data you passed to the canvas
            cx = rect.x + rect.width / 2
            cy = rect.y + rect.height / 2
            radius = min(rect.width, rect.height) / 2
            renderer.draw_circle((int(cx), int(cy)), radius, Color(255, 0, 0, 255))

        canvas = Canvas(
            on_render=draw_custom,
            width=Unit.px(100),
            height=Unit.px(100),
        )

        # With state (for animations, etc)
        canvas = Canvas(
            on_render=lambda r, rect, s: draw_spinner(r, rect, s["angle"]),
            state={"angle": 0},
        )
    """

    def __init__(
        self,
        on_render: Callable[[Renderer2D, Rect, dict], None],
        width: Unit = Unit.px(100),
        height: Unit = Unit.px(100),
        state: Optional[dict] = None,
        background_color: Optional[Color] = None,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=background_color,
        )

        super().__init__(style=style or default_style, **kwargs)

        self.on_render = on_render
        self.state = state or {}

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()

        # Draw background if set
        if self.style.background_color:
            rect = Rect(
                self.computed_x,
                self.computed_y,
                int(self.computed_width),
                int(self.computed_height),
            )
            runtime.renderer.draw_rectangle(rect, self.style.background_color)

        # Create rect for the callback
        canvas_rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )

        # Call custom render function
        if self.on_render:
            self.on_render(runtime.renderer, canvas_rect, self.state)

        # Render children
        for child in self.children:
            child.render()
