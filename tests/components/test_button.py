"""Tests para arepy_ui.components.button"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.core.fonts import TextMetrics


@pytest.fixture(autouse=True)
def mock_runtime():
    """Mock runtime for all tests in this module."""
    mock_metrics = TextMetrics(width=100.0, height=20.0, line_height=24.0)

    with patch("arepy_ui.core.fonts.get_font_manager") as mock_fm:
        mock_fm.return_value.measure_text_ex.return_value = mock_metrics
        yield mock_fm


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
