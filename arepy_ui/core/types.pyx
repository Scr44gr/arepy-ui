# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""
Cython-optimized core types for arepy-ui.

Provides fast C-level types for layout calculations.
"""

from enum import Enum, auto


# Re-export CursorType from arepy
from arepy import CursorType


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


cdef class Color:
    """RGBA Color with fast C-level access."""
    
    cdef public int r
    cdef public int g
    cdef public int b
    cdef public int a
    
    def __init__(self, int r, int g, int b, int a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    
    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a
    
    def __getitem__(self, int index):
        if index == 0:
            return self.r
        elif index == 1:
            return self.g
        elif index == 2:
            return self.b
        elif index == 3:
            return self.a
        raise IndexError("Color index out of range")
    
    def __len__(self):
        return 4
    
    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"
    
    def __eq__(self, other):
        if isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            return self.r == other[0] and self.g == other[1] and self.b == other[2] and (len(other) < 4 or self.a == other[3])
        return False
    
    def __hash__(self):
        return hash((self.r, self.g, self.b, self.a))
    
    cpdef Color with_alpha(self, int alpha):
        """Return a new Color with modified alpha."""
        return Color(self.r, self.g, self.b, alpha)


cdef class Vector2:
    """2D Vector with fast C-level access."""
    
    cdef public float x
    cdef public float y
    
    def __init__(self, float x, float y):
        self.x = x
        self.y = y
    
    def __iter__(self):
        yield self.x
        yield self.y
    
    def __getitem__(self, int index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector2 index out of range")
    
    def __len__(self):
        return 2
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    def __eq__(self, other):
        if isinstance(other, Vector2):
            return self.x == other.x and self.y == other.y
        if isinstance(other, (tuple, list)) and len(other) >= 2:
            return self.x == other[0] and self.y == other[1]
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    cpdef Vector2 add(self, Vector2 other):
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)
    
    cpdef Vector2 sub(self, Vector2 other):
        """Subtract two vectors."""
        return Vector2(self.x - other.x, self.y - other.y)
    
    cpdef Vector2 scale(self, float factor):
        """Scale vector by a factor."""
        return Vector2(self.x * factor, self.y * factor)


cdef class Rectangle:
    """Rectangle with fast C-level access."""
    
    cdef public float x
    cdef public float y
    cdef public float width
    cdef public float height
    
    def __init__(self, float x, float y, float width, float height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.width
        yield self.height
    
    def __getitem__(self, int index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.width
        elif index == 3:
            return self.height
        raise IndexError("Rectangle index out of range")
    
    def __len__(self):
        return 4
    
    def __repr__(self):
        return f"Rectangle({self.x}, {self.y}, {self.width}, {self.height})"
    
    cpdef bint contains_point(self, float px, float py):
        """Check if point is inside rectangle."""
        return (
            px >= self.x and 
            px <= self.x + self.width and 
            py >= self.y and 
            py <= self.y + self.height
        )


cdef class Unit:
    """CSS-like unit with value and type."""
    
    cdef public float value
    cdef public object type  # UnitType enum
    
    def __init__(self, float value, object unit_type):
        self.value = value
        self.type = unit_type
    
    def __repr__(self):
        return f"Unit({self.value}, {self.type})"
    
    def __eq__(self, other):
        if isinstance(other, Unit):
            return self.value == other.value and self.type == other.type
        return False
    
    @staticmethod
    def px(float value) -> "Unit":
        """Create a pixel unit."""
        return Unit(value, UnitType.PIXEL)
    
    @staticmethod
    def percent(float value) -> "Unit":
        """Create a percentage unit."""
        return Unit(value, UnitType.PERCENT)
    
    @staticmethod
    def vw(float value) -> "Unit":
        """Create a viewport width unit."""
        return Unit(value, UnitType.VIEWPORT_WIDTH)
    
    @staticmethod
    def vh(float value) -> "Unit":
        """Create a viewport height unit."""
        return Unit(value, UnitType.VIEWPORT_HEIGHT)
    
    @staticmethod
    def auto() -> "Unit":
        """Create an auto unit."""
        return Unit(0, UnitType.AUTO)
