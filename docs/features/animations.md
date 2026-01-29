# Animations

Animate UI properties with the built-in tweening system.

## Basic Animation

```python
from arepy_ui import Animation, Easing

anim = Animation(
    target=my_node,
    property="style.background_color.r",
    from_value=0,
    to_value=255,
    duration=0.5,
    easing=Easing.EASE_OUT,
)

ui_manager.animator.add(anim)
```

## Animation Class

```python
Animation(
    target=node,           # Target object
    property="path.to.prop", # Property path (dot notation)
    from_value=0,          # Start value
    to_value=100,          # End value
    duration=1.0,          # Duration in seconds
    easing=Easing.LINEAR,  # Easing function
    on_complete=callback,  # Called when done
)
```

## Easing Functions

```python
from arepy_ui import Easing

Easing.LINEAR          # Constant speed
Easing.EASE_IN         # Slow start
Easing.EASE_OUT        # Slow end
Easing.EASE_IN_OUT     # Slow start and end
Easing.EASE_IN_QUAD    # Quadratic ease in
Easing.EASE_OUT_QUAD   # Quadratic ease out
Easing.EASE_IN_OUT_QUAD
Easing.EASE_OUT_BOUNCE # Bouncy end
Easing.EASE_OUT_ELASTIC # Elastic end
```

## Animator

The UIManager has a built-in animator:

```python
# Add animation
ui_manager.animator.add(anim)

# Remove animation
ui_manager.animator.remove(anim)

# Clear all animations
ui_manager.animator.clear()
```

## Examples

### Fade In

```python
Animation(
    target=panel,
    property="style.opacity",
    from_value=0,
    to_value=1,
    duration=0.3,
    easing=Easing.EASE_OUT,
)
```

### Slide In

```python
Animation(
    target=panel,
    property="style.left",
    from_value=-200,
    to_value=0,
    duration=0.4,
    easing=Easing.EASE_OUT_QUAD,
)
```

### Color Pulse

```python
def pulse_red():
    ui_manager.animator.add(Animation(
        target=button,
        property="style.background_color.r",
        from_value=100,
        to_value=255,
        duration=0.2,
        on_complete=pulse_back,
    ))

def pulse_back():
    ui_manager.animator.add(Animation(
        target=button,
        property="style.background_color.r",
        from_value=255,
        to_value=100,
        duration=0.2,
    ))
```

### Scale Effect

```python
# Grow on hover
def on_hover_enter():
    ui_manager.animator.add(Animation(
        target=card,
        property="style.scale",
        from_value=1.0,
        to_value=1.1,
        duration=0.15,
        easing=Easing.EASE_OUT,
    ))

def on_hover_exit():
    ui_manager.animator.add(Animation(
        target=card,
        property="style.scale",
        from_value=1.1,
        to_value=1.0,
        duration=0.15,
    ))
```

### Chained Animations

```python
def animate_sequence():
    # First animation
    anim1 = Animation(
        target=box,
        property="computed_x",
        from_value=0,
        to_value=100,
        duration=0.5,
        on_complete=lambda: ui_manager.animator.add(anim2),
    )
    
    # Second animation (after first completes)
    anim2 = Animation(
        target=box,
        property="computed_y",
        from_value=0,
        to_value=100,
        duration=0.5,
    )
    
    ui_manager.animator.add(anim1)
```
