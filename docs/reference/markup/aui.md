# AUI Markup System

Build UIs using declarative markup with HTML-like syntax and CSS-like styling.

## Overview

The AUI (Arepy UI) markup system lets you design interfaces in `.aui` files (structure) and `.acss` files (styles). This separation makes UI development faster and enables features like:

- **Theme variants** with CSS variables
- **Hot reloading** during development
- **Designer-friendly** syntax
- **Cython-accelerated** parsing

=== "Python"

    ```python
    from arepy_ui import UIManager, Node, Text, Button, Style

    root = Node(
        style=Style(flex_direction=FlexDirection.COLUMN),
        children=[
            Text("My Game", size=48),
            Button("Start", on_click=start_game),
        ],
    )
    ui_manager.set_root(root)
    ```

=== "AUI"

    ```html
    <column class="main-menu">
        <text class="title">My Game</text>
        <button on-click="start_game">Start</button>
    </column>
    ```

    ```python
    from arepy_ui.markup import load_aui

    handlers = {"start_game": start_game}
    result = load_aui("menu.aui", handlers=handlers)
    ui_manager.set_root(result.root)
    ```

---

## AUI Markup Syntax

### Basic Structure

```html
<container id="root" class="main-menu">
    <text class="title">Space Shooter</text>
    
    <column class="buttons">
        <button on-click="start">New Game</button>
        <button on-click="options">Options</button>
        <button class="quit" on-click="quit">Quit</button>
    </column>
</container>
```

### Available Tags

| Tag | Component | Description |
|-----|-----------|-------------|
| `<container>` | `Node` | Generic container |
| `<row>` | `Node` | Horizontal flex container (`flex-direction: row`) |
| `<column>` | `Node` | Vertical flex container (`flex-direction: column`) |
| `<text>` | `Text` | Text display |
| `<button>` | `Button` | Clickable button |
| `<input>` | `TextInput` | Text input field |
| `<slider>` | `Slider` | Range slider |
| `<checkbox>` | `Checkbox` | Toggle checkbox |
| `<select>` | `Select` | Dropdown selector |
| `<image>` | `Image` | Image display |
| `<scroll>` | `ScrollView` | Scrollable container |
| `<tabs>` | `Tabs` | Tab container |
| `<progress>` | `ProgressBar` | Progress indicator |
| `<canvas>` | `Canvas` | Drawing canvas |
| `<video>` | `Video` | Video player |
| `<colorpicker>` | `ColorPicker` | Color selection |
| `<draggable>` | `Draggable` | Draggable element |
| `<dropzone>` | `DropZone` | Drop target |

### Attributes

```html
<!-- ID and classes -->
<container id="main" class="panel dark">

<!-- Event handlers -->
<button on-click="handler_name">Click Me</button>
<slider on-change="volume_changed" />

<!-- Inline styles -->
<text style="color: #ff0000; font-size: 24px">Red Text</text>

<!-- Component-specific attributes -->
<slider min="0" max="100" value="50" />
<input placeholder="Enter name..." />
<checkbox checked="true" label="Enable sound" />
<image src="assets/logo.png" fit="contain" />
<colorpicker color="#ff6600" show-alpha="true" />
```

### Self-Closing Tags

```html
<image src="icon.png" />
<slider min="0" max="100" />
<checkbox label="Option" />
<progress value="75" max="100" />
<colorpicker color="#ff0000" />
```

---

## ACSS Styling Syntax

### Basic Syntax

```css
/* Variables */
:root {
    --primary: #6c5ce7;
    --spacing: 20px;
}

/* Element selector */
button {
    background: var(--primary);
    padding: 10px 20px;
}

/* Class selector */
.menu-btn {
    width: 200px;
    height: 50px;
}

/* ID selector */
#main-title {
    font-size: 48px;
    color: #ffffff;
}
```

### Supported Properties

#### Layout

