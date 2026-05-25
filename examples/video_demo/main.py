"""
YouTube-style Video Player Demo using AUI Markup

This example demonstrates how to use the AUI markup system to create
a YouTube-like video player interface with:
- Header with search bar
- Video player with controls
- Comments section
- Related videos sidebar

ALL UI is defined in ui.aui and ui.acss files - no Python Node creation!
"""

import raylib as rl
from typing import Any, Callable, Dict

from arepy import ArepyEngine, Display, Input, Renderer2D, SystemPipeline
from arepy.ecs.world import World

from arepy_ui import ResizeMode, UIConfig, UIManager, configure_runtime
from arepy_ui.markup import load_aui

ui_manager: UIManager = None  # type: ignore


# Event handlers for buttons
def on_like():
    print("Liked!")


def on_dislike():
    print("Disliked!")


def on_share():
    print("Share clicked!")


def on_save():
    print("Saved!")


def on_subscribe():
    print("Subscribed!")


def setup_ui():
    """Load UI purely from markup files - NO Python Node creation!"""

    handlers: Dict[str, Callable[..., Any]] = {
        "on_like": on_like,
        "on_dislike": on_dislike,
        "on_share": on_share,
        "on_save": on_save,
        "on_subscribe": on_subscribe,
    }

    result = load_aui(
        "examples/video_demo/ui.aui",
        stylesheet="examples/video_demo/ui.acss",
        handlers=handlers,
    )

    if not result.success:
        for error in result.errors:
            print(error)

    return result.root


def ui_update_system(renderer: Renderer2D, input: Input, display: Display):
    global ui_manager
    dt = renderer.get_delta_time()
    wheel = input.get_mouse_wheel_delta()
    ui_manager.update(dt, wheel_scroll=wheel)


def ui_render_system(renderer: Renderer2D):
    global ui_manager
    ui_manager.render()


def setup_system(game: ArepyEngine):
    global ui_manager

    configure_runtime(
        game.renderer_2d,
        game.input,
        game.display,
        game.get_asset_store(),
        game.audio_device,
    )

    ui_manager = UIManager(config=UIConfig(resize_mode=ResizeMode.RESPONSIVE))

    root = setup_ui()
    ui_manager.set_root(root)




def main():
    rl.SetConfigFlags(rl.FLAG_MSAA_4X_HINT | rl.FLAG_WINDOW_RESIZABLE)

    game = ArepyEngine(
        title="arepy-ui Video Player (Pure Markup)",
        width=1280,
        height=720,
    )
    game.on_startup = lambda: setup_system(game)  # type: ignore

    world: World = game.create_world("video_demo")
    world.add_system(SystemPipeline.UPDATE, ui_update_system)
    world.add_system(SystemPipeline.RENDER_UI, ui_render_system)

    game.set_current_world("video_demo")
    game.run()


if __name__ == "__main__":
    main()
