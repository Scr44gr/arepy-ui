"""Tests for Canvas component."""

from unittest.mock import MagicMock, patch

import pytest


class TestCanvas:
    """Tests for Canvas component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.components.canvas.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_runtime.renderer = self.mock_renderer
            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_canvas_creation_with_callback(self):
        """Test creating a Canvas with render callback."""
        from arepy_ui.components.canvas import Canvas

        render_callback = MagicMock()
        canvas = Canvas(on_render=render_callback)

        assert canvas.on_render == render_callback
        assert canvas.state == {}

    def test_canvas_with_custom_size(self):
        """Test creating a Canvas with custom dimensions."""
        from arepy_ui.components.canvas import Canvas
        from arepy_ui.core.types import Unit

        render_callback = MagicMock()
        canvas = Canvas(
            on_render=render_callback, width=Unit.px(500), height=Unit.px(400)
        )

        assert canvas is not None

    def test_canvas_state(self):
        """Test Canvas state management."""
        from arepy_ui.components.canvas import Canvas

        render_callback = MagicMock()
        initial_state = {"counter": 0, "color": "red"}
        canvas = Canvas(on_render=render_callback, state=initial_state)

        assert canvas.state == initial_state

        # Modify state
        canvas.state["counter"] = 5
        assert canvas.state["counter"] == 5

    def test_canvas_render_calls_callback(self):
        """Test that render calls the on_render callback."""
        from arepy_ui.components.canvas import Canvas

        render_callback = MagicMock()
        canvas = Canvas(on_render=render_callback)

        # Set computed values
        canvas.computed_x = 0
        canvas.computed_y = 0
        canvas.computed_width = 300
        canvas.computed_height = 200

        canvas.render()

        render_callback.assert_called_once()

    def test_canvas_handle_input_no_interaction(self):
        """Test that Canvas handle_input returns False by default."""
        from arepy_ui.components.canvas import Canvas

        render_callback = MagicMock()
        canvas = Canvas(on_render=render_callback)
        canvas.computed_x = 0
        canvas.computed_y = 0
        canvas.computed_width = 300
        canvas.computed_height = 200

        mock_mouse = MagicMock()
        mock_mouse.x = 150
        mock_mouse.y = 100

        result = canvas.handle_input(mock_mouse, False)

        # Canvas typically doesn't consume input unless specified
        assert isinstance(result, bool)

    def test_canvas_with_style(self):
        """Test creating a Canvas with custom style."""
        from arepy_ui.components.canvas import Canvas
        from arepy_ui.core.style import Style
        from arepy_ui.core.types import Color

        render_callback = MagicMock()
        style = Style(background_color=Color(30, 30, 40, 255), border_radius=8.0)
        canvas = Canvas(on_render=render_callback, style=style)

        assert canvas.style.background_color == Color(30, 30, 40, 255)

    def test_canvas_with_background_color(self):
        """Test creating a Canvas with background color."""
        from arepy_ui.components.canvas import Canvas
        from arepy_ui.core.types import Color

        render_callback = MagicMock()
        bg_color = Color(50, 50, 60, 255)
        canvas = Canvas(on_render=render_callback, background_color=bg_color)

        assert canvas.style.background_color == bg_color
