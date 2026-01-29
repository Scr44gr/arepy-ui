from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from arepy_ui import Node, Style

from .easing import Easing, apply_easing
from .types import Unit


@dataclass
class Animation:
    target: "Node | Style"  # The object to animate (usually a Node or Style)
    property_name: str
    start_value: float
    end_value: float
    duration: float
    easing: int  # Easing constant (e.g., Easing.EASE_OUT_QUAD)

    elapsed: float = 0.0
    is_finished: bool = False
    on_complete: Optional[Callable[[], None]] = None

    def update(self, dt: float):
        if self.is_finished:
            return

        self.elapsed += dt
        t: int | float = min(self.elapsed / self.duration, 1.0)
        eased_t: int | float = apply_easing(t, self.easing)

        current_value: int | float = (
            self.start_value + (self.end_value - self.start_value) * eased_t
        )

        # Use setattr to update the property
        # Handle nested properties if needed (e.g. style.opacity)
        if "." in self.property_name:
            obj = self.target
            parts = self.property_name.split(".")
            for part in parts[:-1]:
                obj = getattr(obj, part)
            final_attr = parts[-1]
        else:
            obj = self.target
            final_attr = self.property_name

        # Check if the property is a Unit and handle accordingly
        current_attr = getattr(obj, final_attr)
        if isinstance(current_attr, Unit):
            # Preserve the Unit type and only change the value
            new_unit = Unit(current_value, current_attr.type)
            setattr(obj, final_attr, new_unit)
        else:
            setattr(obj, final_attr, current_value)

        if t >= 1.0:
            self.is_finished = True
            if self.on_complete:
                self.on_complete()


class Animator:
    def __init__(self):
        self.animations: list[Animation] = []

    def add(self, animation: Animation):
        self.animations.append(animation)

    def update(self, dt: float):
        active_animations: list[Animation] = []
        for anim in self.animations:
            anim.update(dt)
            if not anim.is_finished:
                active_animations.append(anim)
        self.animations: list[Animation] = active_animations
