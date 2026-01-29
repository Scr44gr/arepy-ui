# Theme Switching

Learn how to add light/dark mode to your game UI!

<!-- TODO: Add theme switching GIF -->
![Theme Switching](../../assets/theme-switch.gif)

## Overview

arepy-ui supports CSS variables with theme variants, making it easy to switch between color schemes at runtime.

## Step 1: Define Theme Variables

Create a `globals.acss` file:

```css
/* globals.acss */

/* Base theme (dark) */
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
    --accent: #e94560;
    --accent-hover: #ff6b6b;
    --success: #4ecca3;
    --warning: #ffc93c;
    --border: #2a2a4e;
}

/* Light theme variant */
:root.light {
    --bg-primary: #f5f5f5;
    --bg-secondary: #ffffff;
    --bg-card: #ffffff;
    --text-primary: #1a1a2e;
    --text-secondary: #666680;
    --accent: #e94560;
    --accent-hover: #d63050;
    --success: #2ecc71;
    --warning: #f39c12;
    --border: #e0e0e0;
}
```

## Step 2: Load Global Styles

```python
from arepy_ui.markup import load_globals, set_theme, get_theme
from arepy_ui import UIManager, UIConfig

def setup(game: ArepyEngine):
    global ui_manager
    
    # Load global styles FIRST
    load_globals("assets/ui/globals.acss")
    
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    ui_manager.set_root(create_ui())
    game.add_resource(ui_manager)
```

## Step 3: Use Variables in ACSS

**menu.acss**
```css
.screen {
    width: 100%;
    height: 100%;
    background: var(--bg-primary);
}

.card {
    background: var(--bg-card);
    border-color: var(--border);
    border-width: 1;
    border-radius: 12px;
    padding: 20px;
}

.title {
    color: var(--text-primary);
    font-size: 24px;
}

.subtitle {
    color: var(--text-secondary);
    font-size: 14px;
}

.btn-primary {
    background: var(--accent);
}

.btn-primary:hover {
    background: var(--accent-hover);
}
```

## Step 4: Toggle Theme

```python
from arepy_ui.markup import set_theme, get_theme

def toggle_theme():
    current = get_theme()
    
    if current == "light":
        set_theme(None)  # Back to base (dark)
    else:
        set_theme("light")
    
    # Rebuild UI to apply new theme
    refresh_ui()

def refresh_ui():
    ui_manager.set_root(create_ui())
```

## Step 5: Theme Toggle Button

```python
def create_settings_panel() -> Node:
    current_theme = get_theme() or "dark"
    
    return Node(
        style=Style(...),
        children=[
            Text("Settings", ...),
            
            # Theme toggle
            Node(
                style=Style(
                    flex_direction=FlexDirection.ROW,
                    justify_content=JustifyContent.SPACE_BETWEEN,
                    align_items=AlignItems.CENTER,
                ),
                children=[
                    Text("Theme", color=Color(200, 200, 200)),
                    Button(
                        "🌙 Dark" if current_theme == "dark" else "☀️ Light",
                        on_click=toggle_theme,
                    ),
                ],
            ),
        ],
    )
```

## Using with Python API

You can also use theme variables directly in Python:

```python
from arepy_ui.markup import get_global_styles

def get_theme_color(var_name: str) -> Color:
    """Get a theme color variable."""
    registry = get_global_styles()
    value = registry.get_variable(var_name)
    
    if value and value.startswith("#"):
        # Parse hex color
        hex_val = value.lstrip("#")
        r = int(hex_val[0:2], 16)
        g = int(hex_val[2:4], 16)
        b = int(hex_val[4:6], 16)
        return Color(r, g, b, 255)
    
    return Color(255, 255, 255)  # Fallback

# Usage
bg_color = get_theme_color("bg-primary")
```

## Multiple Themes

You can define any number of themes:

```css
:root { /* Default/dark */ }
:root.light { /* Light theme */ }
:root.ocean { /* Ocean theme */ }
:root.forest { /* Forest theme */ }
```

```python
set_theme("ocean")
set_theme("forest")
set_theme("light")
set_theme(None)  # Back to default
```

## Persisting Theme Choice

Save the user's preference:

```python
import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")

def save_settings():
    settings = {
        "theme": get_theme() or "dark",
    }
    SETTINGS_FILE.write_text(json.dumps(settings))

def load_settings():
    if SETTINGS_FILE.exists():
        settings = json.loads(SETTINGS_FILE.read_text())
        set_theme(settings.get("theme"))
```

## Tips

!!! tip "Semantic Variable Names"
    Use semantic names like `--bg-primary`, `--text-muted` instead of `--dark-gray`.

!!! tip "Contrast Matters"
    Test both themes for readability. Dark text on dark backgrounds is hard to read!

!!! tip "Transition Animations"
    Consider adding fade transitions when switching themes for a polished feel.

## API Reference

| Function | Description |
|----------|-------------|
| `load_globals(path)` | Load global stylesheet with variables |
| `set_theme(variant)` | Activate a theme (`"light"`, `"dark"`, or `None`) |
| `get_theme()` | Get current theme name |
| `get_global_styles()` | Get the style registry for variable access |

## Next Steps

- [AUI Markup Reference](../../reference/markup/aui.md) - Complete markup guide
- [Global Styles Reference](../../reference/markup/globals.md) - Variables and themes
