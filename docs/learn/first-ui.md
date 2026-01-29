# Your First UI

Let's build a complete game menu from scratch! By the end of this tutorial, you'll understand how arepy-ui works.

## What We'll Build

A simple main menu with:
- A title
- Start and Quit buttons
- A settings panel

<!-- TODO: Add screenshot of final result -->
![Final Menu](../../assets/examples/first-ui-result.png)

## Step 1: Setup

First, create a new Python file:

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig

# We'll fill this in!
ui_manager: UIManager = None

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())

def update(dt: float):
    ui_manager.update(dt)

def render():
    ui_manager.render()

if __name__ == "__main__":
    game = ArepyEngine(title="My Game", width=800, height=600)
    world = game.create_world("main")
    world.add_startup_system(setup)
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER, render)
    game.set_current_world("main")
    game.run()
```

Run this and you'll see... a black screen! That's because we haven't added any UI yet.

## Step 2: Add a Root Node

Everything in arepy-ui is a **Node**. Think of it like a box that can contain other boxes.

```python
from arepy_ui import UIManager, UIConfig, Node, Style, Unit

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    # Create a root node that fills the screen
    root = Node(
        style=Style(
            width=Unit.percent(100),   # 100% of screen width
            height=Unit.percent(100),  # 100% of screen height
        )
    )
    
    ui_manager.set_root(root)
    game.add_resource(ui_manager)
```

Still a black screen, but now we have a container ready!

## Step 3: Add a Title

Let's add some text:

```python
from arepy_ui import UIManager, UIConfig, Node, Text, Style, Color, Unit, FlexDirection, JustifyContent, AlignItems

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    root = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,  # Stack children vertically
            justify_content=JustifyContent.CENTER, # Center vertically
            align_items=AlignItems.CENTER,         # Center horizontally
            background_color=Color(20, 20, 30),    # Dark background
        ),
        children=[
            Text("My Awesome Game", size=48, color=Color(255, 255, 255)),
        ],
    )
    
    ui_manager.set_root(root)
    game.add_resource(ui_manager)
```

Now you should see "My Awesome Game" centered on screen! 🎉

## Step 4: Add Buttons

```python
from arepy_ui import UIManager, UIConfig, Node, Text, Button, Style, Color, Unit, FlexDirection, JustifyContent, AlignItems

def on_start():
    print("Starting game!")

def on_quit():
    print("Goodbye!")
    # In a real game: game.quit()

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    root = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            gap=20,  # Space between children
            background_color=Color(20, 20, 30),
        ),
        children=[
            Text("My Awesome Game", size=48, color=Color(255, 255, 255)),
            
            # Buttons container
            Node(
                style=Style(
                    flex_direction=FlexDirection.COLUMN,
                    gap=10,
                ),
                children=[
                    Button("Start Game", on_click=on_start),
                    Button("Quit", on_click=on_quit),
                ],
            ),
        ],
    )
    
    ui_manager.set_root(root)
    game.add_resource(ui_manager)
```

Click the buttons - you'll see the messages in the console!

## Step 5: Style the Buttons

Let's make the buttons look better:

```python
Button(
    "Start Game",
    on_click=on_start,
    style=Style(
        width=Unit.px(200),
        height=Unit.px(50),
        background_color=Color(100, 80, 200),  # Purple
        border_radius=8.0,
    ),
)
```

## Complete Code

Here's everything together:

```python
from arepy import ArepyEngine
from arepy_ui import UIManager, UIConfig, Node, Text, Button, Style, Color, Unit, FlexDirection, JustifyContent, AlignItems

ui_manager: UIManager = None

def on_start():
    print("Starting game!")

def on_quit():
    print("Goodbye!")

def setup(game: ArepyEngine):
    global ui_manager
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    root = Node(
        style=Style(
            width=Unit.percent(100),
            height=Unit.percent(100),
            flex_direction=FlexDirection.COLUMN,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            gap=30,
            background_color=Color(20, 20, 30),
        ),
        children=[
            Text("My Awesome Game", size=48, color=Color(255, 255, 255)),
            
            Node(
                style=Style(flex_direction=FlexDirection.COLUMN, gap=10),
                children=[
                    Button(
                        "Start Game",
                        on_click=on_start,
                        style=Style(
                            width=Unit.px(200),
                            height=Unit.px(50),
                            background_color=Color(100, 80, 200),
                            border_radius=8.0,
                        ),
                    ),
                    Button(
                        "Quit",
                        on_click=on_quit,
                        style=Style(
                            width=Unit.px(200),
                            height=Unit.px(50),
                            background_color=Color(80, 80, 90),
                            border_radius=8.0,
                        ),
                    ),
                ],
            ),
        ],
    )
    
    ui_manager.set_root(root)
    game.add_resource(ui_manager)

def update(dt: float):
    ui_manager.update(dt)

def render():
    ui_manager.render()

if __name__ == "__main__":
    game = ArepyEngine(title="My Game", width=800, height=600)
    world = game.create_world("main")
    world.add_startup_system(setup)
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER, render)
    game.set_current_world("main")
    game.run()
```

## What's Next?

You've learned the basics! Now explore:

- [Understanding Nodes](concepts/nodes.md) - Deep dive into the Node system
- [Styles & Layout](concepts/styles.md) - Master flexbox layout
- [Components Reference](../reference/components/index.md) - All available components
