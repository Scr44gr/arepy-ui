"""Type stubs for easing Cython module."""

class Easing:
    """Easing type constants."""

    LINEAR: int
    EASE_IN_QUAD: int
    EASE_OUT_QUAD: int
    EASE_IN_OUT_QUAD: int
    EASE_IN_CUBIC: int
    EASE_OUT_CUBIC: int
    EASE_OUT_BOUNCE: int
    EASE_OUT_ELASTIC: int
    EASE_OUT_EXPO: int
    EASE_IN_EXPO: int
    EASE_OUT_BACK: int
    EASE_IN_BACK: int

def apply_easing(t: float, easing_type: int) -> float:
    """
    Apply easing function to a normalized time value.

    Args:
        t: Normalized time (0.0 to 1.0)
        easing_type: Easing type constant from Easing class

    Returns:
        Eased value (0.0 to 1.0)
    """
    ...

def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values."""
    ...

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    ...

def inverse_lerp(start: float, end: float, value: float) -> float:
    """Get the t value for a value between start and end."""
    ...

def remap(
    value: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """Remap a value from one range to another."""
    ...
