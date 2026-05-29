from __future__ import annotations

from arepy.engine.time import Time

from arepy_ui import AlignItems, FlexDirection, Node, PositionType, Spacing, Style, UIManager, Unit
from arepy_ui.runtime import Key, get_runtime

from .i18n import Translator
from .inventory import InventoryHUD
from .menu_motion import MenuLayerMotion
from .pause_menu import PauseMenuHUD
from .scale import hud_px
from .slot import SlotHUD
from .status import StatusHUD
from .theme import Palette
from .vitals import VitalsHUD


LEFT_COLUMN_WIDTH = hud_px(320)
RIGHT_COLUMN_WIDTH = hud_px(214)


class GameUIScreen:
    def __init__(self, translator: Translator, palette: Palette):
        self.slot_hud = SlotHUD(translator, palette)
        self.vitals_hud = VitalsHUD(translator, palette)
        self.inventory_hud = InventoryHUD(translator, palette)
        self.pause_menu = PauseMenuHUD(translator, palette)
        self.status_hud = StatusHUD(palette)
        self.menu_motion = MenuLayerMotion()
        self.inventory_hud.set_menu_callbacks(
            on_open_started=self.menu_motion.menu_opened,
            on_close_started=self.menu_motion.menu_closed,
        )
        self.pause_menu.set_menu_callbacks(
            on_open_started=self.menu_motion.menu_opened,
            on_close_started=self.menu_motion.menu_closed,
        )

    def attach_manager(self, manager: UIManager) -> None:
        self.slot_hud.attach_manager(manager)
        self.inventory_hud.attach_manager(manager)
        self.pause_menu.attach_manager(manager)
        self.menu_motion.attach_manager(manager)

    def build(self) -> Node:
        root = Node(
            style=Style(
                width=Unit.vw(100),
                height=Unit.vh(100),
                background_color=None,
                flex_direction=FlexDirection.COLUMN,
                padding=Spacing(
                    top=Unit.px(hud_px(22)),
                    right=Unit.px(hud_px(22)),
                    bottom=Unit.px(0),
                    left=Unit.px(hud_px(22)),
                ),
                align_items=AlignItems.STRETCH,
            )
        )

        main_layer = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                left=Unit.px(0),
            )
        )
        self.menu_motion.bind_layer(main_layer)

        left_column = Node(
            style=Style(
                width=Unit.px(LEFT_COLUMN_WIDTH),
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                left=Unit.px(0),
                align_items=AlignItems.START,
                height=Unit.auto(),
            )
        )
        left_column.add_child(self.vitals_hud.build())

        center_column = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                left=Unit.px(0),
                flex_direction=FlexDirection.COLUMN,
                align_items=AlignItems.CENTER,
            )
        )
        center_column.add_child(self.slot_hud.build())

        right_column = Node(
            style=Style(
                width=Unit.px(RIGHT_COLUMN_WIDTH),
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                right=Unit.px(0),
                height=Unit.auto(),
                align_items=AlignItems.END,
            )
        )
        right_column.add_child(self.status_hud.build())

        main_layer.add_child(left_column)
        main_layer.add_child(center_column)
        main_layer.add_child(right_column)
        root.add_child(main_layer)
        root.add_child(self.inventory_hud.build())
        root.add_child(self.pause_menu.build())
        return root

    def update(self, time: Time) -> None:
        runtime = get_runtime()

        if runtime.input.is_key_pressed(Key.P) or runtime.input.is_key_pressed(Key.PAUSE):
            if self.pause_menu.is_open:
                self.pause_menu.hide(animated=True)
            else:
                if self.inventory_hud.is_open:
                    self.inventory_hud.hide(animated=False)
                self.pause_menu.show(animated=True)

        if not self.pause_menu.blocks_world_update and runtime.input.is_key_pressed(Key.I):
            self.inventory_hud.toggle_visibility()

        if self.pause_menu.blocks_world_update:
            return

        self.slot_hud.update(time)
        self.status_hud.update(time)
        self.inventory_hud.update()

    def play_intro(self) -> None:
        self.slot_hud.play_intro()
