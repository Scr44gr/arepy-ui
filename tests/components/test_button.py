"""Tests para arepy_ui.components.button"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.core.fonts import TextMetrics


@pytest.fixture(autouse=True)
def mock_runtime():
    """Mock runtime for all tests in this module."""
    mock_metrics = TextMetrics(width=100.0, height=20.0, line_height=24.0)

    with patch("arepy_ui.core.fonts.get_font_manager") as mock_fm:
        manager = mock_fm.return_value
        manager.measure_text_ex.return_value = mock_metrics
        manager.draw_text = MagicMock()
        yield manager


class TestButton:
    def test_button_creation(self, mock_runtime):
        from arepy_ui.components.button import Button
        from arepy_ui.core.types import Color, Unit

        clicked = [False]

        def on_click():
            clicked[0] = True

        btn = Button(
            text="Click Me",
            on_click=on_click,
            width=Unit.px(100),
            height=Unit.px(40),
            bg_color=Color(100, 100, 100, 255),
        )

        # Button has a text_node child with the text
        assert btn.text_node is not None

    def test_button_dimensions(self, mock_runtime):
        from arepy_ui.components.button import Button
        from arepy_ui.core.types import Color, Unit

        btn = Button(
            text="Test",
            on_click=lambda: None,
            width=Unit.px(150),
            height=Unit.px(50),
            bg_color=Color(100, 100, 100, 255),
        )

        assert btn.style.width.value == 150
        assert btn.style.height.value == 50

    def test_button_colors(self, mock_runtime):
        from arepy_ui.components.button import Button
        from arepy_ui.core.types import Color, Unit

        bg_color = Color(50, 100, 150, 255)
        btn = Button(
            text="Colored",
            on_click=lambda: None,
            width=Unit.px(100),
            height=Unit.px(40),
            bg_color=bg_color,
        )

        # Button stores base_color for hover effects
        assert btn.base_color == bg_color
        assert btn.style.background_color is not None

    def test_button_with_font_size(self, mock_runtime):
        from arepy_ui.components.button import Button
        from arepy_ui.core.types import Color, Unit

        btn = Button(
            text="Big Text",
            on_click=lambda: None,
            width=Unit.px(100),
            height=Unit.px(40),
            bg_color=Color(100, 100, 100, 255),
            font_size=20,
        )

        # Font size is passed to text_node
        assert btn.text_node is not None

    def test_button_style_merge_preserves_margin(self, mock_runtime):
        from arepy_ui.components.button import Button
        from arepy_ui.core.style import Spacing, Style

        btn = Button(
            text="Styled",
            on_click=lambda: None,
            style=Style(margin=Spacing.symmetric(6, 10)),
        )

        assert btn.style.margin.top.value == 6
        assert btn.style.margin.left.value == 10

    def test_button_render_uses_texture_when_visual_transform_active(self, mock_runtime):
        from arepy.engine.renderer import Rect
        from arepy_ui.components.button import Button
        from arepy_ui.core.types import Color, Unit

        texture = MagicMock()
        texture.get_size.return_value = (120, 48)

        runtime = MagicMock()
        runtime.display.get_window_size.return_value = (1280, 720)
        runtime.renderer.create_render_texture.return_value = texture

        btn = Button(
            text="Styled",
            on_click=lambda: None,
            width=Unit.px(120),
            height=Unit.px(48),
            bg_color=Color(100, 100, 100, 255),
        )
        btn.render_via_texture = True
        btn.visual_scale_x = 1.08
        btn.visual_scale_y = 0.94
        btn.visual_rotation_degrees = 3.0
        btn.computed_x = 32
        btn.computed_y = 64
        btn.computed_width = 120
        btn.computed_height = 48
        btn.text_node.computed_x = 56
        btn.text_node.computed_y = 76

        with patch("arepy_ui.components.button.get_runtime", return_value=runtime):
            btn.render()

        runtime.renderer.create_render_texture.assert_called_once_with(120, 48)
        runtime.renderer.bind_render_texture.assert_called_once_with(texture)
        runtime.renderer.draw_texture_ex.assert_called_once()
        _, _, destination_rect, origin, _, _ = runtime.renderer.draw_texture_ex.call_args[0]
        assert destination_rect == Rect(92.0, 88.0, 130, 45)
        assert origin == (65.0, 22.5)
        mock_runtime.draw_text.assert_called_once()

    def test_button_hitbox_uses_visual_scale(self, mock_runtime):
        from arepy_ui.components.button import Button
        from arepy_ui.core.types import Color, Unit, Vector2

        runtime = MagicMock()
        runtime.input.is_mouse_button_down.return_value = False

        btn = Button(
            text="Hover",
            on_click=lambda: None,
            width=Unit.px(100),
            height=Unit.px(40),
            bg_color=Color(100, 100, 100, 255),
        )
        btn.computed_x = 0
        btn.computed_y = 0
        btn.computed_width = 100
        btn.computed_height = 40
        btn.visual_scale_x = 1.2
        btn.visual_scale_y = 1.1

        with patch("arepy_ui.components.button.get_runtime", return_value=runtime):
            btn.handle_input(Vector2(105, 20), is_click=False)

        assert btn.is_hovered is True
