# TextInput

Text input field with cursor, selection, and placeholder support.

## Usage

```python
from arepy_ui import TextInput, Unit

# Basic input
input = TextInput(
    placeholder="Enter your name...",
    on_change=lambda text: print(f"Input: {text}"),
)

# With initial value
input = TextInput(
    value="Default text",
    on_change=handle_change,
    width=Unit.px(250),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `str` | `""` | Initial text value |
| `placeholder` | `str` | `""` | Placeholder text |
| `on_change` | `Callable[[str], None]` | `None` | Called when text changes |
| `on_submit` | `Callable[[str], None]` | `None` | Called on Enter key |
| `width` | `Unit` | `Unit.px(200)` | Input width |
| `height` | `Unit` | `Unit.px(32)` | Input height |
| `font_size` | `float` | `14.0` | Text size |
| `style` | `Style` | `None` | Additional styling |

## Properties

```python
input = TextInput()

# Get current value
current = input.value

# Set value programmatically
input.value = "New text"

# Focus is managed by UIManager
# The input handles focus internally when clicked
# To programmatically focus, you would need to access internal methods
# or trigger a click event on the input
```

## Events

### on_change

Called whenever the text content changes:

```python
def handle_change(text: str):
    print(f"Current text: {text}")

TextInput(on_change=handle_change)
```

### on_submit

Called when the user presses Enter:

```python
def handle_submit(text: str):
    print(f"Submitted: {text}")
    # Clear the input
    input.value = ""

input = TextInput(on_submit=handle_submit)
```

## Examples

### Search Box

```python
TextInput(
    placeholder="Search...",
    on_submit=lambda q: search(q),
    width=Unit.px(300),
    style=Style(border_radius=20),
)
```

### Form Input

```python
Node(
    style=Style(flex_direction=FlexDirection.COLUMN, gap=5),
    children=[
        Text("Username", size=12),
        TextInput(
            placeholder="Enter username",
            on_change=lambda v: set_username(v),
        ),
    ],
)
```
