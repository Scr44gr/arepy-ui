"""Tests for fonts module."""

from unittest.mock import MagicMock, patch

import pytest


class TestTextMetrics:
    """Tests for TextMetrics dataclass."""

    def test_text_metrics_creation(self):
        """Test creating TextMetrics."""
        from arepy_ui.core.fonts import TextMetrics

        metrics = TextMetrics(width=100.0, height=20.0, line_height=24.0)

        assert metrics.width == 100.0
        assert metrics.height == 20.0
        assert metrics.line_height == 24.0

    def test_text_metrics_default_line_height(self):
        """Test TextMetrics default line height calculation."""
        from arepy_ui.core.fonts import TextMetrics

        # When line_height is 0.0 (default), post_init sets it to height
        metrics = TextMetrics(width=100.0, height=20.0)

        # According to __post_init__, when line_height == 0.0, it becomes height
        assert metrics.line_height == 20.0


class TestFontInfo:
    """Tests for FontInfo dataclass."""

    def test_font_info_creation(self):
        """Test creating FontInfo."""
        from arepy_ui.core.fonts import FontInfo

        mock_font = MagicMock()
        font_info = FontInfo(font=mock_font, name="test_font", base_size=32)

        assert font_info.font == mock_font
        assert font_info.name == "test_font"
        assert font_info.base_size == 32

    def test_font_info_get_scale(self):
        """Test FontInfo scale calculation."""
        from arepy_ui.core.fonts import FontInfo

        mock_font = MagicMock()
        font_info = FontInfo(font=mock_font, name="test_font", base_size=32)

        # Scale for target size 16 should be 0.5
        scale = font_info.get_scale(16.0)
        assert scale == 0.5

        # Scale for target size 64 should be 2.0
        scale = font_info.get_scale(64.0)
        assert scale == 2.0


