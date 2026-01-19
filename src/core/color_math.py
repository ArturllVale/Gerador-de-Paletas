import colorsys

def rgb_to_hsv(r, g, b):
    """
    Converts RGB (0-255) to HSV (0.0-1.0).
    """
    return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

def hsv_to_rgb(h, s, v):
    """
    Converts HSV (0.0-1.0) to RGB (0-255).
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def apply_hue_shift(color_rgb, shift_amount):
    """
    Shifts the hue of an RGB color.
    shift_amount: Float between -1.0 and 1.0 (or larger, it wraps).
    """
    r, g, b = color_rgb
    h, s, v = rgb_to_hsv(r, g, b)
    
    # Apply shift and wrap around
    new_h = (h + shift_amount) % 1.0
    
    return hsv_to_rgb(new_h, s, v)

def apply_adjustments(color_rgb, hue_shift=0.0, saturation_mult=1.0, value_mult=1.0):
    """
    Applies Hue shift, Saturation multiplier, and Value multiplier to a color.
    """
    r, g, b = color_rgb
    h, s, v = rgb_to_hsv(r, g, b)
    
    new_h = (h + hue_shift) % 1.0
    new_s = max(0.0, min(1.0, s * saturation_mult))
    new_v = max(0.0, min(1.0, v * value_mult))
    
    return hsv_to_rgb(new_h, new_s, new_v)

def apply_colorize(color_rgb, target_hue, target_sat=None, value_mult=1.0):
    """
    Replaces Hue and Saturation of the pixel, preserving relative Value (Luminance).
    Used for dyeing white/grey/black pixels.
    
    target_hue: 0.0 - 1.0
    target_sat: 0.0 - 1.0 (If None, uses original saturation, which makes no sense for grayscale).
                So defaults to High saturation? Or user defined?
                Let's require target_sat.
    """
    r, g, b = color_rgb
    h, s, v = rgb_to_hsv(r, g, b)
    
    # In colorize mode (Standard "Color" blend mode logic):
    # Hue = Target
    # Sat = Target
    # Val = Original * Multiplier
    
    # If target_sat is not provided, we might want to keep original? (No, that's Hue Shift).
    # IF Colorize, we assume we want to force color.
    
    sat = target_sat if target_sat is not None else s
    
    return hsv_to_rgb(target_hue, sat, max(0.0, min(1.0, v * value_mult)))
