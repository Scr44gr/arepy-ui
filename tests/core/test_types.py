"""Tests para arepy_ui.core.types"""

import pytest

from arepy_ui.core.types import (
    AlignItems,
    Color,
    FlexDirection,
    JustifyContent,
    PositionType,
    Rectangle,
    Unit,
    UnitType,
    Vector2,
)


class TestColor:
    def test_color_creation(self):
        c = Color(255, 128, 64, 200)
        assert c.r == 255
        assert c.g == 128
        assert c.b == 64
        assert c.a == 200

    def test_color_default_alpha(self):
        c = Color(100, 100, 100)
        assert c.a == 255

    def test_color_is_sequence(self):
        c = Color(10, 20, 30, 40)
        # Color supports sequence protocol (indexing, iteration, len)
        assert len(c) == 4
        assert c[0] == 10
        assert c[1] == 20
        assert c[2] == 30
        assert c[3] == 40
        assert list(c) == [10, 20, 30, 40]


class TestVector2:
    def test_vector2_creation(self):
        v = Vector2(10.5, 20.5)
        assert v.x == 10.5
        assert v.y == 20.5

    def test_vector2_is_sequence(self):
        v = Vector2(1, 2)
        # Vector2 supports sequence protocol (indexing, iteration, len)
        assert len(v) == 2
        assert v[0] == 1.0
        assert v[1] == 2.0
        assert list(v) == [1.0, 2.0]


class TestRectangle:
    def test_rectangle_creation(self):
        r = Rectangle(10, 20, 100, 50)
        assert r.x == 10
        assert r.y == 20
        assert r.width == 100
        assert r.height == 50


class TestUnit:
    def test_unit_px(self):
        u = Unit.px(100)
        assert u.value == 100
        assert u.type == UnitType.PIXEL

    def test_unit_percent(self):
        u = Unit.percent(50)
        assert u.value == 50
        assert u.type == UnitType.PERCENT

    def test_unit_vw(self):
        u = Unit.vw(100)
        assert u.value == 100
        assert u.type == UnitType.VIEWPORT_WIDTH

    def test_unit_vh(self):
        u = Unit.vh(50)
        assert u.value == 50
        assert u.type == UnitType.VIEWPORT_HEIGHT

    def test_unit_auto(self):
        u = Unit.auto()
        assert u.type == UnitType.AUTO


class TestEnums:
    def test_flex_direction_values(self):
        assert FlexDirection.ROW is not None
        assert FlexDirection.COLUMN is not None

    def test_justify_content_values(self):
        assert JustifyContent.START is not None
        assert JustifyContent.CENTER is not None
        assert JustifyContent.END is not None
        assert JustifyContent.SPACE_BETWEEN is not None
        assert JustifyContent.SPACE_AROUND is not None
        assert JustifyContent.SPACE_EVENLY is not None

    def test_align_items_values(self):
        assert AlignItems.START is not None
        assert AlignItems.CENTER is not None
        assert AlignItems.END is not None
        assert AlignItems.STRETCH is not None

    def test_position_type_values(self):
        assert PositionType.RELATIVE is not None
        assert PositionType.ABSOLUTE is not None