| Property | Values | Description |
|----------|--------|-------------|
| `width` | `200px`, `50%` | Element width |
| `height` | `100px`, `100%` | Element height |
| `min-width` | `100px` | Minimum width |
| `max-width` | `500px` | Maximum width |
| `min-height` | `50px` | Minimum height |
| `max-height` | `300px` | Maximum height |
| `padding` | `10px`, `10px 20px` | Inner spacing |
| `margin` | `15px` | Outer spacing |
| `gap` | `10px` | Gap between children |

#### Flexbox

| Property | Values | Description |
|----------|--------|-------------|
| `flex-direction` | `row`, `column`, `row-reverse`, `column-reverse` | Main axis direction |
| `justify-content` | `flex-start`, `center`, `flex-end`, `space-between`, `space-around` | Main axis alignment |
| `align-items` | `flex-start`, `center`, `flex-end`, `stretch` | Cross axis alignment |
| `flex-wrap` | `nowrap`, `wrap` | Line wrapping |
| `flex-grow` | `1`, `2` | Grow factor |
| `flex-shrink` | `0`, `1` | Shrink factor |

#### Positioning

| Property | Values | Description |
|----------|--------|-------------|
| `position` | `relative`, `absolute` | Position mode |
| `top` | `50px` | Top offset |
| `left` | `100px` | Left offset |
| `right` | `20px` | Right offset |
| `bottom` | `20px` | Bottom offset |
| `z-index` | `100` | Stack order |

#### Appearance

| Property | Values | Description |
|----------|--------|-------------|
| `background` | `#1a1a2e`, `var(--bg)` | Background color |
| `border-radius` | `8px` | Corner rounding |
| `border-width` | `2px` | Border thickness |
| `border-color` | `#333` | Border color |
| `opacity` | `0.9` | Transparency |

#### Text

| Property | Values | Description |
|----------|--------|-------------|
| `color` | `#ffffff`, `var(--text)` | Text color |
| `font-size` | `32px` | Font size |
| `font-family` | `"Inter"` | Font name |
| `text-align` | `left`, `center`, `right` | Text alignment |

### Units

```css
.element {
    width: 200px;      /* Pixels */
    height: 50%;       /* Percentage */
    padding: 20;       /* Unitless (treated as pixels) */
    flex-grow: 1;      /* Number */
}
```

---

## Global Stylesheets

Global stylesheets provide shared styles and CSS variables across your entire application. They support **theme variants** for light/dark modes.

### Loading Global Styles

```python
from arepy_ui.markup import load_globals, load_aui

# Load global styles before loading UI
load_globals("assets/ui/globals.acss")

# Now load UI - it will inherit global styles and variables
result = load_aui("assets/ui/menu.aui", handlers=handlers)
```

### Creating a Global Stylesheet

**globals.acss:**

```css
/* Base theme (dark) */
:root {
    --bg-primary: #292d3e;
    --bg-secondary: #1b1e2b;
    --bg-elevated: #34394e;
    --text-primary: #a6accd;
    --text-heading: #ffffff;
    --text-muted: #676e95;
    --accent: #82aaff;
    --accent-hover: #a8c5ff;
    --success: #c3e88d;
    --warning: #ffcb6b;
    --error: #f07178;
    --border: #3c4155;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --radius-sm: 4px;
    --radius-md: 8px;
}

/* Light theme variant */
:root.light {
    --bg-primary: #fafafa;
    --bg-secondary: #ffffff;
    --bg-elevated: #f0f0f0;
    --text-primary: #4a4a4a;
    --text-heading: #292d3e;
    --text-muted: #8c8c8c;
    --accent: #6182b8;
    --accent-hover: #4a6da0;
    --success: #91b859;
    --warning: #f6a434;
    --error: #e53935;
    --border: #e0e0e0;
}

/* Shared component styles */
.panel {
    background: var(--bg-primary);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    border-width: 1;
    border-color: var(--border);
}

.btn {
    background: var(--accent);
    color: var(--text-heading);
    padding: 10 20;
    border-radius: var(--radius-sm);
}

.btn-danger {
    background: var(--error);
}
```

### Theme Switching

```python
from arepy_ui.markup import set_theme, get_theme

# Get current theme
current = get_theme()  # None (base), "light", "dark", etc.

# Switch to light theme
set_theme("light")

# Return to base theme
set_theme(None)
```

