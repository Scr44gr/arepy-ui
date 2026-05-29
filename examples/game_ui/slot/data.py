from __future__ import annotations

from dataclasses import dataclass

from arepy_ui import Color

from ..theme import Palette, hex_color


@dataclass(frozen=True)
class SlotPrize:
    number: int
    name_key: str
    kind_key: str
    description_key: str
    accent: Color


@dataclass
class SlotMachineState:
    current_index: int = 4
    target_index: int = 4
    reel_position: float = 4.0
    spin_start_position: float = 4.0
    spin_target_position: float = 4.0
    spin_elapsed: float = 0.0
    spin_duration: float = 0.0
    is_spinning: bool = False
    flash: float = 0.0
    elapsed: float = 0.0


def build_slot_prizes(palette: Palette) -> list[SlotPrize]:
    return [
        SlotPrize(0, "slot.prize.0.name", "slot.kind.weapon", "slot.prize.0.description", palette.steel),
        SlotPrize(1, "slot.prize.1.name", "slot.kind.utility", "slot.prize.1.description", hex_color("89a477")),
        SlotPrize(2, "slot.prize.2.name", "slot.kind.weapon", "slot.prize.2.description", palette.red_hover),
        SlotPrize(3, "slot.prize.3.name", "slot.kind.utility", "slot.prize.3.description", palette.royal),
        SlotPrize(4, "slot.prize.4.name", "slot.kind.weapon", "slot.prize.4.description", palette.brass),
        SlotPrize(5, "slot.prize.5.name", "slot.kind.utility", "slot.prize.5.description", hex_color("a6b04f")),
        SlotPrize(6, "slot.prize.6.name", "slot.kind.weapon", "slot.prize.6.description", hex_color("cc8e81")),
        SlotPrize(7, "slot.prize.7.name", "slot.kind.utility", "slot.prize.7.description", hex_color("cae6d9")),
        SlotPrize(8, "slot.prize.8.name", "slot.kind.weapon", "slot.prize.8.description", hex_color("ff9900")),
    ]
