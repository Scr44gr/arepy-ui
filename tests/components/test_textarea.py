"""Tests for TextArea component."""

from unittest.mock import MagicMock, patch

import pytest


class TestTextArea:
    """Tests for TextArea component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with (
            patch("arepy_ui.components.textarea.get_runtime") as mock_get_runtime,
            patch(
                "arepy_ui.components.textarea.check_collision_point_rec"
            ) as mock_collision,
        ):
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_renderer.measure_text.return_value = 100
            self.mock_runtime.renderer = self.mock_renderer
            self.mock_runtime.input = MagicMock()
            self.mock_runtime.input.is_key_pressed.return_value = False
            self.mock_runtime.input.is_key_down.return_value = False
            self.mock_runtime.input.get_char_pressed.return_value = 0
            self.mock_runtime.time = MagicMock()
            self.mock_runtime.time.get_delta_time.return_value = 0.016
            mock_get_runtime.return_value = self.mock_runtime

            self.mock_collision = mock_collision
            mock_collision.return_value = False

            yield

    def test_textarea_creation_default(self):
        """Test creating a TextArea with default values."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()

        assert textarea.placeholder == ""
        assert textarea.value == ""

    def test_textarea_with_placeholder(self):
        """Test creating a TextArea with placeholder."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea(placeholder="Enter text here...")

        assert textarea.placeholder == "Enter text here..."

    def test_textarea_get_value(self):
        """Test getting text from TextArea."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()
        textarea._lines = ["Line 1", "Line 2", "Line 3"]

        text = textarea.value

        assert text == "Line 1\nLine 2\nLine 3"

    def test_textarea_set_value(self):
        """Test setting text in TextArea."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()
        textarea.value = "Hello\nWorld"

        assert textarea._lines == ["Hello", "World"]

    def test_textarea_set_value_single_line(self):
        """Test setting single line text."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()
        textarea.value = "Single line"

        assert textarea._lines == ["Single line"]

    def test_textarea_show_line_numbers(self):
        """Test TextArea with line numbers."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea(show_line_numbers=True)

        assert textarea.show_line_numbers == True

    def test_textarea_font_size(self):
        """Test TextArea with custom font size."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea(font_size=16)

        assert textarea.font_size == 16

    def test_textarea_tab_size(self):
        """Test TextArea with custom tab size."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea(tab_size=2)

        assert textarea.tab_size == 2

    def test_textarea_on_change_callback(self):
        """Test TextArea on_change callback."""
        from arepy_ui.components.textarea import TextArea

        on_change_callback = MagicMock()
        textarea = TextArea(on_change=on_change_callback)

        assert textarea.on_change == on_change_callback

    def test_textarea_cursor_position(self):
        """Test TextArea cursor position."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()
        textarea._lines = ["Hello", "World"]
        textarea.cursor_line = 1
        textarea.cursor_col = 3

        assert textarea.cursor_line == 1
        assert textarea.cursor_col == 3

    def test_textarea_selection_state(self):
        """Test TextArea selection state."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()

        assert textarea.has_selection == False
        assert textarea.selection_start_line == 0
        assert textarea.selection_start_col == 0

    def test_textarea_focus_state(self):
        """Test TextArea focus state."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()

        assert textarea.is_focused == False

    def test_textarea_scroll_state(self):
        """Test TextArea scroll state."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()

        assert textarea.scroll_y == 0.0
        assert textarea.scroll_x == 0.0

    def test_textarea_handle_input(self):
        """Test TextArea input handling."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()
        textarea.computed_x = 0
        textarea.computed_y = 0
        textarea.computed_width = 400
        textarea.computed_height = 200

        mock_mouse = MagicMock()
        mock_mouse.x = 200
        mock_mouse.y = 100

        result = textarea.handle_input(mock_mouse, False)

        assert isinstance(result, bool)

    def test_textarea_render(self):
        """Test TextArea rendering."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()
        textarea._lines = ["Hello", "World"]
        textarea.computed_x = 0
        textarea.computed_y = 0
        textarea.computed_width = 400
        textarea.computed_height = 200

        # Should not raise
        textarea.render()

    def test_textarea_with_custom_size(self):
        """Test TextArea with custom dimensions."""
        from arepy_ui.components.textarea import TextArea
        from arepy_ui.core.types import Unit

        textarea = TextArea(width=Unit.px(500), height=Unit.px(300))

        assert textarea is not None

    def test_textarea_custom_colors(self):
        """Test TextArea with custom colors."""
        from arepy_ui.components.textarea import TextArea
        from arepy_ui.core.types import Color

        textarea = TextArea()

        assert textarea.text_color is not None
        assert textarea.placeholder_color is not None
        assert textarea.selection_color is not None
        assert textarea.line_number_color is not None

    def test_textarea_key_repeat_constants(self):
        """Test TextArea key repeat constants."""
        from arepy_ui.components.textarea import TextArea

        assert TextArea.KEY_REPEAT_DELAY == 0.4
        assert TextArea.KEY_REPEAT_RATE == 0.05

    def test_textarea_cursor_blink(self):
        """Test TextArea cursor blink state."""
        from arepy_ui.components.textarea import TextArea

        textarea = TextArea()

        assert textarea.cursor_timer == 0.0
        assert textarea.show_cursor == True
