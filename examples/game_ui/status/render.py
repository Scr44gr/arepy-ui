from __future__ import annotations

from arepy.engine.renderer import Rect
from arepy_ui import draw_text, measure_text

from ..fonts import font_for
from ..theme import Palette, mix_color, with_alpha
from .data import StatusState


def render_status_badge(renderer, rect: Rect, state: StatusState, palette: Palette) -> None:
    accent = (
        mix_color(palette.brass_soft, palette.parchment, 0.18)
        if state.is_day
        else mix_color(palette.royal, palette.white, 0.22)
    )
    chip_fill = with_alpha(mix_color(palette.surface_soft, accent, 0.16), 236)
    chip_border = with_alpha(mix_color(palette.surface_border, accent, 0.34), 210)
    chip_rect = Rect(
        int(rect.x),
        int(rect.y + 6),
        int(max(44, rect.width * 0.26)),
        int(max(32, rect.height - 12)),
    )
    renderer.draw_rectangle_rounded(
        chip_rect,
        0.30,
        8,
        chip_fill,
    )
    renderer.draw_rectangle_rounded_lines(
        chip_rect,
        0.30,
        8,
        chip_border,
    )

    orb_center_x = chip_rect.x + chip_rect.width / 2
    orb_center_y = chip_rect.y + chip_rect.height / 2
    orb_radius = max(8, int(min(chip_rect.width, chip_rect.height) * 0.20))
    renderer.draw_circle(
        (int(orb_center_x), int(orb_center_y)),
        orb_radius + 2,
        with_alpha(accent, 60),
    )

    if state.is_day:
        renderer.draw_circle(
            (int(orb_center_x), int(orb_center_y)),
            orb_radius,
            with_alpha(accent, 236),
        )
        renderer.draw_circle(
            (int(orb_center_x - orb_radius * 0.35), int(orb_center_y - orb_radius * 0.35)),
            max(2, orb_radius // 4),
            with_alpha(palette.white, 175),
        )
    else:
        renderer.draw_circle(
            (int(orb_center_x), int(orb_center_y)),
            orb_radius,
            with_alpha(accent, 228),
        )
        renderer.draw_circle(
            (int(orb_center_x + orb_radius * 0.42), int(orb_center_y - orb_radius * 0.10)),
            max(4, orb_radius - 1),
            chip_fill,
        )

    separator_x = chip_rect.x + chip_rect.width + 10
    renderer.draw_rectangle(
        Rect(int(separator_x), int(rect.y + 10), 2, int(max(18, rect.height - 20))),
        with_alpha(chip_border, 90),
    )

    time_text = state.formatted_time()
    period_text = state.period
    time_font = font_for("display")
    time_size = max(20, int(rect.height * 0.34))
    period_size = max(10, int(rect.height * 0.16))
    time_x = separator_x + 10
    time_y = int(rect.y + rect.height * 0.14)
    draw_text(
        time_text,
        int(time_x),
        time_y,
        time_size,
        palette.text_primary,
        time_font,
    )

    period_width = measure_text(period_text, period_size, font_for())
    draw_text(
        period_text,
        int(rect.x + rect.width - period_width - 8),
        int(rect.y + rect.height * 0.58),
        period_size,
        with_alpha(palette.text_secondary, 220),
        font_for(),
    )

    underline_width = int(max(26, rect.width - (time_x - rect.x) - period_width - 20))
    renderer.draw_rectangle(
        Rect(
            int(time_x),
            int(rect.y + rect.height - 10),
            underline_width,
            3,
        ),
        with_alpha(accent, 120),
    )
