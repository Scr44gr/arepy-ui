from __future__ import annotations

from collections.abc import Callable

from arepy_ui import AlignItems, Button, Easing, FlexDirection, JustifyContent, Node, PositionType, Spacing, Style, UIManager, Unit

from ..fonts import font_for
from ..i18n import Translator
from ..scale import inventory_px
from ..theme import Palette, mix_color, with_alpha


PANEL_WIDTH = inventory_px(520)
PANEL_PADDING = inventory_px(16)
OPTION_TAB_WIDTH = inventory_px(116)
TAB_HEIGHT = inventory_px(42)
ACTION_BUTTON_HEIGHT = inventory_px(46)
CONTENT_EMPTY_HEIGHT = inventory_px(220)
BACK_BUTTON_WIDTH = inventory_px(104)


class PauseMenuHUD:
    def __init__(self, translator: Translator, palette: Palette):
        self.i18n = translator
        self.palette = palette
        self.ui_manager: UIManager | None = None
        self.overlay: Node | None = None
        self.panel: Node | None = None
        self.body_host: Node | None = None
        self.option_tab_buttons: dict[str, Button] = {}
        self.current_view = "menu"
        self.current_option_tab = "controls"
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

    @property
    def blocks_world_update(self) -> bool:
        return self.is_open or self.is_animating

    def build(self) -> Node:
        self.option_tab_buttons.clear()
        self.current_view = "menu"
        self.current_option_tab = "controls"
        self.is_open = False
        self.is_animating = False

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
                width=Unit.px(PANEL_WIDTH),
                height=Unit.auto(),
                background_color=with_alpha(self.palette.surface_soft, 220),
                border_color=with_alpha(self.palette.surface_border, 188),
                border_width=2.0,
                border_radius=float(inventory_px(18)),
                padding=Spacing.all(PANEL_PADDING),
                flex_direction=FlexDirection.COLUMN,
                gap=inventory_px(12),
                opacity=0.0,
                margin=Spacing.all(0),
            )
        )

        self.body_host = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
            )
        )
        self.panel.add_child(self.body_host)
        self.overlay.add_child(self.panel)

        self._rebuild_body()
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

        self.current_view = "menu"
        self.current_option_tab = "controls"
        self._rebuild_body()

        if self.on_open_started is not None:
            self.on_open_started(animated)

        self.is_open = True
        self.is_animating = True
        self.overlay.style.visible = True
        self.panel.style.opacity = 0.0
        self.panel.style.margin.top = Unit.px(inventory_px(16))

        if self.ui_manager is None or not animated:
            self.panel.style.opacity = 1.0
            self.panel.style.margin.top = Unit.px(0)
            self._finish_open()
            return

        self.ui_manager.animator.create().to(
            self.panel.style,
            "opacity",
            1.0,
            0.18,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().to(
            self.panel.style,
            "margin.top",
            0,
            0.20,
            Easing.EASE_OUT_BACK,
        ).start()
        self.ui_manager.animator.create().wait(0.22).call(self._finish_open).start()

    def hide(self, animated: bool = True) -> None:
        if self.overlay is None or self.panel is None or not self.is_open or self.is_animating:
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
            0.16,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().to(
            self.panel.style,
            "margin.top",
            inventory_px(16),
            0.18,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().wait(0.20).call(self._finish_close).start()

    def _build_main_menu(self) -> Node:
        column = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                gap=inventory_px(8),
            )
        )

        action_keys = (
            "pause.resume",
            "pause.save",
            "pause.load",
            "pause.options",
            "pause.exit_main_menu",
            "pause.exit_game",
        )
        for action_key in action_keys:
            column.add_child(self._create_action_button(action_key))
        return column

    def _build_options_menu(self) -> Node:
        column = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                gap=inventory_px(10),
            )
        )

        header_row = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.START,
                align_items=AlignItems.CENTER,
            )
        )
        header_row.add_child(self._create_back_button())

        tabs_row = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.ROW,
                gap=inventory_px(8),
                align_items=AlignItems.CENTER,
            )
        )
        for option_tab in ("controls", "video", "sound", "accessibility"):
            tabs_row.add_child(self._create_option_tab_button(option_tab))

        empty_body = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.px(CONTENT_EMPTY_HEIGHT),
            )
        )

        column.add_child(header_row)
        column.add_child(tabs_row)
        column.add_child(empty_body)
        return column

    def _rebuild_body(self) -> None:
        if self.body_host is None:
            return

        self.body_host.children.clear()
        if self.current_view == "menu":
            self.body_host.add_child(self._build_main_menu())
        else:
            self.body_host.add_child(self._build_options_menu())

        self._refresh_option_tabs()

    def _create_option_tab_button(self, tab_key: str) -> Button:
        button = Button(
            text=self.i18n.text(f"pause.options.tab.{tab_key}"),
            on_click=lambda key=tab_key: self._select_option_tab(key),
            width=Unit.px(OPTION_TAB_WIDTH),
            height=Unit.px(TAB_HEIGHT),
            bg_color=with_alpha(self.palette.surface, 226),
            text_color=self.palette.text_primary,
            font_size=inventory_px(12),
            border_radius=float(inventory_px(14)),
            font_name=font_for(),
        )
        button.style.padding = Spacing.symmetric(inventory_px(7), inventory_px(10))
        self._bind_tab_interactions(button, lambda: self.current_option_tab == tab_key)
        self.option_tab_buttons[tab_key] = button
        return button

    def _create_back_button(self) -> Button:
        button = Button(
            text=self.i18n.text("pause.options.back"),
            on_click=self._show_main_menu,
            width=Unit.px(BACK_BUTTON_WIDTH),
            height=Unit.px(TAB_HEIGHT),
            bg_color=with_alpha(self.palette.surface, 224),
            text_color=self.palette.text_primary,
            font_size=inventory_px(12),
            border_radius=float(inventory_px(14)),
            font_name=font_for(),
        )
        button.style.border_width = 2.0
        button.style.border_color = with_alpha(self.palette.surface_border, 178)
        button.style.padding = Spacing.symmetric(inventory_px(7), inventory_px(10))
        return button

    def _create_action_button(self, action_key: str) -> Button:
        button = Button(
            text=self.i18n.text(action_key),
            on_click=lambda key=action_key: self._run_action(key),
            width=Unit.percent(100),
            height=Unit.px(ACTION_BUTTON_HEIGHT),
            bg_color=with_alpha(self.palette.surface, 226),
            text_color=self.palette.text_primary,
            font_size=inventory_px(14),
            border_radius=float(inventory_px(14)),
            font_name=font_for(),
        )
        button.style.border_width = 2.0
        button.style.border_color = with_alpha(self.palette.surface_border, 175)
        button.style.padding = Spacing.symmetric(inventory_px(10), inventory_px(14))
        return button

    def _bind_tab_interactions(self, button: Button, is_active: Callable[[], bool]) -> None:
        base_enter = button.on_hover_enter
        base_exit = button.on_hover_exit

        def on_enter() -> None:
            if base_enter is not None:
                base_enter()
            self._apply_tab_style(button, active=is_active(), focused=True)

        def on_exit() -> None:
            if base_exit is not None:
                base_exit()
            self._apply_tab_style(button, active=is_active(), focused=False)

        button.on_hover_enter = on_enter
        button.on_hover_exit = on_exit
        self._apply_tab_style(button, active=is_active(), focused=False)

    def _apply_tab_style(self, button: Button, active: bool, focused: bool) -> None:
        highlight = active or focused
        base_color = with_alpha(
            mix_color(self.palette.surface, self.palette.brass_soft, 0.10 if highlight else 0.03),
            236 if highlight else 226,
        )
        border_color = with_alpha(
            self.palette.brass_soft if highlight else self.palette.surface_border,
            225 if highlight else 178,
        )
        button.base_color = base_color
        button.hover_color = with_alpha(mix_color(base_color, self.palette.brass_soft, 0.12), 246)
        button.pressed_color = with_alpha(mix_color(base_color, self.palette.shadow, 0.08), 250)
        button.style.background_color = base_color
        button.style.border_color = border_color
        button.style.border_width = 4.0 if highlight else 2.0
        button.text_node.color = self.palette.text_primary

    def _refresh_option_tabs(self) -> None:
        for tab_key, button in self.option_tab_buttons.items():
            self._apply_tab_style(
                button,
                active=tab_key == self.current_option_tab,
                focused=button.is_hovered,
            )

    def _select_option_tab(self, tab_key: str) -> None:
        if self.current_option_tab == tab_key:
            return
        self.current_option_tab = tab_key
        self._refresh_option_tabs()

    def _show_main_menu(self) -> None:
        if self.current_view == "menu":
            return
        self.current_view = "menu"
        self._rebuild_body()

    def _run_action(self, action_key: str) -> None:
        if action_key == "pause.resume":
            self.hide(animated=True)
            return
        if action_key == "pause.options":
            self.current_view = "options"
            self._rebuild_body()
            return

    def _finish_open(self) -> None:
        self.is_animating = False

    def _finish_close(self) -> None:
        if self.overlay is not None:
            self.overlay.style.visible = False
        if self.panel is not None:
            self.panel.style.opacity = 0.0
            self.panel.style.margin.top = Unit.px(0)
        self.is_animating = False
