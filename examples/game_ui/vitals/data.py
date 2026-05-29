from __future__ import annotations

from dataclasses import dataclass

from arepy_ui import Color

from ..theme import Palette


@dataclass(frozen=True)
class VitalBar:
    label_key: str
    current: int
    maximum: int
    fill: Color
    background: Color

    @property
    def ratio(self) -> float:
        if self.maximum <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current / self.maximum))


@dataclass(frozen=True)
class PlayerVitals:
    health: VitalBar
    stamina: VitalBar

    def bars(self) -> tuple[VitalBar, VitalBar]:
        return (self.health, self.stamina)


def build_demo_vitals(palette: Palette) -> PlayerVitals:
    return PlayerVitals(
        health=VitalBar(
            label_key="vitals.health",
            current=164,
            maximum=190,
            fill=palette.health_fill,
            background=palette.health_back,
        ),
        stamina=VitalBar(
            label_key="vitals.stamina",
            current=96,
            maximum=120,
            fill=palette.stamina_fill,
            background=palette.stamina_back,
        ),
    )
