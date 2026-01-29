from arepy_ui.logging import logger
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from arepy import ArepyTexture, TextureFilter

from ..runtime import get_runtime
from .types import Color


@dataclass
class TextMetrics:
    """Accurate text measurements from measure_text_ex."""

    width: float
    height: float
    # Line height for proper vertical spacing between lines
    # This is typically larger than height to account for line spacing
    line_height: float = 0.0

    def __post_init__(self):
        # Default line_height to height * 1.2 if not set (standard line spacing)
        if self.line_height == 0.0:
            self.line_height = self.height


@dataclass
class FontInfo:
    """Information about a loaded font."""

    font: Any  # ArepyFont from arepy
    name: str
    base_size: int

    def get_scale(self, target_size: float) -> float:
        """Get the scale factor for a target font size."""
        return target_size / self.base_size


class FontManager:
    """
    Manages fonts for the UI system.
    Provides a default font and allows loading custom fonts.
    Uses measure_text_ex for accurate font measurements.
    """

    _instance: Optional["FontManager"] = None

    def __init__(self):
        self._fonts: Dict[str, FontInfo] = {}
        self._default_font_name: Optional[str] = None
        # Default texture filter for fonts; can be changed dynamically via UIConfig
        self.texture_filter: Optional[TextureFilter] = TextureFilter.BILINEAR

        # Try to register to UIConfig's font texture filter notifications so
        # changes in configuration are applied to already loaded fonts.
        try:
            from ..config import register_font_texture_filter_listener

            register_font_texture_filter_listener(self.set_texture_filter)
        except Exception:
            # Optional; ignore if config module isn't importable yet
            pass

    @classmethod
    def get_instance(cls) -> "FontManager":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = FontManager()
        return cls._instance

    def set_texture_filter(self, texture_filter: Optional[TextureFilter]) -> None:
        """
        Set the default texture filter for fonts and apply it to already-loaded fonts.
        """
        self.texture_filter = texture_filter
        runtime = get_runtime()
        for font_info in self._fonts.values():
            try:
                if texture_filter is None:
                    continue
                tmp_tex = ArepyTexture(
                    -1, size=(font_info.base_size, font_info.base_size)
                )
                tmp_tex._ref_texture = getattr(
                    getattr(font_info.font, "_ref_font", font_info.font),
                    "texture",
                    None,
                )
                if tmp_tex._ref_texture is not None:
                    runtime.renderer.set_texture_filter(tmp_tex, texture_filter)
            except Exception:
                # Ignore per-font failures
                pass

    def load_font(
        self,
        name: str,
        path: str,
        base_size: int = 64,
        set_as_default: bool = False,
        texture_filter: Optional[TextureFilter] = None,
    ) -> bool:
        """
        Load a font from a file.

        Args:
            name: Unique name for the font
            path: Path to the font file (.ttf, .otf)
            base_size: Base size for the font (for quality rendering)
            set_as_default: Whether to set this as the default font
            texture_filter: Optional TextureFilter to apply to this font's texture.
                            If None, FontManager's default `self.texture_filter` is used.

        Returns:
            True if loaded successfully
        """
        runtime = get_runtime()
        # Load font with specified size for quality
        # Provide ASCII character codes (32-126) for glyphCount=95
        font_chars = list(range(32, 127))
        font = runtime.renderer.load_font_ex(Path(path), base_size, font_chars, 95)

        if font is None:
            raise ValueError(f"Font texture not loaded from path: {path}")

        # Check if font texture was loaded successfully
        try:
            if hasattr(font, 'texture') and hasattr(font.texture, 'id') and font.texture.id == 0:
                raise ValueError(f"Font texture not loaded from path: {path}")
        except (AttributeError, TypeError):
            # If we can't check texture.id, assume font loaded successfully
            pass

        # Determine which filter to apply (per-call overrides manager default)
        applied_filter = (
            texture_filter if texture_filter is not None else self.texture_filter
        )
        if applied_filter is not None:
            try:
                _temp_texture = ArepyTexture(-1, size=(base_size, base_size))
                _temp_texture._ref_texture = font._ref_font.texture  # type: ignore
                runtime.renderer.set_texture_filter(_temp_texture, applied_filter)
            except Exception as e:
                logger.error(f"Failed to apply texture filter: {applied_filter} - {e}", exc_info=True)

        font_info = FontInfo(font=font, name=name, base_size=base_size)

        self._fonts[name] = font_info

        if set_as_default:
            self._default_font_name = name

        return True

    def get_font_info(self, name: Optional[str] = None) -> Optional[FontInfo]:
        """Get font info by name, or the default font info."""
        if name is None:
            name = self._default_font_name

        if name and name in self._fonts:
            return self._fonts[name]

        return None

    def get_font(self, name: Optional[str] = None) -> Any:
        """
        Get a font by name, or the default font.

        Args:
            name: Font name, or None for default

        Returns:
            The font, or arepy's default if not found
        """
        font_info = self.get_font_info(name)
        if font_info:
            return font_info.font
        return get_runtime().renderer.get_font_default()

    def get_default_font(self) -> Any:
        """Get the default font."""
        return self.get_font(None)

    def has_font(self, name: str) -> bool:
        """Check if a font is loaded."""
        return name in self._fonts

    def set_default_font(self, name: str) -> bool:
        """Set the default font by name."""
        if name in self._fonts:
            self._default_font_name = name
            return True
        return False

    def measure_text_ex(
        self,
        text: str,
        font_size: float,
        font_name: Optional[str] = None,
        spacing: float = 1.0,
    ) -> TextMetrics:
        """
        Measure text dimensions using arepy's measure_text_ex.
        Returns width, height, and line_height for accurate layout.

        Args:
            text: The text to measure
            font_size: The font size
            font_name: Font name, or None for default
            spacing: Character spacing

        Returns:
            TextMetrics with width, height, and line_height
        """
        runtime = get_runtime()
        font_info = self.get_font_info(font_name)

        if font_info:
            font = font_info.font
            try:
                # Use measure_text_ex for accurate measurements
                size_x, size_y = runtime.renderer.measure_text_ex(
                    font, text, font_size, spacing
                )

                # Calculate line height from font properties
                # baseSize is the font's design size, glyphPadding adds extra spacing
                scale = (
                    font_size / font_info.base_size if font_info.base_size > 0 else 1.0
                )
                # Line height = font height + some padding for readability
                line_height = size_y + (getattr(font, "glyphPadding", 0) * scale * 2)

                return TextMetrics(width=size_x, height=size_y, line_height=line_height)
            except Exception:
                # Fall back to default font if custom font fails (e.g., missing glyphs)
                pass

        # Fallback to default font measurement
        default_font = runtime.renderer.get_font_default()
        size_x, size_y = runtime.renderer.measure_text_ex(
            default_font, text, font_size, spacing
        )
        # Default font: use 1.2x height as standard line height
        line_height = size_y * 1.2
        return TextMetrics(width=size_x, height=size_y, line_height=line_height)

    def measure_text(
        self,
        text: str,
        font_size: float,
        font_name: Optional[str] = None,
        spacing: float = 1.0,
    ) -> float:
        """
        Measure text width with a specific font.

        Args:
            text: The text to measure
            font_size: The font size
            font_name: Font name, or None for default
            spacing: Character spacing

        Returns:
            Width in pixels
        """
        return self.measure_text_ex(text, font_size, font_name, spacing).width

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        font_size: float,
        color: Color,
        font_name: Optional[str] = None,
        spacing: float = 1.0,
    ) -> None:
        """
        Draw text with a specific font.

        Args:
            text: The text to draw
            x: X position
            y: Y position
            font_size: The font size
            color: Text color
            font_name: Font name, or None for default
            spacing: Character spacing
        """
        runtime = get_runtime()
        font_info = self.get_font_info(font_name)

        if font_info:
            # Use custom font with proper size
            runtime.renderer.draw_text_ex(
                font_info.font, text, (x, y), font_size, spacing, color
            )
        else:
            # Fallback to default font with draw_text_ex for consistency
            default_font = runtime.renderer.get_font_default()
            runtime.renderer.draw_text_ex(
                default_font, text, (x, y), font_size, spacing, color
            )

    def draw_text_centered(
        self,
        text: str,
        center_x: float,
        center_y: float,
        font_size: float,
        color: Color,
        font_name: Optional[str] = None,
        spacing: float = 1.0,
    ) -> None:
        """
        Draw text centered at a specific point.

        Args:
            text: The text to draw
            center_x: Center X position
            center_y: Center Y position
            font_size: The font size
            color: Text color
            font_name: Font name, or None for default
            spacing: Character spacing
        """
        metrics = self.measure_text_ex(text, font_size, font_name, spacing)
        x = center_x - metrics.width / 2
        y = center_y - metrics.height / 2
        self.draw_text(text, x, y, font_size, color, font_name, spacing)

    def unload_all(self) -> None:
        """Unload all fonts."""
        runtime = get_runtime()
        for font_info in self._fonts.values():
            runtime.renderer.unload_font(font_info.font)
        self._fonts.clear()
        self._default_font_name = None


