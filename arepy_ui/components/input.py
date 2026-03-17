from bisect import bisect_left
from typing import Callable, Optional

from arepy.engine.input import Key
from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.fonts import draw_text, measure_text
from ..core.node import Node
from ..core.style import Spacing, Style, merge_non_default_style_fields
from ..core.types import AlignItems, Color, CursorType, Unit
from ..runtime import MouseButton, get_runtime


class TextInput(Node):
    """
    Single-line text input component with full selection support.

    Features:
    - Cursor navigation with arrows
    - Home/End navigation
    - Text selection (Shift+arrows, Shift+click, mouse drag)
    - Copy/Paste (Ctrl+C, Ctrl+V, Ctrl+X)
    - Word navigation (Ctrl+arrows)
    - Select all (Ctrl+A)
    """

    # Key repeat settings
    KEY_REPEAT_DELAY = 0.4  # Initial delay before repeating (seconds)
    KEY_REPEAT_RATE = 0.05  # Time between repeats (seconds)

    def __init__(
        self,
        value: str = "",
        placeholder: str = "",
        width: Unit = Unit.px(200),
        height: Unit = Unit.px(40),
        font_size: float = 14.0,
        style: Optional[Style] = None,
        on_change: Optional[Callable[[str], None]] = None,
        on_submit: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=Color(255, 255, 255, 255),
            border_width=1.0,
            border_color=Color(130, 130, 130, 255),
            border_radius=4.0,
            padding=Spacing.symmetric(8, 12),
            align_items=AlignItems.CENTER,
            cursor=CursorType.IBEAM,
        )

        merge_non_default_style_fields(
            default_style,
            style,
            (
                "width",
                "height",
                "min_width",
                "max_width",
                "min_height",
                "max_height",
                "margin",
                "padding",
                "align_items",
                "position",
                "top",
                "left",
                "right",
                "bottom",
                "visible",
                "opacity",
                "background_color",
                "border_color",
                "border_width",
                "border_radius",
                "cursor",
            ),
        )

        super().__init__(style=default_style, **kwargs)

        self.placeholder = placeholder
        self.on_change = on_change
        self.on_submit = on_submit
        self.is_focused = False
        self.font_size = font_size
        self.text_color = Color(0, 0, 0, 255)
        self.placeholder_color = Color(130, 130, 130, 255)
        self.selection_color = Color(0, 121, 241, 100)
        self.focused_border_color = Color(0, 121, 241, 255)
        self.default_border_color = Color(130, 130, 130, 255)

        self._value = ""
        self._cached_metrics_value: Optional[str] = None
        self._cached_metrics_font_size: Optional[float] = None
        self._prefix_widths = [0.0]
        self._midpoint_widths = []

        # Cursor position (0 = before first char, len(value) = after last char)
        self.cursor_pos = 0

        # Selection state
        self.selection_start = 0
        self.has_selection = False

        # Mouse drag state
        self._is_dragging = False

        # Text scroll offset for long text
        self.text_offset_x = 0.0

        # Cursor blink
        self.cursor_timer = 0.0
        self.show_cursor = True

        # Key repeat state
        self._key_states = {}

        self.value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, text: str):
        self._value = text
        self._invalidate_text_metrics()

    def _invalidate_text_metrics(self):
        self._cached_metrics_value = None
        self._cached_metrics_font_size = None

    def _ensure_text_metrics(self):
        if (
            self._cached_metrics_value == self._value
            and self._cached_metrics_font_size == self.font_size
        ):
            return

        prefix_widths = [0.0]
        midpoint_widths = []
        for index in range(len(self._value)):
            next_width = measure_text(self._value[: index + 1], self.font_size)
            prefix_widths.append(next_width)
            midpoint_widths.append((prefix_widths[index] + next_width) / 2)

        self._prefix_widths = prefix_widths
        self._midpoint_widths = midpoint_widths
        self._cached_metrics_value = self._value
        self._cached_metrics_font_size = self.font_size

    def _get_prefix_width(self, position: int) -> float:
        self._ensure_text_metrics()
        clamped = max(0, min(position, len(self._value)))
        return self._prefix_widths[clamped]

    def _clear_selection(self):
        """Clear text selection."""
        self.has_selection = False
        self.selection_start = self.cursor_pos

    def _start_selection(self):
        """Start a new selection at cursor position."""
        if not self.has_selection:
            self.selection_start = self.cursor_pos
            self.has_selection = True

    def _get_selection_range(self):
        """Get selection range as (start, end) where start <= end."""
        if not self.has_selection:
            return None
        start = min(self.selection_start, self.cursor_pos)
        end = max(self.selection_start, self.cursor_pos)
        if start == end:
            return None
        return (start, end)

    def _get_selected_text(self) -> str:
        """Get the currently selected text."""
        sel = self._get_selection_range()
        if not sel:
            return ""
        start, end = sel
        return self.value[start:end]

    def _delete_selection(self):
        """Delete the selected text."""
        sel = self._get_selection_range()
        if not sel:
            return False
        start, end = sel
        self.value = self.value[:start] + self.value[end:]
        self.cursor_pos = start
        self._clear_selection()
        return True

    def _insert_text(self, text: str):
        """Insert text at cursor position, replacing selection if any."""
        if self.has_selection:
            self._delete_selection()
        self.value = (
            self.value[: self.cursor_pos] + text + self.value[self.cursor_pos :]
        )
        self.cursor_pos += len(text)
        self._clear_selection()

    def _move_cursor(self, pos: int, extend_selection: bool = False):
        """Move cursor to position, optionally extending selection."""
        if extend_selection:
            self._start_selection()
        else:
            self._clear_selection()
        self.cursor_pos = max(0, min(pos, len(self.value)))
        self.show_cursor = True
        self.cursor_timer = 0

    def _handle_key(self, key: Key, runtime) -> bool:
        """Handle a key press. Returns True if handled."""
        ctrl = runtime.input.is_key_down(Key.LEFT_CONTROL) or runtime.input.is_key_down(
            Key.RIGHT_CONTROL
        )
        shift = runtime.input.is_key_down(Key.LEFT_SHIFT) or runtime.input.is_key_down(
            Key.RIGHT_SHIFT
        )

        # Navigation
        if key == Key.LEFT:
            if ctrl:
                # Word left
                pos = self.cursor_pos
                while pos > 0 and self.value[pos - 1] == " ":
                    pos -= 1
                while pos > 0 and self.value[pos - 1] != " ":
                    pos -= 1
                self._move_cursor(pos, shift)
            elif self.cursor_pos > 0:
                self._move_cursor(self.cursor_pos - 1, shift)
            return True

        elif key == Key.RIGHT:
            if ctrl:
                # Word right
                pos = self.cursor_pos
                while pos < len(self.value) and self.value[pos] != " ":
                    pos += 1
                while pos < len(self.value) and self.value[pos] == " ":
                    pos += 1
                self._move_cursor(pos, shift)
            elif self.cursor_pos < len(self.value):
                self._move_cursor(self.cursor_pos + 1, shift)
            return True

        elif key == Key.HOME:
            self._move_cursor(0, shift)
            return True

        elif key == Key.END:
            self._move_cursor(len(self.value), shift)
            return True

        elif key == Key.ENTER:
            if self.on_submit:
                self.on_submit(self.value)
            return True

        # Editing
        elif key == Key.BACKSPACE:
            if self.has_selection:
                self._delete_selection()
            elif ctrl:
                # Delete word left
                if self.cursor_pos > 0:
                    pos = self.cursor_pos
                    while pos > 0 and self.value[pos - 1] == " ":
                        pos -= 1
                    while pos > 0 and self.value[pos - 1] != " ":
                        pos -= 1
                    self.value = self.value[:pos] + self.value[self.cursor_pos :]
                    self.cursor_pos = pos
            elif self.cursor_pos > 0:
                self.value = (
                    self.value[: self.cursor_pos - 1] + self.value[self.cursor_pos :]
                )
                self.cursor_pos -= 1
            if self.on_change:
                self.on_change(self.value)
            return True

        elif key == Key.DELETE:
            if self.has_selection:
                self._delete_selection()
            elif ctrl:
                # Delete word right
                pos = self.cursor_pos
                while pos < len(self.value) and self.value[pos] != " ":
                    pos += 1
                while pos < len(self.value) and self.value[pos] == " ":
                    pos += 1
                self.value = self.value[: self.cursor_pos] + self.value[pos:]
            elif self.cursor_pos < len(self.value):
                self.value = (
                    self.value[: self.cursor_pos] + self.value[self.cursor_pos + 1 :]
                )
            if self.on_change:
                self.on_change(self.value)
            return True

        # Clipboard
        elif key == Key.A and ctrl:
            # Select all
            self.selection_start = 0
            self.cursor_pos = len(self.value)
            self.has_selection = True
            return True

        elif key == Key.C and ctrl:
            # Copy
            text = self._get_selected_text()
            if text:
                runtime.display.set_clipboard_text(text)
            return True

        elif key == Key.X and ctrl:
            # Cut
            text = self._get_selected_text()
            if text:
                runtime.display.set_clipboard_text(text)
                self._delete_selection()
                if self.on_change:
                    self.on_change(self.value)
            return True

        elif key == Key.V and ctrl:
            # Paste
            text = runtime.display.get_clipboard_text()
            if text:
                # Remove newlines for single-line input
                text = text.replace("\n", " ").replace("\r", "")
                self._insert_text(text)
                if self.on_change:
                    self.on_change(self.value)
            return True

        return False

    def _check_key_repeat(self, key: Key, runtime) -> bool:
        """Check if a key should repeat."""
        dt = runtime.renderer.get_delta_time()

        if runtime.input.is_key_pressed(key):
            self._key_states[key] = {"held": 0.0, "last_repeat": 0.0}
            return True

        if runtime.input.is_key_down(key) and key in self._key_states:
            state = self._key_states[key]
            state["held"] += dt

            if state["held"] >= self.KEY_REPEAT_DELAY:
                if state["held"] - state["last_repeat"] >= self.KEY_REPEAT_RATE:
                    state["last_repeat"] = state["held"]
                    return True
        elif key in self._key_states:
            del self._key_states[key]

        return False

    def _on_blur(self):
        """Called when this input loses focus."""
        self.is_focused = False
        self.style.border_color = self.default_border_color
        self._is_dragging = False

    def _get_char_position_at_x(self, x: float, runtime) -> int:
        """Get character position at x coordinate."""
        content_x, _, _, _ = self._get_content_area()
        relative_x = x - content_x + self.text_offset_x

        if relative_x <= 0:
            return 0

        self._ensure_text_metrics()
        return min(bisect_left(self._midpoint_widths, relative_x), len(self._value))

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )
        is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        # Focus handling and click to position
        if is_click:
            was_focused = self.is_focused

            if is_over:
                # Request focus from the manager
                if self._manager is not None:
                    self._manager.request_focus(self)
                self.is_focused = True
                self.style.border_color = self.focused_border_color

                # Click to position cursor
                clicked_pos = self._get_char_position_at_x(mouse_pos.x, runtime)
                shift = runtime.input.is_key_down(
                    Key.LEFT_SHIFT
                ) or runtime.input.is_key_down(Key.RIGHT_SHIFT)
                self._move_cursor(clicked_pos, shift)
                self._is_dragging = True
            else:
                # Clicked outside - release focus
                if was_focused:
                    if self._manager is not None:
                        self._manager.release_focus(self)
                    self._on_blur()
                self._is_dragging = False

        # Handle mouse drag for selection
        if (
            self.is_focused
            and self._is_dragging
            and runtime.input.is_mouse_button_down(MouseButton.LEFT)
        ):
            drag_pos = self._get_char_position_at_x(mouse_pos.x, runtime)
            if drag_pos != self.cursor_pos:
                self._move_cursor(drag_pos, extend_selection=True)

        # Stop dragging when mouse is released
        if not runtime.input.is_mouse_button_down(MouseButton.LEFT):
            self._is_dragging = False

        # Handle keyboard input when focused
        if self.is_focused:
            # Check repeatable keys
            for key in [Key.LEFT, Key.RIGHT, Key.BACKSPACE, Key.DELETE]:
                if self._check_key_repeat(key, runtime):
                    self._handle_key(key, runtime)

            # Check single-press keys
            for key in [Key.HOME, Key.END, Key.A, Key.C, Key.V, Key.X]:
                if runtime.input.is_key_pressed(key):
                    self._handle_key(key, runtime)

            # Character input
            char_code = runtime.input.get_char_pressed()
            while char_code != 0:
                if 32 <= char_code <= 126 or char_code > 127:
                    self._insert_text(chr(char_code))
                    if self.on_change:
                        self.on_change(self.value)
                char_code = runtime.input.get_char_pressed()

            return True

        return is_over and is_click

    def _get_content_area(self):
        """Get the text content area (inside padding)."""
        padding_x = 12
        padding_y = 8
        return (
            self.computed_x + padding_x,
            self.computed_y + padding_y,
            self.computed_width - padding_x * 2,
            self.computed_height - padding_y * 2,
        )

    def _ensure_cursor_visible(self):
        """Scroll to keep cursor visible."""
        _, _, content_w, _ = self._get_content_area()

        cursor_x = self._get_prefix_width(self.cursor_pos)

        # Scroll left if cursor is before visible area
        if cursor_x < self.text_offset_x:
            self.text_offset_x = max(0, cursor_x - 10)
        # Scroll right if cursor is after visible area
        elif cursor_x > self.text_offset_x + content_w - 10:
            self.text_offset_x = cursor_x - content_w + 20

        self.text_offset_x = max(0, self.text_offset_x)

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()
        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )

        # Draw background
        if self.style.background_color:
            min_dim = min(self.computed_width, self.computed_height)
            if self.style.border_radius > 0 and min_dim > 0:
                runtime.renderer.draw_rectangle_rounded(
                    rect,
                    self.style.border_radius / min_dim,
                    10,
                    self.style.background_color,
                )
            else:
                runtime.renderer.draw_rectangle(rect, self.style.background_color)

        # Draw border
        if self.style.border_width > 0 and self.style.border_color:
            min_dim = min(self.computed_width, self.computed_height)
            if self.style.border_radius > 0 and min_dim > 0:
                runtime.renderer.draw_rectangle_rounded_lines(
                    rect,
                    self.style.border_radius / min_dim,
                    10,
                    self.style.border_color,
                )
            else:
                runtime.renderer.draw_rectangle_lines_ex(
                    rect, self.style.border_width, self.style.border_color
                )

        # Get content area
        content_x, content_y, content_w, content_h = self._get_content_area()

        # Ensure cursor is visible (updates text_offset_x)
        if self.is_focused:
            self._ensure_cursor_visible()
        elif not self.value:
            self.text_offset_x = 0

        # Determine text to display
        if self.value:
            display_text = self.value
            text_color = self.text_color
        else:
            display_text = self.placeholder
            text_color = self.placeholder_color

        # Scissor mode for clipping
        runtime.renderer.begin_scissor_mode(
            int(content_x),
            int(self.computed_y),
            int(content_w),
            int(self.computed_height),
        )

        text_y = content_y + (content_h - self.font_size) / 2

        # Draw selection background
        sel = self._get_selection_range()
        if sel and self.value:
            start, end = sel
            sel_start_x = self._get_prefix_width(start)
            sel_end_x = self._get_prefix_width(end)

            runtime.renderer.draw_rectangle(
                Rect(
                    int(content_x + sel_start_x - self.text_offset_x),
                    int(text_y),
                    int(sel_end_x - sel_start_x),
                    int(self.font_size),
                ),
                self.selection_color,
            )

        # Draw text
        if display_text:
            draw_text(
                display_text,
                content_x - self.text_offset_x,
                text_y,
                self.font_size,
                text_color,
            )

        # Draw cursor
        if self.is_focused:
            self.cursor_timer += runtime.renderer.get_delta_time()
            if self.cursor_timer >= 0.5:
                self.cursor_timer = 0
                self.show_cursor = not self.show_cursor

            if self.show_cursor:
                cursor_x = self._get_prefix_width(self.cursor_pos)
                runtime.renderer.draw_rectangle(
                    Rect(
                        int(content_x + cursor_x - self.text_offset_x),
                        int(text_y),
                        2,
                        int(self.font_size),
                    ),
                    self.text_color,
                )

        runtime.renderer.end_scissor_mode()
