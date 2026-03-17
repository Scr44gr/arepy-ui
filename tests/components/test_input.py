"""Tests para arepy_ui.components.input"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.components.input import TextInput
from arepy_ui.core.types import Color, CursorType, Unit


@pytest.fixture
def mock_runtime():
    """Mock runtime for render/input tests."""
    with (
        patch("arepy_ui.components.input.get_runtime") as mock_get_runtime,
        patch("arepy_ui.core.fonts.get_runtime") as mock_fonts_get_runtime,
        patch("arepy_ui.core.fonts.get_font_manager") as mock_get_font_manager,
    ):
        mock_rt = MagicMock()
        mock_renderer = MagicMock()
        mock_renderer.measure_text.return_value = 50
        mock_renderer.get_delta_time.return_value = 0.016
        mock_input = MagicMock()
        mock_input.is_key_down.return_value = False
        mock_input.is_key_pressed.return_value = False
        mock_input.is_mouse_button_pressed.return_value = False
        mock_input.is_mouse_button_down.return_value = False
        mock_input.get_char_pressed.return_value = 0
        mock_rt.renderer = mock_renderer
        mock_rt.input = mock_input
        mock_get_runtime.return_value = mock_rt
        mock_fonts_get_runtime.return_value = mock_rt

        # Mock font manager
        mock_font_manager = MagicMock()
        mock_font_manager.measure_text.return_value = 50
        mock_get_font_manager.return_value = mock_font_manager

        yield {
            "runtime": mock_rt,
            "renderer": mock_renderer,
            "input": mock_input,
            "font_manager": mock_font_manager,
        }


@pytest.fixture
def mock_collision():
    """Mock collision detection."""
    with patch("arepy_ui.components.input.check_collision_point_rec") as mock:
        yield mock


class TestTextInput:
    def test_textinput_creation(self):
        input_field = TextInput()
        assert input_field.value == ""

    def test_textinput_with_placeholder(self):
        input_field = TextInput(placeholder="Enter name...")
        assert input_field.placeholder == "Enter name..."

    def test_textinput_initial_value_empty(self):
        input_field = TextInput()
        # Value starts empty, can be set later
        input_field.value = "Initial text"
        assert input_field.value == "Initial text"

    def test_textinput_dimensions(self):
        input_field = TextInput(
            width=Unit.px(200),
            height=Unit.px(40),
        )
        assert input_field.style.width.value == 200
        assert input_field.style.height.value == 40

    def test_textinput_set_value(self):
        input_field = TextInput()
        input_field.value = "New value"
        assert input_field.value == "New value"

    def test_textinput_on_change_callback(self):
        changes = []

        def on_change(value):
            changes.append(value)

        input_field = TextInput(on_change=on_change)
        assert input_field.on_change == on_change

    def test_textinput_focus_state(self):
        input_field = TextInput()
        assert input_field.is_focused == False
        input_field.is_focused = True
        assert input_field.is_focused == True

    def test_textinput_custom_style_preserves_defaults(self):
        from arepy_ui.core.style import Style

        input_field = TextInput(style=Style(border_radius=10.0))

        assert input_field.style.width.value == 200
        assert input_field.style.height.value == 40
        assert input_field.style.border_radius == 10.0
        assert input_field.style.cursor == CursorType.IBEAM


class TestTextInputSelection:
    """Tests for text selection functionality."""

    def test_clear_selection(self):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 5
        input_field.has_selection = True
        input_field.selection_start = 0

        input_field._clear_selection()

        assert input_field.has_selection is False
        assert input_field.selection_start == 5

    def test_start_selection(self):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 3

        input_field._start_selection()

        assert input_field.has_selection is True
        assert input_field.selection_start == 3

    def test_get_selection_range(self):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 8
        input_field.selection_start = 3
        input_field.has_selection = True

        result = input_field._get_selection_range()

        assert result == (3, 8)

    def test_get_selection_range_reversed(self):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 3
        input_field.selection_start = 8
        input_field.has_selection = True

        result = input_field._get_selection_range()

        assert result == (3, 8)

    def test_get_selection_range_no_selection(self):
        input_field = TextInput()
        input_field.has_selection = False

        result = input_field._get_selection_range()

        assert result is None

    def test_get_selection_range_same_position(self):
        input_field = TextInput()
        input_field.cursor_pos = 5
        input_field.selection_start = 5
        input_field.has_selection = True

        result = input_field._get_selection_range()

        assert result is None

    def test_get_selected_text(self):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 5
        input_field.selection_start = 0
        input_field.has_selection = True

        result = input_field._get_selected_text()

        assert result == "Hello"

    def test_delete_selection(self):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 5
        input_field.selection_start = 0
        input_field.has_selection = True

        result = input_field._delete_selection()

        assert result is True
        assert input_field.value == " World"
        assert input_field.cursor_pos == 0
        assert input_field.has_selection is False

    def test_delete_selection_no_selection(self):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.has_selection = False

        result = input_field._delete_selection()

        assert result is False
        assert input_field.value == "Hello"

    def test_insert_text(self):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 5

        input_field._insert_text(" World")

        assert input_field.value == "Hello World"
        assert input_field.cursor_pos == 11

    def test_insert_text_replaces_selection(self):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 5
        input_field.selection_start = 0
        input_field.has_selection = True

        input_field._insert_text("Hi")

        assert input_field.value == "Hi World"
        assert input_field.cursor_pos == 2

    def test_move_cursor(self):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 0

        input_field._move_cursor(3)

        assert input_field.cursor_pos == 3
        assert input_field.has_selection is False

    def test_move_cursor_extend_selection(self):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 0

        input_field._move_cursor(3, extend_selection=True)

        assert input_field.cursor_pos == 3
        assert input_field.has_selection is True
        assert input_field.selection_start == 0

    def test_move_cursor_clamps_to_bounds(self):
        input_field = TextInput()
        input_field.value = "Hello"

        input_field._move_cursor(-5)
        assert input_field.cursor_pos == 0

        input_field._move_cursor(100)
        assert input_field.cursor_pos == 5


class TestTextInputHandleInput:
    """Tests for handle_input method."""

    def test_handle_input_click_focuses(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        input_field = TextInput()
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 30

        result = input_field.handle_input(mouse_pos, is_click=True)

        assert result is True
        assert input_field.is_focused is True

    def test_handle_input_click_outside_unfocuses(self, mock_runtime, mock_collision):
        mock_collision.return_value = False

        input_field = TextInput()
        input_field.is_focused = True
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40

        mouse_pos = MagicMock()
        mouse_pos.x = 500
        mouse_pos.y = 500

        result = input_field.handle_input(mouse_pos, is_click=True)

        assert result is False
        assert input_field.is_focused is False

    def test_handle_input_invisible_returns_false(self, mock_runtime, mock_collision):
        input_field = TextInput()
        input_field.style.visible = False

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 30

        result = input_field.handle_input(mouse_pos, is_click=True)

        assert result is False


class TestTextInputRender:
    """Tests for render method."""

    def test_render_unfocused(self, mock_runtime):
        input_field = TextInput()
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.is_focused = False

        input_field.render()

        renderer = mock_runtime["renderer"]
        renderer.draw_rectangle_rounded.assert_called()

    def test_render_invisible_does_nothing(self, mock_runtime):
        input_field = TextInput()
        input_field.style.visible = False

        input_field.render()

        mock_runtime["renderer"].draw_rectangle_rounded.assert_not_called()

    def test_render_with_placeholder(self, mock_runtime):
        input_field = TextInput(placeholder="Enter text...")
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.value = ""

        input_field.render()

        # Should draw placeholder text
        renderer = mock_runtime["renderer"]
        assert renderer.draw_text.called or renderer.draw_rectangle_rounded.called


class TestTextInputOnBlur:
    """Tests for _on_blur method."""

    def test_on_blur_unfocuses(self, mock_runtime):
        input_field = TextInput()
        input_field.is_focused = True
        input_field._is_dragging = True

        input_field._on_blur()

        assert input_field.is_focused is False
        assert input_field._is_dragging is False


class TestTextInputGetCharPositionAtX:
    """Tests for _get_char_position_at_x method."""

    def test_get_char_position_at_start(self, mock_runtime):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.computed_x = 0
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.text_offset_x = 0

        # Mock measure_text to return incremental values
        mock_runtime["renderer"].measure_text.side_effect = (
            lambda text, size: len(text) * 10
        )

        # Position before any characters
        pos = input_field._get_char_position_at_x(-10, mock_runtime["runtime"])

        assert pos == 0

    def test_get_char_position_at_end(self, mock_runtime):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.computed_x = 0
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.text_offset_x = 0

        # Mock measure_text to return incremental values
        mock_runtime["renderer"].measure_text.side_effect = (
            lambda text, size: len(text) * 10
        )

        # Position way past the text
        pos = input_field._get_char_position_at_x(500, mock_runtime["runtime"])

        assert pos == 5


class TestTextInputEnsureCursorVisible:
    """Tests for _ensure_cursor_visible method."""

    def test_ensure_cursor_visible_scrolls_right(self, mock_runtime):
        input_field = TextInput()
        input_field.value = "Hello World This Is A Long Text"
        input_field.computed_x = 0
        input_field.computed_width = 100
        input_field.computed_height = 40
        input_field.cursor_pos = len(input_field.value)
        input_field.text_offset_x = 0

        mock_runtime["font_manager"].measure_text.return_value = (
            300  # Cursor past visible area
        )

        input_field._ensure_cursor_visible()

        # text_offset_x should be adjusted
        assert input_field.text_offset_x > 0

    def test_ensure_cursor_visible_scrolls_left(self, mock_runtime):
        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.computed_x = 0
        input_field.computed_width = 100
        input_field.computed_height = 40
        input_field.cursor_pos = 0
        input_field.text_offset_x = 50  # Already scrolled

        mock_runtime["font_manager"].measure_text.return_value = 0

        input_field._ensure_cursor_visible()

        assert input_field.text_offset_x == 0

    def test_text_metrics_cache_reuses_prefix_measurements(self, mock_runtime):
        input_field = TextInput()
        input_field.value = "Hello"
        input_field.computed_x = 0
        input_field.computed_width = 200
        input_field.computed_height = 40

        with patch("arepy_ui.components.input.measure_text") as mock_measure_text:
            mock_measure_text.side_effect = lambda text, size: len(text) * 10

            first = input_field._get_char_position_at_x(36, mock_runtime["runtime"])
            second = input_field._get_char_position_at_x(36, mock_runtime["runtime"])

        assert first == 2
        assert second == 2
        assert mock_measure_text.call_count == len(input_field.value)


class TestTextInputHandleKey:
    """Tests for _handle_key method."""

    def test_handle_key_left(self, mock_runtime):
        mock_runtime["input"].is_key_down.return_value = False

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 3

        from arepy import Key

        result = input_field._handle_key(Key.LEFT, mock_runtime["runtime"])

        assert result is True
        assert input_field.cursor_pos == 2

    def test_handle_key_right(self, mock_runtime):
        mock_runtime["input"].is_key_down.return_value = False

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 2

        from arepy import Key

        result = input_field._handle_key(Key.RIGHT, mock_runtime["runtime"])

        assert result is True
        assert input_field.cursor_pos == 3

    def test_handle_key_home(self, mock_runtime):
        mock_runtime["input"].is_key_down.return_value = False

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 3

        from arepy import Key

        result = input_field._handle_key(Key.HOME, mock_runtime["runtime"])

        assert result is True
        assert input_field.cursor_pos == 0

    def test_handle_key_end(self, mock_runtime):
        mock_runtime["input"].is_key_down.return_value = False

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 2

        from arepy import Key

        result = input_field._handle_key(Key.END, mock_runtime["runtime"])

        assert result is True
        assert input_field.cursor_pos == 5

    def test_handle_key_backspace(self, mock_runtime):
        mock_runtime["input"].is_key_down.return_value = False

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 5

        from arepy import Key

        result = input_field._handle_key(Key.BACKSPACE, mock_runtime["runtime"])

        assert result is True
        assert input_field.value == "Hell"
        assert input_field.cursor_pos == 4

    def test_handle_key_delete(self, mock_runtime):
        mock_runtime["input"].is_key_down.return_value = False

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 0

        from arepy import Key

        result = input_field._handle_key(Key.DELETE, mock_runtime["runtime"])

        assert result is True
        assert input_field.value == "ello"

    def test_handle_key_ctrl_a_select_all(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 2

        from arepy import Key

        result = input_field._handle_key(Key.A, mock_runtime["runtime"])

        assert result is True
        assert input_field.has_selection is True
        assert input_field.selection_start == 0
        assert input_field.cursor_pos == 5

    def test_handle_key_ctrl_c_copy(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down
        mock_runtime["runtime"].display = MagicMock()

        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.selection_start = 0
        input_field.cursor_pos = 5
        input_field.has_selection = True

        from arepy import Key

        result = input_field._handle_key(Key.C, mock_runtime["runtime"])

        assert result is True
        mock_runtime["runtime"].display.set_clipboard_text.assert_called_with("Hello")

    def test_handle_key_ctrl_x_cut(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down
        mock_runtime["runtime"].display = MagicMock()

        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.selection_start = 0
        input_field.cursor_pos = 5
        input_field.has_selection = True

        from arepy import Key

        result = input_field._handle_key(Key.X, mock_runtime["runtime"])

        assert result is True
        mock_runtime["runtime"].display.set_clipboard_text.assert_called_with("Hello")
        assert input_field.value == " World"

    def test_handle_key_ctrl_v_paste(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down
        mock_runtime["runtime"].display = MagicMock()
        mock_runtime["runtime"].display.get_clipboard_text.return_value = "Pasted"

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 5
        input_field.has_selection = False

        from arepy import Key

        result = input_field._handle_key(Key.V, mock_runtime["runtime"])

        assert result is True
        assert input_field.value == "HelloPasted"

    def test_handle_key_ctrl_left_word(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down

        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 11

        from arepy import Key

        result = input_field._handle_key(Key.LEFT, mock_runtime["runtime"])

        assert result is True
        assert input_field.cursor_pos == 6  # Before "World"

    def test_handle_key_ctrl_right_word(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down

        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 0

        from arepy import Key

        result = input_field._handle_key(Key.RIGHT, mock_runtime["runtime"])

        assert result is True
        assert input_field.cursor_pos == 6  # After "Hello "

    def test_handle_key_shift_extends_selection(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_SHIFT, Key.RIGHT_SHIFT]

        mock_runtime["input"].is_key_down.side_effect = is_key_down

        input_field = TextInput()
        input_field.value = "Hello"
        input_field.cursor_pos = 3

        from arepy import Key

        result = input_field._handle_key(Key.LEFT, mock_runtime["runtime"])

        assert result is True
        assert input_field.has_selection is True
        assert input_field.cursor_pos == 2

    def test_handle_key_ctrl_backspace_delete_word(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down

        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 11

        from arepy import Key

        result = input_field._handle_key(Key.BACKSPACE, mock_runtime["runtime"])

        assert result is True
        assert input_field.value == "Hello "

    def test_handle_key_ctrl_delete_word(self, mock_runtime):
        def is_key_down(key):
            from arepy import Key

            return key in [Key.LEFT_CONTROL, Key.RIGHT_CONTROL]

        mock_runtime["input"].is_key_down.side_effect = is_key_down

        input_field = TextInput()
        input_field.value = "Hello World"
        input_field.cursor_pos = 0

        from arepy import Key

        result = input_field._handle_key(Key.DELETE, mock_runtime["runtime"])

        assert result is True
        assert input_field.value == "World"


class TestTextInputCheckKeyRepeat:
    """Tests for _check_key_repeat method."""

    def test_check_key_repeat_first_press(self, mock_runtime):
        mock_runtime["input"].is_key_pressed.return_value = True
        mock_runtime["input"].is_key_down.return_value = False
        mock_runtime["renderer"].get_delta_time.return_value = 0.016

        input_field = TextInput()

        from arepy import Key

        result = input_field._check_key_repeat(Key.LEFT, mock_runtime["runtime"])

        assert result is True
        assert Key.LEFT in input_field._key_states

    def test_check_key_repeat_held_not_repeating(self, mock_runtime):
        mock_runtime["input"].is_key_pressed.return_value = False
        mock_runtime["input"].is_key_down.return_value = True
        mock_runtime["renderer"].get_delta_time.return_value = 0.016

        input_field = TextInput()

        from arepy import Key

        input_field._key_states[Key.LEFT] = {"held": 0.1, "last_repeat": 0.0}

        result = input_field._check_key_repeat(Key.LEFT, mock_runtime["runtime"])

        # Not yet at repeat delay
        assert result is False

    def test_check_key_repeat_held_repeating(self, mock_runtime):
        mock_runtime["input"].is_key_pressed.return_value = False
        mock_runtime["input"].is_key_down.return_value = True
        mock_runtime["renderer"].get_delta_time.return_value = 0.016

        input_field = TextInput()

        from arepy import Key

        # Held long enough for repeat
        input_field._key_states[Key.LEFT] = {"held": 0.5, "last_repeat": 0.0}

        result = input_field._check_key_repeat(Key.LEFT, mock_runtime["runtime"])

        assert result is True

    def test_check_key_repeat_released(self, mock_runtime):
        mock_runtime["input"].is_key_pressed.return_value = False
        mock_runtime["input"].is_key_down.return_value = False
        mock_runtime["renderer"].get_delta_time.return_value = 0.016

        input_field = TextInput()

        from arepy import Key

        input_field._key_states[Key.LEFT] = {"held": 0.5, "last_repeat": 0.0}

        result = input_field._check_key_repeat(Key.LEFT, mock_runtime["runtime"])

        assert result is False
        assert Key.LEFT not in input_field._key_states


class TestTextInputRenderScenarios:
    """Additional render tests."""

    def test_render_with_value_and_cursor(self, mock_runtime):
        input_field = TextInput()
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.value = "Hello World"
        input_field.is_focused = True
        input_field.show_cursor = True

        input_field.render()

        # Verify that font_manager.draw_text was called (via fonts.draw_text)
        font_manager = mock_runtime["font_manager"]
        font_manager.draw_text.assert_called()

    def test_render_with_selection(self, mock_runtime):
        input_field = TextInput()
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.value = "Hello World"
        input_field.cursor_pos = 5
        input_field.selection_start = 0
        input_field.has_selection = True

        input_field.render()

        renderer = mock_runtime["renderer"]
        # Should draw selection background
        assert renderer.draw_rectangle.call_count >= 1

    def test_render_with_border_radius(self, mock_runtime):
        input_field = TextInput()
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.style.border_radius = 10
        input_field.style.background_color = Color(255, 255, 255, 255)

        input_field.render()

        renderer = mock_runtime["renderer"]
        renderer.draw_rectangle_rounded.assert_called()

    def test_render_without_border_radius(self, mock_runtime):
        input_field = TextInput()
        input_field.computed_x = 10
        input_field.computed_y = 20
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.style.border_radius = 0
        input_field.style.background_color = Color(255, 255, 255, 255)

        input_field.render()

        renderer = mock_runtime["renderer"]
        renderer.draw_rectangle.assert_called()


class TestTextInputMouseDrag:
    """Tests for mouse drag selection."""

    def test_mouse_drag_selection(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        mock_runtime["input"].is_mouse_button_down.return_value = True
        mock_runtime["renderer"].measure_text.side_effect = (
            lambda text, size: len(text) * 10
        )

        input_field = TextInput()
        input_field.computed_x = 0
        input_field.computed_y = 0
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.value = "Hello World"
        input_field.is_focused = True
        input_field._is_dragging = True
        input_field.cursor_pos = 0

        mouse_pos = MagicMock()
        mouse_pos.x = 100  # Will map to some character
        mouse_pos.y = 20

        input_field.handle_input(mouse_pos, is_click=False)

        # Cursor should have moved
        assert input_field.has_selection is True


class TestTextInputCallbacks:
    """Tests for callback invocations."""

    def test_on_change_called_on_input(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        changes = []

        def on_change(value):
            changes.append(value)

        input_field = TextInput(on_change=on_change)
        input_field.computed_x = 0
        input_field.computed_y = 0
        input_field.computed_width = 200
        input_field.computed_height = 40
        input_field.is_focused = True
        input_field.value = "Hello"
        input_field.cursor_pos = 5

        # Simulate character input
        mock_runtime["input"].get_char_pressed.side_effect = [ord("!"), 0]

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 20

        input_field.handle_input(mouse_pos, is_click=False)

        assert "Hello!" in changes

    def test_on_submit_called_on_enter(self, mock_runtime):
        from arepy import Key

        submitted = []

        def on_submit(value):
            submitted.append(value)

        input_field = TextInput(on_submit=on_submit)
        input_field.value = "test"

        # Simulate Enter press
        input_field._handle_key(Key.ENTER, mock_runtime["runtime"])

        assert submitted == ["test"]
