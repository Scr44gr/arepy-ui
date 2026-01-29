"""Tests for markup converters."""

import pytest

from arepy_ui.core.types import (
    AlignItems,
    Color,
    FlexDirection,
    JustifyContent,
    Unit,
    UnitType,
)
from arepy_ui.markup.converters import (
    convert_to_align_items,
    convert_to_color,
    convert_to_flex_direction,
    convert_to_justify_content,
    convert_to_spacing,
    convert_to_unit,
)


class TestConvertToColor:
    """Tests for color conversion."""

    def test_hex_color_6_digits(self):
        color = convert_to_color("#FF5733")
        assert color is not None
        assert color.r == 255
        assert color.g == 87
        assert color.b == 51
        assert color.a == 255

    def test_hex_color_3_digits(self):
        color = convert_to_color("#F00")
        assert color is not None
        assert color.r == 255
        assert color.g == 0
        assert color.b == 0

    def test_hex_color_8_digits_with_alpha(self):
        color = convert_to_color("#FF573380")
        assert color is not None
        assert color.r == 255
        assert color.g == 87
        assert color.b == 51
        assert color.a == 128

    def test_hex_color_lowercase(self):
        color = convert_to_color("#ff5733")
        assert color is not None
        assert color.r == 255
        assert color.g == 87
        assert color.b == 51

    def test_invalid_color_returns_none(self):
        result = convert_to_color("invalid")
        assert result is None

    def test_none_returns_none(self):
        result = convert_to_color(None)
        assert result is None


class TestConvertToUnit:
    """Tests for unit conversion."""

    def test_pixel_value(self):
        unit = convert_to_unit(("px", 100.0))
        assert unit.type == UnitType.PIXEL
        assert unit.value == 100.0

    def test_percent_value(self):
        unit = convert_to_unit(("percent", 50.0))
        assert unit.type == UnitType.PERCENT
        assert unit.value == 50.0

    def test_viewport_width(self):
        unit = convert_to_unit(("vw", 100.0))
        assert unit.type == UnitType.VIEWPORT_WIDTH
        assert unit.value == 100.0

    def test_viewport_height(self):
        unit = convert_to_unit(("vh", 50.0))
        assert unit.type == UnitType.VIEWPORT_HEIGHT
        assert unit.value == 50.0

    def test_auto_string(self):
        unit = convert_to_unit("auto")
        assert unit.type == UnitType.AUTO

    def test_raw_number(self):
        unit = convert_to_unit(100)
        assert unit.type == UnitType.PIXEL
        assert unit.value == 100.0

    def test_float_number(self):
        unit = convert_to_unit(50.5)
        assert unit.type == UnitType.PIXEL
        assert unit.value == 50.5

    def test_none_returns_auto(self):
        # None values get converted to auto units
        result = convert_to_unit(None)
        assert result.type == UnitType.AUTO


class TestConvertToSpacing:
    """Tests for spacing conversion."""

    def test_single_value(self):
        spacing = convert_to_spacing(("px", 10.0))
        assert spacing.top.value == 10.0
        assert spacing.right.value == 10.0
        assert spacing.bottom.value == 10.0
        assert spacing.left.value == 10.0

    def test_none_returns_default_spacing(self):
        # None values return default spacing
        result = convert_to_spacing(None)
        assert result is not None
        assert result.top.value == 0.0


class TestConvertToFlexDirection:
    """Tests for flex direction conversion."""

    def test_row(self):
        result = convert_to_flex_direction("row")
        assert result == FlexDirection.ROW

    def test_column(self):
        result = convert_to_flex_direction("column")
        assert result == FlexDirection.COLUMN

    def test_invalid_returns_default(self):
        # Invalid values return a default
        result = convert_to_flex_direction("invalid")
        assert result in (FlexDirection.ROW, FlexDirection.COLUMN, None)


class TestConvertToJustifyContent:
    """Tests for justify-content conversion."""

    def test_start(self):
        result = convert_to_justify_content("start")
        assert result == JustifyContent.START

    def test_flex_start(self):
        result = convert_to_justify_content("flex-start")
        assert result == JustifyContent.START

    def test_center(self):
        result = convert_to_justify_content("center")
        assert result == JustifyContent.CENTER

    def test_end(self):
        result = convert_to_justify_content("end")
        assert result == JustifyContent.END

    def test_flex_end(self):
        result = convert_to_justify_content("flex-end")
        assert result == JustifyContent.END

    def test_space_between(self):
        result = convert_to_justify_content("space-between")
        assert result == JustifyContent.SPACE_BETWEEN

    def test_space_around(self):
        result = convert_to_justify_content("space-around")
        assert result == JustifyContent.SPACE_AROUND

    def test_space_evenly(self):
        result = convert_to_justify_content("space-evenly")
        assert result == JustifyContent.SPACE_EVENLY

    def test_invalid_returns_default(self):
        # Invalid values return a default
        result = convert_to_justify_content("invalid")
        assert result is None or result in (JustifyContent.START, JustifyContent.CENTER)


class TestConvertToAlignItems:
    """Tests for align-items conversion."""

    def test_start(self):
        result = convert_to_align_items("start")
        assert result == AlignItems.START

    def test_flex_start(self):
        result = convert_to_align_items("flex-start")
        assert result == AlignItems.START

    def test_center(self):
        result = convert_to_align_items("center")
        assert result == AlignItems.CENTER

    def test_end(self):
        result = convert_to_align_items("end")
        assert result == AlignItems.END

    def test_flex_end(self):
        result = convert_to_align_items("flex-end")
        assert result == AlignItems.END

    def test_stretch(self):
        result = convert_to_align_items("stretch")
        assert result == AlignItems.STRETCH

    def test_invalid_returns_default(self):
        # Invalid values return a default
        result = convert_to_align_items("invalid")
        assert result is None or result in (AlignItems.START, AlignItems.STRETCH)


