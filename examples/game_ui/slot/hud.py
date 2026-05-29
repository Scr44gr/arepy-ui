from __future__ import annotations

import random

from arepy.engine.time import Time

from arepy_ui import AlignItems, Button, Canvas, Easing, FlexDirection, JustifyContent, Node, Spacing, Style, Text, UIManager, Unit

from ..fonts import font_for
from ..i18n import Translator
from ..scale import hud_px
from ..text import fit_text
from ..theme import Palette, mix_color, with_alpha
from .data import SlotMachineState, SlotPrize, build_slot_prizes
from .render import render_slot_reel


MACHINE_COLUMN_WIDTH = hud_px(540)
REEL_CANVAS_WIDTH = hud_px(382)
REEL_CANVAS_HEIGHT = hud_px(160)
CONTROLS_WIDTH = hud_px(132)
HUD_BUTTON_WIDTH = hud_px(208)
HUD_BUTTON_HEIGHT = hud_px(50)
SELECTION_TEXT_MAX_WIDTH = hud_px(500)


def ease_out_expo(progress: float) -> float:
    if progress >= 1.0:
        return 1.0
    return 1.0 - pow(2.0, -10.0 * progress)


class SlotHUD:
    def __init__(self, translator: Translator, palette: Palette):
        self.i18n = translator
        self.palette = palette
        self.prizes = build_slot_prizes(palette)
        self.machine = SlotMachineState()

        self.ui_manager: UIManager | None = None
        self.toggle_button: Button | None = None
        self.spin_button: Button | None = None
        self.status_text: Text | None = None
        self.selection_text: Text | None = None
        self.machine_column: Node | None = None
        self.intro_nodes: list[Node] = []
        self.panel_open = False
        self.panel_animating = False

    def attach_manager(self, manager: UIManager) -> None:
        self.ui_manager = manager

    def build(self) -> Node:
        self.intro_nodes.clear()

        root = Node(
            style=Style(
                width=Unit.px(MACHINE_COLUMN_WIDTH),
                height=Unit.auto(),
                background_color=None,
                flex_direction=FlexDirection.COLUMN,
                gap=hud_px(10),
                align_items=AlignItems.CENTER,
            )
        )

        self.toggle_button = self._create_toggle_button()
        self.machine_column = self._create_machine_column()
        self.machine_column.style.visible = False
        self.machine_column.style.opacity = 0.0
        self.machine_column.style.margin.top = Unit.px(0)

        root.add_child(self.toggle_button)
        root.add_child(self.machine_column)

        self.intro_nodes.append(self.toggle_button)
        self._sync_current_prize()
        self._update_spin_button()
        self._update_toggle_button()
        return root

    def play_intro(self) -> None:
        if self.ui_manager is None:
            return

        for index, node in enumerate(self.intro_nodes):
            node.style.opacity = 0.0
            node.style.margin.top = Unit.px(-hud_px(8))
            delay = index * 0.08
            self.ui_manager.animator.create().wait(delay).to(
                node.style,
                "opacity",
                1.0,
                0.28,
                Easing.EASE_OUT_QUAD,
            ).start()
            self.ui_manager.animator.create().wait(delay).to(
                node.style,
                "margin.top",
                0,
                0.38,
                Easing.EASE_OUT_BACK,
            ).start()

    def update(self, time: Time) -> None:
        dt = max(0.0, time.delta_seconds)
        self.machine.elapsed += dt
        self.machine.flash = max(0.0, self.machine.flash - dt * 2.2)

        if not self.machine.is_spinning:
            return

        self.machine.spin_elapsed += dt
        progress = min(self.machine.spin_elapsed / max(self.machine.spin_duration, 0.001), 1.0)
        eased = ease_out_expo(progress)
        self.machine.reel_position = (
            self.machine.spin_start_position
            + (self.machine.spin_target_position - self.machine.spin_start_position) * eased
        )

        if progress < 1.0:
            return

        self.machine.is_spinning = False
        self.machine.current_index = self.machine.target_index
        self.machine.reel_position = float(self.machine.current_index)
        self.machine.flash = 1.0

        self._sync_current_prize()
        self._update_spin_button()

    def start_spin(self) -> None:
        if self.machine.is_spinning:
            return

        next_index = random.randrange(len(self.prizes))
        if next_index == self.machine.current_index:
            next_index = (next_index + random.randint(1, len(self.prizes) - 1)) % len(self.prizes)

        self.machine.is_spinning = True
        self.machine.target_index = next_index
        self.machine.spin_elapsed = 0.0
        self.machine.spin_duration = random.uniform(2.35, 3.10)
        self.machine.spin_start_position = self.machine.reel_position
        loops = random.randint(8, 11)
        delta_to_target = (next_index - self.machine.current_index) % len(self.prizes)
        self.machine.spin_target_position = (
            self.machine.spin_start_position + loops * len(self.prizes) + delta_to_target
        )
        self.machine.flash = 0.0

        if self.status_text is not None:
            self.status_text.text = self.i18n.text("slot.status.spinning")
        if self.selection_text is not None:
            self.selection_text.text = fit_text(
                self.i18n.text("slot.selection.spinning"),
                SELECTION_TEXT_MAX_WIDTH,
                hud_px(16),
                font_for(),
            )
            self.selection_text.color = self.palette.text_muted

        self._update_spin_button()

    def toggle_panel(self) -> None:
        if self.panel_animating:
            return

        if self.panel_open:
            self.hide_panel(animated=True)
            return

        self.show_panel(animated=True)

    def show_panel(self, animated: bool = True) -> None:
        if self.machine_column is None or self.panel_open or self.panel_animating:
            return

        self.panel_open = True
        self.panel_animating = True
        self.machine_column.style.visible = True
        self.machine_column.style.opacity = 0.0
        self.machine_column.style.margin.top = Unit.px(-hud_px(26))
        self._sync_current_prize()
        self._update_toggle_button()

        if self.ui_manager is None or not animated:
            self.machine_column.style.opacity = 1.0
            self.machine_column.style.margin.top = Unit.px(0)
            self._finish_open_panel()
            return

        self.ui_manager.animator.create().to(
            self.machine_column.style,
            "opacity",
            1.0,
            0.24,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().to(
            self.machine_column.style,
            "margin.top",
            0,
            0.34,
            Easing.EASE_OUT_BACK,
        ).start()
        self.ui_manager.animator.create().wait(0.36).call(self._finish_open_panel).start()

    def hide_panel(self, animated: bool = True) -> None:
        if self.machine_column is None or not self.panel_open or self.panel_animating:
            return
        if self.machine.is_spinning:
            return

        self.panel_open = False
        self.panel_animating = True
        self._update_toggle_button()

        if self.ui_manager is None or not animated:
            self._finish_close_panel()
            return

        self.ui_manager.animator.create().to(
            self.machine_column.style,
            "opacity",
            0.0,
            0.18,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().to(
            self.machine_column.style,
            "margin.top",
            -hud_px(26),
            0.22,
            Easing.EASE_OUT_QUAD,
        ).start()
        self.ui_manager.animator.create().wait(0.24).call(self._finish_close_panel).start()

    def current_prize(self) -> SlotPrize:
        return self.prizes[self.machine.current_index]

    def _create_toggle_button(self) -> Button:
        button = Button(
            text=self.i18n.text("slot.toggle.open"),
            on_click=self.toggle_panel,
            width=Unit.px(HUD_BUTTON_WIDTH),
            height=Unit.px(HUD_BUTTON_HEIGHT),
            bg_color=with_alpha(self.palette.surface_soft, 228),
            text_color=self.palette.text_primary,
            font_size=hud_px(16),
            border_radius=float(hud_px(16)),
            font_name=font_for(),
        )
        button.style.border_width = 2.0
        button.style.border_color = with_alpha(self.palette.surface_border, 170)
        button.style.padding = Spacing.symmetric(hud_px(10), hud_px(18))
        return button

    def _create_machine_column(self) -> Node:
        column = Node(
            style=Style(
                width=Unit.px(MACHINE_COLUMN_WIDTH),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                gap=hud_px(8),
                align_items=AlignItems.CENTER,
                opacity=1.0,
                margin=Spacing.all(0),
            )
        )

        machine_shell = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                background_color=with_alpha(self.palette.surface_soft, 188),
                border_color=with_alpha(self.palette.surface_border, 170),
                border_width=2.0,
                border_radius=float(hud_px(20)),
                padding=Spacing.all(hud_px(12)),
                flex_direction=FlexDirection.ROW,
                gap=hud_px(12),
                align_items=AlignItems.CENTER,
            )
        )

        machine_shell.add_child(
            Canvas(
                on_render=self._render_machine,
                width=Unit.px(REEL_CANVAS_WIDTH),
                height=Unit.px(REEL_CANVAS_HEIGHT),
                state={},
            )
        )

        controls_stack = Node(
            style=Style(
                width=Unit.px(CONTROLS_WIDTH),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.CENTER,
                align_items=AlignItems.CENTER,
                gap=hud_px(10),
            )
        )
        controls_stack.add_child(
            Text(
                self.i18n.text("slot.range"),
                size=hud_px(15),
                color=self.palette.text_muted,
                font_name=font_for(),
            )
        )

        self.spin_button = Button(
            text=self.i18n.text("slot.spin"),
            on_click=self.start_spin,
            width=Unit.px(hud_px(110)),
            height=Unit.px(hud_px(46)),
            bg_color=with_alpha(self.palette.white, 242),
            text_color=self.palette.text_on_accent,
            font_size=hud_px(15),
            border_radius=float(hud_px(14)),
            font_name=font_for(),
        )
        self.spin_button.style.border_width = 2.0
        self.spin_button.style.border_color = with_alpha(self.palette.surface_border, 220)
        controls_stack.add_child(self.spin_button)

        self.status_text = Text(
            self.i18n.text("slot.status.ready"),
            size=hud_px(14),
            color=self.palette.text_secondary,
            font_name=font_for(),
        )
        controls_stack.add_child(self.status_text)
        machine_shell.add_child(controls_stack)

        selection_row = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                justify_content=JustifyContent.CENTER,
                align_items=AlignItems.CENTER,
                padding=Spacing.symmetric(hud_px(3), hud_px(8)),
            )
        )
        self.selection_text = Text(
            "",
            size=hud_px(16),
            color=self.palette.text_secondary,
            font_name=font_for(),
        )
        selection_row.add_child(self.selection_text)

        column.add_child(machine_shell)
        column.add_child(selection_row)
        return column

    def _render_machine(self, renderer, rect, _state: dict) -> None:
        render_slot_reel(
            renderer,
            rect,
            self.machine,
            self.prizes,
            self.palette,
            self.i18n.text("slot.title"),
        )

    def _update_spin_button(self) -> None:
        if self.spin_button is None:
            return

        self.spin_button.text_node.text = self.i18n.text(
            "slot.spin.active" if self.machine.is_spinning else "slot.spin"
        )
        self.spin_button.text_node.color = self.palette.text_on_accent
        self.spin_button.style.border_width = 2.0
        self.spin_button.style.border_color = with_alpha(self.palette.surface_border, 210)

        if self.machine.is_spinning:
            base_color = with_alpha(mix_color(self.palette.surface, self.palette.brass_soft, 0.08), 246)
            hover_color = with_alpha(mix_color(base_color, self.palette.brass_soft, 0.12), 248)
            pressed_color = with_alpha(mix_color(base_color, self.palette.shadow, 0.12), 250)
            self.spin_button.style.opacity = 0.90
        else:
            base_color = with_alpha(self.palette.white, 242)
            hover_color = with_alpha(mix_color(self.palette.white, self.palette.brass_soft, 0.08), 246)
            pressed_color = with_alpha(mix_color(self.palette.white, self.palette.shadow, 0.10), 248)
            self.spin_button.style.opacity = 1.0

        self.spin_button.base_color = base_color
        self.spin_button.hover_color = hover_color
        self.spin_button.pressed_color = pressed_color
        self.spin_button.style.background_color = base_color

    def _update_toggle_button(self) -> None:
        if self.toggle_button is None:
            return

        label_key = "slot.toggle.close" if self.panel_open else "slot.toggle.open"
        self.toggle_button.text_node.text = self.i18n.text(label_key)
        self.toggle_button.text_node.color = self.palette.text_primary

        if self.panel_open:
            base_color = with_alpha(mix_color(self.palette.surface_soft, self.palette.brass, 0.16), 236)
            border_color = with_alpha(self.palette.brass_soft, 220)
        else:
            base_color = with_alpha(mix_color(self.palette.surface_soft, self.palette.background_soft, 0.28), 224)
            border_color = with_alpha(self.palette.surface_border, 175)

        self.toggle_button.base_color = base_color
        self.toggle_button.hover_color = mix_color(base_color, self.palette.brass_soft, 0.12)
        self.toggle_button.pressed_color = mix_color(base_color, self.palette.background, 0.34)
        self.toggle_button.style.background_color = base_color
        self.toggle_button.style.border_color = border_color
        self.toggle_button.style.border_width = 2.0
        self.toggle_button.style.opacity = 0.88 if self.panel_animating else 1.0

    def _sync_current_prize(self) -> None:
        prize = self.current_prize()
        if self.status_text is not None:
            self.status_text.text = self.i18n.text("slot.status.number", number=prize.number)

        if self.selection_text is not None:
            selection_label = self.i18n.text(
                "slot.selection.current",
                name=self.i18n.text(prize.name_key),
            )
            self.selection_text.text = fit_text(
                selection_label,
                SELECTION_TEXT_MAX_WIDTH,
                hud_px(16),
                font_for(),
            )
            self.selection_text.color = self.palette.text_secondary

    def _finish_open_panel(self) -> None:
        self.panel_animating = False
        self._update_toggle_button()

    def _finish_close_panel(self) -> None:
        if self.machine_column is not None:
            self.machine_column.style.visible = False
            self.machine_column.style.opacity = 0.0
            self.machine_column.style.margin.top = Unit.px(0)

        self.panel_animating = False
        self._update_toggle_button()
