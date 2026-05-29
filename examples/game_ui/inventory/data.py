from __future__ import annotations

from dataclasses import dataclass

from arepy_ui import Color

from ..theme import Palette, hex_color


@dataclass(frozen=True)
class InventoryItem:
    id: str
    name_key: str
    width: int
    height: int
    weight: float
    accent: Color


@dataclass(frozen=True)
class InventoryState:
    columns: int
    rows: int
    capacity: float
    items: list[InventoryItem]


@dataclass(frozen=True)
class PlacedInventoryItem:
    item: InventoryItem
    column: int
    row: int


def build_demo_inventory(palette: Palette) -> InventoryState:
    return InventoryState(
        columns=10,
        rows=7,
        capacity=72.0,
        items=[
            InventoryItem("nodachi", "inventory.item.nodachi", 2, 5, 8.6, palette.red_hover),
            InventoryItem("cloak", "inventory.item.cloak", 3, 2, 2.8, palette.royal),
            InventoryItem("chain", "inventory.item.chain", 2, 3, 6.2, palette.brass),
            InventoryItem("relic", "inventory.item.relic", 2, 2, 1.4, hex_color("7fcbb2")),
            InventoryItem("plates", "inventory.item.plates", 3, 2, 7.3, hex_color("8f9ea9")),
            InventoryItem("ore", "inventory.item.ore", 2, 2, 9.1, hex_color("8a6a5f")),
            InventoryItem("medkit", "inventory.item.medkit", 2, 2, 1.2, hex_color("88b7c7")),
            InventoryItem("rations", "inventory.item.rations", 2, 1, 0.7, hex_color("a4a35f")),
            InventoryItem("bolts", "inventory.item.bolts", 1, 3, 1.6, hex_color("a85e4f")),
        ],
    )


def total_weight(state: InventoryState) -> float:
    return sum(item.weight for item in state.items)
