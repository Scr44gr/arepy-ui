from __future__ import annotations

from arepy.engine.renderer import Rect

from ..theme import Palette, mix_color, with_alpha
from .data import VitalBar


def render_vital_bar(renderer, rect: Rect, bar: VitalBar, palette: Palette) -> None:
    shadow_rect = Rect(int(rect.x + 2), int(rect.y + 2), int(rect.width), int(rect.height))
    frame_rect = Rect(int(rect.x), int(rect.y), int(rect.width), int(rect.height))
    trough_rect = Rect(int(rect.x + 4), int(rect.y + 4), int(rect.width - 8), int(rect.height - 8))

    renderer.draw_rectangle_rounded(shadow_rect, 0.42, 8, with_alpha(palette.shadow, 150))
    renderer.draw_rectangle_rounded(frame_rect, 0.42, 8, with_alpha(palette.surface_soft, 230))
    renderer.draw_rectangle_rounded_lines(frame_rect, 0.42, 8, with_alpha(palette.brass_soft, 115))
    renderer.draw_rectangle_rounded(trough_rect, 0.40, 8, with_alpha(bar.background, 245))

    fill_width = int(trough_rect.width * bar.ratio)
    if fill_width <= 0:
        return

    fill_rect = Rect(int(trough_rect.x), int(trough_rect.y), fill_width, int(trough_rect.height))
    renderer.draw_rectangle_rounded(fill_rect, 0.38, 8, with_alpha(bar.fill, 245))

    sheen_rect = Rect(
        int(trough_rect.x + 2),
        int(trough_rect.y + 2),
        max(1, fill_width - 4),
        max(1, int(trough_rect.height * 0.32)),
    )
    renderer.draw_rectangle_rounded(
        sheen_rect,
        0.34,
        6,
        with_alpha(mix_color(bar.fill, palette.white, 0.28), 68),
    )
