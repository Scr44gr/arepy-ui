import os

from typing import Any, Dict

from arepy import ArepyEngine
from arepy import Color as ArepyColor
from arepy import Input, Key, Renderer2D, SystemPipeline

from arepy_ui import UIConfig, UIManager
from arepy_ui.config import ResizeMode
from arepy_ui.debug import UIDebugger
from arepy_ui.markup import get_theme, load_aui, load_globals, set_theme

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Application state
app_state: Dict[str, Any] = {
    "count": 0,
    "counter_text": None,
    "theme_text": None,
}


def create_ui():
    """Load UI from AUI markup file."""

    def increment():
        app_state["count"] = int(app_state["count"]) + 1
        _update_counter()

    def decrement():
        app_state["count"] = int(app_state["count"]) - 1
        _update_counter()

    def reset():
        app_state["count"] = 0
        _update_counter()

    def _update_counter():
        if app_state["counter_text"]:
            app_state["counter_text"].text = f"Clicked: {app_state['count']} times"  # type: ignore

    # Event handlers mapping
    handlers = {
        "increment": increment,
        "decrement": decrement,
        "reset": reset,
    }

    # Load UI from .aui file (automatically loads .acss with same name)
    aui_path = os.path.join(SCRIPT_DIR, "ui.aui")
    result = load_aui(aui_path, handlers=handlers)

    if not result.success:
        for error in result.errors:
            print(error)

    root = result.root

    # Get reference to the counter text for updates using the built-in find_by_id
    if root:
        app_state["counter_text"] = root.find_by_id("counter-text")

    return root


def _find_by_id(node, element_id: str):
    """Recursively find a node by its ID attribute."""
    if hasattr(node, "id") and node.id == element_id:
        return node

    if hasattr(node, "children"):
        for child in node.children:
            result = _find_by_id(child, element_id)
            if result:
                return result

    return None


def update_ui(
    renderer: Renderer2D,
    input: Input,
    ui_manager: UIManager,
    ui_debugger: UIDebugger,
):
    """Update loop - handle input and update UI."""
    delta_time = renderer.get_delta_time()
    ui_manager.update(dt=delta_time)

    if input.is_key_pressed(key=Key.F3):
        ui_debugger.toggle()
    if input.is_key_pressed(key=Key.F4):
        ui_debugger.toggle_bounds()
    if input.is_key_pressed(key=Key.F5):
        ui_debugger.toggle_padding()
    if input.is_key_pressed(key=Key.F6):
        ui_debugger.toggle_tree()

    # Toggle theme with F7
    if input.is_key_pressed(key=Key.F7):
        current = get_theme()
        new_theme = None if current == "light" else "light"
        set_theme(new_theme)
        # Rebuild UI to apply new theme
        ui = create_ui()
        ui_manager.set_root(ui)


def render(
    renderer: Renderer2D,
    ui_manager: UIManager,
    ui_debugger: UIDebugger,
):
    """Render loop - draw the UI."""
    # Match background to current theme
    if get_theme() == "light":
        renderer.clear(ArepyColor(250, 250, 250, 255))  # Light bg
    else:
        renderer.clear(ArepyColor(27, 30, 43, 255))  # Palenight dark bg
    ui_manager.render()
    ui_debugger.render(ui_manager.root)


def setup_ui(game: ArepyEngine):
    """Initialize UI manager and load markup."""
    # Load global styles first
    globals_path = os.path.join(SCRIPT_DIR, "globals.acss")
    load_globals(globals_path)

    ui_manager = UIManager.from_engine(
        game,
        config=UIConfig(
            resize_mode=ResizeMode.RESPONSIVE,
        ),
    )
    ui_debugger = UIDebugger()

    # Store in game as resources
    game.add_resource(ui_manager)
    game.add_resource(ui_debugger)

    # Load and set root UI from markup
    ui = create_ui()
    ui_manager.set_root(ui)


if __name__ == "__main__":
    game = ArepyEngine(title="AUI Markup Demo", width=800, height=600)
    setup_ui(game)

    # Create main world
    world = game.create_world("main")
    world.add_system(SystemPipeline.UPDATE, update_ui)
    world.add_system(SystemPipeline.RENDER_UI, render)
    game.set_current_world("main")
    game.run()