!!! warning "Theme Rebuild"
    After changing themes, you need to rebuild your UI for the new variables to take effect:
    
    ```python
    set_theme("light")
    ui = create_ui()  # Rebuild with new theme
    ui_manager.set_root(ui)
    ```

### Using Variables in ACSS

```css
.card {
    background: var(--bg-elevated);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    border-color: var(--border);
}

.title {
    color: var(--text-heading);
    font-size: 28;
}

.button-primary {
    background: var(--accent);
}

.button-primary:hover {
    background: var(--accent-hover);
}
```

### Global Style Priority

Styles are applied in this order (later overrides earlier):

1. **Global styles** (lowest priority)
2. **Local stylesheet styles** 
3. **Class selectors**
4. **ID selectors**
5. **Inline styles** (highest priority)

```html
<!-- inline style overrides everything -->
<button class="btn" style="background: #ff0000">Red Button</button>
```

### API Reference

| Function | Description |
|----------|-------------|
| `load_globals(path)` | Load global styles from a `.acss` file |
| `load_globals_string(content)` | Load global styles from a string |
| `set_theme(variant)` | Activate a theme variant (`"light"`, `"dark"`, or `None`) |
| `get_theme()` | Get the currently active theme variant |
| `clear_globals()` | Clear all global stylesheets |

---

## Error Handling

The markup system provides detailed error reporting with line numbers, columns, and context.

### ParseResult

Loading AUI files returns a `ParseResult` object:

```python
from arepy_ui.markup import load_aui

result = load_aui("menu.aui", handlers=handlers)

if result.success:
    ui_manager.set_root(result.root)
else:
    for error in result.errors:
        print(error)
```

### Error Levels

| Level | Description |
|-------|-------------|
| `ERROR` | Critical error, parsing failed |
| `WARNING` | Non-critical issue, parsing continued |

### MarkupError Structure

```python
from arepy_ui.markup.errors import MarkupError, ErrorLevel

# Each error contains:
error.level      # ErrorLevel.ERROR or ErrorLevel.WARNING
error.message    # Description of the issue
error.line       # Line number (1-based)
error.column     # Column number (1-based)
error.tag        # Related tag name (optional)
error.attribute  # Related attribute name (optional)

# String representation
print(error)  # "[ERROR] (line 15:8) <button>: Unknown attribute 'onclick'"
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Unknown tag` | Unrecognized element | Check tag spelling, use supported tags |
| `Unknown attribute` | Invalid attribute for tag | Check attribute spelling |
| `Handler not found` | Missing handler function | Add handler to handlers dict |
| `Invalid value` | Malformed attribute value | Check value format |
| `Unclosed tag` | Missing closing tag | Add `</tag>` or use self-closing `/>` |

### Example Error Handling

```python
from arepy_ui.markup import load_aui
from arepy_ui.logging import logger

def load_ui_safely(path: str, handlers: dict):
    result = load_aui(path, handlers=handlers)
    
    # Log warnings
    if result.has_warnings:
        for error in result.errors:
            if error.level.value == "warning":
                logger.warning(str(error))
    
    # Handle errors
    if not result.success:
        for error in result.errors:
            if error.level.value == "error":
                logger.error(str(error))
        return None
    
    return result.root
```

---

## Event Handlers

Map handler names to Python functions:

```python
def on_start():
    print("Starting game...")

def on_volume_change(value):
    print(f"Volume: {value}")

def on_color_pick(color):
    print(f"Color: {color}")

handlers = {
    "start": on_start,
    "volume": on_volume_change,
    "color_pick": on_color_pick,
}

result = load_aui("menu.aui", handlers=handlers)
```

In your `.aui` file:

```html
<button on-click="start">Start</button>
<slider on-change="volume" />
<colorpicker on-change="color_pick" />
```

---

## Complete Example

