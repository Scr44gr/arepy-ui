"""Tests for Toggle component."""

from unittest.mock import MagicMock, patch

import pytest


class TestToggle:
    """Tests for Toggle component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with (
            patch("arepy_ui.components.toggle.get_runtime") as mock_get_runtime,
            patch(
                "arepy_ui.components.toggle.check_collision_point_rec"
            ) as mock_collision,
        ):
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_renderer.measure_text.return_value = 100
            self.mock_runtime.renderer = self.mock_renderer
            mock_get_runtime.return_value = self.mock_runtime

            self.mock_collision = mock_collision
            mock_collision.return_value = False

            yield

    def test_toggle_creation_default(self):
        """Test creating a Toggle with default values."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle()

        assert toggle.checked == False

    def test_toggle_creation_checked(self):
        """Test creating a Toggle in checked state."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(checked=True)

        assert toggle.checked == True

    def test_toggle_with_label(self):
        """Test creating a Toggle with label."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(label="Enable feature")

        assert toggle.label == "Enable feature"

    def test_toggle_disabled(self):
        """Test creating a disabled Toggle."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(disabled=True)

        assert toggle.disabled == True

    def test_toggle_on_change_callback(self):
        """Test Toggle on_change callback."""
        from arepy_ui.components.toggle import Toggle

        on_change_callback = MagicMock()
        toggle = Toggle(on_change=on_change_callback)

        toggle.toggle()

        on_change_callback.assert_called_once_with(True)

    def test_toggle_method(self):
        """Test Toggle toggle method."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(checked=False)

        toggle.toggle()
        assert toggle.checked == True

        toggle.toggle()
        assert toggle.checked == False

    def test_toggle_disabled_no_toggle(self):
        """Test disabled Toggle cannot be toggled."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(checked=False, disabled=True)

        toggle.toggle()

        assert toggle.checked == False

    def test_toggle_animation_progress(self):
        """Test Toggle animation progress initialization."""
        from arepy_ui.components.toggle import Toggle

        toggle_off = Toggle(checked=False)
        toggle_on = Toggle(checked=True)

        assert toggle_off._animation_progress == 0.0
        assert toggle_on._animation_progress == 1.0

    def test_toggle_colors(self):
        """Test Toggle color properties."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle()

        assert toggle.track_color_off is not None
        assert toggle.track_color_on is not None
        assert toggle.track_color_disabled is not None
        assert toggle.thumb_color is not None
        assert toggle.thumb_color_disabled is not None
        assert toggle.label_color is not None
        assert toggle.label_color_disabled is not None

    def test_toggle_sizes(self):
        """Test Toggle size properties."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle()

        assert toggle.thumb_padding == 3
        assert toggle.label_gap == 10
        assert toggle.font_size == 14

    def test_toggle_handle_input_not_visible(self):
        """Test Toggle handle_input when not visible."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle()
        toggle.style.visible = False

        mock_mouse = MagicMock()
        mock_mouse.x = 25
        mock_mouse.y = 13

        result = toggle.handle_input(mock_mouse, False)

        assert result == False

    def test_toggle_handle_input_disabled(self):
        """Test Toggle handle_input when disabled."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(disabled=True)
        toggle.computed_x = 0
        toggle.computed_y = 0
        toggle.computed_width = 50
        toggle.computed_height = 26

        mock_mouse = MagicMock()
        mock_mouse.x = 25
        mock_mouse.y = 13

        result = toggle.handle_input(mock_mouse, True)

        assert result == False

    def test_toggle_handle_input_in_bounds(self):
        """Test Toggle handle_input within bounds."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle()
        toggle.computed_x = 0
        toggle.computed_y = 0
        toggle.computed_width = 50
        toggle.computed_height = 26

        mock_mouse = MagicMock()
        mock_mouse.x = 25
        mock_mouse.y = 13

        result = toggle.handle_input(mock_mouse, False)

        assert isinstance(result, bool)

    def test_toggle_render(self):
        """Test Toggle rendering."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle(checked=True)
        toggle.computed_x = 0
        toggle.computed_y = 0
        toggle.computed_width = 50
        toggle.computed_height = 26

        # Should not raise
        toggle.render()

    def test_toggle_with_custom_size(self):
        """Test Toggle with custom dimensions."""
        from arepy_ui.components.toggle import Toggle
        from arepy_ui.core.types import Unit

        toggle = Toggle(width=Unit.px(60), height=Unit.px(30))

        assert toggle is not None

    def test_toggle_animation_speed(self):
        """Test Toggle animation speed."""
        from arepy_ui.components.toggle import Toggle

        toggle = Toggle()

        assert toggle._animation_speed == 8.0
