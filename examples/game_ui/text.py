from __future__ import annotations

from arepy_ui import Color, draw_text, measure_text

from .fonts import font_for


def text_width(text: str, font_size: int, font_name: str | None = None) -> float:
    try:
        return measure_text(text, font_size, font_name)
    except RuntimeError:
        return len(text) * font_size * 0.62


def fit_text(
    text: str,
    max_width: float,
    font_size: int,
    font_name: str | None = None,
) -> str:
    if text_width(text, font_size, font_name) <= max_width:
        return text

    suffix = "..."
    available_width = max(0.0, max_width - text_width(suffix, font_size, font_name))
    fitted = ""
    for char in text:
        candidate = fitted + char
        if text_width(candidate, font_size, font_name) > available_width:
            break
        fitted = candidate
    return fitted.rstrip() + suffix


def draw_centered_text(
    text: str,
    center_x: float,
    y: float,
    font_size: int,
    color: Color,
    font_name: str | None = None,
) -> None:
    resolved_font = font_name or font_for("display")
    resolved_width = measure_text(text, font_size, resolved_font)
    draw_text(
        text,
        int(center_x - resolved_width / 2),
        int(y),
        font_size,
        color,
        resolved_font,
    )


def draw_outlined_centered_text(
    text: str,
    center_x: float,
    y: float,
    font_size: int,
    color: Color,
    shadow_color: Color,
    highlight_color: Color | None = None,
    font_name: str | None = None,
) -> None:
    resolved_font = font_name or font_for("display")
    resolved_width = measure_text(text, font_size, resolved_font)
    text_x = int(center_x - resolved_width / 2)
    text_y = int(y)
    outline_offset = max(2, int(round(font_size / 26)))

    for dx, dy in (
        (outline_offset, 0),
        (-outline_offset, 0),
        (0, outline_offset),
        (0, -outline_offset),
        (outline_offset, outline_offset),
        (-outline_offset, outline_offset),
        (outline_offset, -outline_offset),
        (-outline_offset, -outline_offset),
    ):
        draw_text(
            text,
            text_x + dx,
            text_y + dy,
            font_size,
            shadow_color,
            resolved_font,
        )

    if highlight_color is not None:
        draw_text(
            text,
            text_x,
            text_y - outline_offset,
            font_size,
            highlight_color,
            resolved_font,
        )

    draw_text(text, text_x, text_y, font_size, color, resolved_font)
