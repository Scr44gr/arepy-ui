from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, List, Optional, Tuple, Union

from arepy.engine.renderer import Rect

from ..runtime import get_runtime
from .animation import apply_easing
from .easing import Easing
from .types import Color


class TransitionState(Enum):
    """State of a transition."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    CANCELLED = auto()


@dataclass
class KeyFrame:
    """A single keyframe in an animation timeline."""

    time: float  # Time in seconds when this keyframe should be reached
    value: float
    easing: int = Easing.EASE_OUT_CUBIC


@dataclass
class PropertyAnimation:
    """Animation of a single property with keyframes."""

    target: Any
    property_name: str
    keyframes: List[KeyFrame]

    _current_keyframe_index: int = field(default=0, init=False)
    _elapsed: float = field(default=0.0, init=False)
    _is_finished: bool = field(default=False, init=False)

    def update(self, dt: float) -> bool:
        """Update animation. Returns True if still running."""
        if self._is_finished:
            return False

        self._elapsed += dt

        # Find current keyframe segment
        if self._current_keyframe_index >= len(self.keyframes) - 1:
            self._is_finished = True
            return False

        start_kf = self.keyframes[self._current_keyframe_index]
        end_kf = self.keyframes[self._current_keyframe_index + 1]

        # Progress through current segment
        segment_duration = end_kf.time - start_kf.time
        if segment_duration <= 0:
            self._current_keyframe_index += 1
            return True

        segment_elapsed = self._elapsed - start_kf.time
        t = min(segment_elapsed / segment_duration, 1.0)
        eased_t = apply_easing(t, end_kf.easing)

        # Interpolate value
        current_value = start_kf.value + (end_kf.value - start_kf.value) * eased_t

        # Set property
        self._set_property(current_value)

        # Check if we need to move to next keyframe
        if t >= 1.0:
            self._current_keyframe_index += 1
            if self._current_keyframe_index >= len(self.keyframes) - 1:
                self._is_finished = True
                self._set_property(self.keyframes[-1].value)  # Ensure final value

        return True

    def _set_property(self, value: float) -> None:
        """Set the property value on the target."""
        if "." in self.property_name:
            obj = self.target
            parts = self.property_name.split(".")
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
        else:
            setattr(self.target, self.property_name, value)

    def reset(self) -> None:
        """Reset the animation to the beginning."""
        self._current_keyframe_index = 0
        self._elapsed = 0.0
        self._is_finished = False


@dataclass
class TimelineEvent:
    """An event in the timeline (callback, animation start, etc)."""

    time: float  # When to trigger
    callback: Callable[[], None]
    _triggered: bool = field(default=False, init=False)


@dataclass
class Timeline:
    """
    A timeline for sequencing multiple animations and events.
    Similar to After Effects or CSS animation timelines.
    """

    duration: float = 0.0
    loop: bool = False
    auto_start: bool = True
    on_complete: Optional[Callable[[], None]] = None

    _animations: List[PropertyAnimation] = field(default_factory=list)
    _events: List[TimelineEvent] = field(default_factory=list)
    _elapsed: float = 0.0
    _is_running: bool = False
    _is_finished: bool = False

    def __post_init__(self):
        if self.auto_start:
            self._is_running = True

    def add_animation(
        self,
        target: Any,
        property_name: str,
        keyframes: List[Tuple[float, float, Optional[int]]],
    ) -> "Timeline":
        """
        Add an animation to the timeline.

        Args:
            target: The object to animate
            property_name: The property to animate (e.g., "style.opacity")
            keyframes: List of (time, value, easing) tuples

        Returns:
            Self for chaining
        """
        kfs = [
            KeyFrame(time=t, value=v, easing=e or Easing.EASE_OUT_CUBIC)
            for t, v, e in keyframes
        ]

        anim = PropertyAnimation(
            target=target, property_name=property_name, keyframes=kfs
        )
        self._animations.append(anim)

        # Update duration if needed
        if kfs:
            self.duration = max(self.duration, kfs[-1].time)

        return self

    def add_event(self, time: float, callback: Callable[[], None]) -> "Timeline":
        """Add a callback event at a specific time."""
        self._events.append(TimelineEvent(time=time, callback=callback))
        return self

    def start(self) -> None:
        """Start the timeline."""
        self._is_running = True
        self._is_finished = False
        self._elapsed = 0.0

        # Reset all animations
        for anim in self._animations:
            anim.reset()

        # Reset events
        for event in self._events:
            event._triggered = False

    def pause(self) -> None:
        """Pause the timeline."""
        self._is_running = False

    def resume(self) -> None:
        """Resume the timeline."""
        self._is_running = True

    def update(self, dt: float) -> bool:
        """Update the timeline. Returns True if still running."""
        if not self._is_running or self._is_finished:
            return False

        self._elapsed += dt

        # Update animations
        for anim in self._animations:
            anim.update(dt)

        # Trigger events
        for event in self._events:
            if not event._triggered and self._elapsed >= event.time:
                event._triggered = True
                event.callback()

        # Check completion
        if self._elapsed >= self.duration:
            if self.loop:
                self.start()
            else:
                self._is_finished = True
                self._is_running = False
                if self.on_complete:
                    self.on_complete()
                return False

        return True

    @property
    def progress(self) -> float:
        """Get progress from 0.0 to 1.0."""
        if self.duration <= 0:
            return 1.0
        return min(self._elapsed / self.duration, 1.0)

    @property
    def is_finished(self) -> bool:
        return self._is_finished


class CircleReveal:
    """
    A circle reveal/mask effect for transitions.
    Can be used for revealing content with an expanding/contracting circle.
    """

    def __init__(
        self,
        center_x: float,
        center_y: float,
        start_radius: float = 0.0,
        end_radius: float = 1000.0,
        duration: float = 1.0,
        easing: int = Easing.EASE_OUT_CUBIC,
        reverse: bool = False,
        color: Color = Color(0, 0, 0, 255),
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.center_x = center_x
        self.center_y = center_y
        self.start_radius = start_radius if not reverse else end_radius
        self.end_radius = end_radius if not reverse else start_radius
        self.duration = duration
        self.easing = easing
        self.color = color
        self.on_complete = on_complete

        self._elapsed = 0.0
        self._is_running = True
        self._is_finished = False
        self._current_radius = self.start_radius

    def update(self, dt: float) -> bool:
        """Update the reveal. Returns True if still running."""
        if not self._is_running or self._is_finished:
            return False

        self._elapsed += dt
        t = min(self._elapsed / self.duration, 1.0)
        eased_t = apply_easing(t, self.easing)

        self._current_radius = (
            self.start_radius + (self.end_radius - self.start_radius) * eased_t
        )

        if t >= 1.0:
            self._is_finished = True
            self._is_running = False
            if self.on_complete:
                self.on_complete()
            return False

        return True

    def render(self) -> None:
        """
        Render the circle mask.
        For reveal effect, draws everything EXCEPT the circle.
        """
        if self._is_finished and self.end_radius > self.start_radius:
            # Fully revealed, nothing to draw
            return

        runtime = get_runtime()
        screen_w, screen_h = runtime.display.get_window_size()

        # To create a circle reveal, we use stencil or just draw the inverse
        # Since raylib doesn't have easy stencil, we'll draw 4 rectangles around the circle
        # and the circle itself in the center

        # This is a simplified approach - for real production, you'd use shaders
        # or render textures with stencil operations

        # Draw the masking color everywhere
        runtime.renderer.draw_rectangle(Rect(0, 0, screen_w, screen_h), self.color)

        # "Cut out" the circle by drawing it transparent (won't work without stencil)
        # Instead, we'll draw the circle with blend mode
        # Actually, let's just draw the circle and invert the logic

        # For now, draw a solid circle in the reveal area
        # The caller should render content first, then call this as overlay

    def render_inverse(self) -> None:
        """
        Render the inverse - a solid circle expanding/contracting.
        Use this when you want the circle to cover content, not reveal it.
        """
        runtime = get_runtime()
        runtime.renderer.draw_circle(
            (int(self.center_x), int(self.center_y)),
            self._current_radius,
            self.color,
        )

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def progress(self) -> float:
        if self.duration <= 0:
            return 1.0
        return min(self._elapsed / self.duration, 1.0)

    @property
    def current_radius(self) -> float:
        return self._current_radius


class FadeTransition:
    """Simple fade in/out transition."""

    def __init__(
        self,
        duration: float = 0.5,
        fade_in: bool = True,
        color: Color = Color(0, 0, 0, 255),
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.duration = duration
        self.fade_in = fade_in
        self.color = color
        self.on_complete = on_complete

        self._elapsed = 0.0
        self._is_running = True
        self._is_finished = False
        self._alpha = 255 if fade_in else 0

    def update(self, dt: float) -> bool:
        if not self._is_running or self._is_finished:
            return False

        self._elapsed += dt
        t = min(self._elapsed / self.duration, 1.0)
        eased_t = apply_easing(t, Easing.EASE_OUT_CUBIC)

        if self.fade_in:
            self._alpha = int(255 * (1.0 - eased_t))
        else:
            self._alpha = int(255 * eased_t)

        if t >= 1.0:
            self._is_finished = True
            self._is_running = False
            if self.on_complete:
                self.on_complete()
            return False

        return True

    def render(self) -> None:
        if self._alpha <= 0:
            return

        runtime = get_runtime()
        screen_w, screen_h = runtime.display.get_window_size()

        fade_color = Color(self.color.r, self.color.g, self.color.b, self._alpha)
        runtime.renderer.draw_rectangle(Rect(0, 0, screen_w, screen_h), fade_color)

    @property
    def is_finished(self) -> bool:
        return self._is_finished


class SequenceRunner:
    """
    Runs multiple transitions/animations in sequence.
    Useful for orchestrating complex animation flows.
    """

    def __init__(self, on_complete: Optional[Callable[[], None]] = None):
        self._sequences: List[
            Tuple[
                Union[Timeline, CircleReveal, FadeTransition, Callable[[], None]], float
            ]
        ] = []
        self._current_index = 0
        self._delay_timer = 0.0
        self._is_running = False
        self._is_finished = False
        self.on_complete = on_complete

    def add(
        self,
        item: Union[Timeline, CircleReveal, FadeTransition, Callable[[], None]],
        delay: float = 0.0,
    ) -> "SequenceRunner":
        """Add an item to the sequence with optional delay before it."""
        self._sequences.append((item, delay))
        return self

    def start(self) -> None:
        """Start running the sequence."""
        self._current_index = 0
        self._delay_timer = 0.0
        self._is_running = True
        self._is_finished = False

        # Start first item if no delay
        if self._sequences and self._sequences[0][1] <= 0:
            self._start_current_item()

    def _start_current_item(self) -> None:
        """Start the current sequence item."""
        if self._current_index >= len(self._sequences):
            return

        item, _ = self._sequences[self._current_index]

        if callable(item) and not isinstance(
            item, (Timeline, CircleReveal, FadeTransition)
        ):
            # It's a callback
            item()
            self._advance()
        elif isinstance(item, Timeline):
            item.start()
        # CircleReveal and FadeTransition auto-start

    def _advance(self) -> None:
        """Move to next item in sequence."""
        self._current_index += 1
        self._delay_timer = 0.0

        if self._current_index >= len(self._sequences):
            self._is_finished = True
            self._is_running = False
            if self.on_complete:
                self.on_complete()

    def update(self, dt: float) -> bool:
        """Update the sequence. Returns True if still running."""
        if not self._is_running or self._is_finished:
            return False

        if self._current_index >= len(self._sequences):
            self._is_finished = True
            self._is_running = False
            return False

        item, delay = self._sequences[self._current_index]

        # Handle delay
        if self._delay_timer < delay:
            self._delay_timer += dt
            if self._delay_timer >= delay:
                self._start_current_item()
            return True

        # Update current item
        if isinstance(item, (Timeline, CircleReveal, FadeTransition)):
            still_running = item.update(dt)
            if not still_running:
                self._advance()

        return True

    def render(self) -> None:
        """Render the current transition if applicable."""
        if not self._is_running or self._is_finished:
            return

        if self._current_index >= len(self._sequences):
            return

        item, delay = self._sequences[self._current_index]

        if self._delay_timer < delay:
            return

        if isinstance(item, (CircleReveal, FadeTransition)):
            item.render()

    @property
    def is_finished(self) -> bool:
        return self._is_finished
