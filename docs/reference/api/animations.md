# Animations and Transitions

This page documents the animation primitives that actually exist in the library today.

## What Exists

- `Animation` and `Animator` for simple property tweens.
- `Timeline`, `KeyFrame`, and `PropertyAnimation` for keyframed sequences.
- `FadeTransition` and `CircleReveal` for full-screen transition effects.
- `SequenceRunner` for orchestrating timelines and transitions.

## Basic Tween

```python
from arepy_ui import Animation, Easing

anim = Animation(
    target=panel.style,
    property_name="opacity",
    start_value=0.0,
    end_value=1.0,
    duration=0.25,
    easing=Easing.EASE_OUT_QUAD,
)

ui_manager.animator.add(anim)
```

## Keyframed Timeline

```python
from arepy_ui import Easing, Timeline

timeline = Timeline(auto_start=False)
timeline.add_animation(
    panel.style,
    "opacity",
    [
        (0.0, 0.0, None),
        (0.15, 1.0, Easing.EASE_OUT_CUBIC),
    ],
)
timeline.add_event(0.15, lambda: print("Fade complete"))
timeline.start()
timeline.update(dt)
```

## Full-Screen Fade

```python
from arepy_ui import FadeTransition

fade = FadeTransition(duration=0.5, fade_in=False)
fade.update(dt)
fade.render()
```

## Reference

::: arepy_ui.core.animation.Animation

::: arepy_ui.core.animation.Animator

::: arepy_ui.core.transitions.KeyFrame

::: arepy_ui.core.transitions.PropertyAnimation

::: arepy_ui.core.transitions.Timeline

::: arepy_ui.core.transitions.CircleReveal

::: arepy_ui.core.transitions.FadeTransition

::: arepy_ui.core.transitions.SequenceRunner

::: arepy_ui.core.transitions.TransitionState