class TestConvertToPositionType:
    """Tests for position type conversion."""

    def test_relative(self):
        from arepy_ui.core.types import PositionType
        from arepy_ui.markup.converters import convert_to_position_type

        result = convert_to_position_type("relative")
        assert result == PositionType.RELATIVE

    def test_absolute(self):
        from arepy_ui.core.types import PositionType
        from arepy_ui.markup.converters import convert_to_position_type

        result = convert_to_position_type("absolute")
        assert result == PositionType.ABSOLUTE

    def test_invalid_returns_relative(self):
        from arepy_ui.core.types import PositionType
        from arepy_ui.markup.converters import convert_to_position_type

        result = convert_to_position_type("invalid")
        assert result == PositionType.RELATIVE


class TestConvertToFloat:
    """Tests for float conversion."""

    def test_int_value(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float(42)
        assert result == 42.0

    def test_float_value(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float(3.14)
        assert result == 3.14

    def test_tuple_px_value(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float(("px", 100))
        assert result == 100.0

    def test_string_with_px(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float("50px")
        assert result == 50.0

    def test_string_number(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float("25.5")
        assert result == 25.5

    def test_invalid_returns_default(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float("invalid", default=0.0)
        assert result == 0.0

    def test_none_returns_default(self):
        from arepy_ui.markup.converters import convert_to_float

        result = convert_to_float(None, default=10.0)
        assert result == 10.0


class TestConvertToInt:
    """Tests for int conversion."""

    def test_int_value(self):
        from arepy_ui.markup.converters import convert_to_int

        result = convert_to_int(42)
        assert result == 42

    def test_float_value(self):
        from arepy_ui.markup.converters import convert_to_int

        result = convert_to_int(3.7)
        assert result == 3

    def test_string_number(self):
        from arepy_ui.markup.converters import convert_to_int

        result = convert_to_int("25")
        assert result == 25

    def test_invalid_returns_default(self):
        from arepy_ui.markup.converters import convert_to_int

        result = convert_to_int("invalid", default=0)
        assert result == 0


class TestConvertToUnitEdgeCases:
    """Edge cases for unit conversion."""

    def test_string_percent(self):
        unit = convert_to_unit("50%")
        assert unit.type == UnitType.PERCENT
        assert unit.value == 50.0

    def test_string_vw(self):
        unit = convert_to_unit("100vw")
        assert unit.type == UnitType.VIEWPORT_WIDTH
        assert unit.value == 100.0

    def test_string_vh(self):
        unit = convert_to_unit("100vh")
        assert unit.type == UnitType.VIEWPORT_HEIGHT
        assert unit.value == 100.0

    def test_string_px(self):
        unit = convert_to_unit("50px")
        assert unit.type == UnitType.PIXEL
        assert unit.value == 50.0

    def test_string_raw_number(self):
        unit = convert_to_unit("100")
        assert unit.type == UnitType.PIXEL
        assert unit.value == 100.0

    def test_auto_tuple(self):
        unit = convert_to_unit(("auto",))
        assert unit.type == UnitType.AUTO

    def test_invalid_percent_returns_auto(self):
        unit = convert_to_unit("abc%")
        assert unit.type == UnitType.AUTO

    def test_invalid_vw_returns_auto(self):
        unit = convert_to_unit("abcvw")
        assert unit.type == UnitType.AUTO

    def test_invalid_vh_returns_auto(self):
        unit = convert_to_unit("abcvh")
        assert unit.type == UnitType.AUTO

    def test_invalid_px_returns_auto(self):
        unit = convert_to_unit("abcpx")
        assert unit.type == UnitType.AUTO

    def test_unit_passthrough(self):
        original = Unit.px(50)
        result = convert_to_unit(original)
        assert result is original


class TestConvertToSpacingEdgeCases:
    """Edge cases for spacing conversion."""

    def test_two_values(self):

        spacing = convert_to_spacing("10px 20px")
        assert spacing.top.value == 10.0
        assert spacing.bottom.value == 10.0
        assert spacing.left.value == 20.0
        assert spacing.right.value == 20.0

    def test_four_values(self):
        spacing = convert_to_spacing("10px 20px 30px 40px")
        assert spacing.top.value == 10.0
        assert spacing.right.value == 20.0
        assert spacing.bottom.value == 30.0
        assert spacing.left.value == 40.0

    def test_numeric_value(self):
        spacing = convert_to_spacing(15)
        assert spacing.top.value == 15.0

    def test_spacing_passthrough(self):
        from arepy_ui.core.style import Spacing

        original = Spacing.all(10)
        result = convert_to_spacing(original)
        assert result is original

    def test_invalid_two_values(self):
        spacing = convert_to_spacing("abc def")
        assert spacing.top.value == 0.0

    def test_invalid_four_values(self):
        spacing = convert_to_spacing("abc def ghi jkl")
        assert spacing.top.value == 0.0


class TestConvertToColorEdgeCases:
    """Edge cases for color conversion."""

    def test_color_passthrough(self):
        original = Color(100, 150, 200, 255)
        result = convert_to_color(original)
        assert result is original

    def test_color_tuple_format(self):
        result = convert_to_color(("color", "#FF0000"))
        assert result is not None
        assert result.r == 255
        assert result.g == 0
        assert result.b == 0

    def test_invalid_hex_returns_none(self):
        result = convert_to_color("#GGGGGG")
        assert result is None
