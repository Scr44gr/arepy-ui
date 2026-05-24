"""Image component for displaying textures."""

from typing import Optional

from arepy.engine.renderer import Rect

from ..core.node import Node
from ..core.style import Style, merge_style_fields
from ..core.types import Color, Unit
from ..logging import logger
from ..runtime import get_runtime


class Image(Node):
    """
    Image component for displaying textures.

    Usage:
        # Load and display an image
        img = Image("assets/icon.png", width=Unit.px(64), height=Unit.px(64))

        # With tint color
        img = Image("assets/icon.png", tint=Color(255, 0, 0, 255))

        # Fit modes
        img = Image("assets/bg.png", fit=ImageFit.COVER)
    """

    def __init__(
        self,
        source: str,
        width: Unit = Unit.auto(),
        height: Unit = Unit.auto(),
        tint: Color = Color(255, 255, 255, 255),
        fit: Optional["ImageFit"] = None,
        border_radius: float = 0.0,
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            border_radius=border_radius,
        )

        merge_style_fields(
            default_style,
            style,
            ("width", "height", "margin", "padding"),
        )
        if style and style.border_radius > 0:
            default_style.border_radius = style.border_radius

        super().__init__(style=default_style, **kwargs)

        self.source = source
        self.tint = tint
        self.fit = fit or ImageFit.FILL
        self.border_radius = border_radius
        self._texture = None
        self._texture_width = 0
        self._texture_height = 0
        self._loaded = False
        self._load_error = False
        self._mask_texture = None

    def _ensure_loaded(self):
        """Lazy load the texture."""
        if self._loaded or self._load_error:
            return

        try:
            runtime = get_runtime()

            if not runtime.has_asset_store:
                raise RuntimeError(
                    "AssetStore not configured. Pass asset_store to configure_runtime() to use Image component."
                )

            # Load texture via AssetStore (requires renderer, name, path)
            runtime.asset_store.load_texture(runtime.renderer, self.source, self.source)
            self._texture = runtime.asset_store.get_texture(self.source)
            self._loaded = True

            # Get texture dimensions
            if self._texture:
                tex_width, tex_height = self._texture.get_size()
                self._texture_width = tex_width
                self._texture_height = tex_height

                # If size is auto, use texture size
                if self.style.width.type.name == "AUTO":
                    self.style.width = Unit.px(tex_width)
                if self.style.height.type.name == "AUTO":
                    self.style.height = Unit.px(tex_height)

        except Exception as e:
            logger.error(f"Failed to load image '{self.source}': {e}")
            self._load_error = True

    @property
    def texture_width(self) -> int:
        """Get the original texture width."""
        self._ensure_loaded()
        return self._texture_width

    @property
    def texture_height(self) -> int:
        """Get the original texture height."""
        self._ensure_loaded()
        return self._texture_height

    def render(self):
        if not self.style.visible:
            return

        self._ensure_loaded()

        if not self._texture or self._load_error:
            # Draw placeholder rectangle
            runtime = get_runtime()
            rect = Rect(
                self.computed_x,
                self.computed_y,
                int(self.computed_width),
                int(self.computed_height),
            )
            runtime.renderer.draw_rectangle(rect, Color(100, 100, 100, 255))
            return

        runtime = get_runtime()

        # Calculate source and destination rectangles based on fit mode
        src_rect, dst_rect = self._calculate_rects()

        # Convert to arepy Color type
        from arepy import Color as ArepyColor

        tint = ArepyColor(self.tint.r, self.tint.g, self.tint.b, self.tint.a)
        white = ArepyColor(255, 255, 255, 255)

        border_radius = self.style.border_radius or self.border_radius

        if border_radius > 0 and runtime.renderer.is_stencil_available():
            # Use stencil buffer for rounded corners
            cx = dst_rect.x + dst_rect.width / 2
            cy = dst_rect.y + dst_rect.height / 2

            # For circular (50% radius), use the smaller dimension
            max_radius = min(dst_rect.width, dst_rect.height) / 2
            radius = min(border_radius, max_radius)

            # Begin stencil mask
            runtime.renderer.begin_stencil_mask()

            if radius >= max_radius * 0.99:  # Essentially circular
                # Draw circle mask
                runtime.renderer.draw_circle((int(cx), int(cy)), radius, white)
            else:
                # Draw rounded rectangle mask
                mask_rect = Rect(
                    dst_rect.x, dst_rect.y, int(dst_rect.width), int(dst_rect.height)
                )
                roundness = (border_radius * 2) / min(dst_rect.width, dst_rect.height)
                runtime.renderer.draw_rectangle_rounded(
                    mask_rect, min(roundness, 1.0), 16, white
                )

            runtime.renderer.end_stencil_mask()

            # Draw texture (only visible inside the mask)
            runtime.renderer.draw_texture_ex(
                self._texture,
                src_rect,
                dst_rect,
                (0.0, 0.0),
                0.0,
                tint,
            )

            # End stencil mode
            runtime.renderer.end_stencil_mode()
        else:
            # No border radius or stencil not available, draw normally
            runtime.renderer.draw_texture_ex(
                self._texture,
                src_rect,
                dst_rect,
                (0.0, 0.0),
                0.0,
                tint,
            )

        # Render children
        for child in self.children:
            child.render()

    def _calculate_rects(self) -> tuple[Rect, Rect]:
        """Calculate source and destination rectangles based on fit mode."""
        tex_w = self._texture_width
        tex_h = self._texture_height
        dst_w = self.computed_width
        dst_h = self.computed_height

        if self.fit == ImageFit.FILL:
            # Stretch to fill (may distort)
            src = Rect(0, 0, int(tex_w), int(tex_h))
            dst = Rect(
                int(self.computed_x), int(self.computed_y), int(dst_w), int(dst_h)
            )

        elif self.fit == ImageFit.CONTAIN:
            # Fit inside, maintain aspect ratio (may have gaps)
            scale = min(dst_w / tex_w, dst_h / tex_h)
            new_w = tex_w * scale
            new_h = tex_h * scale
            offset_x = (dst_w - new_w) / 2
            offset_y = (dst_h - new_h) / 2
            src = Rect(0, 0, int(tex_w), int(tex_h))
            dst = Rect(
                int(self.computed_x + offset_x),
                int(self.computed_y + offset_y),
                int(new_w),
                int(new_h),
            )

        elif self.fit == ImageFit.COVER:
            # Cover area, maintain aspect ratio (may crop)
            scale = max(dst_w / tex_w, dst_h / tex_h)
            src_w = dst_w / scale
            src_h = dst_h / scale
            src_x = (tex_w - src_w) / 2
            src_y = (tex_h - src_h) / 2
            src = Rect(int(src_x), int(src_y), int(src_w), int(src_h))
            dst = Rect(
                int(self.computed_x), int(self.computed_y), int(dst_w), int(dst_h)
            )

        else:  # NONE - original size, centered
            offset_x = (dst_w - tex_w) / 2
            offset_y = (dst_h - tex_h) / 2
            src = Rect(0, 0, int(tex_w), int(tex_h))
            dst = Rect(
                int(self.computed_x + offset_x),
                int(self.computed_y + offset_y),
                int(tex_w),
                int(tex_h),
            )

        return src, dst


class ImageFit:
    """Image fitting modes."""

    FILL = "fill"  # Stretch to fill container (may distort)
    CONTAIN = "contain"  # Fit inside container (may have gaps)
    COVER = "cover"  # Cover container (may crop)
    NONE = "none"  # Original size, centered
