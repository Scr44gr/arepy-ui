from dataclasses import dataclass
from typing import Optional, cast

from arepy.engine.renderer import Rect

from .components.scroll import ScrollView
from .components.text import Text
from .core.node import Node
from .core.style import Spacing
from .core.types import Color, FlexDirection, Unit
from .registry import get_registry
from .runtime import get_runtime


@dataclass
class DebugFrameNode:
    node: Node
    depth: int
    rect: tuple[int, int, int, int]
    visible_rect: Optional[tuple[int, int, int, int]]


class UIDebugger:
    """Visual debugger for UI layout with detailed component inspection."""

    PANEL_BG = Color(20, 20, 25, 240)
    PANEL_BORDER = Color(80, 80, 90, 255)
    HEADER_BG = Color(60, 60, 70, 255)

    ACCENT_BLUE = Color(100, 150, 255, 255)
    ACCENT_GREEN = Color(100, 220, 150, 255)
    ACCENT_YELLOW = Color(255, 220, 100, 255)
    ACCENT_ORANGE = Color(255, 160, 80, 255)
    ACCENT_PURPLE = Color(180, 130, 255, 255)

    TEXT_PRIMARY = Color(240, 240, 245, 255)
    TEXT_SECONDARY = Color(160, 160, 170, 255)
    TEXT_DIM = Color(100, 100, 110, 255)

    DEFAULT_COLOR = (150, 150, 150)

    def __init__(self):
        self.enabled = False
        self.show_bounds = True
        self.show_padding = False
        self.show_info = True
        self.show_tree = False
        self.toggle_hotkey_label = "F3"
        self.bounds_hotkey_label = "F4"
        self.padding_hotkey_label = "F5"
        self.tree_hotkey_label = "F6"
        self.hovered_node: Optional[Node] = None
        self._font_size = 11
        self._line_height = 14
        self._tree_scroll = 0
        self._frame_nodes: list[DebugFrameNode] = []
        self._frame_index: dict[Node, DebugFrameNode] = {}
        self._color_cache: dict[str, Color] = {}

    def set_hotkey_labels(
        self,
        toggle: Optional[str] = None,
        bounds: Optional[str] = None,
        padding: Optional[str] = None,
        tree: Optional[str] = None,
    ):
        if toggle is not None:
            self.toggle_hotkey_label = toggle
        if bounds is not None:
            self.bounds_hotkey_label = bounds
        if padding is not None:
            self.padding_hotkey_label = padding
        if tree is not None:
            self.tree_hotkey_label = tree

    def toggle(self):
        """Toggle debug overlay on/off."""
        self.enabled = not self.enabled

    def toggle_tree(self):
        """Toggle tree view on/off."""
        self.show_tree = not self.show_tree

    def toggle_bounds(self):
        """Toggle bounds visualization."""
        self.show_bounds = not self.show_bounds

    def toggle_padding(self):
        """Toggle padding visualization."""
        self.show_padding = not self.show_padding

    def render(self, root: Optional[Node]):
        """Render debug overlay for the UI tree."""
        if not self.enabled or not root:
            return

        runtime = get_runtime()
        mx, my = runtime.input.get_mouse_position()
        self._build_frame(root)
        self.hovered_node = self._find_node_at(mx, my)

        if self.show_bounds:
            self._render_node_debug(runtime)

        if self.hovered_node and self.show_info:
            self._render_node_info(self.hovered_node, mx, my)

        if self.show_tree:
            self._render_tree_view(root)

        self._render_toolbar()

    def _get_component_color(self, node: Node) -> Color:
        """Get color based on component type."""

        class_name = node.__class__.__name__
        cached = self._color_cache.get(class_name)
        if cached is not None:
            return cached

        meta = get_registry().get(class_name)
        if meta:
            color = meta.get_debug_color(180)
        else:
            color = Color(150, 150, 150, 180)

        self._color_cache[class_name] = color
        return color

    def _build_frame(self, root: Node) -> None:
        self._frame_nodes = []
        self._frame_index = {}
        self._collect_frame_nodes(root, depth=0)

    def _collect_frame_nodes(
        self,
        node: Node,
        depth: int,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        clip_rect: Optional[tuple[float, float, float, float]] = None,
    ) -> None:
        if not node.style.visible:
            return

        rect = (
            node.computed_x + offset_x,
            node.computed_y + offset_y,
            node.computed_width,
            node.computed_height,
        )
        visible_rect = self._intersect_rect(rect, clip_rect)

        frame_node = DebugFrameNode(
            node=node,
            depth=depth,
            rect=self._rect_to_int_tuple(rect),
            visible_rect=(
                self._rect_to_int_tuple(visible_rect)
                if visible_rect is not None
                else None
            ),
        )
        self._frame_nodes.append(frame_node)
        self._frame_index[node] = frame_node

        next_clip = clip_rect
        scroll_clip = self._intersect_rect(rect, clip_rect)

        for child in node.children:
            child_offset_x = offset_x
            child_offset_y = offset_y
            child_clip = next_clip

            if isinstance(node, ScrollView) and child is node.content:
                child_offset_y += node.scroll_y
                child_clip = scroll_clip

            self._collect_frame_nodes(
                child,
                depth + 1,
                child_offset_x,
                child_offset_y,
                child_clip,
            )

    def _intersect_rect(
        self,
        rect: tuple[float, float, float, float],
        clip_rect: Optional[tuple[float, float, float, float]],
    ) -> Optional[tuple[float, float, float, float]]:
        x, y, w, h = rect
        if w <= 0 or h <= 0:
            return None

        if clip_rect is None:
            return rect

        clip_x, clip_y, clip_w, clip_h = clip_rect
        left = max(x, clip_x)
        top = max(y, clip_y)
        right = min(x + w, clip_x + clip_w)
        bottom = min(y + h, clip_y + clip_h)

        width = right - left
        height = bottom - top
        if width <= 0 or height <= 0:
            return None

        return (left, top, width, height)

    def _rect_to_int_tuple(
        self, rect: tuple[float, float, float, float]
    ) -> tuple[int, int, int, int]:
        x, y, w, h = rect
        return (int(x), int(y), int(w), int(h))

    def _find_node_at(self, x: float, y: float) -> Optional[Node]:
        """Find the deepest visible node at the given screen position."""
        for frame_node in reversed(self._frame_nodes):
            visible_rect = frame_node.visible_rect
            if visible_rect is None:
                continue

            rect_x, rect_y, rect_w, rect_h = visible_rect
            if rect_x <= x < rect_x + rect_w and rect_y <= y < rect_y + rect_h:
                return frame_node.node

        return None

    def _render_node_debug(self, runtime):
        """Render debug bounds for the current visual frame."""
        for frame_node in self._frame_nodes:
            visible_rect = frame_node.visible_rect
            if visible_rect is None:
                continue

            node = frame_node.node
            x, y, w, h = visible_rect
            if w <= 0 or h <= 0:
                continue

            color = self._get_component_color(node)
            border_color = Color(color.r, color.g, color.b, 200)

            if self.show_padding and node.style.padding:
                self._render_padding(node, runtime, frame_node)

            runtime.renderer.draw_rectangle_lines_ex(
                Rect(x, y, w, h), 1, border_color
            )  # type: ignore

            if node == self.hovered_node:
                highlight = Color(255, 255, 100, 50)
                runtime.renderer.draw_rectangle(Rect(x, y, w, h), highlight)  # type: ignore
                runtime.renderer.draw_rectangle_lines_ex(
                    Rect(x, y, w, h),
                    2,
                    self.ACCENT_YELLOW,  # type: ignore
                )

    def _render_padding(self, node: Node, runtime, frame_node: DebugFrameNode):
        """Render padding visualization."""
        x, y, w, h = frame_node.rect

        p = node.style.padding
        if not p:
            return

        pt = int(p.top.value) if p.top else 0
        pr = int(p.right.value) if p.right else 0
        pb = int(p.bottom.value) if p.bottom else 0
        pl = int(p.left.value) if p.left else 0

        padding_color = Color(100, 200, 100, 60)

        if pt > 0:
            runtime.renderer.draw_rectangle(Rect(x, y, w, pt), padding_color)
        if pb > 0:
            runtime.renderer.draw_rectangle(Rect(x, y + h - pb, w, pb), padding_color)
        if pl > 0:
            runtime.renderer.draw_rectangle(
                Rect(x, y + pt, pl, h - pt - pb), padding_color
            )
        if pr > 0:
            runtime.renderer.draw_rectangle(
                Rect(x + w - pr, y + pt, pr, h - pt - pb), padding_color
            )

    def _render_node_info(self, node: Node, mouse_x: float, mouse_y: float):
        """Render detailed info panel for a node."""
        runtime = get_runtime()
        class_name = node.__class__.__name__
        frame_node = self._frame_index.get(node)

        sections = []

        header = [f"> {class_name}"]
        if hasattr(node, "id") and node.id:
            header.append(f"  #{node.id}")
        sections.append(("header", header))

        layout_info = [
            f"Layout: ({node.computed_x:.0f}, {node.computed_y:.0f})",
            f"Size: {node.computed_width:.0f} x {node.computed_height:.0f}",
        ]
        if frame_node is not None:
            screen_x, screen_y, _, _ = frame_node.rect
            layout_info.insert(0, f"Screen: ({screen_x}, {screen_y})")
            if (
                frame_node.visible_rect is not None
                and frame_node.visible_rect != frame_node.rect
            ):
                _, _, visible_w, visible_h = frame_node.visible_rect
                layout_info.append(f"Visible: {visible_w} x {visible_h}")
        sections.append(("Layout", layout_info))

        style_info = []
        if node.style.width:
            style_info.append(f"width: {self._format_unit(node.style.width)}")
        if node.style.height:
            style_info.append(f"height: {self._format_unit(node.style.height)}")
        if node.style.flex_direction:
            dir_name = (
                "row" if node.style.flex_direction == FlexDirection.ROW else "column"
            )
            style_info.append(f"flex: {dir_name}")
        if node.style.gap:
            style_info.append(f"gap: {node.style.gap}")
        if node.style.padding:
            style_info.append(f"padding: {self._format_spacing(node.style.padding)}")
        if style_info:
            sections.append(("Style", style_info))

        props_info = self._get_component_props(node)
        if props_info:
            sections.append(("Props", props_info))

        tree_info = []
        if node.parent:
            tree_info.append(f"Parent: {node.parent.__class__.__name__}")
        if node.children:
            tree_info.append(f"Children: {len(node.children)}")
        if tree_info:
            sections.append(("Tree", tree_info))

        self._render_info_panel(sections, mouse_x, mouse_y, runtime)

    def _get_component_props(self, node: Node) -> list:
        """Get component-specific properties."""
        props = []
        class_name = node.__class__.__name__

        if class_name == "Text":
            text_node = cast(Text, node)
            text = getattr(text_node, "_text", None)
            if text is not None:
                preview = text[:20] + "..." if len(text) > 20 else text
                props.append(f'text: "{preview}"')
            size = getattr(text_node, "_size", None)
            if size is not None:
                props.append(f"size: {size}")

        elif class_name == "Button":
            text = getattr(node, "_text", None)
            if text is not None:
                props.append(f'label: "{text}"')

        elif class_name == "TextInput":
            text = getattr(node, "_text", None) or ""
            if text:
                preview = text[:15] + "..." if len(text) > 15 else text
                props.append(f'value: "{preview}"')
            placeholder = getattr(node, "_placeholder", None)
            if placeholder:
                props.append(f'placeholder: "{placeholder[:15]}"')

        elif class_name == "Slider":
            value = getattr(node, "_value", None)
            if value is not None:
                props.append(f"value: {value:.2f}")
            min_val = getattr(node, "_min", None)
            max_val = getattr(node, "_max", None)
            if min_val is not None and max_val is not None:
                props.append(f"range: [{min_val}, {max_val}]")

        elif class_name == "Checkbox":
            checked = getattr(node, "_checked", None)
            if checked is not None:
                props.append(f"checked: {checked}")

        elif class_name == "Image":
            src = getattr(node, "source", None)
            if src:
                if len(src) > 25:
                    src = "..." + src[-22:]
                props.append(f"src: {src}")

        elif class_name == "Video":
            state = getattr(node, "_state", None)
            if state is not None:
                props.append(f"state: {self._format_debug_value(state)}")
            duration = getattr(node, "_duration", None)
            if duration is not None:
                props.append(f"duration: {duration:.1f}s")

        elif class_name == "ColorPicker":
            color = getattr(node, "color", None)
            if color is not None:
                props.append(f"color: rgba({color.r},{color.g},{color.b},{color.a})")

        elif class_name == "Select":
            options = getattr(node, "_options", None)
            if options is not None:
                props.append(f"options: {len(options)}")
            selected = getattr(node, "_selected_index", None)
            if selected is not None:
                props.append(f"selected: {selected}")

        return props

    def _format_debug_value(self, value) -> str:
        """Format debug values safely for display."""
        if hasattr(value, "name"):
            return str(value.name)
        return str(value)

    def _measure_text_width(self, runtime, text: str, font_size: int) -> int:
        try:
            return int(runtime.renderer.measure_text(text, font_size))
        except Exception:
            return len(text) * 7

    def _format_unit(self, unit: Unit) -> str:
        """Format a Unit value for display."""
        if unit.type.name == "PX":
            return f"{unit.value:.0f}px"
        elif unit.type.name == "PERCENT":
            return f"{unit.value:.0f}%"
        elif unit.type.name == "AUTO":
            return "auto"
        return str(unit.value)

    def _format_spacing(self, spacing: Spacing) -> str:
        """Format Spacing for display."""
        t = self._format_unit(spacing.top) if spacing.top else "0"
        r = self._format_unit(spacing.right) if spacing.right else "0"
        b = self._format_unit(spacing.bottom) if spacing.bottom else "0"
        l = self._format_unit(spacing.left) if spacing.left else "0"

        if t == r == b == l:
            return t
        if t == b and l == r:
            return f"{t} {l}"
        return f"{t} {r} {b} {l}"

    def _render_info_panel(
        self, sections: list, mouse_x: float, mouse_y: float, runtime
    ):
        """Render the info panel with sections."""
        padding = 8
        section_gap = 6

        max_width = 0
        total_height = padding

        for section_type, lines in sections:
            if section_type == "header":
                total_height += len(lines) * (self._line_height + 2)
            else:
                total_height += self._line_height + 2
                total_height += len(lines) * self._line_height
                total_height += section_gap

            for line in lines:
                text_width = self._measure_text_width(runtime, line, self._font_size)
                max_width = max(max_width, text_width)

        panel_w = max_width + padding * 2 + 10
        panel_h = total_height + padding

        panel_x = int(mouse_x + 20)
        panel_y = int(mouse_y + 20)

        screen_w, screen_h = runtime.display.get_window_size()

        if panel_x + panel_w > screen_w - 10:
            panel_x = int(mouse_x - panel_w - 20)
        if panel_y + panel_h > screen_h - 10:
            panel_y = int(mouse_y - panel_h - 20)

        panel_x = max(10, panel_x)
        panel_y = max(10, panel_y)

        runtime.renderer.draw_rectangle(
            Rect(panel_x, panel_y, panel_w, panel_h), self.PANEL_BG
        )
        runtime.renderer.draw_rectangle_lines_ex(
            Rect(panel_x, panel_y, panel_w, panel_h), 1, self.PANEL_BORDER
        )

        y_offset = panel_y + padding

        for section_type, lines in sections:
            if section_type == "header":
                for line in lines:
                    color = (
                        self.ACCENT_BLUE
                        if line.startswith(">")
                        else self.TEXT_SECONDARY
                    )
                    runtime.renderer.draw_text(
                        line,
                        (panel_x + padding, y_offset),
                        self._font_size + 1,
                        color,
                    )
                    y_offset += self._line_height + 2
            else:
                runtime.renderer.draw_text(
                    section_type,
                    (panel_x + padding, y_offset),
                    self._font_size,
                    self.TEXT_DIM,
                )
                y_offset += self._line_height + 2

                for line in lines:
                    runtime.renderer.draw_text(
                        f"  {line}",
                        (panel_x + padding, y_offset),
                        self._font_size,
                        self.TEXT_PRIMARY,
                    )
                    y_offset += self._line_height

                y_offset += section_gap

    def _render_tree_view(self, root: Node):
        """Render a tree view of the component hierarchy."""
        runtime = get_runtime()
        screen_w, screen_h = runtime.display.get_window_size()

        panel_w = 220
        panel_h = screen_h - 80
        panel_x = screen_w - panel_w - 10
        panel_y = 40

        runtime.renderer.draw_rectangle(
            Rect(panel_x, panel_y, panel_w, panel_h),
            self.PANEL_BG,  # type: ignore
        )
        runtime.renderer.draw_rectangle_lines_ex(
            Rect(panel_x, panel_y, panel_w, panel_h),
            1,
            self.PANEL_BORDER,  # type: ignore
        )

        runtime.renderer.draw_rectangle(
            Rect(panel_x, panel_y, panel_w, 24),
            self.HEADER_BG,  # type: ignore
        )
        runtime.renderer.draw_text(
            "Component Tree",
            (panel_x + 8, panel_y + 5),
            self._font_size,
            self.TEXT_PRIMARY,  # type: ignore
        )

        self._clamp_tree_scroll(panel_h)

        start_y = panel_y + 32 - self._tree_scroll
        for index, frame_node in enumerate(self._frame_nodes):
            row_y = start_y + index * self._line_height
            if row_y < panel_y + 26:
                continue
            if row_y > panel_y + panel_h - self._line_height:
                break
            self._render_tree_row(frame_node, panel_x + 8, row_y, panel_w - 16, runtime)

    def _clamp_tree_scroll(self, panel_h: int) -> None:
        content_height = len(self._frame_nodes) * self._line_height
        max_scroll = max(0, content_height - max(0, panel_h - 40))
        self._tree_scroll = max(0, min(self._tree_scroll, max_scroll))

    def _render_tree_row(
        self, frame_node: DebugFrameNode, x: int, y: int, max_width: int, runtime
    ) -> None:
        node = frame_node.node
        class_name = node.__class__.__name__
        indent = frame_node.depth * 12

        is_hovered = node == self.hovered_node

        color = self._get_component_color(node)
        marker_color = Color(color.r, color.g, color.b, 255)

        if is_hovered:
            runtime.renderer.draw_rectangle(
                Rect(x - 4, y - 1, max_width, self._line_height + 2),
                Color(255, 255, 100, 40),
            )

        runtime.renderer.draw_rectangle(Rect(x + indent, y + 3, 8, 8), marker_color)

        label = class_name
        if hasattr(node, "id") and node.id:
            label += f" #{node.id}"
        if len(label) > 22:
            label = label[:19] + "..."

        text_color = self.ACCENT_YELLOW if is_hovered else self.TEXT_PRIMARY
        runtime.renderer.draw_text(
            label,
            (x + indent + 12, y),
            self._font_size - 1,
            text_color,
        )

    def _render_toolbar(self):
        """Render toolbar at top of screen."""
        runtime = get_runtime()
        screen_w, _ = runtime.display.get_window_size()

        bar_h = 28
        runtime.renderer.draw_rectangle(
            Rect(0, 0, screen_w, bar_h),
            Color(30, 30, 35, 230),  # type: ignore
        )

        items = [
            (f"[{self.toggle_hotkey_label}] Debug", self.enabled, self.ACCENT_GREEN),
            (
                f"[{self.bounds_hotkey_label}] Bounds",
                self.show_bounds,
                self.ACCENT_BLUE,
            ),
            (
                f"[{self.padding_hotkey_label}] Padding",
                self.show_padding,
                self.ACCENT_PURPLE,
            ),
            (f"[{self.tree_hotkey_label}] Tree", self.show_tree, self.ACCENT_ORANGE),
        ]

        x = 10
        for text, active, color in items:
            text_color = color if active else self.TEXT_DIM
            runtime.renderer.draw_text(text, (x, 7), self._font_size, text_color)  # type: ignore
            x += len(text) * 7 + 20

        if self.hovered_node:
            info = f"Hover: {self.hovered_node.__class__.__name__} | Nodes: {len(self._frame_nodes)}"
            if hasattr(self.hovered_node, "id") and self.hovered_node.id:
                info += f" #{self.hovered_node.id}"
        else:
            info = f"Nodes: {len(self._frame_nodes)}"

        info_width = self._measure_text_width(runtime, info, self._font_size)
        runtime.renderer.draw_text(
            info,
            (screen_w - info_width - 10, 7),
            self._font_size,
            self.ACCENT_YELLOW if self.hovered_node else self.TEXT_SECONDARY,  # type: ignore
        )