**menu.aui**
```html
<container class="main-menu">
    <text class="title">Space Shooter</text>
    
    <column class="menu-buttons">
        <button class="btn" on-click="new_game">New Game</button>
        <button class="btn" on-click="continue">Continue</button>
        <button class="btn" on-click="options">Options</button>
        <button class="btn btn-danger" on-click="quit">Quit</button>
    </column>
    
    <row class="footer">
        <text class="version">v1.0.0</text>
    </row>
</container>
```

**menu.acss**
```css
:root {
    --primary: #6c5ce7;
    --danger: #d63031;
    --bg: #0a0a15;
    --text: #dfe6e9;
}

.main-menu {
    width: 100%;
    height: 100%;
    background: var(--bg);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 40px;
}

.title {
    font-size: 64px;
    color: var(--text);
}

.menu-buttons {
    gap: 15px;
}

.btn {
    width: 250px;
    height: 55px;
    background: var(--primary);
    color: var(--text);
    border-radius: 8px;
    font-size: 20px;
}

.btn-danger {
    background: var(--danger);
}

.footer {
    position: absolute;
    bottom: 20px;
    right: 20px;
}

.version {
    font-size: 14px;
    color: #636e72;
}
```

**main.py**
```python
from arepy import ArepyEngine, SystemPipeline
from arepy_ui import UIManager, UIConfig
from arepy_ui.markup import load_globals, load_aui, set_theme, get_theme

def new_game():
    print("Starting new game...")

def continue_game():
    print("Continuing...")

def options():
    print("Opening options...")

def quit_game():
    game.quit()

handlers = {
    "new_game": new_game,
    "continue": continue_game,
    "options": options,
    "quit": quit_game,
}

def setup(game: ArepyEngine):
    global ui_manager
    
    # Load global styles first
    load_globals("ui/globals.acss")
    
    ui_manager = UIManager.from_engine(game, config=UIConfig())
    
    # Load UI from markup
    result = load_aui("ui/menu.aui", handlers=handlers)
    
    if not result.success:
        for error in result.errors:
            print(f"Markup error: {error}")
        return
    
    ui_manager.set_root(result.root)
    game.add_resource(ui_manager)

def update(dt: float):
    ui_manager.update(dt)

def render():
    ui_manager.render()

if __name__ == "__main__":
    game = ArepyEngine(title="Space Shooter", width=800, height=600)
    world = game.create_world("main")
    world.add_startup_system(setup)
    world.add_system(SystemPipeline.UPDATE, update)
    world.add_system(SystemPipeline.RENDER, render)
    game.set_current_world("main")
    game.run()
```

---

## Registering Custom Components

You can register your own components to use them in AUI markup files.

### Creating a Custom Component

First, create a component class that extends `Node`:

```python
from arepy_ui.core.node import Node
from arepy_ui.core.style import Style
from arepy_ui.core.types import Color

class HealthBar(Node):
    """A custom health bar component."""
    
    def __init__(
        self,
        value: float = 100,
        max_value: float = 100,
        bar_color: Color = Color(0, 255, 0, 255),
        bg_color: Color = Color(50, 50, 50, 255),
        style: Style = None,
        **kwargs
    ):
        super().__init__(style=style, **kwargs)
        self.value = value
        self.max_value = max_value
        self.bar_color = bar_color
        self.bg_color = bg_color
    
    @property
    def percentage(self) -> float:
        return (self.value / self.max_value) * 100
    
    def render(self):
        # Custom rendering logic
        super().render()
        # Draw background, then filled portion...
```

### Registering the Component

Use `register_component` to make it available in AUI markup:

```python
from arepy_ui import register_component

register_component(
    HealthBar,
    name="HealthBar",                    # Display name
    tags=["healthbar", "health-bar"],    # AUI tags that map to this component
    color=(255, 100, 100),               # Debug color (RGB)
    category="custom",                   # Category: core, input, layout, media, custom
)
```

### Using in AUI Markup

Now you can use your component in `.aui` files:

```html
<container class="hud">
    <healthbar value="75" max-value="100" />
    <!-- or with hyphenated tag -->
    <health-bar value="50" max-value="100" bar-color="#ff0000" />
</container>
```

### Complete Example

