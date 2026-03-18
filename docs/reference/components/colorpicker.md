# ColorPicker

HSV color picker component.

::: arepy_ui.components.colorpicker.ColorPicker

Example with markup:

```python
from arepy_ui.markup import load_aui

handlers = {
    "on_theme_change": on_theme_change,
}

result = load_aui("ui/settings.aui", handlers=handlers)
if result.success and result.root is not None:
    ui_manager.set_root(result.root)
```
