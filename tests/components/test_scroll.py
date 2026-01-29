"""Tests para arepy_ui.components.scroll"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.components.scroll import ScrollView
from arepy_ui.core.node import Node
from arepy_ui.core.style import Style
from arepy_ui.core.types import FlexDirection, Unit


@pytest.fixture
def mock_runtime():
    """Mock runtime for render tests."""
    with patch("arepy_ui.components.scroll.get_runtime") as mock_get_runtime:
        mock_rt = MagicMock()
        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_input.is_mouse_button_down.return_value = False
        mock_input.get_mouse_wheel_delta.return_value = 0
        mock_rt.renderer = mock_renderer
        mock_rt.input = mock_input
        mock_get_runtime.return_value = mock_rt
        yield {"runtime": mock_rt, "renderer": mock_renderer, "input": mock_input}


@pytest.fixture
def mock_collision():
    """Mock collision detection."""
    with patch("arepy_ui.components.scroll.check_collision_point_rec") as mock:
        yield mock


class TestScrollView:
    def test_scrollview_creation(self):
        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(
            width=Unit.px(200),
            height=Unit.px(400),
            content=content,
        )
        assert scroll.content is content

    def test_scrollview_initial_scroll(self):
        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(
            width=Unit.px(200),
            height=Unit.px(400),
            content=content,
        )
        assert scroll.scroll_y == 0

    def test_scrollview_dimensions(self):
        content = Node()
        scroll = ScrollView(
            width=Unit.px(300),
            height=Unit.px(500),
            content=content,
        )
        assert scroll.style.width.value == 300
        assert scroll.style.height.value == 500

    def test_scrollview_set_scroll_y(self):
        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(
            width=Unit.px(200),
            height=Unit.px(400),
            content=content,
        )
        # scroll_y is negative when scrolled down
        scroll.scroll_y = -100
        assert scroll.scroll_y == -100

    def test_scrollview_with_tall_content(self):
        # Crear contenido largo
        content = Node(
            style=Style(
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
            )
        )
        for i in range(20):
            content.add_child(Node(style=Style(height=Unit.px(50))))

        scroll = ScrollView(
            width=Unit.px(200),
            height=Unit.px(300),
            content=content,
        )

        # El scroll debería poder contener el contenido
        assert scroll.content is content

    def test_scrollview_scroll_speed(self):
        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(
            width=Unit.px(200),
            height=Unit.px(400),
            content=content,
        )
        assert scroll.scroll_speed == 40.0  # default
        scroll.scroll_speed = 60.0
        assert scroll.scroll_speed == 60.0


class TestScrollViewRender:
    """Tests for scrollview render method."""

    def test_render_with_scrollbar(self, mock_runtime):
        content = MagicMock()
        content.computed_height = 1000
        content.translate = MagicMock()
        content.render = MagicMock()

        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.computed_x = 0
        scroll.computed_y = 0
        scroll.computed_width = 200
        scroll.computed_height = 400

        scroll.render()

        renderer = mock_runtime["renderer"]
        renderer.begin_scissor_mode.assert_called_once()
        renderer.end_scissor_mode.assert_called_once()
        # Should draw scrollbar track and thumb
        renderer.draw_rectangle.assert_called()
        renderer.draw_rectangle_rounded.assert_called()

    def test_render_no_scrollbar_when_content_fits(self, mock_runtime):
        content = MagicMock()
        content.computed_height = 300
        content.translate = MagicMock()
        content.render = MagicMock()

        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.computed_x = 0
        scroll.computed_y = 0
        scroll.computed_width = 200
        scroll.computed_height = 400

        scroll.render()

        renderer = mock_runtime["renderer"]
        renderer.begin_scissor_mode.assert_called_once()
        # Should NOT draw scrollbar since content fits
        renderer.draw_rectangle.assert_not_called()

    def test_render_invisible_does_nothing(self, mock_runtime):
        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.style.visible = False

        scroll.render()

        mock_runtime["renderer"].begin_scissor_mode.assert_not_called()


class TestScrollViewHandleInput:
    """Tests for scrollview handle_input method."""

    def test_handle_input_wheel_scroll(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        mock_runtime["input"].get_mouse_wheel_delta.return_value = -1

        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.computed_x = 0
        scroll.computed_y = 0
        scroll.computed_width = 200
        scroll.computed_height = 400
        scroll.content.computed_height = 1000

        mouse_pos = MagicMock()
        mouse_pos.x = 100
        mouse_pos.y = 200

        result = scroll.handle_input(mouse_pos, is_click=False)

        assert result is True
        assert scroll.scroll_y < 0  # Scrolled down

    def test_handle_input_outside_returns_false(self, mock_runtime, mock_collision):
        mock_collision.return_value = False

        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.computed_x = 0
        scroll.computed_y = 0
        scroll.computed_width = 200
        scroll.computed_height = 400

        mouse_pos = MagicMock()
        mouse_pos.x = 500
        mouse_pos.y = 500

        result = scroll.handle_input(mouse_pos, is_click=False)

        assert result is False

    def test_handle_input_invisible_returns_false(self, mock_runtime, mock_collision):
        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.style.visible = False

        mouse_pos = MagicMock()
        mouse_pos.x = 100
        mouse_pos.y = 200

        result = scroll.handle_input(mouse_pos, is_click=False)

        assert result is False

    def test_handle_input_drag_scrollbar(self, mock_runtime, mock_collision):
        # First call for view, second call for thumb hit
        mock_collision.side_effect = [True, True]
        mock_runtime["input"].is_mouse_button_down.return_value = True

        content = Node(style=Style(height=Unit.px(1000)))
        scroll = ScrollView(width=Unit.px(200), height=Unit.px(400), content=content)
        scroll.computed_x = 0
        scroll.computed_y = 0
        scroll.computed_width = 200
        scroll.computed_height = 400
        scroll.content.computed_height = 1000

        mouse_pos = MagicMock()
        mouse_pos.x = 195  # Near scrollbar
        mouse_pos.y = 50

        result = scroll.handle_input(mouse_pos, is_click=True)

        assert result is True
        assert scroll.is_dragging is True
