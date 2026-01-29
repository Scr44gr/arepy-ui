"""Tests para arepy_ui.components.text"""

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


class TestText:
    def test_text_creation(self, mock_runtime):
        from arepy_ui.components.text import Text

        text = Text("Hello World")
        assert text.text == "Hello World"

    def test_text_with_size(self, mock_runtime):
        from arepy_ui.components.text import Text

        text = Text("Hello", size=24)
        assert text.font_size == 24

    def test_text_with_color(self, mock_runtime):
        from arepy_ui.components.text import Text
        from arepy_ui.core.types import Color

        color = Color(255, 0, 0, 255)
        text = Text("Red text", color=color)
        assert text.color == color

    def test_text_default_color(self, mock_runtime):
        from arepy_ui.components.text import Text

        text = Text("Default")
        assert text.color is not None

    def test_text_update(self, mock_runtime):
        from arepy_ui.components.text import Text

        text = Text("Initial")
        text.text = "Updated"
        assert text.text == "Updated"

    def test_text_empty(self, mock_runtime):
        from arepy_ui.components.text import Text

        text = Text("")
        assert text.text == ""
