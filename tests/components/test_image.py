"""Tests for Image component."""

from unittest.mock import MagicMock, patch

import pytest


class TestImage:
    """Tests for Image component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.components.image.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_runtime.renderer = self.mock_renderer
            self.mock_runtime.has_asset_store = True

            # Mock texture
            self.mock_texture = MagicMock()
            self.mock_texture.id = 1
            self.mock_texture.get_size.return_value = (256, 256)

            # Mock AssetStore
            self.mock_asset_store = MagicMock()
            self.mock_asset_store.get_texture.return_value = self.mock_texture
            self.mock_runtime.asset_store = self.mock_asset_store

            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_image_creation_with_source(self):
        """Test creating an Image with source path."""
        from arepy_ui.components.image import Image

        image = Image(source="assets/test.png")

        assert image.source == "assets/test.png"

    def test_image_with_custom_size(self):
        """Test creating an Image with custom dimensions."""
        from arepy_ui.components.image import Image
        from arepy_ui.core.types import Unit

        image = Image(source="test.png", width=Unit.px(200), height=Unit.px(150))

        assert image is not None

    def test_image_with_tint(self):
        """Test creating an Image with tint color."""
        from arepy_ui.components.image import Image
        from arepy_ui.core.types import Color

        tint = Color(255, 128, 128, 255)
        image = Image(source="test.png", tint=tint)

        assert image.tint == tint

    def test_image_fit_contain(self):
        """Test Image with contain fit mode."""
        from arepy_ui.components.image import Image, ImageFit

        image = Image(source="test.png", fit=ImageFit.CONTAIN)  # type: ignore

        assert image.fit == ImageFit.CONTAIN

    def test_image_fit_cover(self):
        """Test Image with cover fit mode."""
        from arepy_ui.components.image import Image, ImageFit

        image = Image(source="test.png", fit=ImageFit.COVER)  # type: ignore

        assert image.fit == ImageFit.COVER

    def test_image_fit_fill(self):
        """Test Image with fill fit mode."""
        from arepy_ui.components.image import Image, ImageFit

        image = Image(source="test.png", fit=ImageFit.FILL)  # type: ignore

        assert image.fit == ImageFit.FILL

    def test_image_handle_input_no_interaction(self):
        """Test that Image does not consume input by default."""
        from arepy_ui.components.image import Image

        image = Image(source="test.png")
        image.computed_x = 0
        image.computed_y = 0
        image.computed_width = 200
        image.computed_height = 150

        mock_mouse = MagicMock()
        mock_mouse.x = 100
        mock_mouse.y = 75

        result = image.handle_input(mock_mouse, False)

        assert result == False

    def test_image_render(self):
        """Test Image rendering."""
        from arepy_ui.components.image import Image

        image = Image(source="test.png")
        image.computed_x = 0
        image.computed_y = 0
        image.computed_width = 200
        image.computed_height = 150

        # Should not raise
        image.render()

    def test_image_with_style(self):
        """Test creating an Image with custom style."""
        from arepy_ui.components.image import Image
        from arepy_ui.core.style import Spacing, Style
        from arepy_ui.core.types import Unit

        style = Style(
            width=Unit.px(180),
            padding=Spacing.all(6),
            border_radius=8.0,
        )
        image = Image(source="test.png", style=style)

        assert image.style.border_radius == 8.0
        assert image.style.width.value == 180
        assert image.style.padding.top.value == 6

    def test_image_border_radius(self):
        """Test Image with border radius."""
        from arepy_ui.components.image import Image

        image = Image(source="test.png", border_radius=10.0)

        assert image.border_radius == 10.0

    def test_image_default_tint(self):
        """Test Image default tint is white."""
        from arepy_ui.components.image import Image
        from arepy_ui.core.types import Color

        image = Image(source="test.png")

        assert image.tint == Color(255, 255, 255, 255)
