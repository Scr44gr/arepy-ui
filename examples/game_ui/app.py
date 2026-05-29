from __future__ import annotations

import raylib as rl

from arepy import ArepyEngine, Renderer2D, SystemPipeline
from arepy.engine.time import Time

from arepy_ui import ResizeMode, UIConfig, UIManager

from .fonts import setup_game_ui_fonts
from .i18n import Translator
from .screen import GameUIScreen
from .theme import PALETTE


class GameInterfaceApp:
    def __init__(self, locale: str = "es"):
        self.palette = PALETTE
        self.translator = Translator(locale=locale)
        self.screen = GameUIScreen(self.translator, self.palette)
        self.ui_manager: UIManager | None = None

    def create_ui(self):
        setup_game_ui_fonts()
        return self.screen.build()

    def update(self, time: Time) -> None:
        self.screen.update(time)

    def render_background(self, renderer: Renderer2D) -> None:
        renderer.clear(self.palette.background)

    def run(self) -> None:
        rl.SetConfigFlags(rl.FLAG_WINDOW_RESIZABLE)

        game = ArepyEngine(
            title="arepy-ui // Game UI Prototype",
            width=1420,
            height=860,
        )
        world = game.create_world("game_ui")

        def update_system(time: Time) -> None:
            self.update(time)

        def render_background_system(renderer: Renderer2D) -> None:
            self.render_background(renderer)

        world.add_system(SystemPipeline.UPDATE, update_system)
        world.add_system(SystemPipeline.RENDER, render_background_system)

        self.ui_manager = UIManager.install(
            world,
            root=self.create_ui,
            config=UIConfig(
                resize_mode=ResizeMode.RESPONSIVE,
                reference_width=1420,
                reference_height=860,
            ),
        )
        self.screen.attach_manager(self.ui_manager)
        self.screen.play_intro()

        game.set_current_world("game_ui")
        game.run()
