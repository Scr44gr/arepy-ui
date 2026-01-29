# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True


from libc.math cimport pow, sin

# Constants
cdef float PI = 3.14159265358979323846
cdef float HALF_PI = PI / 2.0


# Easing type constants (avoid enum overhead in hot path)
DEF EASING_LINEAR = 0
DEF EASING_EASE_IN_QUAD = 1
DEF EASING_EASE_OUT_QUAD = 2
DEF EASING_EASE_IN_OUT_QUAD = 3
DEF EASING_EASE_IN_CUBIC = 4
DEF EASING_EASE_OUT_CUBIC = 5
DEF EASING_EASE_OUT_BOUNCE = 6
DEF EASING_EASE_OUT_ELASTIC = 7
DEF EASING_EASE_OUT_EXPO = 8
DEF EASING_EASE_IN_EXPO = 9
DEF EASING_EASE_OUT_BACK = 10
DEF EASING_EASE_IN_BACK = 11


cdef inline float _ease_linear(float t) noexcept nogil:
    return t


cdef inline float _ease_in_quad(float t) noexcept nogil:
    return t * t


cdef inline float _ease_out_quad(float t) noexcept nogil:
    return t * (2.0 - t)


cdef inline float _ease_in_out_quad(float t) noexcept nogil:
    if t < 0.5:
        return 2.0 * t * t
    return -1.0 + (4.0 - 2.0 * t) * t


cdef inline float _ease_in_cubic(float t) noexcept nogil:
    return t * t * t


cdef inline float _ease_out_cubic(float t) noexcept nogil:
    cdef float f = t - 1.0
    return f * f * f + 1.0


cdef inline float _ease_out_expo(float t) noexcept nogil:
    if t >= 1.0:
        return 1.0
    return 1.0 - pow(2.0, -10.0 * t)


cdef inline float _ease_in_expo(float t) noexcept nogil:
    if t <= 0.0:
        return 0.0
    return pow(2.0, 10.0 * (t - 1.0))


cdef inline float _ease_out_back(float t) noexcept nogil:
    cdef float c1 = 1.70158
    cdef float c3 = c1 + 1.0
    cdef float f = t - 1.0
    return 1.0 + c3 * f * f * f + c1 * f * f


cdef inline float _ease_in_back(float t) noexcept nogil:
    cdef float c1 = 1.70158
    cdef float c3 = c1 + 1.0
    return c3 * t * t * t - c1 * t * t


cdef inline float _ease_out_bounce(float t) noexcept nogil:
    cdef float n1 = 7.5625
    cdef float d1 = 2.75

    if t < 1.0 / d1:
        return n1 * t * t
    elif t < 2.0 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


cdef inline float _ease_out_elastic(float t) noexcept nogil:
    cdef float c4 = (2.0 * PI) / 3.0

    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return pow(2.0, -10.0 * t) * sin((t * 10.0 - 0.75) * c4) + 1.0


cpdef float apply_easing(float t, int easing_type):
    """
    Apply easing function to a normalized time value.

    Args:
        t: Normalized time (0.0 to 1.0)
        easing_type: Easing type constant (0-11)

    Returns:
        Eased value (0.0 to 1.0)
    """
    if easing_type == EASING_LINEAR:
        return _ease_linear(t)
    elif easing_type == EASING_EASE_IN_QUAD:
        return _ease_in_quad(t)
    elif easing_type == EASING_EASE_OUT_QUAD:
        return _ease_out_quad(t)
    elif easing_type == EASING_EASE_IN_OUT_QUAD:
        return _ease_in_out_quad(t)
    elif easing_type == EASING_EASE_IN_CUBIC:
        return _ease_in_cubic(t)
    elif easing_type == EASING_EASE_OUT_CUBIC:
        return _ease_out_cubic(t)
    elif easing_type == EASING_EASE_OUT_BOUNCE:
        return _ease_out_bounce(t)
    elif easing_type == EASING_EASE_OUT_ELASTIC:
        return _ease_out_elastic(t)
    elif easing_type == EASING_EASE_OUT_EXPO:
        return _ease_out_expo(t)
    elif easing_type == EASING_EASE_IN_EXPO:
        return _ease_in_expo(t)
    elif easing_type == EASING_EASE_OUT_BACK:
        return _ease_out_back(t)
    elif easing_type == EASING_EASE_IN_BACK:
        return _ease_in_back(t)

    return t


cpdef float lerp(float start, float end, float t):
    """Linear interpolation between two values."""
    return start + (end - start) * t


cpdef float clamp(float value, float min_val, float max_val):
    """Clamp a value between min and max."""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


cpdef float inverse_lerp(float start, float end, float value):
    """Get the t value for a value between start and end."""
    if end - start == 0:
        return 0.0
    return (value - start) / (end - start)


cpdef float remap(float value, float in_min, float in_max, float out_min, float out_max):
    """Remap a value from one range to another."""
    cdef float t = inverse_lerp(in_min, in_max, value)
    return lerp(out_min, out_max, t)


# Easing enum for Python API (matches animation.py)
class Easing:
    LINEAR = EASING_LINEAR
    EASE_IN_QUAD = EASING_EASE_IN_QUAD
    EASE_OUT_QUAD = EASING_EASE_OUT_QUAD
    EASE_IN_OUT_QUAD = EASING_EASE_IN_OUT_QUAD
    EASE_IN_CUBIC = EASING_EASE_IN_CUBIC
    EASE_OUT_CUBIC = EASING_EASE_OUT_CUBIC
    EASE_OUT_BOUNCE = EASING_EASE_OUT_BOUNCE
    EASE_OUT_ELASTIC = EASING_EASE_OUT_ELASTIC
    EASE_OUT_EXPO = EASING_EASE_OUT_EXPO
    EASE_IN_EXPO = EASING_EASE_IN_EXPO
    EASE_OUT_BACK = EASING_EASE_OUT_BACK
    EASE_IN_BACK = EASING_EASE_IN_BACK
