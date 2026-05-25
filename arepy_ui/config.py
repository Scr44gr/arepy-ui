from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Optional, Tuple, List

from arepy import TextureFilter
from arepy.engine.input import Key


class ResizeMode(Enum):
    """How the UI should behave when the window is resized."""

    # UI recalculates layout to fit new window size (responsive)
    RESPONSIVE = auto()

    # UI scales uniformly to fit, maintaining aspect ratio (letterboxing)
    SCALE_FIT = auto()

    # UI scales to fill the window, may crop content
    SCALE_FILL = auto()

    # UI stays at fixed size, positioned in corner/center
    FIXED = auto()


class ScaleAnchor(Enum):
    """Where to anchor the UI when using FIXED or SCALE modes."""

    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    CENTER_LEFT = auto()
    CENTER = auto()
    CENTER_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_CENTER = auto()
    BOTTOM_RIGHT = auto()


@dataclass
class UIConfig:
    """Configuration for UI behavior."""

    # === Resize Behavior ===
    resize_mode: ResizeMode = ResizeMode.RESPONSIVE

    # Reference resolution for SCALE_* and FIXED modes
    # When None, uses the initial window size
    reference_width: Optional[int] = None
    reference_height: Optional[int] = None

    # Anchor point for FIXED and SCALE modes
    scale_anchor: ScaleAnchor = ScaleAnchor.CENTER

    # Minimum scale factor (prevents UI from getting too small)
    min_scale: float = 0.5

    # Maximum scale factor (prevents UI from getting too large)
    max_scale: float = 2.0

    # === Font Rendering Options ===
    # The texture filter to apply to font textures. Change this to control
    # how fonts are filtered when scaled (use an Arepy TextureFilter value).
    font_texture_filter: TextureFilter = TextureFilter.BILINEAR

    # === Layout Options ===
    # Debounce layout recalculation (ms) - helps with rapid resize
    layout_debounce_ms: float = 0.0

    # === Debug Overlay ===
    debug_enabled: bool = False
    debug_toggle_key: Optional[Key] = Key.F3
    debug_bounds_key: Optional[Key] = Key.F4
    debug_padding_key: Optional[Key] = Key.F5
    debug_tree_key: Optional[Key] = Key.F6

    # === Callbacks ===
    # Called when window is resized: (new_width, new_height)
    on_resize: Optional[Callable[[int, int], None]] = None

    # Called before layout recalculation
    on_before_layout: Optional[Callable[[], None]] = None

    # Called after layout recalculation
    on_after_layout: Optional[Callable[[], None]] = None

    def set_font_texture_filter(self, filter: TextureFilter) -> None:
        """Set the font texture filter and notify registered listeners.

        This updates the config value and triggers a notification so that
        FontManager, UIManager, or other listeners can apply the new filter.
        """
        self.font_texture_filter = filter
        notify_font_texture_filter_change(filter)


