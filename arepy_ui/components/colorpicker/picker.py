"""
ColorPicker component - Interactive color selection with HSV model.

Features:
- Saturation/Value gradient picker
- Hue slider bar
- Alpha slider (optional)
- Preview of selected color
- Hex/RGB input (optional)
"""

from typing import Callable, Optional, Tuple

from arepy.engine.renderer import Color as RendererColor
from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ...core.node import Node
from ...core.style import Spacing, Style
from ...core.types import Color, FlexDirection, Unit
from ...logging import logger
from ...runtime import MouseButton, get_runtime

# Import HSV functions (Cython when compiled, otherwise the .pyx is interpreted as Python)
from ._hsv import (
    generate_hue_gradient_rgba,
    generate_sv_gradient_rgba,
    hsv_to_rgb,
    rgb_to_hsv,
)


class ColorPicker(Node):
    """
    A color picker component with HSV color model.

    The picker consists of:
    - A square gradient showing Saturation (X) and Value (Y) for the current hue
    - A vertical hue bar to select the base hue
    - Optional alpha slider
    - Preview of the current color

    Args:
        color: Initial color (default: red)
        width: Total width of the picker
        height: Height of the SV gradient area
        show_alpha: Whether to show alpha slider
        show_preview: Whether to show color preview
        on_change: Callback when color changes
        style: Optional style overrides

    Requires:
        numpy: For gradient buffer generation
    """

    # Layout constants
    HUE_BAR_WIDTH = 20
    ALPHA_BAR_WIDTH = 20
    SPACING = 8
    PREVIEW_HEIGHT = 30

    def __init__(
        self,
        color: Color = Color(255, 0, 0, 255),
        width: Unit = Unit.px(250),
        height: Unit = Unit.px(200),
        show_alpha: bool = True,
        show_preview: bool = True,
        on_change: Optional[Callable[[Color], None]] = None,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            flex_direction=FlexDirection.COLUMN,
            padding=Spacing.all(0),
        )

        if style:
            for attr in vars(style):
                val = getattr(style, attr)
                if val is not None:
                    setattr(default_style, attr, val)

        super().__init__(style=default_style, **kwargs)

        self.show_alpha = show_alpha
        self.show_preview = show_preview
        self.on_change = on_change

        # HSV state
        h, s, v = rgb_to_hsv(color.r, color.g, color.b)
        self._hue = h
        self._saturation = s
        self._value = v
        self._alpha = color.a / 255.0

        # Interaction state
        self._dragging_sv = False
        self._dragging_hue = False
        self._dragging_alpha = False

        # Streaming texture IDs (like Video component)
        self._sv_texture_id: Optional[int] = None
        self._hue_texture_id: Optional[int] = None
        self._textures_initialized = False
        self._sv_needs_update = True
        self._last_hue_for_sv = -1.0

        # Gradient resolution (smaller = faster, larger = smoother)
        self._sv_resolution = 64  # 64x64 for SV gradient
        self._hue_resolution = 180  # height for hue bar

    @property
    def color(self) -> Color:
        """Get the current selected color."""
        r, g, b = hsv_to_rgb(self._hue, self._saturation, self._value)
        return Color(r, g, b, int(self._alpha * 255))

    @color.setter
    def color(self, value: Color):
        """Set the current color."""
        h, s, v = rgb_to_hsv(value.r, value.g, value.b)
        self._hue = h
        self._saturation = s
        self._value = v
        self._alpha = value.a / 255.0
        self._sv_needs_update = True

    @property
    def hex_color(self) -> str:
        """Get color as hex string (#RRGGBB or #RRGGBBAA)."""
        c = self.color
        if self.show_alpha and c.a < 255:
            return f"#{c.r:02X}{c.g:02X}{c.b:02X}{c.a:02X}"
        return f"#{c.r:02X}{c.g:02X}{c.b:02X}"

    def _get_layout(self) -> Tuple[Rect, Rect, Optional[Rect], Optional[Rect]]:
        """
        Calculate layout rectangles for all parts.

        Returns:
            (sv_rect, hue_rect, alpha_rect, preview_rect)
        """
        x = int(self.computed_x)
        y = int(self.computed_y)
        total_w = int(self.computed_width)
        total_h = int(self.computed_height)

        # Calculate preview height
        preview_h = self.PREVIEW_HEIGHT if self.show_preview else 0

        # Available height for gradient area
        gradient_area_h = (
            total_h - preview_h - (self.SPACING if self.show_preview else 0)
        )

        # SV gradient width (subtract hue bar and optionally alpha bar)
        bars_width = self.HUE_BAR_WIDTH + self.SPACING
        if self.show_alpha:
            bars_width += self.ALPHA_BAR_WIDTH + self.SPACING

        sv_w = total_w - bars_width
        sv_h = gradient_area_h

        sv_rect = Rect(x, y, sv_w, sv_h)

        # Hue bar (to the right of SV)
        hue_x = x + sv_w + self.SPACING
        hue_rect = Rect(hue_x, y, self.HUE_BAR_WIDTH, sv_h)

        # Alpha bar (optional, to the right of hue)
        alpha_rect = None
        if self.show_alpha:
            alpha_x = hue_x + self.HUE_BAR_WIDTH + self.SPACING
            alpha_rect = Rect(alpha_x, y, self.ALPHA_BAR_WIDTH, sv_h)

        # Preview (at bottom)
        preview_rect = None
        if self.show_preview:
            preview_y = y + gradient_area_h + self.SPACING
            preview_rect = Rect(x, preview_y, total_w, preview_h)

        return sv_rect, hue_rect, alpha_rect, preview_rect

    def _init_streaming_textures(self, runtime):
        """Initialize streaming textures (like Video component)."""
        if self._textures_initialized:
            return

        # Init PBO streaming if not available
        if not runtime.renderer.is_streaming_available():
            runtime.renderer.init_streaming()

        if not runtime.renderer.is_streaming_available():
            logger.error("Failed to initialize PBO streaming for ColorPicker")
            return

        # Create SV gradient texture (RGBA - 4 channels)
        res = self._sv_resolution
        self._sv_texture_id = runtime.renderer.create_streaming_texture(res, res, 4)

        if self._sv_texture_id is None:
            logger.error("Failed to create SV streaming texture")
            return

        # Create hue bar texture (RGBA - 4 channels)
        hue_h = self._hue_resolution  # 180
        hue_w = self.HUE_BAR_WIDTH  # 20

        # Generate hue gradient RGBA bytes directly (no numpy)
        hue_bytes = generate_hue_gradient_rgba(hue_w, hue_h, vertical=True)

        # Texture dimensions: width first, then height (OpenGL convention)
        self._hue_texture_id = runtime.renderer.create_streaming_texture(
            hue_w, hue_h, 4
        )
        if self._hue_texture_id is None:
            logger.error("Failed to create hue streaming texture")
            return

        # Upload hue texture TWICE to fill both PBO buffers (double buffering)
        runtime.renderer.update_streaming_texture(self._hue_texture_id, hue_bytes)
        runtime.renderer.update_streaming_texture(self._hue_texture_id, hue_bytes)

        # Also upload initial SV texture twice
        self._update_sv_texture(runtime)

        self._textures_initialized = True
        self._sv_needs_update = False  # Already updated

    def _update_sv_texture(self, runtime):
        """Update the SV gradient texture if hue changed."""
        if self._sv_texture_id is None:
            return

        # Only regenerate if hue changed significantly
        if abs(self._hue - self._last_hue_for_sv) < 0.5 and not self._sv_needs_update:
            return

        self._last_hue_for_sv = self._hue
        self._sv_needs_update = False

        # Generate the gradient RGBA bytes directly (no numpy)
        res = self._sv_resolution
        sv_bytes = generate_sv_gradient_rgba(self._hue, res, res)

        # Upload to GPU via streaming texture - upload TWICE for double buffering
        runtime.renderer.update_streaming_texture(self._sv_texture_id, sv_bytes)
        runtime.renderer.update_streaming_texture(self._sv_texture_id, sv_bytes)

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        sv_rect, hue_rect, alpha_rect, _ = self._get_layout()

        mx, my = mouse_pos.x, mouse_pos.y
        mouse_down = runtime.input.is_mouse_button_down(MouseButton.LEFT)

        # Check for click/drag start
        if is_click:
            if check_collision_point_rec((mx, my), sv_rect):
                self._dragging_sv = True
            elif check_collision_point_rec((mx, my), hue_rect):
                self._dragging_hue = True
            elif alpha_rect and check_collision_point_rec((mx, my), alpha_rect):
                self._dragging_alpha = True

        # Handle dragging
        changed = False

        if self._dragging_sv and mouse_down:
            # Update saturation and value
            rel_x = (mx - sv_rect.x) / sv_rect.width
            rel_y = (my - sv_rect.y) / sv_rect.height

            self._saturation = max(0.0, min(1.0, rel_x))
            self._value = max(0.0, min(1.0, 1.0 - rel_y))
            changed = True

        if self._dragging_hue and mouse_down:
            # Update hue
            rel_y = (my - hue_rect.y) / hue_rect.height
            self._hue = max(0.0, min(360.0, rel_y * 360.0))
            self._sv_needs_update = True
            changed = True

        if self._dragging_alpha and mouse_down and alpha_rect:
            # Update alpha
            rel_y = (my - alpha_rect.y) / alpha_rect.height
            self._alpha = max(0.0, min(1.0, 1.0 - rel_y))
            changed = True

        # Stop dragging when mouse released
        if not mouse_down:
            self._dragging_sv = False
            self._dragging_hue = False
            self._dragging_alpha = False

        # Fire callback
        if changed and self.on_change:
            self.on_change(self.color)

        # Check if we're interacting with this component
        is_interacting = self._dragging_sv or self._dragging_hue or self._dragging_alpha

        is_over_sv = check_collision_point_rec((mx, my), sv_rect)
        is_over_hue = check_collision_point_rec((mx, my), hue_rect)
        is_over_alpha = alpha_rect is not None and check_collision_point_rec(
            (mx, my), alpha_rect
        )
        is_over = is_over_sv or is_over_hue or is_over_alpha

        return is_interacting or (is_click and is_over)

    def _draw_checkerboard(self, runtime, rect: Rect, size: int = 8):
        """Draw a checkerboard pattern for alpha visualization."""
        light = Color(200, 200, 200, 255)
        dark = Color(150, 150, 150, 255)

        for y in range(0, int(rect.height), size):
            for x in range(0, int(rect.width), size):
                is_light = ((x // size) + (y // size)) % 2 == 0
                color = light if is_light else dark
                w = min(size, int(rect.width) - x)
                h = min(size, int(rect.height) - y)
                runtime.renderer.draw_rectangle(
                    Rect(int(rect.x) + x, int(rect.y) + y, w, h), color
                )

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        sv_rect, hue_rect, alpha_rect, preview_rect = self._get_layout()

        # Init streaming textures if needed
        self._init_streaming_textures(runtime)

        # Update SV texture if hue changed
        self._update_sv_texture(runtime)

        # Draw SV gradient using streaming texture
        if self._sv_texture_id is not None:
            texture = runtime.renderer.get_streaming_texture(self._sv_texture_id)
            if texture:
                # src = full texture, dst = scaled to sv_rect
                src_rect = Rect(0, 0, self._sv_resolution, self._sv_resolution)
                dst_rect = Rect(
                    int(sv_rect.x),
                    int(sv_rect.y),
                    int(sv_rect.width),
                    int(sv_rect.height),
                )
                runtime.renderer.draw_texture_ex(
                    texture,
                    src_rect,
                    dst_rect,
                    (0, 0),
                    0.0,
                    RendererColor(255, 255, 255, 255),
                )

        # Draw SV cursor
        cursor_x = int(sv_rect.x + self._saturation * sv_rect.width)
        cursor_y = int(sv_rect.y + (1.0 - self._value) * sv_rect.height)
        cursor_size = 10

        # White outline
        runtime.renderer.draw_circle_lines(
            (cursor_x, cursor_y), cursor_size // 2 + 1, Color(255, 255, 255, 255)
        )
        # Black outline
        runtime.renderer.draw_circle_lines(
            (cursor_x, cursor_y), cursor_size // 2, Color(0, 0, 0, 255)
        )

        # Draw hue bar using streaming texture
        if self._hue_texture_id is not None:
            texture = runtime.renderer.get_streaming_texture(self._hue_texture_id)
            if texture:
                # src = full texture, dst = scaled to hue_rect
                src_rect = Rect(0, 0, self.HUE_BAR_WIDTH, self._hue_resolution)
                dst_rect = Rect(
                    int(hue_rect.x),
                    int(hue_rect.y),
                    int(hue_rect.width),
                    int(hue_rect.height),
                )
                runtime.renderer.draw_texture_ex(
                    texture,
                    src_rect,
                    dst_rect,
                    (0, 0),
                    0.0,
                    RendererColor(255, 255, 255, 255),
                )

        # Draw hue cursor
        hue_cursor_y = int(hue_rect.y + (self._hue / 360.0) * hue_rect.height)
        runtime.renderer.draw_rectangle(
            Rect(int(hue_rect.x) - 2, hue_cursor_y - 2, int(hue_rect.width) + 4, 4),
            Color(255, 255, 255, 255),
        )
        runtime.renderer.draw_rectangle_lines_ex(
            Rect(int(hue_rect.x) - 2, hue_cursor_y - 2, int(hue_rect.width) + 4, 4),
            1,
            Color(0, 0, 0, 255),
        )

        # Draw alpha bar (optional)
        if alpha_rect:
            # Checkerboard background
            self._draw_checkerboard(runtime, alpha_rect)

            # Alpha gradient overlay
            current_color = self.color
            for i in range(int(alpha_rect.height)):
                a = int((1.0 - i / alpha_rect.height) * 255)
                runtime.renderer.draw_rectangle(
                    Rect(
                        int(alpha_rect.x),
                        int(alpha_rect.y) + i,
                        int(alpha_rect.width),
                        1,
                    ),
                    Color(current_color.r, current_color.g, current_color.b, a),
                )

            # Alpha cursor
            alpha_cursor_y = int(alpha_rect.y + (1.0 - self._alpha) * alpha_rect.height)
            runtime.renderer.draw_rectangle(
                Rect(
                    int(alpha_rect.x) - 2,
                    alpha_cursor_y - 2,
                    int(alpha_rect.width) + 4,
                    4,
                ),
                Color(255, 255, 255, 255),
            )
            runtime.renderer.draw_rectangle_lines_ex(
                Rect(
                    int(alpha_rect.x) - 2,
                    alpha_cursor_y - 2,
                    int(alpha_rect.width) + 4,
                    4,
                ),
                1,
                Color(0, 0, 0, 255),
            )

        # Draw preview (optional)
        if preview_rect:
            # Checkerboard for alpha
            self._draw_checkerboard(runtime, preview_rect)

            # Current color
            runtime.renderer.draw_rectangle(preview_rect, self.color)

            # Border
            runtime.renderer.draw_rectangle_lines_ex(
                preview_rect, 1, Color(100, 100, 100, 255)
            )

            # Hex text
            hex_text = self.hex_color
            text_size = 12
            text_width = runtime.renderer.measure_text(hex_text, text_size)
            text_x = int(preview_rect.x + (preview_rect.width - text_width) / 2)
            text_y = int(preview_rect.y + (preview_rect.height - text_size) / 2)

            # Text shadow for readability
            runtime.renderer.draw_text(
                hex_text, (text_x + 1, text_y + 1), text_size, Color(0, 0, 0, 150)
            )

            # Use contrasting text color
            c = self.color
            luminance = (0.299 * c.r + 0.587 * c.g + 0.114 * c.b) / 255.0
            text_color = (
                Color(0, 0, 0, 255) if luminance > 0.5 else Color(255, 255, 255, 255)
            )
            runtime.renderer.draw_text(
                hex_text, (text_x, text_y), text_size, text_color
            )

        # Render children
        for child in self.children:
            child.render()

    def cleanup(self):
        """Clean up streaming textures when component is destroyed."""
        runtime = get_runtime()
        if self._sv_texture_id is not None:
            runtime.renderer.destroy_streaming_texture(self._sv_texture_id)
            self._sv_texture_id = None
        if self._hue_texture_id is not None:
            runtime.renderer.destroy_streaming_texture(self._hue_texture_id)
            self._hue_texture_id = None
        self._textures_initialized = False
