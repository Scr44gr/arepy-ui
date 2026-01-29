from arepy import ArepyEngine, Renderer2D, SystemPipeline

from arepy_ui import (
    AlignItems,
    Button,
    JustifyContent,
    Node,
    Style,
    Text,
    UIConfig,
    UIManager,
    Unit,
)


def setup(game: ArepyEngine):
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    ui_manager.set_root(
        Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                align_items=AlignItems.CENTER,
                justify_content=JustifyContent.CENTER,
            ),
            children=[
                Text("Hello!", size=24),
                Button("Click me", on_click=lambda: print("Clicked!")),
            ],
        )
    )
    game.add_resource(ui_manager)


def update(ui_manager: UIManager, renderer: Renderer2D):
    ui_manager.update(renderer.get_delta_time())


def render(ui_manager: UIManager):
    ui_manager.render()


if __name__ == "__main__":
    game = ArepyEngine(title="My Game", width=800, height=600)
    setup(game)

    world = game.create_world("main")
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER_UI, render)
    game.set_current_world("main")
    game.run()
