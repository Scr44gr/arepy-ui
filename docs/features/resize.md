# Window Resize

Handle window resizing with different strategies.

## Resize Modes

```python
from arepy_ui import UIConfig, ResizeMode

config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)
ui_manager = UIManager.from_engine(game, config=config)
```

### RESPONSIVE (Default)

Layout recalculates to fit new window size. Best for desktop applications.

```python
UIConfig(resize_mode=ResizeMode.RESPONSIVE)
```

### FIXED

Layout stays at reference resolution. UI does not scale or reflow.

```python
UIConfig(
    resize_mode=ResizeMode.FIXED,
    reference_width=1280,
    reference_height=720,
)
```

### SCALE_FIT

Layout scales to fit window, maintaining aspect ratio. May have letterboxing.

```python
UIConfig(
    resize_mode=ResizeMode.SCALE_FIT,
    reference_width=1280,
    reference_height=720,
)
```

### SCALE_FILL

Layout scales to fill window, maintaining aspect ratio. May crop edges.

```python
UIConfig(
    resize_mode=ResizeMode.SCALE_FILL,
    reference_width=1280,
    reference_height=720,
)
```

## Resize Callback

React to window size changes:

```python
def on_resize(width: int, height: int):
    print(f"Window resized to {width}x{height}")

config = UIConfig(
    resize_mode=ResizeMode.RESPONSIVE,
    on_resize=on_resize,
)
```

## Layout Callbacks

Execute code before/after layout recalculation:

```python
config = UIConfig(
    on_before_layout=lambda: print("Recalculating..."),
    on_after_layout=lambda: print("Layout complete"),
)
```

## Debouncing

Delay layout recalculation during rapid resizing:

```python
config = UIConfig(
    layout_debounce_ms=100,  # Wait 100ms after last resize
)
```

## Helpers

```python
# Get reference resolution
ref_w, ref_h = ui_manager.get_reference_size()

# Get current window size
curr_w, curr_h = ui_manager.get_current_size()

# Get scale transform (for SCALE_* modes)
transform = ui_manager.get_scale_transform()
```

## Examples

### Responsive Game UI

```python
config = UIConfig(
    resize_mode=ResizeMode.RESPONSIVE,
    on_resize=lambda w, h: update_ui_layout(w, h),
)
```

### Fixed Resolution Game

```python
config = UIConfig(
    resize_mode=ResizeMode.SCALE_FIT,
    reference_width=1920,
    reference_height=1080,
)
```

### Mobile-Style Scaling

```python
config = UIConfig(
    resize_mode=ResizeMode.SCALE_FILL,
    reference_width=720,
    reference_height=1280,
)
```
