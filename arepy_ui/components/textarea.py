"""TextArea component - Multi-line text input."""

from bisect import bisect_left
from typing import Callable, List, Optional

from arepy import CursorType
from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Spacing, Style
from ..core.types import Color, Unit
from ..runtime import Key, MouseButton, get_runtime


class TextArea(Node):
    """
    Multi-line text input component.

    Features:
    - Multiple lines of text
    - Vertical scrolling
    - Optional line numbers
    - Cursor navigation with arrows
    - Home/End, Ctrl+Home/End
    - Text selection (Shift+arrows)
    - Copy/Paste (Ctrl+C, Ctrl+V, Ctrl+X)
    - Word navigation (Ctrl+arrows)
    """

    KEY_REPEAT_DELAY = 0.4
    KEY_REPEAT_RATE = 0.05

    def __init__(
        self,
        placeholder: str = "",
        width: Unit = Unit.px(400),
        height: Unit = Unit.px(200),
        style: Optional[Style] = None,
        on_change: Optional[Callable[[str], None]] = None,
        show_line_numbers: bool = False,
        font_size: int = 14,
        tab_size: int = 4,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=Color(30, 30, 35, 255),
            border_color=Color(60, 60, 70, 255),
            border_width=1.0,
            border_radius=4.0,
            padding=Spacing.all(8),
            cursor=CursorType.IBEAM,
        )

        if style:
            merged = default_style
            for attr in vars(style):
                val = getattr(style, attr)
                if val is not None:
                    setattr(merged, attr, val)
            style = merged
        else:
            style = default_style

        super().__init__(style=style, **kwargs)

        self.placeholder = placeholder
        self.on_change = on_change
        self.show_line_numbers = show_line_numbers
        self.font_size = font_size
        self.tab_size = tab_size

        # Text state
        self._lines: List[str] = [""]
        self.cursor_line = 0
        self.cursor_col = 0

        # Selection state
        self.selection_start_line = 0
        self.selection_start_col = 0
        self.has_selection = False

        # Visual state
        self.is_focused = False
        self.scroll_y = 0.0
        self.scroll_x = 0.0

        # Cursor blink
        self.cursor_timer = 0.0
        self.show_cursor = True

        # Key repeat
        self._key_states = {}

        # Mouse drag state
        self._is_dragging = False

        self._line_metrics_cache = {}
        self._line_number_width_cache = {}

        # Colors
        self.text_color = Color(220, 220, 230, 255)
        self.placeholder_color = Color(100, 100, 110, 255)
        self.selection_color = Color(60, 100, 180, 100)
        self.line_number_color = Color(80, 80, 90, 255)
        self.line_number_bg = Color(25, 25, 30, 255)
        self.focused_border_color = Color(100, 140, 200, 255)

    @property
    def value(self) -> str:
        """Get the full text content."""
        return "\n".join(self._lines)

    @value.setter
    def value(self, text: str):
        """Set the text content."""
        self._lines = text.split("\n") if text else [""]
        self.cursor_line = min(self.cursor_line, len(self._lines) - 1)
        self.cursor_col = min(self.cursor_col, len(self._lines[self.cursor_line]))
        self._clear_selection()

    @property
    def line_count(self) -> int:
        """Get number of lines."""
        return len(self._lines)

    def _get_line_height(self) -> float:
        """Get height of a single line."""
        return self.font_size * 1.4

    def _get_line_number_width(self) -> float:
        """Get width reserved for line numbers."""
        if not self.show_line_numbers:
            return 0

        cache_key = (len(self._lines), self.font_size)
        cached_width = self._line_number_width_cache.get(cache_key)
        if cached_width is not None:
            return cached_width

        runtime = get_runtime()
        max_num = str(len(self._lines))
        width = runtime.renderer.measure_text(max_num, self.font_size) + 20
        if len(self._line_number_width_cache) >= 32:
            self._line_number_width_cache.clear()
        self._line_number_width_cache[cache_key] = width
        return width

    def _get_line_metrics(self, line: str, runtime):
        cache_key = (line, self.font_size)
        cached_metrics = self._line_metrics_cache.get(cache_key)
        if cached_metrics is not None:
            return cached_metrics

        prefix_widths = [0.0]
        midpoint_widths = []
        for index in range(len(line)):
            next_width = runtime.renderer.measure_text(
                line[: index + 1], self.font_size
            )
            prefix_widths.append(next_width)
            midpoint_widths.append((prefix_widths[index] + next_width) / 2)

        metrics = (prefix_widths, midpoint_widths, prefix_widths[-1])
        if len(self._line_metrics_cache) >= 512:
            self._line_metrics_cache.clear()
        self._line_metrics_cache[cache_key] = metrics
        return metrics

    def _get_prefix_width(self, line_index: int, column: int, runtime) -> float:
        line = self._lines[line_index]
        prefix_widths, _, _ = self._get_line_metrics(line, runtime)
        clamped = max(0, min(column, len(line)))
        return prefix_widths[clamped]

    def _get_line_width(self, line_index: int, runtime) -> float:
        _, _, width = self._get_line_metrics(self._lines[line_index], runtime)
        return width

    def _get_column_at_x(
        self, line_index: int, x: float, content_x: float, runtime
    ) -> int:
        relative_x = x - content_x + self.scroll_x
        if relative_x <= 0:
            return 0

        line = self._lines[line_index]
        _, midpoint_widths, _ = self._get_line_metrics(line, runtime)
        return min(bisect_left(midpoint_widths, relative_x), len(line))

    def _get_content_area(self):
        """Get the content area for text (excluding line numbers)."""
        padding_x = 8  # Fixed padding value
        padding_y = 8
        line_num_width = self._get_line_number_width()

        x = self.computed_x + padding_x + line_num_width
        y = self.computed_y + padding_y
        w = self.computed_width - padding_x * 2 - line_num_width
        h = self.computed_height - padding_y * 2

        return x, y, w, h

    def _clear_selection(self):
        """Clear text selection."""
        self.has_selection = False
        self.selection_start_line = self.cursor_line
        self.selection_start_col = self.cursor_col

    def _start_selection(self):
        """Start a new selection at cursor position."""
        if not self.has_selection:
            self.selection_start_line = self.cursor_line
            self.selection_start_col = self.cursor_col
            self.has_selection = True

    def _get_selection_range(self):
        """Get selection range as (start_line, start_col, end_line, end_col)."""
        if not self.has_selection:
            return None

        # Normalize so start is before end
        if (self.selection_start_line, self.selection_start_col) <= (
            self.cursor_line,
            self.cursor_col,
        ):
            return (
                self.selection_start_line,
                self.selection_start_col,
                self.cursor_line,
                self.cursor_col,
            )
        else:
            return (
                self.cursor_line,
                self.cursor_col,
                self.selection_start_line,
                self.selection_start_col,
            )

    def _get_selected_text(self) -> str:
        """Get the currently selected text."""
        sel = self._get_selection_range()
        if not sel:
            return ""

        start_line, start_col, end_line, end_col = sel

        if start_line == end_line:
            return self._lines[start_line][start_col:end_col]

        result = [self._lines[start_line][start_col:]]
        for i in range(start_line + 1, end_line):
            result.append(self._lines[i])
        result.append(self._lines[end_line][:end_col])

        return "\n".join(result)

    def _delete_selection(self):
        """Delete the selected text."""
        sel = self._get_selection_range()
        if not sel:
            return

        start_line, start_col, end_line, end_col = sel

        if start_line == end_line:
            line = self._lines[start_line]
            self._lines[start_line] = line[:start_col] + line[end_col:]
        else:
            # Merge first and last line
            self._lines[start_line] = (
                self._lines[start_line][:start_col] + self._lines[end_line][end_col:]
            )
            # Delete middle lines
            del self._lines[start_line + 1 : end_line + 1]

        self.cursor_line = start_line
        self.cursor_col = start_col
        self._clear_selection()

    def _insert_text(self, text: str):
        """Insert text at cursor position."""
        if self.has_selection:
            self._delete_selection()

        lines = text.split("\n")

        if len(lines) == 1:
            # Single line insert
            line = self._lines[self.cursor_line]
            self._lines[self.cursor_line] = (
                line[: self.cursor_col] + text + line[self.cursor_col :]
            )
            self.cursor_col += len(text)
        else:
            # Multi-line insert
            current_line = self._lines[self.cursor_line]
            before = current_line[: self.cursor_col]
            after = current_line[self.cursor_col :]

            # First line
            self._lines[self.cursor_line] = before + lines[0]

            # Middle lines
            for i, line in enumerate(lines[1:-1], 1):
                self._lines.insert(self.cursor_line + i, line)

            # Last line
            self._lines.insert(self.cursor_line + len(lines) - 1, lines[-1] + after)

            self.cursor_line += len(lines) - 1
            self.cursor_col = len(lines[-1])

    def _move_cursor(self, line: int, col: int, extend_selection: bool = False):
        """Move cursor to position, optionally extending selection."""
        if extend_selection:
            self._start_selection()
        else:
            self._clear_selection()

        self.cursor_line = max(0, min(line, len(self._lines) - 1))
        self.cursor_col = max(0, min(col, len(self._lines[self.cursor_line])))
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
                col = self.cursor_col
                line = self._lines[self.cursor_line]
                while col > 0 and line[col - 1] == " ":
                    col -= 1
                while col > 0 and line[col - 1] != " ":
                    col -= 1
                self._move_cursor(self.cursor_line, col, shift)
            elif self.cursor_col > 0:
                self._move_cursor(self.cursor_line, self.cursor_col - 1, shift)
            elif self.cursor_line > 0:
                self._move_cursor(
                    self.cursor_line - 1, len(self._lines[self.cursor_line - 1]), shift
                )
            return True

        elif key == Key.RIGHT:
            if ctrl:
                # Word right
                col = self.cursor_col
                line = self._lines[self.cursor_line]
                while col < len(line) and line[col] != " ":
                    col += 1
                while col < len(line) and line[col] == " ":
                    col += 1
                self._move_cursor(self.cursor_line, col, shift)
            elif self.cursor_col < len(self._lines[self.cursor_line]):
                self._move_cursor(self.cursor_line, self.cursor_col + 1, shift)
            elif self.cursor_line < len(self._lines) - 1:
                self._move_cursor(self.cursor_line + 1, 0, shift)
            return True

        elif key == Key.UP:
            if self.cursor_line > 0:
                self._move_cursor(self.cursor_line - 1, self.cursor_col, shift)
            return True

        elif key == Key.DOWN:
            if self.cursor_line < len(self._lines) - 1:
                self._move_cursor(self.cursor_line + 1, self.cursor_col, shift)
            return True

        elif key == Key.HOME:
            if ctrl:
                self._move_cursor(0, 0, shift)
            else:
                self._move_cursor(self.cursor_line, 0, shift)
            return True

        elif key == Key.END:
            if ctrl:
                last_line = len(self._lines) - 1
                self._move_cursor(last_line, len(self._lines[last_line]), shift)
            else:
                self._move_cursor(
                    self.cursor_line, len(self._lines[self.cursor_line]), shift
                )
            return True

        elif key == Key.PAGE_UP:
            _, _, _, h = self._get_content_area()
            lines_per_page = int(h / self._get_line_height())
            self._move_cursor(self.cursor_line - lines_per_page, self.cursor_col, shift)
            return True

        elif key == Key.PAGE_DOWN:
            _, _, _, h = self._get_content_area()
            lines_per_page = int(h / self._get_line_height())
            self._move_cursor(self.cursor_line + lines_per_page, self.cursor_col, shift)
            return True

        # Editing
        elif key == Key.BACKSPACE:
            if self.has_selection:
                self._delete_selection()
            elif ctrl:
                # Delete word
                if self.cursor_col > 0:
                    line = self._lines[self.cursor_line]
                    col = self.cursor_col
                    while col > 0 and line[col - 1] == " ":
                        col -= 1
                    while col > 0 and line[col - 1] != " ":
                        col -= 1
                    self._lines[self.cursor_line] = line[:col] + line[self.cursor_col :]
                    self.cursor_col = col
            elif self.cursor_col > 0:
                line = self._lines[self.cursor_line]
                self._lines[self.cursor_line] = (
                    line[: self.cursor_col - 1] + line[self.cursor_col :]
                )
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                # Merge with previous line
                prev_len = len(self._lines[self.cursor_line - 1])
                self._lines[self.cursor_line - 1] += self._lines[self.cursor_line]
                del self._lines[self.cursor_line]
                self.cursor_line -= 1
                self.cursor_col = prev_len
            if self.on_change:
                self.on_change(self.value)
            return True

        elif key == Key.DELETE:
            if self.has_selection:
                self._delete_selection()
            elif ctrl:
                # Delete word forward
                line = self._lines[self.cursor_line]
                col = self.cursor_col
                while col < len(line) and line[col] != " ":
                    col += 1
                while col < len(line) and line[col] == " ":
                    col += 1
                self._lines[self.cursor_line] = line[: self.cursor_col] + line[col:]
            elif self.cursor_col < len(self._lines[self.cursor_line]):
                line = self._lines[self.cursor_line]
                self._lines[self.cursor_line] = (
                    line[: self.cursor_col] + line[self.cursor_col + 1 :]
                )
            elif self.cursor_line < len(self._lines) - 1:
                # Merge with next line
                self._lines[self.cursor_line] += self._lines[self.cursor_line + 1]
                del self._lines[self.cursor_line + 1]
            if self.on_change:
                self.on_change(self.value)
            return True

        elif key == Key.ENTER:
            if self.has_selection:
                self._delete_selection()
            line = self._lines[self.cursor_line]
            self._lines[self.cursor_line] = line[: self.cursor_col]
            self._lines.insert(self.cursor_line + 1, line[self.cursor_col :])
            self.cursor_line += 1
            self.cursor_col = 0
            if self.on_change:
                self.on_change(self.value)
            return True

        elif key == Key.TAB:
            spaces = " " * self.tab_size
            self._insert_text(spaces)
            if self.on_change:
                self.on_change(self.value)
            return True

        # Clipboard
        elif key == Key.A and ctrl:
            # Select all
            self.selection_start_line = 0
            self.selection_start_col = 0
            self.cursor_line = len(self._lines) - 1
            self.cursor_col = len(self._lines[-1])
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
        """Called when this textarea loses focus."""
        self.is_focused = False
        self.style.border_color = Color(60, 60, 70, 255)
        self._is_dragging = False

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
        is_inside = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        # Focus handling
        if is_click:
            was_focused = self.is_focused

            if is_inside:
                # Request focus from the manager
                if self._manager is not None:
                    self._manager.request_focus(self)
                self.is_focused = True
                self.style.border_color = self.focused_border_color
            else:
                # Clicked outside - release focus
                if was_focused:
                    if self._manager is not None:
                        self._manager.release_focus(self)
                    self._on_blur()

            # Click to position cursor and start drag
            if self.is_focused and is_inside:
                content_x, content_y, _, _ = self._get_content_area()
                line_height = self._get_line_height()

                # Calculate clicked line
                clicked_line = int(
                    (mouse_pos.y - content_y + self.scroll_y) / line_height
                )
                clicked_line = max(0, min(clicked_line, len(self._lines) - 1))

                # Calculate clicked column
                clicked_col = self._get_column_at_x(
                    clicked_line, mouse_pos.x, content_x, runtime
                )

                shift = runtime.input.is_key_down(
                    Key.LEFT_SHIFT
                ) or runtime.input.is_key_down(Key.RIGHT_SHIFT)
                self._move_cursor(clicked_line, clicked_col, shift)

                # Start dragging for selection
                self._is_dragging = True
            else:
                self._is_dragging = False

        # Handle mouse drag for selection (when mouse button is held)
        if (
            self.is_focused
            and self._is_dragging
            and runtime.input.is_mouse_button_down(MouseButton.LEFT)
        ):
            content_x, content_y, _, _ = self._get_content_area()
            line_height = self._get_line_height()

            # Calculate dragged position
            drag_line = int((mouse_pos.y - content_y + self.scroll_y) / line_height)
            drag_line = max(0, min(drag_line, len(self._lines) - 1))

            drag_col = self._get_column_at_x(drag_line, mouse_pos.x, content_x, runtime)

            # Extend selection while dragging
            if drag_line != self.cursor_line or drag_col != self.cursor_col:
                self._move_cursor(drag_line, drag_col, extend_selection=True)

        # Stop dragging when mouse is released
        if not runtime.input.is_mouse_button_down(MouseButton.LEFT):
            self._is_dragging = False

        # Scroll handling
        if is_inside and wheel_scroll != 0:
            line_height = self._get_line_height()
            self.scroll_y -= wheel_scroll * line_height * 3
            content_height = len(self._lines) * line_height
            _, _, _, view_h = self._get_content_area()
            max_scroll = max(0, content_height - view_h)
            self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        # Key handling
        if self.is_focused:
            # Check repeatable keys
            for key in [
                Key.LEFT,
                Key.RIGHT,
                Key.UP,
                Key.DOWN,
                Key.BACKSPACE,
                Key.DELETE,
            ]:
                if self._check_key_repeat(key, runtime):
                    self._handle_key(key, runtime)

            # Check single-press keys
            for key in [
                Key.HOME,
                Key.END,
                Key.PAGE_UP,
                Key.PAGE_DOWN,
                Key.ENTER,
                Key.TAB,
                Key.A,
                Key.C,
                Key.V,
                Key.X,
            ]:
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

        return is_inside and is_click

    def _ensure_cursor_visible(self):
        """Scroll to keep cursor visible."""
        _, content_y, content_w, content_h = self._get_content_area()
        line_height = self._get_line_height()

        # Vertical scroll
        cursor_y = self.cursor_line * line_height
        if cursor_y < self.scroll_y:
            self.scroll_y = cursor_y
        elif cursor_y + line_height > self.scroll_y + content_h:
            self.scroll_y = cursor_y + line_height - content_h

        # Horizontal scroll
        runtime = get_runtime()
        cursor_x = self._get_prefix_width(self.cursor_line, self.cursor_col, runtime)
        if cursor_x < self.scroll_x:
            self.scroll_x = cursor_x - 10
        elif cursor_x > self.scroll_x + content_w - 10:
            self.scroll_x = cursor_x - content_w + 20
        self.scroll_x = max(0, self.scroll_x)

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()

        # Background
        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )

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

        # Border
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

        self._ensure_cursor_visible()

        content_x, content_y, content_w, content_h = self._get_content_area()
        line_height = self._get_line_height()
        padding_x = 8  # Fixed padding value
        padding_y = 8

        # Line numbers background
        if self.show_line_numbers:
            line_num_width = self._get_line_number_width()
            runtime.renderer.draw_rectangle(
                Rect(
                    int(self.computed_x + padding_x),
                    int(self.computed_y + padding_y),
                    int(line_num_width - 5),
                    int(self.computed_height - padding_y * 2),
                ),
                self.line_number_bg,
            )

        # Scissor for content
        runtime.renderer.begin_scissor_mode(
            int(self.computed_x + padding_x),
            int(self.computed_y + padding_y),
            int(self.computed_width - padding_x * 2),
            int(self.computed_height - padding_y * 2),
        )

        # Calculate visible lines
        first_visible = max(0, int(self.scroll_y / line_height))
        last_visible = min(
            len(self._lines), int((self.scroll_y + content_h) / line_height) + 1
        )

        # Draw selection
        sel = self._get_selection_range()
        if sel:
            start_line, start_col, end_line, end_col = sel
            for i in range(
                max(first_visible, start_line), min(last_visible, end_line + 1)
            ):
                line = self._lines[i]
                y = content_y + i * line_height - self.scroll_y

                if i == start_line and i == end_line:
                    # Selection on single line
                    x1 = (
                        content_x
                        + self._get_prefix_width(i, start_col, runtime)
                        - self.scroll_x
                    )
                    x2 = (
                        content_x
                        + self._get_prefix_width(i, end_col, runtime)
                        - self.scroll_x
                    )
                elif i == start_line:
                    x1 = (
                        content_x
                        + self._get_prefix_width(i, start_col, runtime)
                        - self.scroll_x
                    )
                    x2 = (
                        content_x + self._get_line_width(i, runtime) - self.scroll_x + 5
                    )
                elif i == end_line:
                    x1 = content_x - self.scroll_x
                    x2 = (
                        content_x
                        + self._get_prefix_width(i, end_col, runtime)
                        - self.scroll_x
                    )
                else:
                    x1 = content_x - self.scroll_x
                    x2 = (
                        content_x + self._get_line_width(i, runtime) - self.scroll_x + 5
                    )

                runtime.renderer.draw_rectangle(
                    Rect(int(x1), int(y), int(x2 - x1), int(line_height)),
                    self.selection_color,
                )

        # Draw line numbers and text
        for i in range(first_visible, last_visible):
            y = content_y + i * line_height - self.scroll_y

            # Line number
            if self.show_line_numbers:
                line_num_x = self.computed_x + padding_x + 5
                runtime.renderer.draw_text(
                    str(i + 1),
                    (int(line_num_x), int(y + (line_height - self.font_size) / 2)),
                    self.font_size,
                    self.line_number_color,
                )

            # Line text
            line_text = self._lines[i] if self._lines[i] else ""
            if line_text or (i == 0 and not self.value and self.placeholder):
                display_text = line_text if line_text else self.placeholder
                color = self.text_color if line_text else self.placeholder_color
                runtime.renderer.draw_text(
                    display_text,
                    (
                        int(content_x - self.scroll_x),
                        int(y + (line_height - self.font_size) / 2),
                    ),
                    self.font_size,
                    color,
                )

        # Draw cursor
        if self.is_focused:
            self.cursor_timer += runtime.renderer.get_delta_time()
            if self.cursor_timer >= 0.5:
                self.cursor_timer = 0
                self.show_cursor = not self.show_cursor

            if self.show_cursor:
                cursor_x = (
                    content_x
                    + self._get_prefix_width(self.cursor_line, self.cursor_col, runtime)
                    - self.scroll_x
                )
                cursor_y = content_y + self.cursor_line * line_height - self.scroll_y

                runtime.renderer.draw_rectangle(
                    Rect(int(cursor_x), int(cursor_y), 2, int(line_height)),
                    self.text_color,
                )

        runtime.renderer.end_scissor_mode()

        # Render children
        for child in self.children:
            child.render()