@dataclass
class ScaleTransform:
    """Represents the current scale transformation applied to the UI."""

    scale_x: float = 1.0
    scale_y: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0

    @property
    def uniform_scale(self) -> float:
        """Returns the minimum scale (for uniform scaling)."""
        return min(self.scale_x, self.scale_y)

    def apply_to_point(self, x: float, y: float) -> Tuple[float, float]:
        """Transform a point from UI coordinates to screen coordinates."""
        return (x * self.scale_x + self.offset_x, y * self.scale_y + self.offset_y)

    def inverse_point(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Transform a point from screen coordinates to UI coordinates."""
        if self.scale_x == 0 or self.scale_y == 0:
            return (screen_x, screen_y)
        return (
            (screen_x - self.offset_x) / self.scale_x,
            (screen_y - self.offset_y) / self.scale_y,
        )


# === Font texture filter change notification helpers ===
_font_texture_filter_listeners: List[Callable[[TextureFilter], None]] = []


def register_font_texture_filter_listener(
    listener: Callable[[TextureFilter], None],
) -> None:
    """Register a listener to be called when UIConfig.font_texture_filter changes."""
    if listener not in _font_texture_filter_listeners:
        _font_texture_filter_listeners.append(listener)


def unregister_font_texture_filter_listener(
    listener: Callable[[TextureFilter], None],
) -> None:
    """Unregister a previously registered listener."""
    try:
        _font_texture_filter_listeners.remove(listener)
    except ValueError:
        pass


def notify_font_texture_filter_change(filter: TextureFilter) -> None:
    """Notify listeners and attempt to apply the filter to loaded fonts.

    This will attempt to apply the TextureFilter to any fonts already loaded
    via the FontManager. Failures while applying are swallowed to avoid
    breaking UI initialization.
    """
    font_manager_factory: Optional[Callable[[], Any]] = None
    runtime_factory: Optional[Callable[[], Any]] = None
    texture_cls: Optional[type[Any]] = None

    try:
        from .core.fonts import get_font_manager as font_manager_factory
        from .runtime import get_runtime as runtime_factory
        from arepy import ArepyTexture as texture_cls
    except Exception:
        # Required modules unavailable; still notify listeners below.
        pass

    # Apply filter to already-loaded fonts if possible
    if font_manager_factory and texture_cls and runtime_factory:
        try:
            fm = font_manager_factory()
            runtime = runtime_factory()
            for font_info in fm._fonts.values():
                try:
                    tmp_tex = texture_cls(
                        -1, size=(font_info.base_size, font_info.base_size)
                    )
                    tmp_tex._ref_texture = getattr(
                        getattr(font_info.font, "_ref_font", font_info.font),
                        "texture",
                        None,
                    )
                    if tmp_tex._ref_texture is not None:
                        runtime.renderer.set_texture_filter(tmp_tex, filter)
                except Exception:
                    # Don't let per-font failures block the process
                    pass
        except Exception:
            pass

    # Notify registered listeners
    for listener in list(_font_texture_filter_listeners):
        try:
            listener(filter)
        except Exception:
            pass


def calculate_scale_transform(
    config: UIConfig,
    reference_width: int,
    reference_height: int,
    current_width: int,
    current_height: int,
) -> ScaleTransform:
    """Calculate the scale transform based on config and window sizes."""

    if config.resize_mode == ResizeMode.RESPONSIVE:
        # No scaling, just use actual window size
        return ScaleTransform()

    elif config.resize_mode == ResizeMode.FIXED:
        # No scaling, just offset based on anchor
        transform = ScaleTransform()
        transform.offset_x, transform.offset_y = _calculate_anchor_offset(
            config.scale_anchor,
            reference_width,
            reference_height,
            current_width,
            current_height,
        )
        return transform

    elif config.resize_mode == ResizeMode.SCALE_FIT:
        # Scale uniformly to fit, with letterboxing
        scale_x = current_width / reference_width
        scale_y = current_height / reference_height
        scale = min(scale_x, scale_y)

        # Clamp scale
        scale = max(config.min_scale, min(config.max_scale, scale))

        scaled_width = reference_width * scale
        scaled_height = reference_height * scale

        offset_x, offset_y = _calculate_anchor_offset(
            config.scale_anchor,
            scaled_width,
            scaled_height,
            current_width,
            current_height,
        )

        return ScaleTransform(
            scale_x=scale,
            scale_y=scale,
            offset_x=offset_x,
            offset_y=offset_y,
        )

    elif config.resize_mode == ResizeMode.SCALE_FILL:
        # Scale to fill, may crop
        scale_x = current_width / reference_width
        scale_y = current_height / reference_height
        scale = max(scale_x, scale_y)

        # Clamp scale
        scale = max(config.min_scale, min(config.max_scale, scale))

        scaled_width = reference_width * scale
        scaled_height = reference_height * scale

        offset_x, offset_y = _calculate_anchor_offset(
            config.scale_anchor,
            scaled_width,
            scaled_height,
            current_width,
            current_height,
        )

        return ScaleTransform(
            scale_x=scale,
            scale_y=scale,
            offset_x=offset_x,
            offset_y=offset_y,
        )

    return ScaleTransform()


def _calculate_anchor_offset(
    anchor: ScaleAnchor,
    content_width: float,
    content_height: float,
    container_width: float,
    container_height: float,
) -> Tuple[float, float]:
    """Calculate offset based on anchor point."""

    # Horizontal offset
    if anchor in (
        ScaleAnchor.TOP_LEFT,
        ScaleAnchor.CENTER_LEFT,
        ScaleAnchor.BOTTOM_LEFT,
    ):
        offset_x = 0.0
    elif anchor in (
        ScaleAnchor.TOP_CENTER,
        ScaleAnchor.CENTER,
        ScaleAnchor.BOTTOM_CENTER,
    ):
        offset_x = (container_width - content_width) / 2
    else:  # RIGHT
        offset_x = container_width - content_width

    # Vertical offset
    if anchor in (ScaleAnchor.TOP_LEFT, ScaleAnchor.TOP_CENTER, ScaleAnchor.TOP_RIGHT):
        offset_y = 0.0
    elif anchor in (
        ScaleAnchor.CENTER_LEFT,
        ScaleAnchor.CENTER,
        ScaleAnchor.CENTER_RIGHT,
    ):
        offset_y = (container_height - content_height) / 2
    else:  # BOTTOM
        offset_y = container_height - content_height

    return (offset_x, offset_y)
