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

    def test_single_line_text_uses_single_cached_line(self, mock_runtime):
        from arepy_ui.components.text import Text

        text = Text("Hello")

        assert text._lines == ("Hello",)
        assert text._is_multiline is False

    def test_multiline_text_measures_first_line_once(self, mock_runtime):
        from arepy_ui.components.text import Text
        from arepy_ui.core.fonts import TextMetrics

        metrics_by_line = {
            "Line 1": TextMetrics(width=80.0, height=20.0, line_height=24.0),
            "Line 2": TextMetrics(width=100.0, height=20.0, line_height=24.0),
            "Line 3": TextMetrics(width=90.0, height=20.0, line_height=24.0),
        }

        with patch(
            "arepy_ui.components.text.measure_text_ex",
            side_effect=lambda text, *_args: metrics_by_line[text],
        ) as measure_mock:
            text = Text("Line 1\nLine 2\nLine 3")

        assert measure_mock.call_count == 3
        assert text.style.width.value == 100.0
        assert text.style.height.value == 72.0
