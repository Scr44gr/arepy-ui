# Global Styles

Shared CSS variables and theme management.

## Overview

Global styles define CSS variables that can be used across all ACSS files. This enables theming, consistent design tokens, and easy customization.

## Creating globals.acss

```css
/* assets/ui/globals.acss */

:root {
    /* Colors */
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
    --text-muted: #666680;
    
    --accent: #e94560;
    --accent-hover: #ff6b6b;
    --success: #4ecca3;
    --warning: #ffc93c;
    --error: #e74c3c;
    
    /* Spacing */
    --gap-sm: 8px;
    --gap-md: 16px;
    --gap-lg: 24px;
    
    /* Border radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
}
```

## Loading Global Styles

Load globals before any UI is created:

```python
from arepy_ui.markup import load_globals, load_aui
from arepy_ui import UIManager, UIConfig

def setup(game: ArepyEngine):
    # Load global variables FIRST
    load_globals("assets/ui/globals.acss")
    
    # Now create UI
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    result = load_aui("menu.aui")
    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
    game.add_resource(ui_manager)
```

## Using Variables

Use `var()` in any ACSS file:

```css
/* menu.acss */

.screen {
    background: var(--bg-primary);
}

.card {
    background: var(--bg-card);
    border-radius: var(--radius-md);
    padding: var(--gap-md);
}

.title {
    color: var(--text-primary);
}

.btn-primary {
    background: var(--accent);
}
```

## Theme Variants

Define multiple themes using `:root.themename`:

```css
/* globals.acss */

/* Base theme (dark) */
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
    --accent: #e94560;
}

/* Light theme */
:root.light {
    --bg-primary: #f5f5f5;
    --bg-secondary: #ffffff;
    --text-primary: #1a1a2e;
    --text-secondary: #666680;
    --accent: #e94560;
}

/* Ocean theme */
:root.ocean {
    --bg-primary: #0d1b2a;
    --bg-secondary: #1b263b;
    --text-primary: #e0e1dd;
    --text-secondary: #778da9;
    --accent: #00b4d8;
}

/* Forest theme */
:root.forest {
    --bg-primary: #1a1c16;
    --bg-secondary: #2d3a24;
    --text-primary: #e8e4c9;
    --text-secondary: #9caf88;
    --accent: #4a7c59;
}
```

## Switching Themes

```python
from arepy_ui.markup import set_theme, get_theme

def toggle_theme():
    current = get_theme()
    
    if current == "light":
        set_theme(None)  # Back to base (dark)
    else:
        set_theme("light")
    
    refresh_ui()

def set_ocean_theme():
    set_theme("ocean")
    refresh_ui()

def refresh_ui():
    # Rebuild UI to apply theme
    result = load_aui("menu.aui")
    if result.success and result.root is not None:
        ui_manager.set_root(result.root)
```

## Theme API

| Function | Description |
|----------|-------------|
| `load_globals(path)` | Load global stylesheet |
| `set_theme(variant)` | Activate theme (`"light"`, `"ocean"`, or `None` for base) |
| `get_theme()` | Get current theme name |
| `get_global_styles()` | Get style registry for direct access |

## Accessing Variables in Python

```python
from arepy_ui.markup import get_global_styles

def get_theme_color(var_name: str) -> Color:
    """Get a theme color variable."""
    registry = get_global_styles()
    value = registry.get_variable(var_name)
    
    if value and value.startswith("#"):
        hex_val = value.lstrip("#")
        r = int(hex_val[0:2], 16)
        g = int(hex_val[2:4], 16)
        b = int(hex_val[4:6], 16)
        return Color(r, g, b)
    
    return Color(255, 255, 255)  # Fallback

# Usage
accent = get_theme_color("accent")
bg = get_theme_color("bg-primary")
```

## Fallback Values

Provide fallbacks for undefined variables:

```css
.element {
    /* Falls back to #333 if --custom-color undefined */
    background: var(--custom-color, #333);
}
```

## Best Practices

!!! tip "Semantic Naming"
    Use semantic names like `--bg-primary` instead of `--dark-gray`.

!!! tip "Design Tokens"
    Define spacing, radii, and sizes as variables for consistency.

!!! tip "Theme Testing"
    Test all themes for readability and contrast.

!!! tip "Persist User Choice"
    Save theme preference to a file:
    
    ```python
    import json
    from pathlib import Path
    
    def save_theme(theme: str):
        Path("settings.json").write_text(
            json.dumps({"theme": theme})
        )
    
    def load_saved_theme():
        try:
            data = json.loads(Path("settings.json").read_text())
            set_theme(data.get("theme"))
        except FileNotFoundError:
            pass
    ```

## File Organization

```
assets/
└── ui/
    ├── globals.acss     # Variables & themes
    ├── main-menu.aui
    ├── main-menu.acss
    ├── options.aui
    └── options.acss
```

## See Also

- [ACSS Styling](acss.md) - Stylesheet syntax
- [Theme Tutorial](../../learn/tutorials/theming.md) - Complete theming guide