```python
from arepy_ui import register_component, Node
from arepy_ui.core.style import Style
from arepy_ui.core.types import Color, Unit

class StarRating(Node):
    """A star rating component."""
    
    def __init__(
        self,
        rating: int = 0,
        max_stars: int = 5,
        on_change=None,
        style: Style = None,
        **kwargs
    ):
        super().__init__(style=style, **kwargs)
        self._rating = rating
        self.max_stars = max_stars
        self.on_change = on_change
    
    @property
    def rating(self) -> int:
        return self._rating
    
    @rating.setter
    def rating(self, value: int):
        self._rating = max(0, min(value, self.max_stars))
        if self.on_change:
            self.on_change(self._rating)


# Register before loading any AUI that uses it
register_component(
    StarRating,
    tags=["star-rating", "starrating", "rating"],
    color=(255, 215, 0),  # Gold color for debugger
    category="input",
)
```

**Usage in AUI:**

```html
<container class="review-form">
    <text>Rate this game:</text>
    <star-rating rating="4" max-stars="5" on-change="on_rating_change" />
</container>
```

**Python handler:**

```python
def on_rating_change(value):
    print(f"New rating: {value} stars")

handlers = {"on_rating_change": on_rating_change}
result = load_aui("review.aui", handlers=handlers)
```

### ComponentMeta Properties

When registering a component, you can set these properties:

| Property | Type | Description |
|----------|------|-------------|
| `component_class` | `Type` | The component class |
| `name` | `str` | Display name (defaults to class name) |
| `tags` | `List[str]` | AUI markup tags that map to this component |
| `color` | `tuple[int,int,int]` | RGB color for debugger visualization |
| `category` | `str` | Category: `core`, `input`, `layout`, `media`, `custom` |

### Registry API

| Function | Description |
|----------|-------------|
| `register_component(cls, ...)` | Register a custom component |
| `get_registry()` | Get the global component registry |
| `registry.get(name)` | Get component metadata by name |
| `registry.get_by_tag(tag)` | Get component metadata by markup tag |
| `registry.get_class(name)` | Get component class by name |
| `registry.is_valid_tag(tag)` | Check if a tag is registered |
| `registry.get_valid_tags()` | Get all valid markup tags |

### Tips

!!! tip "Register Early"
    Register custom components **before** calling `load_aui()`. Components must be registered before the parser encounters their tags.

!!! tip "Multiple Tags"
    Use multiple tags for flexibility: `["my-widget", "mywidget", "mw"]`

!!! tip "Debug Colors"
    Choose distinctive colors for your components to make them easy to identify in the debugger (F3).

---

## Performance

The markup parser is performance-sensitive code and the project ships with compiled parser modules in the normal build workflow. The public runtime API does not require a separate `arepy_ui.markup.build_ext` command.

If you are working from source, use the repository build flow documented in the project setup instead of ad-hoc markup-specific commands.

---

## API Reference

### Loading Functions

| Function | Description |
|----------|-------------|
| `load_aui(path, stylesheet=None, handlers=None)` | Load UI from `.aui` file |
| `load_aui_string(content, stylesheet=None, handlers=None)` | Load UI from string |
| `parse_acss(content)` | Parse ACSS content to StyleSheet |
| `parse_aui(content)` | Parse AUI content |

### Global Styles

| Function | Description |
|----------|-------------|
| `load_globals(path)` | Load global stylesheet file |
| `load_globals_string(content)` | Load global styles from string |
| `set_theme(variant)` | Activate theme variant |
| `get_theme()` | Get current theme |
| `clear_globals()` | Clear all global styles |

### Component Registration

| Function | Description |
|----------|-------------|
| `register_component(cls, name, tags, color, category)` | Register a custom component |
| `get_registry()` | Get the global component registry |

### ParseResult

| Property | Type | Description |
|----------|------|-------------|
| `root` | `Node` | Parsed root node |
| `errors` | `List[MarkupError]` | List of errors/warnings |
| `success` | `bool` | `True` if no errors |
| `has_warnings` | `bool` | `True` if any warnings |
