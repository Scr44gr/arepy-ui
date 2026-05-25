from arepy_ui.logging import logger
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

from arepy import ArepyTexture, TextureFilter

from ..runtime import get_runtime
from .types import Color

_ASCII_FONT_CHARS = list(range(32, 127))


@dataclass(frozen=True, slots=True)
class FontLoadRequest:
    """Configuration for loading a font into the FontManager."""

    name: str
    path: str
    base_size: int = 64
    set_as_default: bool = False
    texture_filter: Optional[TextureFilter] = None
    glyphs: Optional[str | tuple[int, ...]] = None


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
    glyph_count: int = 0

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
        self._measurement_cache: Dict[Tuple[str, str, float, float], TextMetrics] = {}
        self._measurement_cache_limit = 2048
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

    def _normalize_glyphs(self, glyphs: Optional[str | tuple[int, ...]]) -> list[int]:
        if glyphs is None:
            return _ASCII_FONT_CHARS

        if isinstance(glyphs, str):
            seen: set[int] = set()
            normalized: list[int] = []
            for character in glyphs:
                codepoint = ord(character)
                if codepoint not in seen:
                    seen.add(codepoint)
                    normalized.append(codepoint)
            return normalized or _ASCII_FONT_CHARS

        seen_ints: set[int] = set()
        normalized_ints: list[int] = []
        for codepoint in glyphs:
            value = int(codepoint)
            if value not in seen_ints:
                seen_ints.add(value)
                normalized_ints.append(value)
        return normalized_ints or _ASCII_FONT_CHARS

    def _invalidate_measurement_cache(
        self,
        font_names: Iterable[str],
        include_default: bool = False,
    ) -> None:
        names = set(font_names)
        if not names and not include_default:
            return

        self._measurement_cache = {
            key: metrics
            for key, metrics in self._measurement_cache.items()
            if key[0] not in names and not (include_default and key[0] == "__default__")
        }

    def _apply_texture_filter(
        self,
        runtime,
        font: Any,
        base_size: int,
        texture_filter: Optional[TextureFilter],
    ) -> None:
        if texture_filter is None:
            return

        try:
            temp_texture = ArepyTexture(-1, size=(base_size, base_size))
            temp_texture._ref_texture = font._ref_font.texture
            runtime.renderer.set_texture_filter(temp_texture, texture_filter)
        except Exception as e:
            logger.error(
                f"Failed to apply texture filter: {texture_filter} - {e}",
                exc_info=True,
            )

    def _load_font_request(
        self,
        runtime,
        request: FontLoadRequest,
        clear_cache: bool = True,
    ) -> bool:
        glyph_codes = self._normalize_glyphs(request.glyphs)
        font = runtime.renderer.load_font_ex(
            Path(request.path),
            request.base_size,
            glyph_codes,
            len(glyph_codes),
        )

        if font is None:
            raise ValueError(f"Font texture not loaded from path: {request.path}")

        try:
            if (
                hasattr(font, "texture")
                and hasattr(font.texture, "id")
                and font.texture.id == 0
            ):
                raise ValueError(f"Font texture not loaded from path: {request.path}")
        except (AttributeError, TypeError):
            pass

        applied_filter = (
            request.texture_filter
            if request.texture_filter is not None
            else self.texture_filter
        )
        self._apply_texture_filter(runtime, font, request.base_size, applied_filter)

        replacing_existing = request.name in self._fonts
        default_will_change = request.set_as_default

        self._fonts[request.name] = FontInfo(
            font=font,
            name=request.name,
            base_size=request.base_size,
            glyph_count=len(glyph_codes),
        )

        if request.set_as_default:
            self._default_font_name = request.name

        if clear_cache:
            self._invalidate_measurement_cache(
                {request.name} if replacing_existing else set(),
                include_default=default_will_change,
            )

        return True

    def load_font(
        self,
        name: str,
        path: str,
        base_size: int = 64,
        set_as_default: bool = False,
        texture_filter: Optional[TextureFilter] = None,
        glyphs: Optional[str | tuple[int, ...]] = None,
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
                glyphs: Optional glyph subset. Pass a string like `"ABC123"` or a tuple
                    of integer codepoints to limit what gets loaded.

        Returns:
            True if loaded successfully
        """
        runtime = get_runtime()
        request = FontLoadRequest(
            name=name,
            path=path,
            base_size=base_size,
            set_as_default=set_as_default,
            texture_filter=texture_filter,
            glyphs=glyphs,
        )
        return self._load_font_request(runtime, request)

    def load_fonts(self, font_requests: list[FontLoadRequest]) -> list[str]:
        """Load multiple fonts efficiently using a single runtime lookup."""
        if not font_requests:
            return []

        runtime = get_runtime()
        loaded_fonts: list[str] = []
        replaced_names = {
            request.name for request in font_requests if request.name in self._fonts
        }

        for request in font_requests:
            self._load_font_request(runtime, request, clear_cache=False)
            loaded_fonts.append(request.name)

        include_default = any(request.set_as_default for request in font_requests)
        self._invalidate_measurement_cache(
            replaced_names, include_default=include_default
        )
        return loaded_fonts

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
            self._invalidate_measurement_cache(set(), include_default=True)
            return True
        return False

    def unload_font(self, name: str) -> bool:
        """Unload a single font and remove it from the registry."""
        font_info = self._fonts.get(name)
        if font_info is None:
            return False

        runtime = get_runtime()
        runtime.renderer.unload_font(font_info.font)
        del self._fonts[name]

        removed_default = self._default_font_name == name
        if removed_default:
            self._default_font_name = None

        self._invalidate_measurement_cache({name}, include_default=removed_default)
        return True

    def unload_fonts(self, names: list[str]) -> list[str]:
        """Unload multiple fonts and return the names successfully removed."""
        if not names:
            return []

        runtime = get_runtime()
        unloaded: list[str] = []
        removed_default = False

        for name in names:
            font_info = self._fonts.get(name)
            if font_info is None:
                continue

            runtime.renderer.unload_font(font_info.font)
            del self._fonts[name]
            unloaded.append(name)

            if self._default_font_name == name:
                removed_default = True

        if removed_default:
            self._default_font_name = None

        self._invalidate_measurement_cache(
            set(unloaded), include_default=removed_default
        )
        return unloaded

    def _clear_measurement_cache(self) -> None:
        self._measurement_cache.clear()

    def _get_measurement_cache_key(
        self,
        text: str,
        font_size: float,
        font_name: Optional[str],
        spacing: float,
    ) -> Tuple[str, str, float, float]:
        return (
            font_name or "__default__",
            text,
            round(font_size, 4),
            round(spacing, 4),
        )

    def _cache_measurement(
        self,
        cache_key: Tuple[str, str, float, float],
        metrics: TextMetrics,
    ) -> TextMetrics:
        if cache_key in self._measurement_cache:
            return self._measurement_cache[cache_key]

        if len(self._measurement_cache) >= self._measurement_cache_limit:
            oldest_key = next(iter(self._measurement_cache))
            self._measurement_cache.pop(oldest_key, None)

        self._measurement_cache[cache_key] = metrics
        return metrics

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
        cache_key = self._get_measurement_cache_key(text, font_size, font_name, spacing)
        cached_metrics = self._measurement_cache.get(cache_key)
        if cached_metrics is not None:
            return cached_metrics

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
                try:
                    glyph_padding = font.glyphPadding
                except AttributeError:
                    glyph_padding = 0
                line_height = size_y + (glyph_padding * scale * 2)

                return self._cache_measurement(
                    cache_key,
                    TextMetrics(width=size_x, height=size_y, line_height=line_height),
                )
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
        return self._cache_measurement(
            cache_key,
            TextMetrics(width=size_x, height=size_y, line_height=line_height),
        )

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
        self._clear_measurement_cache()


# Convenience functions
def get_font_manager() -> FontManager:
    """Get the font manager instance."""
    return FontManager.get_instance()


def load_font(
    name: str,
    path: str,
    base_size: int = 32,
    set_as_default: bool = False,
    texture_filter: Optional[TextureFilter] = None,
    glyphs: Optional[str | tuple[int, ...]] = None,
) -> bool:
    """Load a font."""
    return get_font_manager().load_font(
        name,
        path,
        base_size,
        set_as_default,
        texture_filter,
        glyphs,
    )


def load_fonts(font_requests: list[FontLoadRequest]) -> list[str]:
    """Load multiple fonts in one call."""
    return get_font_manager().load_fonts(font_requests)


def unload_font(name: str) -> bool:
    """Unload a single font by name."""
    return get_font_manager().unload_font(name)


def unload_fonts(names: list[str]) -> list[str]:
    """Unload multiple fonts by name."""
    return get_font_manager().unload_fonts(names)


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
