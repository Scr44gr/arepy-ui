"""Tests para arepy_ui.components.select"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.components.select import Select
from arepy_ui.core.types import Unit


@pytest.fixture
def mock_runtime():
    """Mock runtime for render tests."""
    with patch("arepy_ui.components.select.get_runtime") as mock_get_runtime:
        mock_rt = MagicMock()
        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_input.get_mouse_position.return_value = (100, 100)
        mock_rt.renderer = mock_renderer
        mock_rt.input = mock_input
        mock_get_runtime.return_value = mock_rt
        yield {"runtime": mock_rt, "renderer": mock_renderer, "input": mock_input}


@pytest.fixture
def mock_collision():
    """Mock collision detection."""
    with patch("arepy_ui.components.select.check_collision_point_rec") as mock:
        yield mock


@pytest.fixture
def mock_overlay():
    """Mock register_overlay."""
    with patch("arepy_ui.components.select.register_overlay") as mock:
        yield mock


class TestSelect:
    def test_select_creation(self):
        options = ["Option 1", "Option 2", "Option 3"]
        select = Select(options=options)
        assert select.options == options

    def test_select_default_index(self):
        options = ["A", "B", "C"]
        select = Select(options=options)
        # Default selected_index is 0
        assert select.selected_index == 0

    def test_select_selected_index(self):
        options = ["X", "Y", "Z"]
        select = Select(options=options)
        assert select.selected_index == 0
        select.selected_index = 2
        assert select.selected_index == 2

    def test_select_empty_options(self):
        select = Select(options=[])
        assert select.options == []
        # selected_index is still 0 but options are empty
        assert select.selected_index == 0

    def test_select_on_change_callback(self):
        selected_values = []

        def on_change(index, value):
            selected_values.append((index, value))

        options = ["First", "Second", "Third"]
        select = Select(options=options, on_change=on_change)

        assert select.on_change == on_change

    def test_select_change_selected_index(self):
        options = ["One", "Two", "Three"]
        select = Select(options=options)

        select.selected_index = 2
        assert select.selected_index == 2

    def test_select_is_open_state(self):
        options = ["A", "B"]
        select = Select(options=options)
        assert select.is_open == False
        select.is_open = True
        assert select.is_open == True

    def test_select_dimensions(self):
        options = ["Test"]
        select = Select(options=options, width=Unit.px(200), height=Unit.px(50))
        assert select.style.width.value == 200
        assert select.style.height.value == 50


class TestSelectHandleInput:
    """Tests for select handle_input method."""

    def test_handle_input_click_opens_dropdown(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        select = Select(options=["A", "B", "C"])
        select.computed_x = 10
        select.computed_y = 20
        select.computed_width = 150
        select.computed_height = 40

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 30

        result = select.handle_input(mouse_pos, is_click=True)

        assert result is True
        assert select.is_open is True

    def test_handle_input_click_closes_dropdown(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        select = Select(options=["A", "B", "C"])
        select.is_open = True
        select.computed_x = 10
        select.computed_y = 20
        select.computed_width = 150
        select.computed_height = 40
        select._render_x = 10
        select._render_y = 20

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 30

        # Click on main rect with dropdown open toggles it closed
        result = select.handle_input(mouse_pos, is_click=True)

        # First checks options, then main box
        assert result is True

    def test_handle_input_select_option(self, mock_runtime, mock_collision):
        # First check main rect, then option rect
        mock_collision.side_effect = [False, True]
        mock_runtime["input"].get_mouse_position.return_value = (50, 80)

        selected = []
        select = Select(
            options=["A", "B", "C"], on_change=lambda i, v: selected.append((i, v))
        )
        select.is_open = True
        select.computed_x = 10
        select.computed_y = 20
        select.computed_width = 150
        select.computed_height = 40
        select._render_x = 10
        select._render_y = 20

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 80

        result = select.handle_input(mouse_pos, is_click=True)

        assert result is True
        assert select.is_open is False
        assert selected == [(0, "A")]

    def test_handle_input_hover_sets_flag(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        select = Select(options=["A", "B"])
        select.computed_x = 10
        select.computed_y = 20
        select.computed_width = 150
        select.computed_height = 40

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 30

        result = select.handle_input(mouse_pos, is_click=False)

        assert result is True
        assert select.is_hovered is True

    def test_handle_input_invisible_returns_false(self, mock_runtime, mock_collision):
        select = Select(options=["A", "B"])
        select.style.visible = False

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 30

        result = select.handle_input(mouse_pos, is_click=True)

        assert result is False


class TestSelectRender:
    """Tests for select render method."""

    def test_render_closed(self, mock_runtime, mock_overlay):
        select = Select(options=["A", "B", "C"])
        select.computed_x = 10
        select.computed_y = 20
        select.computed_width = 150
        select.computed_height = 40

        select.render()

        renderer = mock_runtime["renderer"]
        renderer.draw_rectangle_rounded.assert_called()
        # Verify something was rendered (text uses draw_text internally)
        assert renderer.draw_rectangle_rounded.call_count >= 1

    def test_render_invisible_does_nothing(self, mock_runtime, mock_overlay):
        select = Select(options=["A", "B", "C"])
        select.style.visible = False

        select.render()

        mock_runtime["renderer"].draw_rectangle_rounded.assert_not_called()

    def test_render_open_registers_overlay(self, mock_runtime, mock_overlay):
        select = Select(options=["A", "B", "C"])
        select.is_open = True
        select.computed_x = 10
        select.computed_y = 20
        select.computed_width = 150
        select.computed_height = 40

        select.render()

        # Should register overlay for dropdown
        mock_overlay.assert_called_once()
