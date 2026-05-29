from __future__ import annotations

from dataclasses import dataclass

from arepy_ui import Color


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def hex_color(value: str, alpha: int = 255) -> Color:
    hex_value = value.lstrip("#")
    return Color(
        int(hex_value[0:2], 16),
        int(hex_value[2:4], 16),
        int(hex_value[4:6], 16),
        alpha,
    )


def with_alpha(color: Color, alpha: float) -> Color:
    return Color(color.r, color.g, color.b, int(clamp(alpha, 0.0, 255.0)))


def mix_color(start: Color, end: Color, amount: float) -> Color:
    t = clamp(amount, 0.0, 1.0)
    return Color(
        int(start.r + (end.r - start.r) * t),
        int(start.g + (end.g - start.g) * t),
        int(start.b + (end.b - start.b) * t),
        int(start.a + (end.a - start.a) * t),
    )


@dataclass(frozen=True)
class Palette:
    background: Color
    background_soft: Color
    surface: Color
    surface_soft: Color
    surface_border: Color
    grid: Color
    grid_soft: Color
    text_primary: Color
    text_secondary: Color
    text_muted: Color
    text_on_accent: Color
    red: Color
    red_hover: Color
    red_pressed: Color
    health_fill: Color
    health_back: Color
    stamina_fill: Color
    stamina_back: Color
    brass: Color
    brass_soft: Color
    shadow: Color
    royal: Color
    parchment: Color
    steel: Color
    white: Color


PALETTE = Palette(
    background=hex_color("08111a"),
    background_soft=hex_color("d8d1c4"),
    surface=hex_color("f7f3eb"),
    surface_soft=hex_color("fbf8f2"),
    surface_border=hex_color("b8ae9f"),
    grid=hex_color("c8bfb2"),
    grid_soft=hex_color("efe9df"),
    text_primary=hex_color("231c16"),
    text_secondary=hex_color("4d4238"),
    text_muted=hex_color("75695d"),
    text_on_accent=hex_color("231c16"),
    red=hex_color("b93b40"),
    red_hover=hex_color("d55157"),
    red_pressed=hex_color("8f2b30"),
    health_fill=hex_color("912e35"),
    health_back=hex_color("341218"),
    stamina_fill=hex_color("5b8a37"),
    stamina_back=hex_color("20321a"),
    brass=hex_color("c89b57"),
    brass_soft=hex_color("e4c483"),
    shadow=hex_color("17120d"),
    royal=hex_color("72a4ff"),
    parchment=hex_color("f5e3be"),
    steel=hex_color("aac7e0"),
    white=hex_color("ffffff"),
)
