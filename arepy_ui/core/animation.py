from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Callable, Protocol, TypeAlias

from .easing import Easing, apply_easing
from .types import Unit

EasingFunction: TypeAlias = Callable[[float], float]
EasingLike: TypeAlias = int | EasingFunction


def _resolve_property(target: Any, property_name: str) -> tuple[Any, str]:
    obj = target
    parts = property_name.split(".")
    for part in parts[:-1]:
        obj = getattr(obj, part)
    return obj, parts[-1]


def _read_property(target: Any, property_name: str) -> Any:
    obj, attr = _resolve_property(target, property_name)
    return getattr(obj, attr)


def _write_property(target: Any, property_name: str, value: Any) -> None:
    obj, attr = _resolve_property(target, property_name)
    setattr(obj, attr, value)


def _is_number(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _is_vector_like(value: Any) -> bool:
    return hasattr(value, "x") and hasattr(value, "y")


def _is_color_like(value: Any) -> bool:
    return hasattr(value, "r") and hasattr(value, "g") and hasattr(value, "b")


def _copy_value(value: Any) -> Any:
    if isinstance(value, Unit):
        return Unit(value.value, value.type)
    if _is_vector_like(value):
        return type(value)(float(value.x), float(value.y))
    if _is_color_like(value):
        return type(value)(
            int(value.r),
            int(value.g),
            int(value.b),
            int(getattr(value, "a", 255)),
        )
    return value


def _clamp_channel(value: float) -> int:
    return max(0, min(255, round(value)))


def _interpolate_value(start: Any, end: Any, progress: float) -> Any:
    if isinstance(start, Unit):
        if isinstance(end, Unit):
            if start.type != end.type:
                raise ValueError("Unit animations require matching unit types.")
            if progress <= 0.0:
                return Unit(start.value, start.type)
            if progress >= 1.0:
                return Unit(end.value, end.type)
            value = start.value + (end.value - start.value) * progress
            return Unit(value, start.type)

        if not _is_number(end):
            raise TypeError("Unit animations require a numeric or Unit target value.")

        if progress <= 0.0:
            return Unit(start.value, start.type)
        if progress >= 1.0:
            return Unit(float(end), start.type)
        value = start.value + (float(end) - start.value) * progress
        return Unit(value, start.type)

    if _is_number(start) and _is_number(end):
        if progress <= 0.0:
            return start
        if progress >= 1.0:
            return end
        return float(start) + (float(end) - float(start)) * progress

    if _is_vector_like(start) and _is_vector_like(end):
        if progress <= 0.0:
            return _copy_value(start)
        if progress >= 1.0:
            return _copy_value(end)
        return type(start)(
            float(start.x) + (float(end.x) - float(start.x)) * progress,
            float(start.y) + (float(end.y) - float(start.y)) * progress,
        )

    if _is_color_like(start) and _is_color_like(end):
        start_a = int(getattr(start, "a", 255))
        end_a = int(getattr(end, "a", 255))
        if progress <= 0.0:
            return _copy_value(start)
        if progress >= 1.0:
            return _copy_value(end)
        return type(start)(
            _clamp_channel(float(start.r) + (float(end.r) - float(start.r)) * progress),
            _clamp_channel(float(start.g) + (float(end.g) - float(start.g)) * progress),
            _clamp_channel(float(start.b) + (float(end.b) - float(start.b)) * progress),
            _clamp_channel(float(start_a) + (float(end_a) - float(start_a)) * progress),
        )

    raise TypeError(
        f"Unsupported animation values: {type(start).__name__} -> {type(end).__name__}."
    )


def _apply_easing(progress: float, easing: EasingLike) -> float:
    if isinstance(easing, int):
        return apply_easing(progress, easing)
    return easing(progress)


class _AnimationStep(Protocol):
    def reset(self) -> None: ...

    def advance(self, dt: float) -> tuple[float, bool]: ...


@dataclass
class _WaitStep:
    duration: float
    elapsed: float = 0.0

    def reset(self) -> None:
        self.elapsed = 0.0

    def advance(self, dt: float) -> tuple[float, bool]:
        if self.duration <= 0.0:
            return 0.0, True
        remaining = self.duration - self.elapsed
        consumed = min(dt, remaining)
        self.elapsed += consumed
        return consumed, self.elapsed >= self.duration


@dataclass
class _CallStep:
    callback: Callable[[], None]
    called: bool = False

    def reset(self) -> None:
        self.called = False

    def advance(self, dt: float) -> tuple[float, bool]:
        if not self.called:
            self.called = True
            self.callback()
        return 0.0, True


@dataclass
class _TweenStep:
    target: Any
    property_name: str
    end_value: Any
    duration: float
    easing: EasingLike = Easing.LINEAR
    elapsed: float = 0.0
    started: bool = False
    start_value: Any = field(default=None, init=False)

    def reset(self) -> None:
        self.elapsed = 0.0
        self.started = False
        self.start_value = None

    def _ensure_started(self) -> None:
        if self.started:
            return
        self.started = True
        self.start_value = _copy_value(_read_property(self.target, self.property_name))

    def advance(self, dt: float) -> tuple[float, bool]:
        self._ensure_started()

        if self.duration <= 0.0:
            _write_property(
                self.target,
                self.property_name,
                _interpolate_value(self.start_value, self.end_value, 1.0),
            )
            return 0.0, True

        remaining = self.duration - self.elapsed
        consumed = min(dt, remaining)
        self.elapsed += consumed
        progress = min(self.elapsed / self.duration, 1.0)
        eased_progress = _apply_easing(progress, self.easing)
        _write_property(
            self.target,
            self.property_name,
            _interpolate_value(self.start_value, self.end_value, eased_progress),
        )
        return consumed, self.elapsed >= self.duration


class Animation:
    """A sequenced animation built from waits, tweens, and callbacks."""

    def __init__(self) -> None:
        self._animator: Animator | None = None
        self._steps: list[_AnimationStep] = []
        self._current_step_index = 0
        self._started = False
        self._finished = False
        self._cancelled = False

    def bind(self, animator: "Animator") -> "Animation":
        self._animator = animator
        return self

    def _ensure_editable(self) -> None:
        if self._started:
            raise RuntimeError("Cannot modify an animation after start().")

    def wait(self, duration: float) -> "Animation":
        self._ensure_editable()
        if duration < 0.0:
            raise ValueError("Animation wait duration must be >= 0.")
        self._steps.append(_WaitStep(duration=duration))
        return self

    def to(
        self,
        target: Any,
        property_name: str,
        end_value: Any,
        duration: float,
        easing: EasingLike = Easing.LINEAR,
    ) -> "Animation":
        self._ensure_editable()
        if duration < 0.0:
            raise ValueError("Animation duration must be >= 0.")
        self._steps.append(
            _TweenStep(
                target=target,
                property_name=property_name,
                end_value=_copy_value(end_value),
                duration=duration,
                easing=easing,
            )
        )
        return self

    def call(self, callback: Callable[[], None]) -> "Animation":
        self._ensure_editable()
        self._steps.append(_CallStep(callback=callback))
        return self

    def start(self) -> "Animation":
        if self._animator is None:
            raise RuntimeError(
                "Animation must be created by Animator.create() before start()."
            )
        if self._started:
            raise RuntimeError("Animation has already been started.")

        self._started = True
        self._finished = False
        self._cancelled = False
        self._current_step_index = 0
        for step in self._steps:
            step.reset()
        self._animator._activate(self)
        return self

    def cancel(self) -> None:
        self._cancelled = True

    def update(self, dt: float) -> bool:
        if self._cancelled or self._finished:
            return False

        remaining = max(0.0, dt)
        while self._current_step_index < len(self._steps):
            step = self._steps[self._current_step_index]
            consumed, completed = step.advance(remaining)
            remaining = max(0.0, remaining - consumed)

            if not completed:
                return True

            self._current_step_index += 1

        self._finished = True
        return False

    @property
    def is_finished(self) -> bool:
        return self._finished


class Animator:
    """Runs active animations built with the fluent Animation API."""

    def __init__(self) -> None:
        self._animations: list[Animation] = []
        self._queued_animations: list[Animation] = []
        self._is_updating = False

    @property
    def animations(self) -> tuple[Animation, ...]:
        return tuple(self._animations + self._queued_animations)

    def __len__(self) -> int:
        return len(self._animations)

    def create(self) -> Animation:
        return Animation().bind(self)

    def clear(self) -> None:
        for animation in self._animations:
            animation.cancel()
        for animation in self._queued_animations:
            animation.cancel()
        self._animations.clear()
        self._queued_animations.clear()

    def update(self, dt: float) -> None:
        if dt < 0.0:
            raise ValueError("Animator delta time must be >= 0.")

        active: list[Animation] = []
        self._is_updating = True
        try:
            for animation in self._animations:
                if animation.update(dt):
                    active.append(animation)
        finally:
            self._is_updating = False

        if self._queued_animations:
            active.extend(self._queued_animations)
            self._queued_animations.clear()

        self._animations = active

    def _activate(self, animation: Animation) -> None:
        if self._is_updating:
            self._queued_animations.append(animation)
            return
        self._animations.append(animation)
