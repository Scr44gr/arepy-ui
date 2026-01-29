"""Tests para arepy_ui.core.style"""

import pytest

from arepy_ui.core.style import Spacing, Style
from arepy_ui.core.types import (
    AlignItems,
    Color,
    FlexDirection,
    JustifyContent,
    PositionType,
    Unit,
    UnitType,
)


class TestSpacing:
    def test_spacing_default(self):
        s = Spacing()
        assert s.top.value == 0
        assert s.right.value == 0
        assert s.bottom.value == 0
        assert s.left.value == 0

    def test_spacing_all(self):
        s = Spacing.all(10)
        assert s.top.value == 10
        assert s.right.value == 10
        assert s.bottom.value == 10
        assert s.left.value == 10

    def test_spacing_symmetric(self):
        s = Spacing.symmetric(vertical=10, horizontal=20)
        assert s.top.value == 10
        assert s.bottom.value == 10
        assert s.left.value == 20
        assert s.right.value == 20


class TestStyle:
    def test_style_defaults(self):
        style = Style()
        assert style.width.type == UnitType.AUTO
        assert style.height.type == UnitType.AUTO
        assert style.opacity == 1.0
        assert style.visible == True
        assert style.flex_direction == FlexDirection.COLUMN
        assert style.justify_content == JustifyContent.START
        assert style.align_items == AlignItems.STRETCH
        assert style.gap == 0.0
        assert style.position == PositionType.RELATIVE
        assert style.z_index == 0

    def test_style_with_dimensions(self):
        style = Style(
            width=Unit.px(100),
            height=Unit.px(50),
        )
        assert style.width.value == 100
        assert style.width.type == UnitType.PIXEL
        assert style.height.value == 50

    def test_style_with_flex(self):
        style = Style(
            flex_direction=FlexDirection.ROW,
            justify_content=JustifyContent.CENTER,
            align_items=AlignItems.CENTER,
            gap=10,
        )
        assert style.flex_direction == FlexDirection.ROW
        assert style.justify_content == JustifyContent.CENTER
        assert style.align_items == AlignItems.CENTER
        assert style.gap == 10

    def test_style_with_colors(self):
        bg = Color(255, 0, 0, 255)
        border = Color(0, 255, 0, 255)
        style = Style(
            background_color=bg,
            border_color=border,
            border_width=2.0,
            border_radius=8.0,
        )
        assert style.background_color == bg
        assert style.border_color == border
        assert style.border_width == 2.0
        assert style.border_radius == 8.0

    def test_style_with_padding_margin(self):
        style = Style(
            padding=Spacing.all(10),
            margin=Spacing.symmetric(5, 15),
        )
        assert style.padding.top.value == 10
        assert style.margin.top.value == 5
        assert style.margin.left.value == 15

    def test_style_with_min_max(self):
        style = Style(
            min_width=Unit.px(50),
            max_width=Unit.px(500),
            min_height=Unit.px(20),
            max_height=Unit.px(200),
        )
        assert style.min_width.value == 50  # type: ignore
        assert style.max_width.value == 500  # type: ignore
        assert style.min_height.value == 20  # type: ignore
        assert style.max_height.value == 200  # type: ignore
