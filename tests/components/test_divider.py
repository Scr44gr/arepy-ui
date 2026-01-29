"""Tests for Divider component."""

from unittest.mock import MagicMock, patch

import pytest


class TestDivider:
    """Tests for Divider component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.components.divider.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_runtime.renderer = self.mock_renderer
            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_divider_creation_default(self):
        """Test creating a Divider with default parameters."""
        from arepy_ui.components.divider import Divider

        divider = Divider()

        assert divider is not None

    def test_divider_horizontal_orientation(self):
        """Test creating a horizontal Divider."""
        from arepy_ui.components.divider import Divider, DividerOrientation

        divider = Divider(orientation=DividerOrientation.HORIZONTAL)

        assert divider.orientation == DividerOrientation.HORIZONTAL

    def test_divider_vertical_orientation(self):
        """Test creating a vertical Divider."""
        from arepy_ui.components.divider import Divider, DividerOrientation

        divider = Divider(orientation=DividerOrientation.VERTICAL)

        assert divider.orientation == DividerOrientation.VERTICAL

    def test_divider_custom_thickness(self):
        """Test creating a Divider with custom thickness."""
        from arepy_ui.components.divider import Divider

        divider = Divider(thickness=3)

        assert divider.thickness == 3

    def test_divider_custom_color(self):
        """Test creating a Divider with custom color."""
        from arepy_ui.components.divider import Divider
        from arepy_ui.core.types import Color

        custom_color = Color(255, 0, 0, 255)
        divider = Divider(color=custom_color)

        assert divider.divider_color == custom_color

    def test_divider_with_label(self):
        """Test creating a Divider with label."""
        from arepy_ui.components.divider import Divider

        divider = Divider(label="Section")

        assert divider.label == "Section"

    def test_divider_handle_input_no_interaction(self):
        """Test that Divider does not consume input."""
        from arepy_ui.components.divider import Divider

        divider = Divider()
        divider.computed_x = 0
        divider.computed_y = 0
        divider.computed_width = 200
        divider.computed_height = 1

        mock_mouse = MagicMock()
        mock_mouse.x = 100
        mock_mouse.y = 0

        result = divider.handle_input(mock_mouse, False)

        # Divider should not consume input
        assert result == False

    def test_divider_render(self):
        """Test Divider rendering."""
        from arepy_ui.components.divider import Divider

        divider = Divider()
        divider.computed_x = 0
        divider.computed_y = 50
        divider.computed_width = 300
        divider.computed_height = 1

        # Should not raise
        divider.render()

    def test_divider_with_style(self):
        """Test creating a Divider with custom style."""
        from arepy_ui.components.divider import Divider
        from arepy_ui.core.style import Style
        from arepy_ui.core.types import Unit

        style = Style(width=Unit.percent(80))
        divider = Divider(style=style)

        assert divider is not None

    def test_divider_label_position(self):
        """Test Divider with label position."""
        from arepy_ui.components.divider import Divider

        divider = Divider(label="Test", label_position="center")

        assert divider.label == "Test"
        assert divider.label_position == "center"
