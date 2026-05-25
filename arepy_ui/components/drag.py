from dataclasses import dataclass
from typing import Any, Callable, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..core.animation import Easing
from ..core.node import Node
from ..core.style import Style
from ..core.types import Color, CursorType, FlexDirection, Unit, Vector2
from ..manager import register_overlay
from ..runtime import MouseButton, get_runtime


@dataclass
class DragState:
    is_dragging: bool = False
    source: Optional["Draggable"] = None
    data: Any = None
    start_x: float = 0.0
    start_y: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    current_target: Optional["DropZone"] = None


_drag_state = DragState()


def get_drag_state() -> DragState:
    return _drag_state


def is_dragging() -> bool:
    return _drag_state.is_dragging


class Draggable(Node):
    """
    Node that can be dragged.

    Args:
        content: Child node representing the visual content
        data: Arbitrary data passed to the DropZone
        style: Base style for the node
        on_drag_start: Callback when drag starts
        on_drag_end: Callback when drag ends (receives bool and target DropZone)
        drag_cursor: Cursor during drag
        return_on_fail: If True, animates back if not dropped on a DropZone
        drag_threshold: Pixels of movement before starting drag
        drag_opacity: Opacity during drag
    """

    def __init__(
        self,
        content: Node,
        data: Any = None,
        style: Optional[Style] = None,
        on_drag_start: Optional[Callable[[], None]] = None,
        on_drag_end: Optional[Callable[[bool, Optional["DropZone"]], None]] = None,
        drag_cursor: CursorType = CursorType.RESIZE_ALL,
        return_on_fail: bool = True,
        drag_threshold: float = 5.0,
        drag_opacity: float = 0.85,
        **kwargs,
    ):
        base_style = style or Style(
            width=Unit.auto(),
            height=Unit.auto(),
        )
        if base_style.cursor is None:
            base_style.cursor = CursorType.POINTING_HAND

        super().__init__(style=base_style, **kwargs)

        self.content = content
        self.add_child(content)

        self.data = data
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
        self.drag_cursor = drag_cursor
        self.return_on_fail = return_on_fail
        self.drag_threshold = drag_threshold
        self.drag_opacity = drag_opacity

        # Internal state
        self._is_pressed = False
        self._is_being_dragged = False
        self._original_x = 0.0
        self._original_y = 0.0
        self._original_opacity = 1.0
        self._original_parent: Optional[Node] = None
        self._press_start_x = 0.0
        self._press_start_y = 0.0

    def handle_input(
        self, mouse_pos: Vector2, is_click: bool, wheel_scroll: float = 0.0
    ) -> bool:
        if not self.style.visible:
            return False

        runtime = get_runtime()
        is_mouse_down = runtime.input.is_mouse_button_down(MouseButton.LEFT)
        is_mouse_released = runtime.input.is_mouse_button_released(MouseButton.LEFT)

        global _drag_state

        # If we are being dragged
        if _drag_state.is_dragging and _drag_state.source is self:
            # Re-register overlay each frame (cleared on each update)
            register_overlay(lambda: self._render_as_overlay())

            # Move with the mouse
            new_x = mouse_pos.x - _drag_state.offset_x
            new_y = mouse_pos.y - _drag_state.offset_y

            dx = new_x - self.computed_x
            dy = new_y - self.computed_y
            self.translate(dx, dy)

            # Release
            if is_mouse_released:
                self._end_drag(mouse_pos)

            return True

        # Only process clicks if no other drag is active
        if _drag_state.is_dragging:
            return False

        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )
        is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        # Start potential drag
        if is_over and is_click:
            self._is_pressed = True
            self._press_start_x = mouse_pos.x
            self._press_start_y = mouse_pos.y
            return True

        # Check if threshold is exceeded to start drag
        if self._is_pressed and is_mouse_down:
            dx = abs(mouse_pos.x - self._press_start_x)
            dy = abs(mouse_pos.y - self._press_start_y)

            if dx > self.drag_threshold or dy > self.drag_threshold:
                self._start_drag(mouse_pos)
            return True

        # Cancel if released without exceeding threshold
        if self._is_pressed and is_mouse_released:
            self._is_pressed = False

        return super().handle_input(mouse_pos, is_click, wheel_scroll)

    def _start_drag(self, mouse_pos: Vector2):
        """Start the drag."""
        global _drag_state

        self._original_x = self.computed_x
        self._original_y = self.computed_y
        self._original_opacity = self.style.opacity
        self._original_parent = self.parent
        self._is_being_dragged = True

        # Global state
        _drag_state.is_dragging = True
        _drag_state.source = self
        _drag_state.data = self.data
        _drag_state.start_x = self.computed_x
        _drag_state.start_y = self.computed_y
        _drag_state.offset_x = mouse_pos.x - self.computed_x
        _drag_state.offset_y = mouse_pos.y - self.computed_y

        # Change opacity
        self.style.opacity = self.drag_opacity

        # Change cursor
        runtime = get_runtime()
        runtime.display.set_mouse_cursor(self.drag_cursor)

        if self.on_drag_start:
            self.on_drag_start()

    def _render_as_overlay(self):
        """Render as overlay (on top of everything)."""
        # Call Node's render directly (not Draggable's which has the check)
        Node.render(self)

    def _end_drag(self, mouse_pos: Vector2):
        """End the drag."""
        global _drag_state

        dropped = False
        target = _drag_state.current_target

        # Check if there's a DropZone below
        if target:
            dropped = target._receive_drop(self, self.data)

        # Restore opacity
        self.style.opacity = self._original_opacity
        self._is_being_dragged = False

        # If not dropped and return_on_fail, animate back
        if not dropped and self.return_on_fail:
            self._animate_return()

        # Restore cursor
        runtime = get_runtime()
        runtime.display.set_mouse_cursor(CursorType.DEFAULT)

        # Clear state
        _drag_state.is_dragging = False
        _drag_state.source = None
        _drag_state.data = None
        _drag_state.current_target = None
        self._is_pressed = False

        if self.on_drag_end:
            self.on_drag_end(dropped, target)

    def _animate_return(self):
        """Animate back to the original position."""
        if not self._manager:
            dx = self._original_x - self.computed_x
            dy = self._original_y - self.computed_y
            self.translate(dx, dy)
            return

        self._manager.animator.create().to(
            self,
            "computed_x",
            self._original_x,
            0.2,
            Easing.EASE_OUT_CUBIC,
        ).start()

        self._manager.animator.create().to(
            self,
            "computed_y",
            self._original_y,
            0.2,
            Easing.EASE_OUT_CUBIC,
        ).call(self.mark_dirty).start()

    def render(self):
        """Override render to avoid double rendering during drag."""
        if self._is_being_dragged:
            # During drag, don't render here (rendered in overlay)
            return
        super().render()


