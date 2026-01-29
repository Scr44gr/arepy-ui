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
