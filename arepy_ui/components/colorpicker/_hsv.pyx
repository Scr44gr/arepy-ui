# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""
Optimized HSV color conversion functions for ColorPicker.

This module provides fast HSV to RGB conversion and gradient generation.
No numpy dependency - returns bytes directly for GPU upload.
"""

from math import fmod, fabs


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    """
    Convert HSV to RGB color.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        v: Value/Brightness (0-1)
        
    Returns:
        Tuple of (r, g, b) as integers 0-255
    """
    # Normalize hue to 0-360
    h = fmod(h, 360.0)
    if h < 0:
        h += 360.0
    
    c = v * s
    hi = int(h / 60.0)
    x = c * (1.0 - fabs(fmod(h / 60.0, 2.0) - 1.0))
    m = v - c
    
    if hi == 0:
        r, g, b = c, x, 0.0
    elif hi == 1:
        r, g, b = x, c, 0.0
    elif hi == 2:
        r, g, b = 0.0, c, x
    elif hi == 3:
        r, g, b = 0.0, x, c
    elif hi == 4:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x
    
    return (
        int((r + m) * 255.0),
        int((g + m) * 255.0),
        int((b + m) * 255.0)
    )


def rgb_to_hsv(r: int, g: int, b: int) -> tuple:
    """
    Convert RGB to HSV color.
    
    Args:
        r, g, b: RGB values 0-255
        
    Returns:
        Tuple of (h, s, v) where h is 0-360, s and v are 0-1
    """
    rf = r / 255.0
    gf = g / 255.0
    bf = b / 255.0
    
    cmax = max(rf, gf, bf)
    cmin = min(rf, gf, bf)
    
    delta = cmax - cmin
    v = cmax
    
    if delta < 0.00001:
        return (0.0, 0.0, v)
    
    s = delta / cmax if cmax > 0 else 0.0
    
    if rf >= cmax:
        h = (gf - bf) / delta
    elif gf >= cmax:
        h = 2.0 + (bf - rf) / delta
    else:
        h = 4.0 + (rf - gf) / delta
    
    h *= 60.0
    if h < 0:
        h += 360.0
    
    return (h, s, v)


def generate_sv_gradient_rgba(hue: float, width: int, height: int) -> bytes:
    """
    Generate a Saturation-Value gradient as RGBA bytes.
    
    This creates RGBA data where:
    - X axis = Saturation (0 to 1)
    - Y axis = Value (1 to 0, top is bright)
    
    Args:
        hue: The hue value (0-360)
        width: Width of the gradient
        height: Height of the gradient
        
    Returns:
        bytes of length width * height * 4 (RGBA)
    """
    # Pre-allocate buffer
    buffer = bytearray(width * height * 4)
    
    # Normalize hue
    h_norm = fmod(hue, 360.0)
    if h_norm < 0:
        h_norm += 360.0
    
    # Pre-compute hue sector values (constant for all pixels)
    hi = int(h_norm / 60.0) % 6
    h_frac = fmod(h_norm / 60.0, 2.0) - 1.0
    if h_frac < 0:
        h_frac = -h_frac
    
    idx = 0
    for y in range(height):
        # Value goes from 1 (top) to 0 (bottom)
        v = 1.0 - (y / (height - 1)) if height > 1 else 1.0
        
        for x in range(width):
            # Saturation goes from 0 (left) to 1 (right)
            s = x / (width - 1) if width > 1 else 0.0
            
            # HSV to RGB
            c = v * s
            x_val = c * (1.0 - h_frac)
            m = v - c
            
            if hi == 0:
                r = int((c + m) * 255.0)
                g = int((x_val + m) * 255.0)
                b = int(m * 255.0)
            elif hi == 1:
                r = int((x_val + m) * 255.0)
                g = int((c + m) * 255.0)
                b = int(m * 255.0)
            elif hi == 2:
                r = int(m * 255.0)
                g = int((c + m) * 255.0)
                b = int((x_val + m) * 255.0)
            elif hi == 3:
                r = int(m * 255.0)
                g = int((x_val + m) * 255.0)
                b = int((c + m) * 255.0)
            elif hi == 4:
                r = int((x_val + m) * 255.0)
                g = int(m * 255.0)
                b = int((c + m) * 255.0)
            else:
                r = int((c + m) * 255.0)
                g = int(m * 255.0)
                b = int((x_val + m) * 255.0)
            
            buffer[idx] = r
            buffer[idx + 1] = g
            buffer[idx + 2] = b
            buffer[idx + 3] = 255  # Alpha
            idx += 4
    
    return bytes(buffer)


def generate_hue_gradient_rgba(width: int, height: int, vertical: bool = True) -> bytes:
    """
    Generate a hue gradient bar as RGBA bytes.
    
    Args:
        width: Width of the gradient
        height: Height of the gradient
        vertical: If True, hue varies vertically; if False, horizontally
        
    Returns:
        bytes of length width * height * 4 (RGBA)
    """
    buffer = bytearray(width * height * 4)
    
    size = height if vertical else width
    
    idx = 0
    for y in range(height):
        for x in range(width):
            # Calculate hue based on position
            if vertical:
                h = (y / (size - 1)) * 360.0 if size > 1 else 0.0
            else:
                h = (x / (size - 1)) * 360.0 if size > 1 else 0.0
            
            # HSV to RGB with S=1, V=1
            hi = int(h / 60.0) % 6
            h_frac = fmod(h / 60.0, 2.0) - 1.0
            if h_frac < 0:
                h_frac = -h_frac
            x_val = 1.0 - h_frac  # c * (1 - |h'|) where c=1
            
            if hi == 0:
                r, g, b = 255, int(x_val * 255), 0
            elif hi == 1:
                r, g, b = int(x_val * 255), 255, 0
            elif hi == 2:
                r, g, b = 0, 255, int(x_val * 255)
            elif hi == 3:
                r, g, b = 0, int(x_val * 255), 255
            elif hi == 4:
                r, g, b = int(x_val * 255), 0, 255
            else:
                r, g, b = 255, 0, int(x_val * 255)
            
            buffer[idx] = r
            buffer[idx + 1] = g
            buffer[idx + 2] = b
            buffer[idx + 3] = 255  # Alpha
            idx += 4
    
    return bytes(buffer)
