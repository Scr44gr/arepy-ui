"""Tests for ProgressBar component."""

from unittest.mock import MagicMock, patch

import pytest


class TestProgressBar:
    """Tests for ProgressBar component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.components.progressbar.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_runtime.renderer = self.mock_renderer
            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_progressbar_creation_default(self):
        """Test creating a ProgressBar with default values."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar()

        assert progressbar.value == 0.0
        assert progressbar.max_value == 100.0

    def test_progressbar_with_initial_value(self):
        """Test creating a ProgressBar with initial value."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(value=50.0)

        assert progressbar.value == 50.0

    def test_progressbar_with_custom_max(self):
        """Test creating a ProgressBar with custom max value."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(max_value=200.0, value=100.0)

        assert progressbar.max_value == 200.0
        assert progressbar.value == 100.0

    def test_progressbar_value_clamping_min(self):
        """Test that value is clamped to minimum."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(value=-10.0)

        assert progressbar.value == 0.0

    def test_progressbar_value_clamping_max(self):
        """Test that value is clamped to maximum."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(value=150.0, max_value=100.0)

        assert progressbar.value == 100.0

    def test_progressbar_percentage_property(self):
        """Test percentage calculation."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(value=50.0, max_value=100.0)

        assert progressbar.percentage == 50.0

    def test_progressbar_percentage_zero_max(self):
        """Test percentage with zero max value."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(max_value=0.0)

        assert progressbar.percentage == 0.0

    def test_progressbar_set_percentage(self):
        """Test setting value by percentage."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(max_value=100.0)
        progressbar.set_percentage(75.0)

        assert progressbar.value == 75.0

    def test_progressbar_value_setter(self):
        """Test value setter with clamping."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(max_value=100.0)

        progressbar.value = 80.0
        assert progressbar.value == 80.0

        progressbar.value = -20.0
        assert progressbar.value == 0.0

        progressbar.value = 200.0
        assert progressbar.value == 100.0

    def test_progressbar_show_label(self):
        """Test ProgressBar with label display."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(show_label=True)

        assert progressbar.show_label == True

    def test_progressbar_indeterminate_mode(self):
        """Test ProgressBar in indeterminate mode."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(indeterminate=True)

        assert progressbar.indeterminate == True

    def test_progressbar_handle_input_no_interaction(self):
        """Test that ProgressBar does not consume input."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar()
        progressbar.computed_x = 0
        progressbar.computed_y = 0
        progressbar.computed_width = 200
        progressbar.computed_height = 20

        mock_mouse = MagicMock()
        mock_mouse.x = 100
        mock_mouse.y = 10

        result = progressbar.handle_input(mock_mouse, False)

        # ProgressBar should not consume input (it's display only)
        assert result == False

    def test_progressbar_render(self):
        """Test ProgressBar rendering."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(value=50.0)
        progressbar.computed_x = 0
        progressbar.computed_y = 0
        progressbar.computed_width = 200
        progressbar.computed_height = 20

        # Should not raise
        progressbar.render()

    def test_progressbar_custom_colors(self):
        """Test ProgressBar with custom colors."""
        from arepy_ui.components.progressbar import ProgressBar
        from arepy_ui.core.types import Color

        progressbar = ProgressBar()
        progressbar.fill_color = Color(0, 255, 0, 255)
        progressbar.label_color = Color(255, 255, 255, 255)

        assert progressbar.fill_color == Color(0, 255, 0, 255)
        assert progressbar.label_color == Color(255, 255, 255, 255)

    def test_progressbar_with_custom_size(self):
        """Test ProgressBar with custom dimensions."""
        from arepy_ui.components.progressbar import ProgressBar
        from arepy_ui.core.types import Unit

        progressbar = ProgressBar(width=Unit.px(300), height=Unit.px(16))

        assert progressbar is not None

    def test_progressbar_animation_state(self):
        """Test ProgressBar animation state initialization."""
        from arepy_ui.components.progressbar import ProgressBar

        progressbar = ProgressBar(value=50.0)

        # Animation display value starts at the same as value
        assert progressbar._display_value == 50.0
