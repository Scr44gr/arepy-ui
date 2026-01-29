# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True


from .types import UnitType


# Unit type constants for fast comparison
DEF UNIT_PIXEL = 0
DEF UNIT_PERCENT = 1
DEF UNIT_VW = 2
DEF UNIT_VH = 3
DEF UNIT_AUTO = 4


cdef class LayoutContext:
    """
    Context for layout calculations.
    Holds viewport size to avoid repeated lookups.
    """

    cdef public float viewport_width
    cdef public float viewport_height

    def __init__(self, float viewport_width, float viewport_height):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height


cpdef float resolve_unit(object unit, float parent_value, float viewport_width, float viewport_height):
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
    cdef int unit_type_value
    cdef float value = unit.value

    # Get enum value for fast comparison
    if unit.type == UnitType.PIXEL:
        return value
    elif unit.type == UnitType.PERCENT:
        return parent_value * (value / 100.0)
    elif unit.type == UnitType.VIEWPORT_WIDTH:
        return viewport_width * (value / 100.0)
    elif unit.type == UnitType.VIEWPORT_HEIGHT:
        return viewport_height * (value / 100.0)
    elif unit.type == UnitType.AUTO:
        return parent_value

    return 0.0


cpdef float resolve_unit_fast(float value, int unit_type, float parent_value, float vw, float vh):
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
    if unit_type == UNIT_PIXEL:
        return value
    elif unit_type == UNIT_PERCENT:
        return parent_value * (value / 100.0)
    elif unit_type == UNIT_VW:
        return vw * (value / 100.0)
    elif unit_type == UNIT_VH:
        return vh * (value / 100.0)
    elif unit_type == UNIT_AUTO:
        return parent_value

    return 0.0


cpdef tuple calculate_content_area(
    float x, float y, float width, float height,
    object padding_top, object padding_right,
    object padding_bottom, object padding_left,
    float vw, float vh
):
    """
    Calculate content area after applying padding.

    Returns:
        Tuple of (content_x, content_y, content_width, content_height)
    """
    cdef float pt = resolve_unit(padding_top, height, vw, vh)
    cdef float pr = resolve_unit(padding_right, width, vw, vh)
    cdef float pb = resolve_unit(padding_bottom, height, vw, vh)
    cdef float pl = resolve_unit(padding_left, width, vw, vh)

    return (
        x + pl,
        y + pt,
        width - pl - pr,
        height - pt - pb
    )


cpdef tuple calculate_margin_offset(
    object margin_top, object margin_right,
    object margin_bottom, object margin_left,
    float parent_width, float parent_height,
    float vw, float vh
):
    """
    Calculate margin offsets.

    Returns:
        Tuple of (top, right, bottom, left) in pixels
    """
    return (
        resolve_unit(margin_top, parent_height, vw, vh),
        resolve_unit(margin_right, parent_width, vw, vh),
        resolve_unit(margin_bottom, parent_height, vw, vh),
        resolve_unit(margin_left, parent_width, vw, vh)
    )


cpdef float calculate_flex_main_offset(
    int justify_content,
    float content_size,
    float total_children_size,
    int child_count
):
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
    cdef float remaining = content_size - total_children_size

    if justify_content == 0:  # START
        return 0.0
    elif justify_content == 1:  # CENTER
        return remaining / 2.0
    elif justify_content == 2:  # END
        return remaining
    elif justify_content == 3:  # SPACE_BETWEEN
        return 0.0
    elif justify_content == 4:  # SPACE_AROUND
        if child_count > 0:
            return remaining / (child_count * 2.0)
        return 0.0
    elif justify_content == 5:  # SPACE_EVENLY
        if child_count > 0:
            return remaining / (child_count + 1.0)
        return 0.0

    return 0.0


cpdef float calculate_flex_spacing(
    int justify_content,
    float content_size,
    float total_children_size,
    int child_count,
    float gap
):
    """
    Calculate spacing between flex items.

    Returns:
        Spacing to add between each item
    """
    cdef float remaining = content_size - total_children_size

    if justify_content == 3:  # SPACE_BETWEEN
        if child_count > 1:
            return remaining / (child_count - 1.0)
        return 0.0
    elif justify_content == 4:  # SPACE_AROUND
        if child_count > 0:
            return remaining / child_count
        return 0.0
    elif justify_content == 5:  # SPACE_EVENLY
        if child_count > 0:
            return remaining / (child_count + 1.0)
        return 0.0

    return gap


cpdef float calculate_cross_offset(int align_items, float content_size, float child_size):
    """
    Calculate cross-axis offset based on align-items.

    Args:
        align_items: 0=start, 1=center, 2=end, 3=stretch
        content_size: Available space on cross axis
        child_size: Size of the child

    Returns:
        Offset for cross axis positioning
    """
    if align_items == 0:  # START
        return 0.0
    elif align_items == 1:  # CENTER
        return (content_size - child_size) / 2.0
    elif align_items == 2:  # END
        return content_size - child_size
    elif align_items == 3:  # STRETCH
        return 0.0

    return 0.0


cpdef bint point_in_rect(float px, float py, float rx, float ry, float rw, float rh):
    """Fast point-in-rectangle check."""
    return px >= rx and px <= rx + rw and py >= ry and py <= ry + rh


cpdef float max_f(float a, float b):
    """Fast float max."""
    if a > b:
        return a
    return b


cpdef float min_f(float a, float b):
    """Fast float min."""
    if a < b:
        return a
    return b


cpdef float clamp_f(float value, float min_val, float max_val):
    """Fast float clamp."""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value
