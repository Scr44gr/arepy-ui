# Modals

Display overlays and dialog boxes on top of the main UI.

## Basic Usage

```python
# Create modal content
modal = Node(
    style=Style(
        width=Unit.px(300),
        height=Unit.px(200),
        background_color=Color(50, 50, 50),
        border_radius=10,
        padding=Spacing.all(20),
    ),
    children=[
        Text("Are you sure?", size=18),
        Button("Yes", on_click=confirm),
        Button("No", on_click=lambda: ui_manager.close_modal()),
    ],
)

# Show modal
ui_manager.show_modal(modal)
```

## show_modal()

```python
ui_manager.show_modal(
    modal,                    # Node to display
    backdrop=True,            # Show dark backdrop
    close_on_backdrop=True,   # Close when clicking backdrop
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modal` | `Node` | required | Content to display |
| `backdrop` | `bool` | `True` | Show dark overlay |
| `close_on_backdrop` | `bool` | `True` | Click outside to close |

## Closing Modals

```python
# Close specific modal
ui_manager.close_modal(modal)

# Close topmost modal
ui_manager.close_modal()

# Close all modals
ui_manager.close_all_modals()

# Check if modal is open
if ui_manager.has_modal:
    print("Modal is open")
```

## Examples

### Confirmation Dialog

```python
def show_confirm(message: str, on_confirm):
    modal = Node(
        style=Style(
            width=Unit.px(300),
            padding=Spacing.all(20),
            background_color=Color(45, 45, 45),
            border_radius=8,
            flex_direction=FlexDirection.COLUMN,
            gap=15,
        ),
        children=[
            Text(message, size=16),
            Node(
                style=Style(
                    flex_direction=FlexDirection.ROW,
                    justify_content=JustifyContent.FLEX_END,
                    gap=10,
                ),
                children=[
                    Button("Cancel", on_click=lambda: ui_manager.close_modal()),
                    Button("Confirm", on_click=lambda: (on_confirm(), ui_manager.close_modal())),
                ],
            ),
        ],
    )
    ui_manager.show_modal(modal)

# Usage
show_confirm("Delete this item?", on_confirm=delete_item)
```

### Pause Menu

```python
def show_pause_menu():
    menu = Node(
        style=Style(
            width=Unit.px(250),
            padding=Spacing.all(30),
            background_color=Color(30, 30, 30, 240),
            border_radius=10,
            flex_direction=FlexDirection.COLUMN,
            gap=10,
            align_items=AlignItems.STRETCH,
        ),
        children=[
            Text("PAUSED", size=24),
            Button("Resume", on_click=resume_game),
            Button("Settings", on_click=show_settings),
            Button("Quit", on_click=quit_game),
        ],
    )
    ui_manager.show_modal(menu, close_on_backdrop=False)
```

### Loading Screen

```python
loading_bar = ProgressBar(value=0, width=Unit.px(250))

loading_modal = Node(
    style=Style(
        width=Unit.px(300),
        padding=Spacing.all(30),
        background_color=Color(20, 20, 20),
        border_radius=8,
        flex_direction=FlexDirection.COLUMN,
        gap=15,
        align_items=AlignItems.CENTER,
    ),
    children=[
        Text("Loading...", size=18),
        loading_bar,
    ],
)

# Show non-dismissable loading modal
ui_manager.show_modal(loading_modal, close_on_backdrop=False)

# Update progress
loading_bar.value = 0.5

# Close when done
ui_manager.close_modal(loading_modal)
```

### Stacked Modals

Modals can be stacked. The topmost receives input.

```python
# First modal
ui_manager.show_modal(settings_modal)

# Second modal on top
ui_manager.show_modal(confirm_modal)

# close_modal() closes the topmost
ui_manager.close_modal()  # Closes confirm_modal
ui_manager.close_modal()  # Closes settings_modal
```
