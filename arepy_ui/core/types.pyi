"""Type stubs for types Cython module."""

from enum import Enum
from typing import Iterator, Tuple, Union

from arepy import CursorType as CursorType
from arepy.engine.renderer import Color as BaseColor

class UnitType(Enum):
    PIXEL = 0
    PERCENT = 1
    VIEWPORT_WIDTH = 2
    VIEWPORT_HEIGHT = 3
    AUTO = 4

class FlexDirection(Enum):
    ROW = 0
    COLUMN = 1

class JustifyContent(Enum):
    START = 0
    CENTER = 1
    END = 2
    SPACE_BETWEEN = 3
    SPACE_AROUND = 4
    SPACE_EVENLY = 5

class AlignItems(Enum):
    START = 0
    CENTER = 1
    END = 2
    STRETCH = 3

class PositionType(Enum):
    RELATIVE = 0
    ABSOLUTE = 1

class Color(BaseColor):
    """RGBA Color with fast C-level access."""

    r: int
    g: int
    b: int
    a: int

    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None: ...
    def __iter__(self) -> Iterator[int]: ...
    def __getitem__(self, index: int) -> int: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def with_alpha(self, alpha: int) -> "Color": ...

class Vector2:
    """2D Vector with fast C-level access."""

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None: ...
    def __iter__(self) -> Iterator[float]: ...
    def __getitem__(self, index: int) -> float: ...
    def __len__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def add(self, other: "Vector2") -> "Vector2": ...
    def sub(self, other: "Vector2") -> "Vector2": ...
    def scale(self, factor: float) -> "Vector2": ...

class Rectangle:
    """Rectangle with fast C-level access."""

    x: float
    y: float
    width: float
    height: float

    def __init__(self, x: float, y: float, width: float, height: float) -> None: ...
    def __iter__(self) -> Iterator[float]: ...
    def __getitem__(self, index: int) -> float: ...
    def __len__(self) -> int: ...
    def contains_point(self, px: float, py: float) -> bool: ...

class Unit:
    """CSS-like unit with value and type."""

    value: float
    type: UnitType

    def __init__(self, value: float, unit_type: UnitType) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    @staticmethod
    def px(value: float) -> "Unit": ...
    @staticmethod
    def percent(value: float) -> "Unit": ...
    @staticmethod
    def vw(value: float) -> "Unit": ...
    @staticmethod
    def vh(value: float) -> "Unit": ...
    @staticmethod
    def auto() -> "Unit": ...