# Convenience functions
def get_font_manager() -> FontManager:
    """Get the font manager instance."""
    return FontManager.get_instance()


def load_font(
    name: str, path: str, base_size: int = 32, set_as_default: bool = False
) -> bool:
    """Load a font."""
    return get_font_manager().load_font(name, path, base_size, set_as_default)


def get_font(name: Optional[str] = None) -> Any:
    """Get a font by name."""
    return get_font_manager().get_font(name)


def draw_text(
    text: str,
    x: float,
    y: float,
    font_size: float,
    color: Color,
    font_name: Optional[str] = None,
    spacing: float = 1.0,
) -> None:
    """Draw text with optional custom font."""
    get_font_manager().draw_text(text, x, y, font_size, color, font_name, spacing)


def measure_text(
    text: str, font_size: float, font_name: Optional[str] = None, spacing: float = 1.0
) -> float:
    """Measure text width."""
    return get_font_manager().measure_text(text, font_size, font_name, spacing)


def measure_text_ex(
    text: str, font_size: float, font_name: Optional[str] = None, spacing: float = 1.0
) -> TextMetrics:
    """Measure text dimensions (width and height)."""
    return get_font_manager().measure_text_ex(text, font_size, font_name, spacing)


def draw_text_centered(
    text: str,
    center_x: float,
    center_y: float,
    font_size: float,
    color: Color,
    font_name: Optional[str] = None,
    spacing: float = 1.0,
) -> None:
    """Draw text centered at a point."""
    get_font_manager().draw_text_centered(
        text, center_x, center_y, font_size, color, font_name, spacing
    )
