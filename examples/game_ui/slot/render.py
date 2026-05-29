from __future__ import annotations

import math

from arepy.engine.renderer import Rect
from arepy_ui import Color

from ..text import draw_centered_text, draw_outlined_centered_text
from ..theme import Palette, clamp, mix_color, with_alpha
from .data import SlotMachineState, SlotPrize


BASE_REEL_WIDTH = 254.0
BASE_REEL_HEIGHT = 104.0


def render_slot_reel(
    renderer,
    rect: Rect,
    machine: SlotMachineState,
    prizes: list[SlotPrize],
    palette: Palette,
    title: str,
) -> None:
    scale = min(rect.width / BASE_REEL_WIDTH, rect.height / BASE_REEL_HEIGHT)

    def scaled(value: float) -> int:
        return max(1, int(round(value * scale)))

    def draw_rounded_border(border_rect: Rect, roundness: float, segments: int, color: Color) -> None:
        for inset in range(2):
            inset_width = border_rect.width - inset * 2
            inset_height = border_rect.height - inset * 2
            if inset_width <= 0 or inset_height <= 0:
                break
            renderer.draw_rectangle_rounded_lines(
                Rect(
                    int(border_rect.x + inset),
                    int(border_rect.y + inset),
                    int(inset_width),
                    int(inset_height),
                ),
                roundness,
                segments,
                color,
            )

    base_index = math.floor(machine.reel_position) % len(prizes)
    next_index = (base_index + 1) % len(prizes)
    phase = machine.reel_position - math.floor(machine.reel_position)
    if not machine.is_spinning:
        phase = 0.0

    current_prize = prizes[base_index]
    next_prize = prizes[next_index]
    active_accent = (
        mix_color(current_prize.accent, next_prize.accent, phase)
        if machine.is_spinning
        else current_prize.accent
    )
    spin_progress = (
        clamp(machine.spin_elapsed / max(machine.spin_duration, 0.001), 0.0, 1.0)
        if machine.is_spinning
        else 1.0
    )
    speed = 1.0 - spin_progress
    shake_power = (0.35 + speed * 1.2) if machine.is_spinning else machine.flash * 2.0
    shake_x = math.sin(machine.elapsed * 70.0) * shake_power
    shake_y = math.sin(machine.elapsed * 87.0) * shake_power * 0.28
    x = rect.x + shake_x
    y = rect.y + shake_y

    shadow_rect = Rect(
        int(x + scaled(5)),
        int(y + scaled(5)),
        int(rect.width - scaled(10)),
        int(rect.height - scaled(7)),
    )
    body_rect = Rect(int(x), int(y), int(rect.width), int(rect.height - scaled(3)))
    renderer.draw_rectangle_rounded(shadow_rect, 0.18, 8, with_alpha(palette.shadow, 160))
    renderer.draw_rectangle_rounded(body_rect, 0.18, 8, with_alpha(palette.surface, 244))
    draw_rounded_border(
        body_rect,
        0.18,
        8,
        with_alpha(mix_color(active_accent, palette.surface_border, 0.38), 190),
    )

    label_rect = Rect(int(x + scaled(12)), int(y + scaled(9)), scaled(90), scaled(20))
    renderer.draw_rectangle_rounded(
        label_rect,
        0.22,
        5,
        with_alpha(mix_color(active_accent, palette.surface_soft, 0.35), 110),
    )
    draw_centered_text(
        title,
        label_rect.x + label_rect.width / 2,
        label_rect.y + scaled(5),
        scaled(10),
        palette.text_primary,
    )

    lamp_y = y + scaled(18)
    for index in range(4):
        lamp_x = x + rect.width - scaled(66) + index * scaled(14)
        lamp_wave = 0.55 + 0.45 * math.sin(machine.elapsed * 8.0 + index * 0.75)
        lamp_alpha = 95 + int(115 * lamp_wave) if machine.is_spinning else 110
        renderer.draw_circle(
            (int(lamp_x), int(lamp_y)),
            scaled(3) + int(machine.flash),
            with_alpha(mix_color(palette.brass, active_accent, 0.42), lamp_alpha),
        )

    window_rect = Rect(
        int(x + scaled(18)),
        int(y + scaled(32)),
        int(rect.width - scaled(36)),
        int(rect.height - scaled(54)),
    )
    renderer.draw_rectangle_rounded(window_rect, 0.16, 8, palette.shadow)
    renderer.draw_rectangle_rounded(
        Rect(
            int(window_rect.x + scaled(4)),
            int(window_rect.y + scaled(4)),
            int(window_rect.width - scaled(8)),
            int(window_rect.height - scaled(8)),
        ),
        0.14,
        7,
        with_alpha(mix_color(palette.background, active_accent, 0.10), 248),
    )

    center_x = window_rect.x + window_rect.width / 2
    center_y = window_rect.y + window_rect.height / 2

    focus_rect = Rect(
        int(window_rect.x + scaled(12)),
        int(center_y - scaled(24)),
        int(window_rect.width - scaled(24)),
        scaled(48),
    )
    renderer.draw_rectangle_rounded(
        focus_rect,
        0.16,
        7,
        with_alpha(mix_color(active_accent, palette.white, 0.08), 34 + machine.flash * 68),
    )

    renderer.begin_scissor_mode(
        int(window_rect.x + scaled(5)),
        int(window_rect.y + scaled(5)),
        int(window_rect.width - scaled(10)),
        int(window_rect.height - scaled(10)),
    )

    number_size = int(scaled(58) + machine.flash * scaled(12))
    number_step = scaled(48)

    def draw_slot_number(number: int, offset: float, alpha: float, scale_factor: float) -> None:
        font_size = max(26, int(number_size * scale_factor))
        draw_outlined_centered_text(
            str(number),
            center_x,
            center_y - font_size / 2 + offset,
            font_size,
            with_alpha(palette.parchment, alpha),
            with_alpha(palette.shadow, min(255, alpha + 25)),
            with_alpha(palette.white, alpha * 0.18),
        )

    if machine.is_spinning:
        for offset_index in range(-1, 3):
            prize = prizes[(base_index + offset_index) % len(prizes)]
            offset = (offset_index - phase) * number_step
            distance = abs(offset) / number_step
            alpha = int(clamp(225 - distance * 105, 25, 235))
            scale_factor = clamp(1.0 - distance * 0.18, 0.62, 1.0)
            draw_slot_number(prize.number, offset, alpha, scale_factor)

        for streak in range(2):
            streak_y = center_y - scaled(16) + streak * scaled(22) + phase * scaled(13)
            renderer.draw_line_ex(
                (window_rect.x + scaled(24), streak_y),
                (window_rect.x + window_rect.width - scaled(24), streak_y),
                float(scaled(2)),
                with_alpha(palette.parchment, 26 + streak * 10),
            )
    else:
        prev_prize = prizes[(base_index - 1) % len(prizes)]
        settled_prize = prizes[base_index]
        next_prize = prizes[(base_index + 1) % len(prizes)]
        impact_drop = -math.sin(machine.flash * math.pi) * 5
        draw_slot_number(prev_prize.number, -number_step, 34, 0.62)
        draw_slot_number(next_prize.number, number_step, 34, 0.62)
        draw_slot_number(settled_prize.number, impact_drop, 255, 1.0 + machine.flash * 0.08)

    renderer.end_scissor_mode()

    if machine.flash > 0.0:
        ring_alpha = int(105 * machine.flash)
        for spark in range(7):
            angle = spark * (math.tau / 7.0) + machine.elapsed * 0.6
            radius = scaled(24) + (1.0 - machine.flash) * scaled(18)
            spark_x = center_x + math.cos(angle) * radius
            spark_y = center_y + math.sin(angle) * radius * 0.55
            renderer.draw_circle(
                (int(spark_x), int(spark_y)),
                scaled(1) + int(machine.flash * 2),
                with_alpha(active_accent, ring_alpha),
            )
        renderer.draw_rectangle_rounded(
            focus_rect,
            0.16,
            7,
            with_alpha(palette.parchment, 28 * machine.flash),
        )

    footer_rect = Rect(
        int(x + scaled(18)),
        int(y + rect.height - scaled(16)),
        int(rect.width - scaled(36)),
        scaled(6),
    )
    renderer.draw_rectangle_rounded(
        footer_rect,
        0.45,
        6,
        with_alpha(palette.background_soft, 220),
    )
    if machine.is_spinning:
        fill_width = int(footer_rect.width * spin_progress)
        renderer.draw_rectangle_rounded(
            Rect(int(footer_rect.x), int(footer_rect.y), fill_width, scaled(6)),
            0.45,
            5,
            with_alpha(active_accent, 210),
        )
