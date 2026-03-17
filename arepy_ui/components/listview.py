"""List component - Selectable list with virtualization."""

from dataclasses import dataclass
from typing import Any, Callable, Generic
from typing import List as PyList
from typing import Optional, TypeVar

from arepy import CursorType
from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.node import Node
from ..core.style import Spacing, Style
from ..core.types import Color, Unit
from ..runtime import Key, MouseButton, get_runtime

T = TypeVar("T")


@dataclass
class ListItem(Generic[T]):
    """Represents an item in the list."""

    label: str
    value: T
    disabled: bool = False


class ListView(Node, Generic[T]):
    """
    Selectable list component with virtualization.

    Features:
    - Single and multi-selection
    - Keyboard navigation (arrows, Home, End, Page Up/Down)
    - Shift+click for range selection
    - Ctrl+click for toggle selection
    - Virtualization for large lists
    - Custom item height
    - Hover highlighting
    """

    def __init__(
        self,
        items: Optional[PyList[ListItem[T]]] = None,
        width: Unit = Unit.px(250),
        height: Unit = Unit.px(300),
        style: Optional[Style] = None,
        on_select: Optional[Callable[[PyList[T]], None]] = None,
        on_item_click: Optional[Callable[[T], None]] = None,
        multi_select: bool = False,
        item_height: int = 32,
        font_size: int = 14,
        **kwargs,
    ):
        default_style = Style(
            width=width,
            height=height,
            background_color=Color(25, 25, 30, 255),
            border_color=Color(50, 50, 60, 255),
            border_width=1.0,
            border_radius=4.0,
            cursor=CursorType.POINTING_HAND,
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

        self.items: PyList[ListItem[T]] = items or []
        self.on_select = on_select
        self.on_item_click = on_item_click
        self.multi_select = multi_select
        self.item_height = item_height
        self.font_size = font_size

        # Selection state
        self._selected_indices: set = set()
        self._focused_index: int = 0
        self._anchor_index: int = 0  # For shift+click range selection

        # Scroll state
        self.scroll_y = 0.0
        self.is_focused = False

        # Visual state
        self._hovered_index: int = -1

        # Colors
        self.text_color = Color(220, 220, 230, 255)
        self.disabled_color = Color(100, 100, 110, 255)
        self.hover_color = Color(50, 50, 60, 255)
        self.selected_color = Color(60, 100, 180, 255)
        self.focused_border_color = Color(100, 140, 200, 255)

        # Scrollbar
        self.scrollbar_width = 8
        self.scrollbar_color = Color(70, 70, 80, 255)
        self.scrollbar_thumb_color = Color(100, 100, 110, 255)

    @property
    def selected_values(self) -> PyList[T]:
        """Get list of selected values."""
        return [
            self.items[i].value
            for i in sorted(self._selected_indices)
            if i < len(self.items)
        ]

    @property
    def selected_items(self) -> PyList[ListItem[T]]:
        """Get list of selected items."""
        return [
            self.items[i] for i in sorted(self._selected_indices) if i < len(self.items)
        ]

    def select_index(self, index: int, clear_others: bool = True):
        """Select an item by index."""
        if 0 <= index < len(self.items) and not self.items[index].disabled:
            if clear_others:
                self._selected_indices.clear()
            self._selected_indices.add(index)
            self._focused_index = index
            self._notify_selection()

    def select_value(self, value: T, clear_others: bool = True):
        """Select an item by value."""
        for i, item in enumerate(self.items):
            if item.value == value:
                self.select_index(i, clear_others)
                break

    def clear_selection(self):
        """Clear all selections."""
        self._selected_indices.clear()
        self._notify_selection()

    def _notify_selection(self):
        """Notify selection change."""
        if self.on_select:
            self.on_select(self.selected_values)

    def _get_content_height(self) -> float:
        """Get total content height."""
        return len(self.items) * self.item_height

    def _get_visible_range(self) -> tuple:
        """Get range of visible items (first, last)."""
        padding_y = 4  # Fixed padding value
        view_height = self.computed_height - padding_y * 2

        first = int(self.scroll_y / self.item_height)
        last = int((self.scroll_y + view_height) / self.item_height) + 1

        return max(0, first), min(len(self.items), last)

    def _ensure_visible(self, index: int):
        """Scroll to make item visible."""
        if index < 0 or index >= len(self.items):
            return

        padding_y = 4  # Fixed padding value
        view_height = self.computed_height - padding_y * 2

        item_top = index * self.item_height
        item_bottom = item_top + self.item_height

        if item_top < self.scroll_y:
            self.scroll_y = item_top
        elif item_bottom > self.scroll_y + view_height:
            self.scroll_y = item_bottom - view_height

    def _clamp_scroll(self):
        """Clamp scroll to valid range."""
        padding_y = 4  # Fixed padding value
        view_height = self.computed_height - padding_y * 2
        max_scroll = max(0, self._get_content_height() - view_height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

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
            self.is_focused = is_inside
            if self.is_focused:
                self.style.border_color = self.focused_border_color
            else:
                self.style.border_color = Color(50, 50, 60, 255)

        # Hover handling
        self._hovered_index = -1
        if is_inside:
            padding_y = 4  # Fixed padding value
            content_y = self.computed_y + padding_y
            rel_y = mouse_pos.y - content_y + self.scroll_y
            hover_idx = int(rel_y / self.item_height)
            if 0 <= hover_idx < len(self.items):
                self._hovered_index = hover_idx

        # Click handling
        if is_click and is_inside and self._hovered_index >= 0:
            idx = self._hovered_index
            item = self.items[idx]

            if not item.disabled:
                ctrl = runtime.input.is_key_down(
                    Key.LEFT_CONTROL
                ) or runtime.input.is_key_down(Key.RIGHT_CONTROL)
                shift = runtime.input.is_key_down(
                    Key.LEFT_SHIFT
                ) or runtime.input.is_key_down(Key.RIGHT_SHIFT)

                if self.multi_select:
                    if ctrl:
                        # Toggle selection
                        if idx in self._selected_indices:
                            self._selected_indices.remove(idx)
                        else:
                            self._selected_indices.add(idx)
                        self._anchor_index = idx
                    elif shift:
                        # Range selection
                        self._selected_indices.clear()
                        start, end = min(self._anchor_index, idx), max(
                            self._anchor_index, idx
                        )
                        for i in range(start, end + 1):
                            if not self.items[i].disabled:
                                self._selected_indices.add(i)
                    else:
                        # Single selection
                        self._selected_indices.clear()
                        self._selected_indices.add(idx)
                        self._anchor_index = idx
                else:
                    self._selected_indices.clear()
                    self._selected_indices.add(idx)

                self._focused_index = idx
                self._notify_selection()

                if self.on_item_click:
                    self.on_item_click(item.value)

        # Scroll handling - consume scroll event if we have scrollable content
        if is_inside and wheel_scroll != 0:
            content_height = self._get_content_height()
            padding_y = 4
            view_height = self.computed_height - padding_y * 2

            # Only scroll if content is larger than view
            if content_height > view_height:
                self.scroll_y -= wheel_scroll * self.item_height * 3
                self._clamp_scroll()
                return True  # Consume the scroll event

        # Keyboard handling
        if self.is_focused and len(self.items) > 0:
            ctrl = runtime.input.is_key_down(
                Key.LEFT_CONTROL
            ) or runtime.input.is_key_down(Key.RIGHT_CONTROL)
            shift = runtime.input.is_key_down(
                Key.LEFT_SHIFT
            ) or runtime.input.is_key_down(Key.RIGHT_SHIFT)

            new_focus = self._focused_index

            if runtime.input.is_key_pressed(Key.UP):
                new_focus = max(0, self._focused_index - 1)
            elif runtime.input.is_key_pressed(Key.DOWN):
                new_focus = min(len(self.items) - 1, self._focused_index + 1)
            elif runtime.input.is_key_pressed(Key.HOME):
                new_focus = 0
            elif runtime.input.is_key_pressed(Key.END):
                new_focus = len(self.items) - 1
            elif runtime.input.is_key_pressed(Key.PAGE_UP):
                padding_y = 4
                view_height = self.computed_height - padding_y * 2
                page_items = int(view_height / self.item_height)
                new_focus = max(0, self._focused_index - page_items)
            elif runtime.input.is_key_pressed(Key.PAGE_DOWN):
                padding_y = 4
                view_height = self.computed_height - padding_y * 2
                page_items = int(view_height / self.item_height)
                new_focus = min(len(self.items) - 1, self._focused_index + page_items)
            elif runtime.input.is_key_pressed(
                Key.ENTER
            ) or runtime.input.is_key_pressed(Key.SPACE):
                if 0 <= self._focused_index < len(self.items):
                    item = self.items[self._focused_index]
                    if not item.disabled:
                        if self.multi_select and ctrl:
                            if self._focused_index in self._selected_indices:
                                self._selected_indices.remove(self._focused_index)
                            else:
                                self._selected_indices.add(self._focused_index)
                        else:
                            self._selected_indices.clear()
                            self._selected_indices.add(self._focused_index)
                        self._notify_selection()
                        if self.on_item_click:
                            self.on_item_click(item.value)
            elif runtime.input.is_key_pressed(Key.A) and ctrl and self.multi_select:
                # Select all
                self._selected_indices.clear()
                for i, item in enumerate(self.items):
                    if not item.disabled:
                        self._selected_indices.add(i)
                self._notify_selection()

            if new_focus != self._focused_index:
                # Skip disabled items
                direction = 1 if new_focus > self._focused_index else -1
                while (
                    0 <= new_focus < len(self.items) and self.items[new_focus].disabled
                ):
                    new_focus += direction

                if 0 <= new_focus < len(self.items):
                    self._focused_index = new_focus

                    if self.multi_select and shift:
                        # Range selection with keyboard
                        self._selected_indices.clear()
                        start, end = min(self._anchor_index, new_focus), max(
                            self._anchor_index, new_focus
                        )
                        for i in range(start, end + 1):
                            if not self.items[i].disabled:
                                self._selected_indices.add(i)
                    elif not shift:
                        if not ctrl:
                            self._selected_indices.clear()
                            self._selected_indices.add(new_focus)
                        self._anchor_index = new_focus

                    self._ensure_visible(new_focus)
                    self._notify_selection()

        return is_inside and is_click

    def render(self):
        if not self.style.visible:
            return

        runtime = get_runtime()

        # Clamp scroll on every render to handle resize
        self._clamp_scroll()

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

        padding_x = 4
        padding_y = 4
        content_x = self.computed_x + padding_x
        content_y = self.computed_y + padding_y
        content_w = self.computed_width - padding_x * 2 - self.scrollbar_width - 4
        content_h = self.computed_height - padding_y * 2

        # Draw visible items (virtualization)
        first_visible, last_visible = self._get_visible_range()
        content_bottom = content_y + content_h

        for i in range(first_visible, last_visible):
            item = self.items[i]
            item_y = content_y + i * self.item_height - self.scroll_y

            if item_y + self.item_height <= content_y or item_y >= content_bottom:
                continue

            # Item background
            is_selected = i in self._selected_indices
            is_hovered = i == self._hovered_index
            is_focused_item = i == self._focused_index and self.is_focused

            if is_selected:
                bg_color = self.selected_color
            elif is_hovered:
                bg_color = self.hover_color
            else:
                bg_color = None

            if bg_color:
                runtime.renderer.draw_rectangle(
                    Rect(int(content_x), int(item_y), int(content_w), self.item_height),
                    bg_color,
                )

            # Focus indicator
            if is_focused_item and not is_selected:
                runtime.renderer.draw_rectangle_lines_ex(
                    Rect(int(content_x), int(item_y), int(content_w), self.item_height),
                    1,
                    Color(100, 100, 120, 255),
                )

            # Item text
            text_color = self.disabled_color if item.disabled else self.text_color
            text_y = item_y + (self.item_height - self.font_size) / 2
            runtime.renderer.draw_text(
                item.label,
                (int(content_x + 8), int(text_y)),
                self.font_size,
                text_color,
            )

        # Scrollbar
        total_content = self._get_content_height()
        if total_content > content_h:
            scrollbar_x = content_x + content_w + 4

            # Track
            runtime.renderer.draw_rectangle(
                Rect(
                    int(scrollbar_x),
                    int(content_y),
                    self.scrollbar_width,
                    int(content_h),
                ),
                self.scrollbar_color,
            )

            # Thumb
            thumb_height = max(20, content_h * (content_h / total_content))
            thumb_y = content_y + (self.scroll_y / (total_content - content_h)) * (
                content_h - thumb_height
            )
            runtime.renderer.draw_rectangle(
                Rect(
                    int(scrollbar_x),
                    int(thumb_y),
                    self.scrollbar_width,
                    int(thumb_height),
                ),
                self.scrollbar_thumb_color,
            )

        # Render children
        for child in self.children:
            child.render()
