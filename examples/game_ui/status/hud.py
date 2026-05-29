from __future__ import annotations

from arepy.engine.time import Time

from arepy_ui import AlignItems, Canvas, FlexDirection, JustifyContent, Node, Spacing, Style, Text, Unit

from ..fonts import font_for
from ..scale import hud_px
from ..theme import Palette, with_alpha
from .data import StatusState
from .render import render_status_badge


PANEL_WIDTH = hud_px(214)
HEADER_HEIGHT = hud_px(74)


class StatusHUD:
    def __init__(self, palette: Palette):
        self.palette = palette
        self.state = StatusState()
        self.money_text: Text | None = None

    def build(self) -> Node:
        panel = Node(
            style=Style(
                width=Unit.px(PANEL_WIDTH),
                height=Unit.auto(),
                background_color=with_alpha(self.palette.surface_soft, 212),
                border_color=with_alpha(self.palette.surface_border, 182),
                border_width=2.0,
                border_radius=float(hud_px(18)),
                padding=Spacing.all(hud_px(12)),
                flex_direction=FlexDirection.COLUMN,
                gap=hud_px(8),
            )
        )

        top_row = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
            )
        )
        top_row.add_child(
            Canvas(
                on_render=self._render_badge,
                width=Unit.percent(100),
                height=Unit.px(HEADER_HEIGHT),
                state={},
            )
        )

        money_row = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.END,
                align_items=AlignItems.CENTER,
                gap=hud_px(6),
            )
        )
        money_row.add_child(
            Text(
                "$",
                size=hud_px(18),
                color=self.palette.brass,
                font_name=font_for(),
            )
        )
        self.money_text = Text(
            self.state.formatted_gold(),
            size=hud_px(18),
            color=self.palette.text_primary,
            font_name=font_for(),
        )
        money_row.add_child(self.money_text)

        panel.add_child(top_row)
        panel.add_child(money_row)
        return panel

    def update(self, time: Time) -> None:
        self.state.update(time.delta_seconds)
        if self.money_text is not None:
            self.money_text.text = self.state.formatted_gold()

    def _render_badge(self, renderer, rect, _state: dict) -> None:
        render_status_badge(renderer, rect, self.state, self.palette)