class TestFontManager:
    """Tests for FontManager class."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.core.fonts.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_runtime.renderer = self.mock_renderer

            # Mock font loading
            self.mock_font = MagicMock()
            self.mock_font.texture = MagicMock()
            self.mock_font.texture.id = 1
            self.mock_renderer.load_font_ex.return_value = self.mock_font

            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_font_manager_singleton(self):
        """Test FontManager singleton pattern."""
        from arepy_ui.core.fonts import FontManager

        # Reset singleton for test
        FontManager._instance = None

        manager1 = FontManager.get_instance()
        manager2 = FontManager.get_instance()

        assert manager1 is manager2

    def test_font_manager_initial_state(self):
        """Test FontManager initial state."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()

        assert manager._fonts == {}
        assert manager._default_font_name is None

    def test_font_manager_load_font(self):
        """Test loading a font."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()

        result = manager.load_font("test", "path/to/font.ttf", base_size=32)

        assert result == True
        assert "test" in manager._fonts
        self.mock_renderer.load_font_ex.assert_called_once()

    def test_font_manager_load_font_set_as_default(self):
        """Test loading a font and setting as default."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()

        manager.load_font("default_font", "path/to/font.ttf", set_as_default=True)

        assert manager._default_font_name == "default_font"

    def test_font_manager_load_font_failed(self):
        """Test loading a font with failed texture."""
        from arepy_ui.core.fonts import FontManager

        # Make texture.id = 0 to simulate failed load
        self.mock_font.texture.id = 0

        manager = FontManager()

        with pytest.raises(ValueError) as exc_info:
            manager.load_font("test", "invalid/path.ttf")

        assert "Font texture not loaded" in str(exc_info.value)

    def test_font_manager_get_font_info(self):
        """Test getting font info by name."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        manager.load_font("my_font", "path/to/font.ttf")

        font_info = manager.get_font_info("my_font")

        assert font_info is not None
        assert font_info.name == "my_font"

    def test_font_manager_get_font_info_default(self):
        """Test getting default font info."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        manager.load_font("default", "path/to/font.ttf", set_as_default=True)

        font_info = manager.get_font_info()  # No name, should return default

        assert font_info is not None
        assert font_info.name == "default"

    def test_font_manager_get_font_info_not_found(self):
        """Test getting font info for non-existent font."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()

        font_info = manager.get_font_info("non_existent")

        assert font_info is None

    def test_font_manager_get_font(self):
        """Test getting a font object."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        manager.load_font("my_font", "path/to/font.ttf")

        font = manager.get_font("my_font")

        assert font is not None

    def test_measure_text_ex_uses_cache(self):
        """Repeated measurements with the same key should hit the in-memory cache."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        self.mock_renderer.measure_text_ex.return_value = (120.0, 24.0)
        self.mock_renderer.get_font_default.return_value = MagicMock()

        first = manager.measure_text_ex("Hello cache", 18.0)
        second = manager.measure_text_ex("Hello cache", 18.0)

        assert first.width == second.width
        assert self.mock_renderer.measure_text_ex.call_count == 1

    def test_font_manager_load_multiple_fonts(self):
        """Batch loading should load all requests and return their names."""
        from arepy_ui.core.fonts import FontLoadRequest, FontManager

        manager = FontManager()
        requests = [
            FontLoadRequest(name="title", path="fonts/title.ttf", base_size=48),
            FontLoadRequest(
                name="body",
                path="fonts/body.ttf",
                base_size=24,
                set_as_default=True,
            ),
            FontLoadRequest(name="mono", path="fonts/mono.ttf", base_size=16),
        ]

        loaded = manager.load_fonts(requests)

        assert loaded == ["title", "body", "mono"]
        assert set(manager._fonts.keys()) == {"title", "body", "mono"}
        assert manager._default_font_name == "body"
        assert self.mock_renderer.load_font_ex.call_count == 3

    def test_font_manager_batch_load_preserves_unaffected_measurement_cache(self):
        """Batch loading should preserve cached default metrics when the default font is unchanged."""
        from arepy_ui.core.fonts import FontLoadRequest, FontManager, TextMetrics

        manager = FontManager()
        manager._measurement_cache[("__default__", "Hello", 16.0, 1.0)] = TextMetrics(
            width=100.0,
            height=20.0,
            line_height=20.0,
        )

        manager.load_fonts(
            [
                FontLoadRequest(name="title", path="fonts/title.ttf", base_size=48),
                FontLoadRequest(name="body", path="fonts/body.ttf", base_size=24),
            ]
        )

        assert ("__default__", "Hello", 16.0, 1.0) in manager._measurement_cache

    def test_font_manager_batch_load_invalidates_default_cache_when_default_changes(
        self,
    ):
        """Changing the default font in a batch should invalidate default-font measurements."""
        from arepy_ui.core.fonts import FontLoadRequest, FontManager, TextMetrics

        manager = FontManager()
        manager._measurement_cache[("__default__", "Hello", 16.0, 1.0)] = TextMetrics(
            width=100.0,
            height=20.0,
            line_height=20.0,
        )

        manager.load_fonts(
            [
                FontLoadRequest(
                    name="body",
                    path="fonts/body.ttf",
                    base_size=24,
                    set_as_default=True,
                ),
            ]
        )

        assert ("__default__", "Hello", 16.0, 1.0) not in manager._measurement_cache

    def test_font_manager_load_font_with_glyph_subset(self):
        """Glyph subsets should be forwarded to the renderer as codepoints."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        manager.load_font("score", "fonts/score.ttf", glyphs="SCORE: 0123456789")

        glyph_codes = self.mock_renderer.load_font_ex.call_args.args[2]
        assert ord("S") in glyph_codes
        assert ord("0") in glyph_codes
        assert len(glyph_codes) < len(range(32, 127))

    def test_font_manager_unload_font(self):
        """Unloading a single font should remove it and return True."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        manager.load_font("hud", "fonts/hud.ttf", set_as_default=True)

        unloaded = manager.unload_font("hud")

        assert unloaded is True
        assert "hud" not in manager._fonts
        assert manager._default_font_name is None
        self.mock_renderer.unload_font.assert_called_once()

    def test_font_manager_unload_fonts(self):
        """Batch unload should remove all known names and ignore unknown ones."""
        from arepy_ui.core.fonts import FontManager

        manager = FontManager()
        manager.load_font("title", "fonts/title.ttf")
        manager.load_font("body", "fonts/body.ttf", set_as_default=True)

        unloaded = manager.unload_fonts(["title", "body", "missing"])

        assert unloaded == ["title", "body"]
        assert manager._fonts == {}
        assert manager._default_font_name is None
        assert self.mock_renderer.unload_font.call_count == 2
