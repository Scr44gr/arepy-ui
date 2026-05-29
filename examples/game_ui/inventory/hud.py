from __future__ import annotations

from collections.abc import Callable

from arepy_ui import AlignItems, Canvas, Draggable, Easing, FlexDirection, JustifyContent, Node, PositionType, Spacing, Style, Text, UIManager, Unit

from ..fonts import font_for
from ..i18n import Translator
from ..scale import inventory_px
from ..text import fit_text
from ..theme import Palette, mix_color, with_alpha
from .data import InventoryState, build_demo_inventory, total_weight
from .layout import InventoryDropPreview, auto_place_items, build_drop_preview, cell_to_pixel, find_placement, grid_pixel_height, grid_pixel_width, item_pixel_size, move_item
from .render import render_inventory_grid


PANEL_PADDING = inventory_px(14)


class InventoryHUD:
    def __init__(self, translator: Translator, palette: Palette):
        self.i18n = translator
        self.palette = palette
        self.inventory: InventoryState = build_demo_inventory(palette)
        self.placements = auto_place_items(self.inventory)
        self.ui_manager: UIManager | None = None
        self.item_nodes: dict[str, Draggable] = {}
        self.overlay: Node | None = None
        self.panel: Node | None = None
        self.grid_layer: Node | None = None
        self.active_drag_item_id: str | None = None
        self.drag_preview: InventoryDropPreview | None = None
        self.is_open = False
        self.is_animating = False
        self.on_open_started: Callable[[bool], None] | None = None
        self.on_close_started: Callable[[bool], None] | None = None

    def attach_manager(self, manager: UIManager) -> None:
        self.ui_manager = manager

    def set_menu_callbacks(
        self,
        on_open_started: Callable[[bool], None] | None = None,
        on_close_started: Callable[[bool], None] | None = None,
    ) -> None:
        self.on_open_started = on_open_started
        self.on_close_started = on_close_started

    def update(self) -> None:
        if self.panel is None or not self.is_open:
            self.drag_preview = None
            return

        if self.active_drag_item_id is None or self.grid_layer is None:
            self.drag_preview = None
            return

        draggable = self.item_nodes.get(self.active_drag_item_id)
        placement = find_placement(self.placements, self.active_drag_item_id)
        if draggable is None:
            self.drag_preview = None
            return

        self.drag_preview = build_drop_preview(
            self.inventory,
            self.placements,
            placement.item.id,
            placement.item.width,
            placement.item.height,
            draggable.computed_x - self.grid_layer.computed_x,
            draggable.computed_y - self.grid_layer.computed_y,
        )

    def build(self) -> Node:
        self.item_nodes.clear()
        self.drag_preview = None
        self.active_drag_item_id = None
        self.is_open = False
        self.is_animating = False

        grid_width = grid_pixel_width(self.inventory.columns)
        grid_height = grid_pixel_height(self.inventory.rows)

        self.overlay = Node(
            style=Style(
                width=Unit.vw(100),
                height=Unit.vh(100),
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                left=Unit.px(0),
                background_color=None,
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.CENTER,
                align_items=AlignItems.CENTER,
                visible=False,
            )
        )

        self.panel = Node(
            style=Style(
                width=Unit.px(grid_width + PANEL_PADDING * 2),
                height=Unit.auto(),
                background_color=with_alpha(self.palette.surface_soft, 178),
                border_color=with_alpha(self.palette.surface_border, 172),
                border_width=2.0,
                border_radius=float(inventory_px(18)),
                padding=Spacing.all(PANEL_PADDING),
                flex_direction=FlexDirection.COLUMN,
                gap=inventory_px(10),
                opacity=0.0,
                margin=Spacing.all(0),
            )
        )

        header = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.SPACE_BETWEEN,
                align_items=AlignItems.CENTER,
            )
        )
        header.add_child(
            Text(
                self.i18n.text("inventory.title"),
                size=inventory_px(14),
                color=self.palette.text_secondary,
                font_name=font_for(),
            )
        )
        header.add_child(
            Text(
                self.i18n.text(
                    "inventory.weight",
                    current=total_weight(self.inventory),
                    capacity=self.inventory.capacity,
                ),
                size=inventory_px(12),
                color=self.palette.text_muted,
                font_name=font_for(),
            )
        )
        self.panel.add_child(header)

        self.grid_layer = Node(
            style=Style(
                width=Unit.px(grid_width),
                height=Unit.px(grid_height),
            )
        )
        self.grid_layer.add_child(
            Canvas(
                on_render=self._render_inventory,
                width=Unit.px(grid_width),
                height=Unit.px(grid_height),
                state={},
            )
        )

        for placement in self.placements:
            draggable = self._create_item_node(placement)
            self.item_nodes[placement.item.id] = draggable
            self.grid_layer.add_child(draggable)

        self.panel.add_child(self.grid_layer)
        self.overlay.add_child(self.panel)
        return self.overlay

    def toggle_visibility(self) -> None:
        if self.is_animating:
            return
        if self.is_open:
            self.hide(animated=True)
            return
        self.show(animated=True)

    def show(self, animated: bool = True) -> None:
        if self.overlay is None or self.panel is None or self.is_open or self.is_animating:
            return

        if self.on_open_started is not None:
            self.on_open_started(animated)

        self.is_open = True
        self.is_animating = True
        self.overlay.style.visible = True
        self.panel.style.opacity = 0.0
        self.panel.style.margin.top = Unit.px(inventory_px(20))

        if self.ui_manager is None or not animated:
            self.panel.style.opacity = 1.0
            self.panel.style.margin.top = Unit.px(0)
            self._finish_open()
            return

        self.ui_manager.animator.create().to(
            self.panel.style,
            "opacity",
            1.0,
            0.20,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().to(
            self.panel.style,
            "margin.top",
            0,
            0.28,
            Easing.EASE_OUT_BACK,
        ).start()
        self.ui_manager.animator.create().wait(0.30).call(self._finish_open).start()

    def hide(self, animated: bool = True) -> None:
        if self.overlay is None or self.panel is None or not self.is_open or self.is_animating:
            return
        if self.active_drag_item_id is not None:
            return

        if self.on_close_started is not None:
            self.on_close_started(animated)

        self.is_open = False
        self.is_animating = True

        if self.ui_manager is None or not animated:
            self._finish_close()
            return

        self.ui_manager.animator.create().to(
            self.panel.style,
            "opacity",
            0.0,
            0.18,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().to(
            self.panel.style,
            "margin.top",
            inventory_px(20),
            0.20,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().wait(0.22).call(self._finish_close).start()

    def _render_inventory(self, renderer, rect, _state: dict) -> None:
        render_inventory_grid(
            renderer,
            rect,
            self.inventory,
            self.palette,
            self.drag_preview,
        )

    def _create_item_node(self, placement) -> Draggable:
        item = placement.item
        width, height = item_pixel_size(item.width, item.height)
        left, top = cell_to_pixel(placement.column, placement.row)

        content = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                background_color=with_alpha(mix_color(item.accent, self.palette.surface_soft, 0.55), 242),
                border_color=with_alpha(mix_color(item.accent, self.palette.white, 0.12), 205),
                border_width=2.0,
                border_radius=float(inventory_px(10)),
                padding=Spacing.all(inventory_px(6)),
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.SPACE_BETWEEN,
            )
        )
        content.add_child(
            Text(
                fit_text(
                    self.i18n.text(item.name_key),
                    width - inventory_px(12),
                    inventory_px(11),
                    font_for(),
                ),
                size=inventory_px(11),
                color=self.palette.text_primary,
                font_name=font_for(),
            )
        )
        content.add_child(
            Text(
                f"{item.weight:.1f} kg",
                size=inventory_px(10),
                color=self.palette.text_secondary,
                font_name=font_for(),
            )
        )

        draggable = Draggable(
            content=content,
            data={"item_id": item.id},
            style=Style(
                width=Unit.px(width),
                height=Unit.px(height),
                position=PositionType.ABSOLUTE,
                left=Unit.px(left),
                top=Unit.px(top),
            ),
            return_on_fail=False,
            drag_opacity=0.90,
        )
        draggable.on_drag_start = lambda item_id=item.id: self._begin_drag(item_id)
        draggable.on_drag_end = (
            lambda _dropped, _target, item_id=item.id, node=draggable: self._finish_drag(item_id, node)
        )
        return draggable

    def _begin_drag(self, item_id: str) -> None:
        self.active_drag_item_id = item_id
        self.drag_preview = None

    def _finish_drag(self, item_id: str, draggable: Draggable) -> None:
        placement = find_placement(self.placements, item_id)
        preview = build_drop_preview(
            self.inventory,
            self.placements,
            placement.item.id,
            placement.item.width,
            placement.item.height,
            draggable.computed_x - (self.grid_layer.computed_x if self.grid_layer else 0),
            draggable.computed_y - (self.grid_layer.computed_y if self.grid_layer else 0),
        )

        if preview is not None and preview.valid:
            self.placements = move_item(self.placements, item_id, preview.column, preview.row)
            self._sync_item_positions()
        else:
            draggable._animate_return()

        self.active_drag_item_id = None
        self.drag_preview = None

    def _sync_item_positions(self) -> None:
        for placement in self.placements:
            draggable = self.item_nodes.get(placement.item.id)
            if draggable is None:
                continue
            left, top = cell_to_pixel(placement.column, placement.row)
            draggable.style.left = Unit.px(left)
            draggable.style.top = Unit.px(top)

    def _finish_open(self) -> None:
        self.is_animating = False

    def _finish_close(self) -> None:
        if self.overlay is not None:
            self.overlay.style.visible = False
        if self.panel is not None:
            self.panel.style.opacity = 0.0
            self.panel.style.margin.top = Unit.px(0)
        self.is_animating = False
