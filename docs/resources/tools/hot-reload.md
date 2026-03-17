# Hot Reload

Rapidly iterate on your UI without restarting.

## Overview

Hot reload allows you to see changes instantly when you edit AUI/ACSS files.

## Setup

```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig
from arepy_ui.markup import load_aui, load_globals
from pathlib import Path

ui_manager: UIManager = None
last_modified = {}
WATCH_FILES = ["assets/ui/menu.aui", "assets/ui/menu.acss"]

def setup(game: ArepyEngine):
    global ui_manager
    load_globals("assets/ui/globals.acss")
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    reload_ui()
    game.add_resource(ui_manager)
    
    # Record initial timestamps
    for path in WATCH_FILES:
        last_modified[path] = Path(path).stat().st_mtime

def reload_ui():
    """Reload UI from files."""
    try:
        result = load_aui("assets/ui/menu.aui", handlers={
            "start_game": lambda: print("Start!"),
        })
        if result.success and result.root is not None:
            ui_manager.set_root(result.root)
            print("UI reloaded!")
        else:
            for error in result.errors:
                print(error)
    except Exception as e:
        print(f"Reload failed: {e}")

def check_for_changes():
    """Check if any watched files changed."""
    for path in WATCH_FILES:
        try:
            current = Path(path).stat().st_mtime
            if current != last_modified.get(path):
                last_modified[path] = current
                return True
        except FileNotFoundError:
            pass
    return False

def update(game: ArepyEngine):
    # Check every frame (or throttle for performance)
    if check_for_changes():
        reload_ui()
    
    ui_manager.update(game.get_delta_time())

def draw():
    ui_manager.render()

game = ArepyEngine(title="Hot Reload Demo", width=800, height=600)
world = game.create_world("main")
world.add_startup_system(setup)
world.add_system(SystemPipeline.UPDATE, update)
world.add_system(SystemPipeline.RENDER, draw)
game.set_current_world("main")
game.run()
```

`load_aui()` returns a `ParseResult`, so hot reload should only replace the root when parsing succeeds.

## Using Watchdog

For better performance, use the `watchdog` package:

```bash
pip install watchdog
```

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class UIReloadHandler(FileSystemEventHandler):
    def __init__(self, reload_callback):
        self.reload_callback = reload_callback
    
    def on_modified(self, event):
        if event.src_path.endswith(('.aui', '.acss')):
            self.reload_callback()

# In setup:
handler = UIReloadHandler(reload_ui)
observer = Observer()
observer.schedule(handler, "assets/ui", recursive=True)
observer.start()
```

## Tips

!!! tip "Development Only"
    Disable hot reload in production builds.

!!! tip "Error Handling"
    Always catch exceptions in reload to prevent crashes.

!!! tip "Throttle Reloads"
    Add a small delay to batch rapid file changes.

## Benefits

- **Faster iteration** - See changes instantly
- **No restart** - Keep game state between edits
- **Designer friendly** - Non-programmers can edit ACSS

## See Also

- [AUI Markup](../../reference/markup/aui.md) - Markup syntax
- [ACSS Styling](../../reference/markup/acss.md) - Style syntax
