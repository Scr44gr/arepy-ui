"""
Value converters for transforming ACSS values to arepy-ui types.
"""

from __future__ import annotations

from typing import Any

from arepy_ui.core.style import Spacing
from arepy_ui.core.types import (
    AlignItems,
    Color,
    FlexDirection,
    JustifyContent,
    PositionType,
    Unit,
)


def convert_to_unit(value: Any) -> Unit:
    """Convert a parsed value to a Unit instance."""
    if isinstance(value, Unit):
        return value

    if isinstance(value, tuple):
        if value[0] == "px":
            return Unit.px(float(value[1]))
        elif value[0] == "percent":
            return Unit.percent(float(value[1]))
        elif value[0] == "vw":
            return Unit.vw(float(value[1]))
        elif value[0] == "vh":
            return Unit.vh(float(value[1]))
        elif value[0] == "auto":
            return Unit.auto()

    if value == "auto":
        return Unit.auto()

    if isinstance(value, str):
        v = value.strip()
        if v.endswith("%"):
            try:
                return Unit.percent(float(v[:-1]))
            except ValueError:
                return Unit.auto()
        if v.endswith("vw"):
            try:
                return Unit.vw(float(v[:-2]))
            except ValueError:
                return Unit.auto()
        if v.endswith("vh"):
            try:
                return Unit.vh(float(v[:-2]))
            except ValueError:
                return Unit.auto()
        if v.endswith("px"):
            try:
                return Unit.px(float(v[:-2]))
            except ValueError:
                return Unit.auto()
        try:
            return Unit.px(float(v))
        except ValueError:
            return Unit.auto()

    if isinstance(value, (int, float)):
        return Unit.px(float(value))

    return Unit.auto()


def convert_to_spacing(value: Any) -> Spacing:
    """Convert a parsed value to a Spacing instance."""
    if isinstance(value, Spacing):
        return value

    if isinstance(value, tuple) and len(value) >= 2 and value[0] == "px":
        return Spacing.all(float(value[1]))

    if isinstance(value, (int, float)):
        return Spacing.all(float(value))

    if isinstance(value, str):
        parts = value.split()

        if len(parts) == 1:
            # Single value: all sides
            try:
                return Spacing.all(float(parts[0].replace("px", "")))
            except ValueError:
                return Spacing()

        elif len(parts) == 2:
            # Two values: vertical horizontal
            try:
                vertical = float(parts[0].replace("px", ""))
                horizontal = float(parts[1].replace("px", ""))
                return Spacing.symmetric(vertical=vertical, horizontal=horizontal)
            except ValueError:
                return Spacing()

        elif len(parts) == 4:
            # Four values: top right bottom left
            try:
                top = Unit.px(float(parts[0].replace("px", "")))
                right = Unit.px(float(parts[1].replace("px", "")))
                bottom = Unit.px(float(parts[2].replace("px", "")))
                left = Unit.px(float(parts[3].replace("px", "")))
                return Spacing(top=top, right=right, bottom=bottom, left=left)
            except ValueError:
                return Spacing()

    return Spacing()


def convert_to_flex_direction(value: Any) -> FlexDirection:
    """Convert a parsed value to FlexDirection enum."""
    mapping = {
        "row": FlexDirection.ROW,
        "column": FlexDirection.COLUMN,
        "row_reverse": FlexDirection.ROW,
        "column_reverse": FlexDirection.COLUMN,
    }
    key = str(value).lower().replace("-", "_")
    return mapping.get(key, FlexDirection.COLUMN)


def convert_to_justify_content(value: Any) -> JustifyContent:
    """Convert a parsed value to JustifyContent enum."""
    mapping = {
        "start": JustifyContent.START,
        "flex_start": JustifyContent.START,
        "end": JustifyContent.END,
        "flex_end": JustifyContent.END,
        "center": JustifyContent.CENTER,
        "space_between": JustifyContent.SPACE_BETWEEN,
        "space_around": JustifyContent.SPACE_AROUND,
        "space_evenly": JustifyContent.SPACE_EVENLY,
    }
    key = str(value).lower().replace("-", "_")
    return mapping.get(key, JustifyContent.START)


def convert_to_align_items(value: Any) -> AlignItems:
    """Convert a parsed value to AlignItems enum."""
    mapping = {
        "start": AlignItems.START,
        "flex_start": AlignItems.START,
        "end": AlignItems.END,
        "flex_end": AlignItems.END,
        "center": AlignItems.CENTER,
        "stretch": AlignItems.STRETCH,
    }
    key = str(value).lower().replace("-", "_")
    return mapping.get(key, AlignItems.STRETCH)


def convert_to_position_type(value: Any) -> PositionType:
    """Convert a parsed value to PositionType enum."""
    mapping = {
        "relative": PositionType.RELATIVE,
        "absolute": PositionType.ABSOLUTE,
    }
    return mapping.get(str(value).lower(), PositionType.RELATIVE)


def convert_to_color(value: Any) -> Color | None:
    """Convert a parsed value to a Color instance."""
    if isinstance(value, Color):
        return value

    if isinstance(value, tuple) and value[0] == "color":
        value = value[1]

    if isinstance(value, str) and value.startswith("#"):
        hex_str = value[1:]

        # Expand shorthand (#RGB -> #RRGGBB)
        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)

        # Add alpha if missing
        if len(hex_str) == 6:
            hex_str += "ff"

        if len(hex_str) == 8:
            try:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                a = int(hex_str[6:8], 16)
                return Color(r, g, b, a)
            except ValueError:
                return None

    return None


def convert_to_float(value: Any, default: float = 0.0) -> float:
    """Convert a parsed value to a float."""
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, tuple) and value[0] == "px":
        return float(value[1])

    if isinstance(value, str):
        try:
            return float(value.replace("px", ""))
        except ValueError:
            return default

    return default


def convert_to_int(value: Any, default: int = 0) -> int:
    """Convert a parsed value to an integer."""
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default

    return default
