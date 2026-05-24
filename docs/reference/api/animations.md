# Animations and Transitions

This page documents the motion and timing primitives currently available in the library.

## What Exists

- `Animation` and `Animator` for chained waits, tweens, and callbacks.
- `Timer` and `Timers` for `after(...)` and `every(...)` scheduling.
- `Timeline`, `KeyFrame`, and `PropertyAnimation` for keyframed sequences.
- `FadeTransition` and `CircleReveal` for full-screen transition effects.
- `SequenceRunner` for orchestrating timelines and transitions.

`Timeline` and `SequenceRunner` now sit on the same scheduler model as `Animator` and `Timers`, so callback timing, restart behavior, and chained motion use one consistent runtime path.

## Sequenced Animator

```python
from arepy_ui import Easing

ui_manager.animator.create().wait(0.08).to(
    panel.style,
    "opacity",
    1.0,
    0.25,
    Easing.EASE_OUT_QUAD,
).call(
    lambda: print("Fade complete")
).start()
```

`Animation` instances are usually created via `Animator.create()` so they can be started and tracked by the scheduler.

## Timers

```python
from arepy_ui import Timers

timers = Timers()
timers.after(0.5, lambda: print("Once"))
timers.every(1.0, lambda: print("Tick"))
timers.update(dt)
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

## Sequence Runner

```python
from arepy_ui import FadeTransition, SequenceRunner, Timeline

runner = SequenceRunner()
runner.add(Timeline(auto_start=False), delay=0.1)
runner.add(FadeTransition(duration=0.35, fade_in=False))
runner.start()
runner.update(dt)
runner.render()
```

## Reference

::: arepy_ui.core.animation.Animation

::: arepy_ui.core.animation.Animator

::: arepy_ui.core.timers.Timer

::: arepy_ui.core.timers.Timers

::: arepy_ui.core.transitions.KeyFrame

::: arepy_ui.core.transitions.PropertyAnimation

::: arepy_ui.core.transitions.Timeline

::: arepy_ui.core.transitions.CircleReveal

::: arepy_ui.core.transitions.FadeTransition

::: arepy_ui.core.transitions.SequenceRunner

::: arepy_ui.core.transitions.TransitionState