class DropZone(Node):
    """
    Zone that can receive dragged elements.

    Args:
        style: Base style
        on_drop: Callback when an element is dropped (receives draggable and data)
        on_drag_enter: Callback when a draggable enters the zone
        on_drag_leave: Callback when a draggable leaves the zone
        accept: Function that validates if the data is accepted (optional)
        highlight_color: Background color when a drag is over
        auto_adopt: If True, automatically adopts the Draggable on drop
        sortable: If True, allows reordering items within the zone
        drop_indicator_color: Color of the indicator showing where item will be inserted
    auto_adopt: If True, adds dropped element as child
    sortable: If True, shows insertion indicator and reorders children
    drop_indicator_color: Color of insertion indicator
    data: Arbitrary data associated with the DropZone
    """

    def __init__(
        self,
        style: Optional[Style] = None,
        on_drop: Optional[Callable[["Draggable", Any], Optional[bool]]] = None,
        on_drag_enter: Optional[Callable[[], None]] = None,
        on_drag_leave: Optional[Callable[[], None]] = None,
        accept: Optional[Callable[[Any], bool]] = None,
        highlight_color: Optional[Color] = None,
        auto_adopt: bool = True,
        sortable: bool = False,
        drop_indicator_color: Optional[Color] = None,
        data: Any = None,
        **kwargs,
    ):
        super().__init__(style=style or Style(), **kwargs)

        self.on_drop = on_drop
        self.on_drag_enter = on_drag_enter
        self.on_drag_leave = on_drag_leave
        self.accept = accept
        self.highlight_color = highlight_color
        self.auto_adopt = auto_adopt
        self.sortable = sortable
        self.drop_indicator_color = drop_indicator_color or Color(100, 150, 255, 200)
        self.data = data

        self._is_drag_over = False
        self._original_bg_color: Optional[Color] = None
        self._drop_index: Optional[int] = None
        self._indicator_rect: Optional[tuple[float, float, float, float]] = None

    def adopt(self, draggable: Draggable, index: Optional[int] = None):
        """
        Adopt a Draggable, moving it to this DropZone.

        Args:
            draggable: The draggable node to adopt
            index: Position to insert at (None = at the end)
        """
        # Remove from previous parent
        if draggable.parent and draggable in draggable.parent.children:
            draggable.parent.children.remove(draggable)

        # Add as child of this DropZone
        draggable.parent = self
        if index is not None and 0 <= index < len(self.children):
            self.children.insert(index, draggable)
        else:
            self.children.append(draggable)

        # Propagate the manager
        if self._manager:
            draggable._manager = self._manager

        # Force layout recalculation
        self.mark_dirty()

    def _calculate_drop_index(self, mouse_pos: Vector2) -> int:
        """
        Calculate the index where to insert based on mouse position.
        Considers the flex direction (COLUMN or ROW).
        """
        if not self.children:
            return 0

        is_vertical = self.style.flex_direction == FlexDirection.COLUMN

        # Get only visible Draggables (excluding the one being dragged)
        visible_children = [
            c
            for c in self.children
            if isinstance(c, Draggable) and c is not _drag_state.source
        ]

        if not visible_children:
            return 0

        for i, child in enumerate(visible_children):
            if is_vertical:
                # For COLUMN: compare Y position
                child_center = child.computed_y + child.computed_height / 2
                if mouse_pos.y < child_center:
                    # Find the real index in self.children
                    return self.children.index(child)
            else:
                # For ROW: compare X position
                child_center = child.computed_x + child.computed_width / 2
                if mouse_pos.x < child_center:
                    return self.children.index(child)

        # If reached here, insert at the end
        return len(self.children)

    def _calculate_indicator_rect(
        self, index: int
    ) -> Optional[tuple[float, float, float, float]]:
        """Calculate the rectangle for the drop indicator."""
        is_vertical = self.style.flex_direction == FlexDirection.COLUMN

        # Get visible children (excluding the one being dragged)
        visible_children = [
            c
            for c in self.children
            if isinstance(c, Draggable) and c is not _drag_state.source
        ]

        indicator_thickness = 3
        gap = self.style.gap

        if is_vertical:
            # Horizontal indicator
            x = self.computed_x + self.style.padding.left.value
            width = (
                self.computed_width
                - self.style.padding.left.value
                - self.style.padding.right.value
            )

            if not visible_children:
                y = self.computed_y + self.style.padding.top.value
            elif index >= len(visible_children):
                # At the end
                last = visible_children[-1]
                y = last.computed_y + last.computed_height + gap / 2
            else:
                # Before the element at index
                target_child = None
                count = 0
                for c in self.children:
                    if isinstance(c, Draggable) and c is not _drag_state.source:
                        if count == index:
                            target_child = c
                            break
                        count += 1
                if target_child:
                    y = target_child.computed_y - gap / 2 - indicator_thickness
                else:
                    y = self.computed_y + self.style.padding.top.value

            return (x, y, width, indicator_thickness)
        else:
            # Vertical indicator
            y = self.computed_y + self.style.padding.top.value
            height = (
                self.computed_height
                - self.style.padding.top.value
                - self.style.padding.bottom.value
            )

            if not visible_children:
                x = self.computed_x + self.style.padding.left.value
            elif index >= len(visible_children):
                last = visible_children[-1]
                x = last.computed_x + last.computed_width + gap / 2
            else:
                target_child = None
                count = 0
                for c in self.children:
                    if isinstance(c, Draggable) and c is not _drag_state.source:
                        if count == index:
                            target_child = c
                            break
                        count += 1
                if target_child:
                    x = target_child.computed_x - gap / 2 - indicator_thickness
                else:
                    x = self.computed_x + self.style.padding.left.value

            return (x, y, indicator_thickness, height)

    def handle_input(
        self, mouse_pos: Vector2, is_click: bool, wheel_scroll: float = 0.0
    ) -> bool:
        if not self.style.visible:
            return False

        # Process children first (including Draggables)
        for child in reversed(self.children):
            if child.handle_input(mouse_pos, is_click, wheel_scroll):
                return True

        global _drag_state

        # Only process zone detection if there's an active drag
        if _drag_state.is_dragging:
            rect = Rect(
                self.computed_x,
                self.computed_y,
                int(self.computed_width),
                int(self.computed_height),
            )
            is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

            # Verify if it accepts this type of data
            can_accept = True
            if self.accept and _drag_state.data is not None:
                can_accept = self.accept(_drag_state.data)

            if is_over and can_accept:
                if not self._is_drag_over:
                    self._is_drag_over = True
                    _drag_state.current_target = self

                    if self.highlight_color:
                        self._original_bg_color = self.style.background_color
                        self.style.background_color = self.highlight_color

                    if self.on_drag_enter:
                        self.on_drag_enter()

                # Calculate drop index if sortable
                if self.sortable:
                    self._drop_index = self._calculate_drop_index(mouse_pos)
                    self._indicator_rect = self._calculate_indicator_rect(
                        self._drop_index
                    )
            else:
                if self._is_drag_over:
                    self._is_drag_over = False
                    self._drop_index = None
                    self._indicator_rect = None

                    if _drag_state.current_target is self:
                        _drag_state.current_target = None

                    if self._original_bg_color is not None:
                        self.style.background_color = self._original_bg_color
                        self._original_bg_color = None

                    if self.on_drag_leave:
                        self.on_drag_leave()

        return False

    def render(self):
        """Render the zone and the drop indicator if applicable."""
        super().render()

        # Draw drop indicator if one is active
        if self._is_drag_over and self.sortable and self._indicator_rect:
            runtime = get_runtime()
            if runtime:
                x, y, w, h = self._indicator_rect
                indicator_rect = Rect(int(x), int(y), int(w), int(h))
                runtime.renderer.draw_rectangle(
                    indicator_rect,
                    self.drop_indicator_color,
                )

    def _receive_drop(self, draggable: Draggable, data: Any) -> bool:
        """Receive a drop. Returns True if accepted."""
        # Save index before clearing state
        drop_index = self._drop_index if self.sortable else None

        # Restore color
        if self._original_bg_color is not None:
            self.style.background_color = self._original_bg_color
            self._original_bg_color = None

        self._is_drag_over = False
        self._drop_index = None
        self._indicator_rect = None

        # Verify acceptance
        if self.accept and not self.accept(data):
            return False

        # Auto-adopt if enabled
        if self.auto_adopt:
            self.adopt(draggable, index=drop_index)

        # Callback
        if self.on_drop:
            result = self.on_drop(draggable, data)
            return result if isinstance(result, bool) else True

        return self.auto_adopt
