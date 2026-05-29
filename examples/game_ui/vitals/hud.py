from __future__ import annotations

from arepy_ui import Canvas, FlexDirection, Node, Style, Unit

from ..scale import hud_px
from ..i18n import Translator
from ..theme import Palette
from .data import build_demo_vitals
from .render import render_vital_bar


HEALTH_BAR_WIDTH = hud_px(320)
HEALTH_BAR_HEIGHT = hud_px(28)
STAMINA_BAR_WIDTH = hud_px(274)
STAMINA_BAR_HEIGHT = hud_px(18)


class VitalsHUD:
    def __init__(self, translator: Translator, palette: Palette):
        self.i18n = translator
        self.palette = palette
        self.vitals = build_demo_vitals(palette)

    def build(self) -> Node:
        root = Node(
            style=Style(
                width=Unit.px(HEALTH_BAR_WIDTH),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                gap=hud_px(6),
            )
        )

        root.add_child(
            Canvas(
                on_render=self._render_bar,
                width=Unit.px(HEALTH_BAR_WIDTH),
                height=Unit.px(HEALTH_BAR_HEIGHT),
                state={"bar": self.vitals.health},
            )
        )
        root.add_child(
            Canvas(
                on_render=self._render_bar,
                width=Unit.px(STAMINA_BAR_WIDTH),
                height=Unit.px(STAMINA_BAR_HEIGHT),
                state={"bar": self.vitals.stamina},
            )
        )
        return root

    def _render_bar(self, renderer, rect, state: dict) -> None:
        render_vital_bar(renderer, rect, state["bar"], self.palette)
