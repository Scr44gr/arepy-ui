from arepy import ArepyEngine

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

if __name__ == "__main__":
    game = ArepyEngine(title="My Game", width=800, height=600)
    world = game.create_world("main")
    UIManager.install(
        world,
        config=UIConfig(),
        root=Node(
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
        ),
    )
    game.set_current_world("main")
    game.run()
