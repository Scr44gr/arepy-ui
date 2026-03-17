from typing import Callable, List, Optional

from arepy.engine.renderer import Rect
from arepy.math import check_collision_point_rec

from ..runtime import get_runtime
from .style import Style
from .types import (
    AlignItems,
    Color,
    FlexDirection,
    JustifyContent,
    PositionType,
    Rectangle,
    Unit,
    UnitType,
    Vector2,
)


class Node:
    def __init__(
        self,
        style: Optional[Style] = None,
        children: Optional[List["Node"]] = None,
        id: Optional[str] = None,
    ):
        self.id = id
        self._style = Style()
        self.children: List["Node"] = children or []
        self.parent: Optional["Node"] = None
        self._manager = None  # Reference to UIManager

        for child in self.children:
            child.parent = self

        # Computed layout
        self.computed_x: float = 0.0
        self.computed_y: float = 0.0
        self.computed_width: float = 0.0
        self.computed_height: float = 0.0

        # Event handlers
        self.on_click: Optional[Callable[[], None]] = None
        self.on_hover_enter: Optional[Callable[[], None]] = None
        self.on_hover_exit: Optional[Callable[[], None]] = None

        # State
        self.is_hovered: bool = False
        self.pickable: bool = (
            True  # If False, input passes through (unless children consume it)
        )
        self._layout_viewport_size: Optional[tuple[float, float]] = None
        self._last_layout_request: Optional[tuple[float, float, float, float]] = None
        self.style = style or Style()

    @property
    def style(self) -> Style:
        return self._style

    @style.setter
    def style(self, value: Style):
        self._style = value
        self._style._bind_owner(self)
        if hasattr(self, "computed_width"):
            self.mark_dirty()

    def mark_dirty(self):
        """Mark the UI as dirty to trigger re-layout."""
        if self._manager:
            if hasattr(self._manager, "mark_dirty_node"):
                self._manager.mark_dirty_node(self._get_relayout_root())
            else:
                self._manager.mark_dirty()
        elif self.parent:
            self.parent.mark_dirty()

    def is_ancestor_of(self, node: Optional["Node"]) -> bool:
        current = node
        while current is not None:
            if current is self:
                return True
            current = current.parent
        return False

    def _get_relayout_root(self) -> "Node":
        candidate = self.parent or self
        while candidate.parent is not None and (
            candidate.style.width.type == UnitType.AUTO
            or candidate.style.height.type == UnitType.AUTO
        ):
            candidate = candidate.parent
        return candidate

    def add_child(self, child: "Node"):
        child.parent = self
        # Propagate manager to new child and its descendants
        if self._manager:
            self._propagate_manager(child)
        self.children.append(child)
        self.mark_dirty()

    def _propagate_manager(self, node: "Node"):
        """Recursively set manager reference on node and descendants."""
        node._manager = self._manager
        for child in node.children:
            self._propagate_manager(child)

    def find_by_id(self, element_id: str) -> Optional["Node"]:
        """
        Find a descendant node by its ID.

        Args:
            element_id: The ID to search for

        Returns:
            The node with the matching ID, or None if not found
        """
        if self.id == element_id:
            return self

        for child in self.children:
            result = child.find_by_id(element_id)
            if result is not None:
                return result

        return None

    def calculate_layout(
        self,
        parent_x: float,
        parent_y: float,
        parent_width: float,
        parent_height: float,
    ):
        """
        Simplified layout calculation.
        """
        self._last_layout_request = (parent_x, parent_y, parent_width, parent_height)

        # Optimization: If not visible, skip layout
        if not self.style.visible:
            self.computed_width = 0
            self.computed_height = 0
            return

        if self.parent is None:
            self._layout_viewport_size = None

        # 1. Calculate own dimensions
        self.computed_width = self._resolve_unit(self.style.width, parent_width)
        self.computed_height = self._resolve_unit(self.style.height, parent_height)

        # Auto Sizing Logic (Basic)
        # If width/height is AUTO, we need to measure children first.
        # But children need parent size to resolve percentages.
        # This is the classic layout circular dependency.
        # For now, if AUTO, we assume 0 initially, then expand after children measurement.

        is_width_auto = self.style.width.type == UnitType.AUTO
        is_height_auto = self.style.height.type == UnitType.AUTO

        if is_width_auto:
            self.computed_width = 0  # Will expand
        if is_height_auto:
            self.computed_height = 0  # Will expand

        # Handle margins
        margin_left = self._resolve_unit(self.style.margin.left, parent_width)
        margin_top = self._resolve_unit(self.style.margin.top, parent_height)

        # Position
        if self.style.position == PositionType.ABSOLUTE:
            # Absolute positioning relative to parent
            # Handle left/right positioning
            if self.style.left is not None:
                left = self._resolve_unit(self.style.left, parent_width)
                self.computed_x = parent_x + left + margin_left
            elif self.style.right is not None:
                right = self._resolve_unit(self.style.right, parent_width)
                self.computed_x = (
                    parent_x + parent_width - self.computed_width - right - margin_left
                )
            else:
                self.computed_x = parent_x + margin_left

            # Handle top/bottom positioning
            if self.style.top is not None:
                top = self._resolve_unit(self.style.top, parent_height)
                self.computed_y = parent_y + top + margin_top
            elif self.style.bottom is not None:
                bottom = self._resolve_unit(self.style.bottom, parent_height)
                self.computed_y = (
                    parent_y
                    + parent_height
                    - self.computed_height
                    - bottom
                    - margin_top
                )
            else:
                self.computed_y = parent_y + margin_top
        else:
            # Relative positioning (handled by parent's flex layout usually, but here we set base)
            self.computed_x = parent_x + margin_left
            self.computed_y = parent_y + margin_top

        # 2. Layout children (Flexbox-ish)
        if not self.children:
            # If leaf node and auto, maybe use content size (like Text)?
            # Text node should override calculate_layout or set size before.
            return

        # Available space for children
        # If auto, we pass parent_width/height as available space for percentages?
        # Or 0? Usually parent_width.
        avail_width = parent_width if is_width_auto else self.computed_width
        avail_height = parent_height if is_height_auto else self.computed_height

        padding_left = self._resolve_unit(self.style.padding.left, avail_width)
        padding_right = self._resolve_unit(self.style.padding.right, avail_width)
        padding_top = self._resolve_unit(self.style.padding.top, avail_height)
        padding_bottom = self._resolve_unit(self.style.padding.bottom, avail_height)

        content_width = avail_width - padding_left - padding_right
        content_height = avail_height - padding_top - padding_bottom

        start_x = self.computed_x + padding_left
        start_y = self.computed_y + padding_top

        current_x = start_x
        current_y = start_y

        # First pass: Measure children and determine total size
        # Skip absolute positioned children - they don't participate in flex layout
        total_flex_size = 0.0
        max_cross_size = 0.0  # For auto sizing
        flex_children = []  # Only non-absolute children

        for child in self.children:
            child._layout_viewport_size = self._layout_viewport_size
            # Recursive layout with available space
            child.calculate_layout(current_x, current_y, content_width, content_height)

            # Skip absolute positioned children for flex calculations
            if child.style.position == PositionType.ABSOLUTE:
                continue

            flex_children.append(child)

            if self.style.flex_direction == FlexDirection.COLUMN:
                total_flex_size += child.computed_height + self.style.gap
                max_cross_size = max(max_cross_size, child.computed_width)
            else:
                total_flex_size += child.computed_width + self.style.gap
                max_cross_size = max(max_cross_size, child.computed_height)

        if flex_children:
            total_flex_size -= self.style.gap  # Remove last gap

        # Update Auto Size
        if is_width_auto:
            if self.style.flex_direction == FlexDirection.ROW:
                self.computed_width = total_flex_size + padding_left + padding_right
            else:
                self.computed_width = max_cross_size + padding_left + padding_right

        if is_height_auto:
            if self.style.flex_direction == FlexDirection.COLUMN:
                self.computed_height = total_flex_size + padding_top + padding_bottom
            else:
                self.computed_height = max_cross_size + padding_top + padding_bottom

        # Re-calculate content size if we changed size
        if is_width_auto or is_height_auto:
            content_width = self.computed_width - padding_left - padding_right
            content_height = self.computed_height - padding_top - padding_bottom

        # Second pass: Position children based on JustifyContent
        # (Simplified: assuming children have fixed sizes for now, not handling flex-grow/shrink yet)

        offset_main = 0.0

        if self.style.justify_content == JustifyContent.CENTER:
            if self.style.flex_direction == FlexDirection.COLUMN:
                offset_main = (content_height - total_flex_size) / 2
            else:
                offset_main = (content_width - total_flex_size) / 2
        elif self.style.justify_content == JustifyContent.END:
            if self.style.flex_direction == FlexDirection.COLUMN:
                offset_main = content_height - total_flex_size
            else:
                offset_main = content_width - total_flex_size

        # Apply positions
        current_x = start_x
        current_y = start_y

        if self.style.flex_direction == FlexDirection.COLUMN:
            current_y += offset_main
        else:
            current_x += offset_main

        # Only position non-absolute children in the flex flow
        for child in flex_children:
            # Get child margins
            child_margin_left = self._resolve_unit(
                child.style.margin.left, content_width
            )
            child_margin_top = self._resolve_unit(
                child.style.margin.top, content_height
            )

            # Align Items (Cross Axis)
            cross_offset = 0.0
            if self.style.align_items == AlignItems.CENTER:
                if self.style.flex_direction == FlexDirection.COLUMN:
                    cross_offset = (content_width - child.computed_width) / 2
                else:
                    cross_offset = (content_height - child.computed_height) / 2

            # Update child position based on flex alignment + margins
            if self.style.flex_direction == FlexDirection.COLUMN:
                child.computed_x = start_x + cross_offset + child_margin_left
                child.computed_y = current_y + child_margin_top
                current_y += child.computed_height + self.style.gap
            else:
                child.computed_x = current_x + child_margin_left
                child.computed_y = start_y + cross_offset + child_margin_top
                current_x += child.computed_width + self.style.gap

            # Recursively update grandchildren positions if the child moved
            if child.children:
                self._propagate_position_to_children(child)

    def _propagate_position_to_children(self, node: "Node"):
        """
        Propagate position changes to children.
        This recalculates child positions based on parent's new position.
        """
        if not node.style.visible or not node.children:
            return

        # For nodes with children, we need to recalculate their layout
        # since the parent position changed
        # Get the content area
        padding_left = self._resolve_unit(node.style.padding.left, node.computed_width)
        padding_right = self._resolve_unit(
            node.style.padding.right, node.computed_width
        )
        padding_top = self._resolve_unit(node.style.padding.top, node.computed_height)
        padding_bottom = self._resolve_unit(
            node.style.padding.bottom, node.computed_height
        )

        content_width = node.computed_width - padding_left - padding_right
        content_height = node.computed_height - padding_top - padding_bottom

        start_x = node.computed_x + padding_left
        start_y = node.computed_y + padding_top

        # Calculate total size of flex children for justify/align
        total_flex_size = 0.0
        flex_children = []

        for child in node.children:
            if not child.style.visible:
                continue
            if child.style.position == PositionType.ABSOLUTE:
                # Handle absolute children
                margin_left = self._resolve_unit(
                    child.style.margin.left, node.computed_width
                )
                margin_top = self._resolve_unit(
                    child.style.margin.top, node.computed_height
                )

                if child.style.left is not None:
                    left = self._resolve_unit(child.style.left, node.computed_width)
                    child.computed_x = node.computed_x + left + margin_left
                elif child.style.right is not None:
                    right = self._resolve_unit(child.style.right, node.computed_width)
                    child.computed_x = (
                        node.computed_x
                        + node.computed_width
                        - child.computed_width
                        - right
                        - margin_left
                    )
                else:
                    child.computed_x = node.computed_x + margin_left

                if child.style.top is not None:
                    top = self._resolve_unit(child.style.top, node.computed_height)
                    child.computed_y = node.computed_y + top + margin_top
                elif child.style.bottom is not None:
                    bottom = self._resolve_unit(
                        child.style.bottom, node.computed_height
                    )
                    child.computed_y = (
                        node.computed_y
                        + node.computed_height
                        - child.computed_height
                        - bottom
                        - margin_top
                    )
                else:
                    child.computed_y = node.computed_y + margin_top

                if child.children:
                    child._layout_viewport_size = node._layout_viewport_size
                    self._propagate_position_to_children(child)
                continue

            flex_children.append(child)
            if node.style.flex_direction == FlexDirection.COLUMN:
                total_flex_size += child.computed_height + node.style.gap
            else:
                total_flex_size += child.computed_width + node.style.gap

        if flex_children:
            total_flex_size -= node.style.gap

        # Calculate main axis offset (justify_content)
        offset_main = 0.0
        if node.style.justify_content == JustifyContent.CENTER:
            if node.style.flex_direction == FlexDirection.COLUMN:
                offset_main = (content_height - total_flex_size) / 2
            else:
                offset_main = (content_width - total_flex_size) / 2
        elif node.style.justify_content == JustifyContent.END:
            if node.style.flex_direction == FlexDirection.COLUMN:
                offset_main = content_height - total_flex_size
            else:
                offset_main = content_width - total_flex_size

        current_x = start_x
        current_y = start_y

        if node.style.flex_direction == FlexDirection.COLUMN:
            current_y += offset_main
        else:
            current_x += offset_main

        # Position flex children with proper alignment
        for child in flex_children:
            # Get child margins
            child_margin_left = self._resolve_unit(
                child.style.margin.left, content_width
            )
            child_margin_top = self._resolve_unit(
                child.style.margin.top, content_height
            )

            cross_offset = 0.0
            if node.style.align_items == AlignItems.CENTER:
                if node.style.flex_direction == FlexDirection.COLUMN:
                    cross_offset = (content_width - child.computed_width) / 2
                else:
                    cross_offset = (content_height - child.computed_height) / 2

            if node.style.flex_direction == FlexDirection.COLUMN:
                child.computed_x = start_x + cross_offset + child_margin_left
                child.computed_y = current_y + child_margin_top
                current_y += child.computed_height + node.style.gap
            else:
                child.computed_x = current_x + child_margin_left
                child.computed_y = start_y + cross_offset + child_margin_top
                current_x += child.computed_width + node.style.gap

            if child.children:
                child._layout_viewport_size = node._layout_viewport_size
                self._propagate_position_to_children(child)

    def _get_layout_viewport_size(self, refresh: bool = False) -> tuple[float, float]:
        if refresh or self._layout_viewport_size is None:
            width, height = get_runtime().display.get_window_size()
            self._layout_viewport_size = (float(width), float(height))
        return self._layout_viewport_size

    def _resolve_unit(self, unit: Unit, parent_value: float) -> float:
        if unit.type == UnitType.PIXEL:
            return unit.value
        elif unit.type == UnitType.PERCENT:
            return parent_value * (unit.value / 100.0)
        elif unit.type == UnitType.VIEWPORT_WIDTH:
            width, _ = self._get_layout_viewport_size()
            return width * (unit.value / 100.0)
        elif unit.type == UnitType.VIEWPORT_HEIGHT:
            _, height = self._get_layout_viewport_size()
            return height * (unit.value / 100.0)
        elif unit.type == UnitType.AUTO:
            # For auto, we usually default to 0 or content size.
            # For this simple engine, let's default to parent size if it's width/height,
            # or 0 if it's margin/padding.
            # Ideally 'auto' triggers a measure pass.
            return parent_value  # Simplified: Auto fills parent
        return 0.0

    def translate(self, dx: float, dy: float):
        """
        Efficiently move this node and all its children by (dx, dy).
        Avoids full layout recalculation.
        """
        self.computed_x += dx
        self.computed_y += dy

        for child in self.children:
            child.translate(dx, dy)

    def render(self):
        if not self.style.visible or self.style.opacity <= 0:
            return

        # Culling Optimization:
        # If we are completely off-screen, don't render.
        runtime = get_runtime()
        screen_w, screen_h = runtime.display.get_window_size()

        if (
            self.computed_x > screen_w
            or self.computed_x + self.computed_width < 0
            or self.computed_y > screen_h
            or self.computed_y + self.computed_height < 0
        ):
            # Off screen
            return

        # Draw Background
        if self.style.background_color:
            color = self.style.background_color
            # Apply opacity
            if self.style.opacity < 1.0:
                color = Color(
                    color.r, color.g, color.b, int(color.a * self.style.opacity)
                )

            rect = Rect(
                self.computed_x,
                self.computed_y,
                int(self.computed_width),
                int(self.computed_height),
            )

            if self.style.border_radius > 0:
                min_dim = min(self.computed_width, self.computed_height)
                roundness = self.style.border_radius / min_dim if min_dim > 0 else 0
                runtime.renderer.draw_rectangle_rounded(
                    rect,
                    roundness,
                    10,
                    color,  # type: ignore
                )
            else:
                runtime.renderer.draw_rectangle(rect, color)  # type: ignore

        # Draw Border
        if self.style.border_width > 0 and self.style.border_color:
            # Raylib doesn't have draw_rectangle_rounded_lines with thickness easily
            # We can simulate or use lines
            rect = Rect(
                self.computed_x,
                self.computed_y,
                int(self.computed_width),
                int(self.computed_height),
            )
            if self.style.border_radius > 0:
                runtime.renderer.draw_rectangle_rounded_lines(
                    rect,
                    self.style.border_radius
                    / min(self.computed_width, self.computed_height),
                    10,
                    self.style.border_color,  # type: ignore
                )
            else:
                runtime.renderer.draw_rectangle_lines_ex(
                    rect,
                    self.style.border_width,
                    self.style.border_color,  # type: ignore
                )

        # Render Children
        for child in self.children:
            child.render()

    def handle_input(
        self, mouse_pos: Vector2, is_click: bool, wheel_scroll: float = 0.0
    ) -> bool:
        """
        Handle input events. Returns True if input was consumed (click handled).
        Hover state is tracked but doesn't consume input.
        """
        if not self.style.visible:
            return False

        # Check children first (reverse order for z-index)
        for child in reversed(self.children):
            if child.handle_input(mouse_pos, is_click, wheel_scroll):
                return True

        if not self.pickable:
            return False

        # Check if mouse is over this node
        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )
        is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        # Update hover state
        if is_over:
            if not self.is_hovered:
                self.is_hovered = True
                if self.on_hover_enter:
                    self.on_hover_enter()

            # Only consume input if there's a click AND we have a click handler
            if is_click and self.on_click:
                self.on_click()
                return True
        else:
            if self.is_hovered:
                self.is_hovered = False
                if self.on_hover_exit:
                    self.on_hover_exit()

        # Don't consume input just for hover - let it propagate
        return False
