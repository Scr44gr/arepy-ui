from __future__ import annotations

from arepy.engine.renderer import Rect

from ..theme import Palette, with_alpha
from .data import InventoryState
from .layout import InventoryDropPreview, CELL_SIZE, grid_pixel_height, grid_pixel_width, item_pixel_size, cell_to_pixel


def render_inventory_grid(
    renderer,
    rect: Rect,
    state: InventoryState,
    palette: Palette,
    preview: InventoryDropPreview | None = None,
) -> None:
    for row in range(state.rows):
        for column in range(state.columns):
            cell_x = rect.x + cell_to_pixel(column, row)[0]
            cell_y = rect.y + cell_to_pixel(column, row)[1]
            renderer.draw_rectangle_rounded(
                Rect(int(cell_x), int(cell_y), CELL_SIZE, CELL_SIZE),
                0.18,
                5,
                with_alpha(palette.grid_soft, 226),
            )
            renderer.draw_rectangle_rounded_lines(
                Rect(int(cell_x), int(cell_y), CELL_SIZE, CELL_SIZE),
                0.18,
                5,
                with_alpha(palette.grid, 110),
            )

    frame_rect = Rect(int(rect.x), int(rect.y), grid_pixel_width(state.columns), grid_pixel_height(state.rows))
    renderer.draw_rectangle_rounded_lines(
        frame_rect,
        0.04,
        8,
        with_alpha(palette.surface_border, 110),
    )

    if preview is None:
        return

    preview_x, preview_y = cell_to_pixel(preview.column, preview.row)
    preview_width, preview_height = item_pixel_size(preview.width, preview.height)
    preview_rect = Rect(
        int(rect.x + preview_x),
        int(rect.y + preview_y),
        preview_width,
        preview_height,
    )
    highlight = palette.stamina_fill if preview.valid else palette.red
    renderer.draw_rectangle_rounded(
        preview_rect,
        0.16,
        6,
        with_alpha(highlight, 54),
    )
    renderer.draw_rectangle_rounded_lines(
        preview_rect,
        0.16,
        6,
        with_alpha(highlight, 215),
    )
