from __future__ import annotations

from dataclasses import dataclass

from ..scale import inventory_px
from .data import InventoryState, PlacedInventoryItem


CELL_SIZE = inventory_px(28)
CELL_GAP = max(2, inventory_px(3))


@dataclass(frozen=True)
class InventoryDropPreview:
    column: int
    row: int
    width: int
    height: int
    valid: bool


def auto_place_items(state: InventoryState) -> list[PlacedInventoryItem]:
    occupancy = [[False for _ in range(state.columns)] for _ in range(state.rows)]
    placements: list[PlacedInventoryItem] = []

    ordered_items = sorted(
        state.items,
        key=lambda item: (item.width * item.height, item.height, item.width, item.weight),
        reverse=True,
    )

    for item in ordered_items:
        placed = False
        for row in range(state.rows - item.height + 1):
            for column in range(state.columns - item.width + 1):
                if not _can_place(occupancy, column, row, item.width, item.height):
                    continue

                _mark_cells(occupancy, column, row, item.width, item.height)
                placements.append(
                    PlacedInventoryItem(
                        item=item,
                        column=column,
                        row=row,
                    )
                )
                placed = True
                break
            if placed:
                break

        if not placed:
            raise ValueError(f"Item {item.id} does not fit in the inventory grid")

    return placements


def grid_pixel_width(columns: int) -> int:
    return columns * CELL_SIZE + max(0, columns - 1) * CELL_GAP


def grid_pixel_height(rows: int) -> int:
    return rows * CELL_SIZE + max(0, rows - 1) * CELL_GAP


def item_pixel_size(width: int, height: int) -> tuple[int, int]:
    return (
        width * CELL_SIZE + max(0, width - 1) * CELL_GAP,
        height * CELL_SIZE + max(0, height - 1) * CELL_GAP,
    )


def cell_to_pixel(column: int, row: int) -> tuple[int, int]:
    step = CELL_SIZE + CELL_GAP
    return (column * step, row * step)


def find_placement(
    placements: list[PlacedInventoryItem],
    item_id: str,
) -> PlacedInventoryItem:
    for placement in placements:
        if placement.item.id == item_id:
            return placement
    raise ValueError(f"Unknown inventory item: {item_id}")


def can_place_item(
    state: InventoryState,
    placements: list[PlacedInventoryItem],
    item_id: str,
    width: int,
    height: int,
    column: int,
    row: int,
) -> bool:
    if column < 0 or row < 0:
        return False
    if column + width > state.columns or row + height > state.rows:
        return False

    for placement in placements:
        if placement.item.id == item_id:
            continue
        if _overlaps(
            column,
            row,
            width,
            height,
            placement.column,
            placement.row,
            placement.item.width,
            placement.item.height,
        ):
            return False

    return True


def build_drop_preview(
    state: InventoryState,
    placements: list[PlacedInventoryItem],
    item_id: str,
    width: int,
    height: int,
    left: float,
    top: float,
) -> InventoryDropPreview | None:
    cell = pixel_to_cell(state, width, height, left, top)
    if cell is None:
        return None

    column, row = cell
    return InventoryDropPreview(
        column=column,
        row=row,
        width=width,
        height=height,
        valid=can_place_item(state, placements, item_id, width, height, column, row),
    )


def move_item(
    placements: list[PlacedInventoryItem],
    item_id: str,
    column: int,
    row: int,
) -> list[PlacedInventoryItem]:
    updated: list[PlacedInventoryItem] = []
    for placement in placements:
        if placement.item.id == item_id:
            updated.append(
                PlacedInventoryItem(
                    item=placement.item,
                    column=column,
                    row=row,
                )
            )
            continue
        updated.append(placement)
    return updated


def pixel_to_cell(
    state: InventoryState,
    width: int,
    height: int,
    left: float,
    top: float,
) -> tuple[int, int] | None:
    max_left = grid_pixel_width(state.columns) - item_pixel_size(width, height)[0]
    max_top = grid_pixel_height(state.rows) - item_pixel_size(width, height)[1]
    tolerance = CELL_SIZE / 2

    if left < -tolerance or top < -tolerance:
        return None
    if left > max_left + tolerance or top > max_top + tolerance:
        return None

    step = CELL_SIZE + CELL_GAP
    column = int(round(left / step))
    row = int(round(top / step))

    if column < 0 or row < 0:
        return None
    if column + width > state.columns or row + height > state.rows:
        return None

    return (column, row)


def _can_place(
    occupancy: list[list[bool]],
    column: int,
    row: int,
    width: int,
    height: int,
) -> bool:
    for current_row in range(row, row + height):
        for current_column in range(column, column + width):
            if occupancy[current_row][current_column]:
                return False
    return True


def _overlaps(
    first_column: int,
    first_row: int,
    first_width: int,
    first_height: int,
    second_column: int,
    second_row: int,
    second_width: int,
    second_height: int,
) -> bool:
    return not (
        first_column + first_width <= second_column
        or second_column + second_width <= first_column
        or first_row + first_height <= second_row
        or second_row + second_height <= first_row
    )


def _mark_cells(
    occupancy: list[list[bool]],
    column: int,
    row: int,
    width: int,
    height: int,
) -> None:
    for current_row in range(row, row + height):
        for current_column in range(column, column + width):
            occupancy[current_row][current_column] = True
