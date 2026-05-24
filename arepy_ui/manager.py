from typing import TYPE_CHECKING, Callable, List, Optional

from .config import ResizeMode, ScaleTransform, UIConfig, calculate_scale_transform
from .core.animation import Animator
from .core.fonts import get_font_manager
from .core.node import Node
from .core.types import Color, CursorType, Vector2
from .runtime import MouseButton, configure_runtime, get_runtime
from arepy import TextureFilter

if TYPE_CHECKING:
    from arepy import ArepyEngine

# Global list for overlay renders (dropdowns, tooltips, etc)
_overlay_renders: List[Callable[[], None]] = []


def register_overlay(render_fn: Callable[[], None]):
    """Register a function to be called during overlay render pass."""
    _overlay_renders.append(render_fn)


def clear_overlays():
    """Clear all registered overlays."""
    _overlay_renders.clear()


class UIManager:
    """Main UI manager that handles layout, input, and rendering."""

    def __init__(self, config: Optional[UIConfig] = None):
        self.root: Optional[Node] = None
        self.animator = Animator()
        self.config = config or UIConfig()

        runtime = get_runtime()
        width, height = runtime.display.get_window_size()

        # Store initial size as reference if not specified
        if self.config.reference_width is None:
            self.config.reference_width = width
        if self.config.reference_height is None:
            self.config.reference_height = height

        self.screen_width = width
        self.screen_height = height
        self.is_dirty = True
        self.is_input_captured = False

        # Scale transform for non-responsive modes
        self.scale_transform = ScaleTransform()

        # Debounce timer
        self._resize_debounce_timer = 0.0
        self._pending_resize = False

        # Cursor management
        self._current_cursor = CursorType.DEFAULT
        self._hovered_node: Optional[Node] = None

        # Tooltip system
        self._tooltip_text: Optional[str] = None
        self._tooltip_delay = 0.5  # seconds before showing
        self._tooltip_timer = 0.0
        self._tooltip_visible = False
        self._tooltip_pos = Vector2(0, 0)

        # Modal/Overlay system
        self._modals: List[Node] = []
        self._modal_backdrop_color = Color(0, 0, 0, 150)

        # Focus management for inputs
        self._focused_node: Optional[Node] = None

        # Stencil initialization flag
        self._stencil_initialized = False

        # Font scaling (multiplier applied to font sizes)
        # This value is used by `set_font_scale` to scale nodes that expose a `font_size`.
        self._font_scale: float = 1.0



    @classmethod
    def from_engine(
        cls, engine: "ArepyEngine", config: Optional[UIConfig] = None
    ) -> "UIManager":
        """
        Create a UIManager from an ArepyEngine instance.

        This is the recommended way to initialize arepy-ui as it automatically
        configures the runtime with all necessary engine components.

        Args:
            engine: The ArepyEngine instance
            config: Optional UI configuration

        Returns:
            A configured UIManager instance

        Example:
            ui_manager = UIManager.from_engine(game)
            ui_manager.set_root(create_ui())
        """
        # Configure the runtime with engine components
        configure_runtime(
            renderer=engine.renderer_2d,
            input=engine.input,
            display=engine.display,
            asset_store=engine.get_asset_store(),
            audio_device=engine.audio_device,
        )

        return cls(config=config)

    def _ensure_stencil(self):
        """Initialize stencil buffer if not already done."""
        if self._stencil_initialized:
            return
        runtime = get_runtime()
        if not runtime.renderer.is_stencil_available():
            runtime.renderer.init_stencil()
        self._stencil_initialized = True

    def set_font_texture_filter(self, texture_filter: TextureFilter) -> None:
        """
        Set the texture filter used for font textures at runtime.

        This uses the UIConfig API to update the configured value and then
        delegates to the FontManager to apply the change to already-loaded fonts.
        Accepts a non-optional TextureFilter (UIConfig expects a concrete value).
        """
        # Update UIConfig using its setter which notifies listeners
        try:
            self.config.set_font_texture_filter(texture_filter)
        except Exception:
            # If config update fails for any reason, still attempt to apply it
            pass

        # Apply to font manager directly as well to ensure immediate effect
        try:
            get_font_manager().set_texture_filter(texture_filter)
        except Exception:
            # Swallow exceptions to avoid disrupting runtime
            pass

    def set_font_scale(self, scale: float) -> None:
        """
        Set the global font scale multiplier and apply it to all nodes that expose a `font_size`.

        Behavior:
        - `scale` must be > 0. Values < 0 are ignored.
        - The first time a node with `font_size` is scaled, its original size is stored
          in `_aui_base_font_size` so subsequent scale changes are applied relative
          to the original size (avoids compounding).
        - This attempts to call `_update_size()` on nodes that expose it (e.g., `Text`)
          and marks nodes dirty to trigger layout recalculation.
        """
        if scale <= 0:
            return

        self._font_scale = scale
        if self.root:
            try:
                self._apply_font_scale_to_node(self.root)
                self.mark_dirty()
            except Exception:
                # Avoid raising from a single node failure
                pass

    def _apply_font_scale_to_node(self, node: Node) -> None:
        """Recursively apply the current font scale to nodes with a `font_size` attribute."""
        # If a node has a font_size attribute, scale it relative to its stored base size.
        if hasattr(node, "font_size"):
            base_attr = "_aui_base_font_size"
            # Store base size if not present
            if not hasattr(node, base_attr):
                try:
                    setattr(node, base_attr, float(getattr(node, "font_size")))
                except Exception:
                    # Fallback to raw value if conversion fails
                    setattr(node, base_attr, getattr(node, "font_size"))

            # Apply scale
            try:
                base_val = getattr(node, base_attr)
                setattr(node, "font_size", base_val * self._font_scale)
            except Exception:
                # Ignore errors setting font size for safety
                pass

            # Invalidate cached metrics if present
            if hasattr(node, "_cached_metrics"):
                try:
                    setattr(node, "_cached_metrics", None)
                except Exception:
                    pass

            # Allow node to update internal sizing if it has that hook
            update_size = getattr(node, "_update_size", None)
            if callable(update_size):
                try:
                    update_size()
                except Exception:
                    pass

            try:
                node.mark_dirty()
            except Exception:
                pass

        # Recurse into children
        for child in node.children:
            try:
                self._apply_font_scale_to_node(child)
            except Exception:
                # Continue despite failures on particular children
                pass

    def set_root(self, node: Node):
        self.root = node
        self.is_dirty = True
        if self.root:
            self._propagate_manager(self.root)
            # Calculate layout immediately to avoid 1-frame glitch
            self._recalculate_layout()

    def _propagate_manager(self, node: Node):
        """Recursively set manager reference on all nodes."""
        node._manager = self
        for child in node.children:
            self._propagate_manager(child)

    def request_focus(self, node: Node) -> bool:
        """Request focus for a node. Returns True if focus was granted."""
        if self._focused_node is node:
            return True

        # Blur the previously focused node
        if self._focused_node is not None:
            if hasattr(self._focused_node, "_on_blur"):
                self._focused_node._on_blur()  # type: ignore

        # Focus the new node
        self._focused_node = node
        return True

    def release_focus(self, node: Node):
        """Release focus from a node."""
        if self._focused_node is node:
            self._focused_node = None

    def get_focused_node(self) -> Optional[Node]:
        """Get the currently focused node."""
        return self._focused_node

    def clear_focus(self):
        """Clear focus from any focused node."""
        if self._focused_node is not None:
            if hasattr(self._focused_node, "_on_blur"):
                self._focused_node._on_blur()  # type: ignore
            self._focused_node = None

    def mark_dirty(self):
        self.is_dirty = True

    def update(self, dt: float, wheel_scroll: float = 0.0):
        # Clear overlays from previous frame
        clear_overlays()

        # Update animations
        self.animator.update(dt)

        # Handle Input
        runtime = get_runtime()

        # Get mouse position, converting from screen to UI coords if needed
        raw_mx, raw_my = runtime.input.get_mouse_position()

        # Transform mouse position for scaled modes
        if self.config.resize_mode != ResizeMode.RESPONSIVE:
            mx, my = self.scale_transform.inverse_point(raw_mx, raw_my)
        else:
            mx, my = raw_mx, raw_my

        mouse_pos = Vector2(mx, my)
        is_click = runtime.input.is_mouse_button_pressed(MouseButton.LEFT)

        self.is_input_captured = False

        # Handle modal input first (modals block input to main UI)
        if self._modals:
            topmost_modal = self._modals[-1]

            # Check if click is inside the modal bounds
            is_inside_modal = (
                topmost_modal.computed_x
                <= mx
                <= topmost_modal.computed_x + topmost_modal.computed_width
                and topmost_modal.computed_y
                <= my
                <= topmost_modal.computed_y + topmost_modal.computed_height
            )

            consumed = topmost_modal.handle_input(mouse_pos, is_click, wheel_scroll)
            self.is_input_captured = consumed or is_inside_modal

            # Check if clicked outside modal (on backdrop) to close it
            if is_click and not is_inside_modal:
                close_on_backdrop = getattr(topmost_modal, "_close_on_backdrop", True)
                if close_on_backdrop:
                    self.close_modal(topmost_modal)

            # Update cursor for modal content
            self._hovered_node = self._find_node_with_cursor(topmost_modal, mx, my)
            self._apply_cursor()
        elif self.root and self.root.style.visible:
            # Track if a focusable element captured the click
            focused_before = self._focused_node

            consumed = self.root.handle_input(mouse_pos, is_click, wheel_scroll)
            if consumed:
                self.is_input_captured = True

            # If user clicked but focus didn't change to a new focusable element,
            # clear focus (like clicking on empty space in a browser)
            if (
                is_click
                and self._focused_node is focused_before
                and focused_before is not None
            ):
                # Check if the click was outside the focused element
                if focused_before is not None:
                    outside_focused = not (
                        focused_before.computed_x
                        <= mx
                        <= focused_before.computed_x + focused_before.computed_width
                        and focused_before.computed_y
                        <= my
                        <= focused_before.computed_y + focused_before.computed_height
                    )
                    if outside_focused:
                        self.clear_focus()

            # Update cursor based on hovered node
            self._update_cursor(mouse_pos)

        # Update tooltip
        self._update_tooltip(mouse_pos, dt)

        # Check for window resize
        current_w, current_h = runtime.display.get_window_size()

        # Only trigger resize when size actually changes
        # Note: is_window_resized() may return True every frame in some cases,
        # so we rely on actual size comparison
        size_changed = current_w != self.screen_width or current_h != self.screen_height

        if size_changed:
            self.screen_width = current_w
            self.screen_height = current_h

            # Call resize callback if set
            if self.config.on_resize:
                self.config.on_resize(current_w, current_h)

            # Handle debounce
            if self.config.layout_debounce_ms > 0:
                self._resize_debounce_timer = self.config.layout_debounce_ms / 1000.0
                self._pending_resize = True
            else:
                self._handle_resize()

        # Process debounced resize
        if self._pending_resize:
            self._resize_debounce_timer -= dt
            if self._resize_debounce_timer <= 0:
                self._pending_resize = False
                self._handle_resize()

        # Normal dirty check (for non-resize layout changes)
        if self.root and self.is_dirty and not self._pending_resize:
            self._recalculate_layout()

    def _handle_resize(self):
        """Handle window resize based on config mode."""
        if self.config.resize_mode == ResizeMode.RESPONSIVE:
            # Responsive: just recalculate layout with new size
            self.is_dirty = True
        else:
            # Scale modes: calculate transform
            self.scale_transform = calculate_scale_transform(
                self.config,
                self.config.reference_width or self.screen_width,
                self.config.reference_height or self.screen_height,
                self.screen_width,
                self.screen_height,
            )
            # For FIXED mode, we don't need to recalculate layout
            if self.config.resize_mode != ResizeMode.FIXED:
                self.is_dirty = True

    def _recalculate_layout(self):
        """Recalculate UI layout."""
        if not self.root:
            return

        # Call before callback
        if self.config.on_before_layout:
            self.config.on_before_layout()

        # Determine layout size based on mode
        if self.config.resize_mode == ResizeMode.RESPONSIVE:
            layout_w = float(self.screen_width)
            layout_h = float(self.screen_height)
        else:
            # Use reference resolution for scaled modes
            layout_w = float(self.config.reference_width or self.screen_width)
            layout_h = float(self.config.reference_height or self.screen_height)

        self.root.calculate_layout(0, 0, layout_w, layout_h)
        self.is_dirty = False

        # Call after callback
        if self.config.on_after_layout:
            self.config.on_after_layout()

    def render(self):
        """Render the UI tree."""
        if not self.root:
            return

        # Ensure stencil is initialized for components that need it (e.g., Image with border_radius)
        self._ensure_stencil()

        # Render the UI tree
        # Note: SCALE_FIT/SCALE_FILL modes transform mouse coordinates but not render.
        # For proper scaled rendering, use RESPONSIVE mode which recalculates layout.
        self.root.render()

        # Render overlays on top of everything
        for overlay_fn in _overlay_renders:
            overlay_fn()

        # Render modals
        self._render_modals()

        # Render tooltip (always on top)
        self._render_tooltip()

    def get_reference_size(self) -> tuple[int, int]:
        """Get the reference resolution used for layout."""
        return (
            self.config.reference_width or self.screen_width,
            self.config.reference_height or self.screen_height,
        )

    def get_current_size(self) -> tuple[int, int]:
        """Get the current window size."""
        return (self.screen_width, self.screen_height)

    def get_scale_transform(self) -> ScaleTransform:
        """Get the current scale transform (for non-responsive modes)."""
        return self.scale_transform

    def _update_cursor(self, mouse_pos: Vector2):
        """Update cursor based on hovered node."""
        # Find the topmost node under mouse that has a cursor set
        self._hovered_node = self._find_node_with_cursor(
            self.root, mouse_pos.x, mouse_pos.y
        )
        self._apply_cursor()

    def _apply_cursor(self):
        """Apply the cursor based on the currently hovered node."""
        cursor_to_set = CursorType.DEFAULT

        if self._hovered_node and self._hovered_node.style.cursor is not None:
            cursor_to_set = self._hovered_node.style.cursor

        # Only change cursor if different
        if cursor_to_set != self._current_cursor:
            self._current_cursor = cursor_to_set
            runtime = get_runtime()
            runtime.display.set_mouse_cursor(cursor_to_set)

    def _find_node_with_cursor(
        self, node: Optional[Node], mx: float, my: float
    ) -> Optional[Node]:
        """Find the topmost node under mouse position that has a cursor defined."""
        if not node or not node.style.visible:
            return None

        # Check if mouse is over this node
        in_bounds = (
            node.computed_x <= mx < node.computed_x + node.computed_width
            and node.computed_y <= my < node.computed_y + node.computed_height
        )

        if not in_bounds:
            return None

        # Adjust mouse coords for ScrollView children
        child_mx, child_my = mx, my
        from .components.scroll import ScrollView

        if isinstance(node, ScrollView):
            child_my = my - node.scroll_y

        # Check children first (they're on top)
        for child in reversed(node.children):
            result = self._find_node_with_cursor(child, child_mx, child_my)
            if result and result.style.cursor is not None:
                return result

        # Return this node if it has a cursor or is pickable
        if node.style.cursor is not None or node.pickable:
            return node

        return None

    # ==================== MODAL SYSTEM ====================

    def show_modal(
        self, modal: Node, backdrop: bool = True, close_on_backdrop: bool = True
    ):
        """
        Show a modal/overlay on top of everything.

        Args:
            modal: The node to show as modal
            backdrop: Whether to show a dark backdrop behind
            close_on_backdrop: Whether clicking the backdrop closes the modal
        """
        modal._is_modal = True  # type: ignore
        modal._has_backdrop = backdrop  # type: ignore
        modal._close_on_backdrop = close_on_backdrop  # type: ignore
        modal._manager = self
        self._modals.append(modal)

        # First pass: calculate modal's intrinsic size
        modal.calculate_layout(
            0, 0, float(self.screen_width), float(self.screen_height)
        )

        # Second pass: center the modal
        modal_width = modal.computed_width
        modal_height = modal.computed_height
        center_x = (self.screen_width - modal_width) / 2
        center_y = (self.screen_height - modal_height) / 2

        # Recalculate with centered position
        modal.calculate_layout(center_x, center_y, modal_width, modal_height)

    def close_modal(self, modal: Optional[Node] = None):
        """
        Close a modal. If no modal specified, closes the topmost.

        Args:
            modal: Specific modal to close, or None for topmost
        """
        if modal and modal in self._modals:
            self._modals.remove(modal)
        elif self._modals:
            self._modals.pop()

    def close_all_modals(self):
        """Close all open modals."""
        self._modals.clear()

    @property
    def has_modal(self) -> bool:
        """Check if any modal is open."""
        return len(self._modals) > 0

    # ==================== TOOLTIP SYSTEM ====================

    def set_tooltip_delay(self, delay: float):
        """Set the delay before tooltips appear (in seconds)."""
        self._tooltip_delay = delay

    def _update_tooltip(self, mouse_pos: Vector2, dt: float):
        """Update tooltip state based on hovered node."""
        # Check if hovered node has tooltip
        tooltip = None
        if self._hovered_node:
            tooltip = getattr(self._hovered_node, "tooltip", None)

        if tooltip:
            if tooltip != self._tooltip_text:
                # New tooltip, reset timer
                self._tooltip_text = tooltip
                self._tooltip_timer = 0.0
                self._tooltip_visible = False
            else:
                # Same tooltip, increment timer
                self._tooltip_timer += dt
                if self._tooltip_timer >= self._tooltip_delay:
                    self._tooltip_visible = True
                    self._tooltip_pos = mouse_pos
        else:
            # No tooltip
            self._tooltip_text = None
            self._tooltip_timer = 0.0
            self._tooltip_visible = False

    def _render_tooltip(self):
        """Render the current tooltip if visible."""
        if not self._tooltip_visible or not self._tooltip_text:
            return

        runtime = get_runtime()
        from arepy.engine.renderer import Rect

        # Measure text
        font_size = 12
        padding = 8
        text_width = runtime.renderer.measure_text(self._tooltip_text, font_size)

        # Position tooltip near mouse, but keep on screen
        x = self._tooltip_pos.x + 15
        y = self._tooltip_pos.y + 15
        width = text_width + padding * 2
        height = font_size + padding * 2

        # Keep on screen
        if x + width > self.screen_width:
            x = self.screen_width - width - 5
        if y + height > self.screen_height:
            y = self._tooltip_pos.y - height - 5

        # Draw background
        bg_rect = Rect(x, y, int(width), int(height))
        runtime.renderer.draw_rectangle_rounded(bg_rect, 0.3, 8, Color(30, 30, 30, 240))

        # Draw text
        runtime.renderer.draw_text(
            self._tooltip_text,
            (int(x + padding), int(y + padding)),
            font_size,
            Color(255, 255, 255, 255),
        )

    def _render_modals(self):
        """Render all open modals."""
        from arepy.engine.renderer import Rect

        runtime = get_runtime()

        for modal in self._modals:
            # Draw backdrop
            if getattr(modal, "_has_backdrop", True):
                backdrop_rect = Rect(0, 0, self.screen_width, self.screen_height)
                runtime.renderer.draw_rectangle(
                    backdrop_rect,
                    self._modal_backdrop_color,
                )

            # Render modal
            modal.render()
