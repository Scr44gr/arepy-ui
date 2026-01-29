"""Tests for Slider component."""

from unittest.mock import MagicMock, patch

import pytest


class TestSlider:
    """Tests for Slider component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.components.slider.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_runtime.renderer = self.mock_renderer
            self.mock_runtime.input = MagicMock()
            self.mock_runtime.input.is_mouse_button_down.return_value = False
            self.mock_runtime.input.is_mouse_button_released.return_value = False
            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_slider_creation_default(self):
        """Test creating a Slider with default values."""
        from arepy_ui.components.slider import Slider

        slider = Slider()

        assert slider.min_value == 0.0
        assert slider.max_value == 1.0
        assert slider.value == 0.0

    def test_slider_with_custom_range(self):
        """Test creating a Slider with custom range."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100, value=50)

        assert slider.min_value == 0
        assert slider.max_value == 100
        assert slider.value == 50

    def test_slider_value_clamping_min(self):
        """Test that value is clamped to minimum."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100, value=-10)

        assert slider.value == 0

    def test_slider_value_clamping_max(self):
        """Test that value is clamped to maximum."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100, value=150)

        assert slider.value == 100

    def test_slider_value_setter(self):
        """Test Slider value setter."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100)

        slider.value = 75
        assert slider.value == 75

        slider.value = -10
        assert slider.value == 0

        slider.value = 200
        assert slider.value == 100

    def test_slider_value_with_step(self):
        """Test Slider value with step."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100, step=10)

        slider.value = 53
        # Should snap to nearest step (50)
        assert slider.value == 50

    def test_slider_normalized_value(self):
        """Test normalized value property."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100, value=50)

        assert slider.normalized_value == 0.5

    def test_slider_normalized_value_setter(self):
        """Test setting normalized value."""
        from arepy_ui.components.slider import Slider

        slider = Slider(min_value=0, max_value=100)

        slider.normalized_value = 0.75
        assert slider.value == 75

    def test_slider_on_change_callback(self):
        """Test Slider on_change callback."""
        from arepy_ui.components.slider import Slider

        on_change_callback = MagicMock()
        slider = Slider(on_change=on_change_callback)

        slider.value = 0.5

        on_change_callback.assert_called_once_with(0.5)

    def test_slider_on_change_not_called_same_value(self):
        """Test on_change is not called when value doesn't change."""
        from arepy_ui.components.slider import Slider

        on_change_callback = MagicMock()
        slider = Slider(value=0.5, on_change=on_change_callback)

        slider.value = 0.5

        on_change_callback.assert_not_called()

    def test_slider_horizontal_orientation(self):
        """Test Slider with horizontal orientation."""
        from arepy_ui.components.slider import Slider, SliderOrientation

        slider = Slider(orientation=SliderOrientation.HORIZONTAL)  # type: ignore

        assert slider.orientation == SliderOrientation.HORIZONTAL

    def test_slider_vertical_orientation(self):
        """Test Slider with vertical orientation."""
        from arepy_ui.components.slider import Slider, SliderOrientation

        slider = Slider(orientation=SliderOrientation.VERTICAL)  # type: ignore

        assert slider.orientation == SliderOrientation.VERTICAL

    def test_slider_custom_colors(self):
        """Test Slider with custom colors."""
        from arepy_ui.components.slider import Slider
        from arepy_ui.core.types import Color

        track_color = Color(60, 60, 60, 255)
        fill_color = Color(0, 200, 100, 255)
        thumb_color = Color(255, 255, 255, 255)

        slider = Slider(
            track_color=track_color, fill_color=fill_color, thumb_color=thumb_color
        )

        assert slider.track_color == track_color
        assert slider.fill_color == fill_color
        assert slider.thumb_color == thumb_color

    def test_slider_thumb_size(self):
        """Test Slider with custom thumb size."""
        from arepy_ui.components.slider import Slider

        slider = Slider(thumb_size=20.0)

        assert slider.thumb_size == 20.0

    def test_slider_track_height(self):
        """Test Slider with custom track height."""
        from arepy_ui.components.slider import Slider

        slider = Slider(track_height=10.0)

        assert slider.track_height == 10.0

    def test_slider_handle_input_not_visible(self):
        """Test Slider handle_input when not visible."""
        from arepy_ui.components.slider import Slider

        slider = Slider()
        slider.style.visible = False

        mock_mouse = MagicMock()
        mock_mouse.x = 100
        mock_mouse.y = 12

        result = slider.handle_input(mock_mouse, False)

        assert result == False

    def test_slider_handle_input_in_bounds(self):
        """Test Slider handle_input within bounds."""
        from arepy_ui.components.slider import Slider

        slider = Slider()
        slider.computed_x = 0
        slider.computed_y = 0
        slider.computed_width = 200
        slider.computed_height = 24

        mock_mouse = MagicMock()
        mock_mouse.x = 100
        mock_mouse.y = 12

        result = slider.handle_input(mock_mouse, False)

        assert isinstance(result, bool)

    def test_slider_render(self):
        """Test Slider rendering."""
        from arepy_ui.components.slider import Slider

        slider = Slider(value=0.5)
        slider.computed_x = 0
        slider.computed_y = 0
        slider.computed_width = 200
        slider.computed_height = 24

        # Should not raise
        slider.render()

    def test_slider_with_custom_size(self):
        """Test Slider with custom dimensions."""
        from arepy_ui.components.slider import Slider
        from arepy_ui.core.types import Unit

        slider = Slider(width=Unit.px(300), height=Unit.px(30))

        assert slider is not None

    def test_slider_dragging_state(self):
        """Test Slider dragging state initialization."""
        from arepy_ui.components.slider import Slider

        slider = Slider()

        assert slider._is_dragging == False
        assert slider._is_hovered == False
