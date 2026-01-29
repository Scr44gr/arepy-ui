# Tabs

Tabbed container for switching between content panels.

## Usage

```python
from arepy_ui import Tabs, Node, Text

tabs = Tabs(
    labels=["Inventory", "Stats", "Settings"],
    contents=[
        inventory_panel,
        stats_panel,
        settings_panel,
    ],
    on_tab_change=lambda idx: print(f"Tab: {idx}"),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `labels` | `list[str]` | required | Tab labels |
| `contents` | `list[Node]` | required | Content panels |
| `selected_index` | `int` | `0` | Initially selected tab |
| `on_tab_change` | `Callable[[int], None]` | `None` | Called on tab change |
| `style` | `Style` | `None` | Additional styling |

## Properties

```python
tabs = Tabs(labels=["A", "B", "C"], contents=[...])

# Get selected index
current = tabs.selected_index

# Change tab programmatically
tabs.selected_index = 1
```

## Examples

### Character Menu

```python
Tabs(
    labels=["Inventory", "Equipment", "Skills", "Quests"],
    contents=[
        create_inventory_panel(),
        create_equipment_panel(),
        create_skills_panel(),
        create_quests_panel(),
    ],
)
```

### Settings Page

```python
Tabs(
    labels=["Video", "Audio", "Controls", "Gameplay"],
    contents=[
        Node(children=[
            Checkbox(label="Fullscreen", on_change=set_fullscreen),
            Select(options=["Low", "Medium", "High"], on_change=set_quality),
        ]),
        Node(children=[
            Slider(value=100, on_change=set_master_volume),
            Slider(value=80, on_change=set_music_volume),
        ]),
        Node(children=[Text("Key bindings...")]),
        Node(children=[
            Checkbox(label="Show tutorials", checked=True),
        ]),
    ],
)
```

### Simple Two-Tab Layout

```python
tabs = Tabs(
    labels=["Tab 1", "Tab 2"],
    contents=[
        Text("Content for tab 1"),
        Text("Content for tab 2"),
    ],
    on_tab_change=lambda i: print(f"Switched to tab {i}"),
)
```
