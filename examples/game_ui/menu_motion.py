from __future__ import annotations

from arepy_ui import Easing, Node, UIManager, Unit
from arepy_ui.runtime import get_runtime

from .scale import hud_px


MENU_HIDE_EXTRA_OFFSET = hud_px(36)
MENU_TRANSITION_DURATION = 0.18


class MenuLayerMotion:
    def __init__(self) -> None:
        self.ui_manager: UIManager | None = None
        self.target_layer: Node | None = None
        self.active_menus = 0

    def attach_manager(self, manager: UIManager) -> None:
        self.ui_manager = manager

    def bind_layer(self, layer: Node) -> None:
        self.target_layer = layer
        self.target_layer.style.top = Unit.px(0)

    def menu_opened(self, animated: bool = True) -> None:
        self.active_menus += 1
        if self.active_menus > 1:
            return
        self._move_to(self._hidden_offset(), animated, opening=True)

    def menu_closed(self, animated: bool = True) -> None:
        if self.active_menus <= 0:
            self.active_menus = 0
            self._move_to(0, animated, opening=False)
            return

        self.active_menus -= 1
        if self.active_menus > 0:
            return
        self._move_to(0, animated, opening=False)

    def _hidden_offset(self) -> int:
        _, height = get_runtime().display.get_window_size()
        return -(int(height) + MENU_HIDE_EXTRA_OFFSET)

    def _move_to(self, target_top: int, animated: bool, opening: bool) -> None:
        if self.target_layer is None:
            return

        if self.ui_manager is None or not animated:
            self.target_layer.style.top = Unit.px(target_top)
            return

        duration = MENU_TRANSITION_DURATION
        easing = Easing.EASE_IN_OUT_QUAD
        self.ui_manager.animator.create().to(
            self.target_layer.style,
            "top",
            target_top,
            duration,
            easing,
        ).start()
