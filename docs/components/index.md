# Components

arepy-ui includes a set of ready-to-use UI components.

## Available Components

| Component | Description |
|-----------|-------------|
| [Text](text.md) | Text rendering with custom fonts |
| [Button](button.md) | Clickable button with hover states |
| [TextInput](textinput.md) | Text field with cursor and selection |
| [Checkbox](checkbox.md) | Toggle with label |
| [Slider](slider.md) | Horizontal/vertical value slider |
| [Select](select.md) | Dropdown menu |
| [Tabs](tabs.md) | Tabbed container |
| [Image](image.md) | Texture display with fit modes |
| [ScrollView](scrollview.md) | Scrollable container |
| [ProgressBar](progressbar.md) | Progress indicator |
| [Canvas](canvas.md) | Custom drawing |
| [Video](video.md) | Video playback (experimental) |
| [ColorPicker](colorpicker.md) | HSV color selection |

## Common Patterns

All components inherit from `Node`, so they support:

- **Children** - Add nested nodes
- **Styles** - Apply layout and visual styles  
- **Events** - Handle hover, click, etc.

```python
from arepy_ui import Button, Text, Style, Spacing

# Components can have children
button = Button("Save", on_click=save)
button.add_child(Icon("save"))  # Add icon inside button

# Components accept style overrides
text = Text("Hello", style=Style(margin=Spacing.all(10)))
```
