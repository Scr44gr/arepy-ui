"""Tests para arepy_ui.components.checkbox"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.components.checkbox import Checkbox
from arepy_ui.core.types import Color


@pytest.fixture
def mock_runtime():
    """Mock runtime for render tests."""
    with patch("arepy_ui.components.checkbox.get_runtime") as mock_get_runtime:
        mock_rt = MagicMock()
        mock_renderer = MagicMock()
        mock_renderer.measure_text.return_value = 50  # Mock text width
        mock_rt.renderer = mock_renderer
        mock_rt.input = MagicMock()
        mock_rt.input.is_mouse_button_down = MagicMock(return_value=False)
        mock_get_runtime.return_value = mock_rt
        yield mock_renderer


@pytest.fixture
def mock_collision():
    """Mock collision detection."""
    with patch("arepy_ui.components.checkbox.check_collision_point_rec") as mock:
        yield mock


class TestCheckbox:
    def test_checkbox_creation_unchecked(self):
        checkbox = Checkbox(checked=False)
        assert checkbox.checked == False

    def test_checkbox_creation_checked(self):
        checkbox = Checkbox(checked=True)
        assert checkbox.checked == True

    def test_checkbox_with_custom_size(self):
        checkbox = Checkbox(checked=False, size=30.0)
        assert checkbox.size == 30.0

    def test_checkbox_toggle(self):
        checkbox = Checkbox(checked=False)
        checkbox.checked = True
        assert checkbox.checked == True
        checkbox.checked = False
        assert checkbox.checked == False

    def test_checkbox_on_change_callback(self):
        changed_values = []

        def on_change(value):
            changed_values.append(value)

        checkbox = Checkbox(checked=False, on_change=on_change)
        # Simulate the toggle by directly calling on_change
        checkbox.checked = not checkbox.checked
        if checkbox.on_change:
            checkbox.on_change(checkbox.checked)
        assert len(changed_values) == 1
        assert changed_values[0] == True

    def test_checkbox_with_custom_color(self):
        custom_color = Color(0, 255, 0, 255)
        checkbox = Checkbox(
            checked=True,
            color=custom_color,
        )
        assert checkbox.check_color == custom_color

    def test_checkbox_with_label(self):
        checkbox = Checkbox(checked=False, label="Test Label")
        assert checkbox.label == "Test Label"


class TestCheckboxRender:
    """Tests for checkbox render method."""

    def test_render_unchecked(self, mock_runtime):
        checkbox = Checkbox(checked=False)
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        checkbox.render()

        # Should draw rounded rectangle for background
        mock_runtime.draw_rectangle_rounded.assert_called()
        # Should draw border lines
        mock_runtime.draw_rectangle_rounded_lines.assert_called()

    def test_render_checked(self, mock_runtime):
        checkbox = Checkbox(checked=True)
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        checkbox.render()

        # Should draw filled background
        mock_runtime.draw_rectangle_rounded.assert_called()
        # Should draw checkmark lines
        assert mock_runtime.draw_line_ex.call_count == 2

    def test_render_invisible_does_nothing(self, mock_runtime):
        checkbox = Checkbox(checked=True)
        checkbox.style.visible = False

        checkbox.render()

        mock_runtime.draw_rectangle_rounded.assert_not_called()

    def test_render_hovered_changes_color(self, mock_runtime):
        checkbox = Checkbox(checked=False)
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22
        checkbox.is_hovered = True

        checkbox.render()

        # Verify render was called (hover affects colors internally)
        mock_runtime.draw_rectangle_rounded.assert_called()

    def test_render_with_label(self, mock_runtime):
        checkbox = Checkbox(checked=False, label="Label")
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        checkbox.render()

        mock_runtime.draw_text.assert_called()


class TestCheckboxHandleInput:
    """Tests for checkbox handle_input method."""

    def test_handle_input_click_toggles(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        checkbox = Checkbox(checked=False)
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        mouse_pos = MagicMock()
        mouse_pos.x = 15
        mouse_pos.y = 25

        result = checkbox.handle_input(mouse_pos, is_click=True)

        assert result is True
        assert checkbox.checked is True

    def test_handle_input_click_calls_callback(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        changed = []
        checkbox = Checkbox(checked=False, on_change=lambda v: changed.append(v))
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        mouse_pos = MagicMock()
        mouse_pos.x = 15
        mouse_pos.y = 25

        checkbox.handle_input(mouse_pos, is_click=True)

        assert changed == [True]

    def test_handle_input_hover_sets_flag(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        checkbox = Checkbox(checked=False)
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        mouse_pos = MagicMock()
        mouse_pos.x = 15
        mouse_pos.y = 25

        checkbox.handle_input(mouse_pos, is_click=False)

        assert checkbox.is_hovered is True

    def test_handle_input_outside_does_not_toggle(self, mock_runtime, mock_collision):
        mock_collision.return_value = False
        checkbox = Checkbox(checked=False)
        checkbox.computed_x = 10
        checkbox.computed_y = 20
        checkbox.computed_width = 22
        checkbox.computed_height = 22

        mouse_pos = MagicMock()
        mouse_pos.x = 100
        mouse_pos.y = 100

        result = checkbox.handle_input(mouse_pos, is_click=True)

        assert result is False
        assert checkbox.checked is False

    def test_handle_input_invisible_returns_false(self, mock_collision):
        checkbox = Checkbox(checked=False)
        checkbox.style.visible = False

        mouse_pos = MagicMock()
        mouse_pos.x = 15
        mouse_pos.y = 25

        result = checkbox.handle_input(mouse_pos, is_click=True)

        assert result is False
        mock_collision.assert_not_called()
