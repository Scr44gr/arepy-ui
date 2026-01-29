"""Type stubs for layout Cython module."""

from typing import Tuple

from .types import Unit

class LayoutContext:
    """Context for layout calculations."""

    viewport_width: float
    viewport_height: float

    def __init__(self, viewport_width: float, viewport_height: float) -> None: ...

def resolve_unit(
    unit: Unit, parent_value: float, viewport_width: float, viewport_height: float
) -> float:
    """
    Resolve a Unit to a pixel value.

    Args:
        unit: The Unit object to resolve
        parent_value: Parent dimension for percentage calculations
        viewport_width: Viewport width for vw units
        viewport_height: Viewport height for vh units

    Returns:
        Resolved pixel value
    """
    ...

def resolve_unit_fast(
    value: float, unit_type: int, parent_value: float, vw: float, vh: float
) -> float:
    """
    Fast unit resolution using raw values (no object overhead).

    Args:
        value: The numeric value
        unit_type: Unit type as int (0=px, 1=%, 2=vw, 3=vh, 4=auto)
        parent_value: Parent dimension
        vw: Viewport width
        vh: Viewport height

    Returns:
        Resolved pixel value
    """
    ...

def calculate_content_area(
    x: float,
    y: float,
    width: float,
    height: float,
    padding_top: Unit,
    padding_right: Unit,
    padding_bottom: Unit,
    padding_left: Unit,
    vw: float,
    vh: float,
) -> Tuple[float, float, float, float]:
    """
    Calculate content area after applying padding.

    Returns:
        Tuple of (content_x, content_y, content_width, content_height)
    """
    ...

def calculate_margin_offset(
    margin_top: Unit,
    margin_right: Unit,
    margin_bottom: Unit,
    margin_left: Unit,
    parent_width: float,
    parent_height: float,
    vw: float,
    vh: float,
) -> Tuple[float, float, float, float]:
    """
    Calculate margin offsets.

    Returns:
        Tuple of (top, right, bottom, left) in pixels
    """
    ...

def calculate_flex_main_offset(
    justify_content: int,
    content_size: float,
    total_children_size: float,
    child_count: int,
) -> float:
    """
    Calculate initial offset for flex main axis based on justify-content.

    Args:
        justify_content: 0=start, 1=center, 2=end, 3=space-between, 4=space-around, 5=space-evenly
        content_size: Available space on main axis
        total_children_size: Total size of all children
        child_count: Number of children

    Returns:
        Initial offset
    """
    ...

def calculate_flex_spacing(
    justify_content: int,
    content_size: float,
    total_children_size: float,
    child_count: int,
    gap: float,
) -> float:
    """
    Calculate spacing between flex items.

    Returns:
        Spacing to add between each item
    """
    ...

def calculate_cross_offset(
    align_items: int, content_size: float, child_size: float
) -> float:
    """
    Calculate cross-axis offset based on align-items.

    Args:
        align_items: 0=start, 1=center, 2=end, 3=stretch
        content_size: Available space on cross axis
        child_size: Size of the child

    Returns:
        Offset for cross axis positioning
    """
    ...

def point_in_rect(
    px: float, py: float, rx: float, ry: float, rw: float, rh: float
) -> bool:
    """Fast point-in-rectangle check."""
    ...

def max_f(a: float, b: float) -> float:
    """Fast float max."""
    ...

def min_f(a: float, b: float) -> float:
    """Fast float min."""
    ...

def clamp_f(value: float, min_val: float, max_val: float) -> float:
    """Fast float clamp."""
    ...
