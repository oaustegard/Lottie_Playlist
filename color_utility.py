
import math
import colorsys 


def normalize_color(rgb:tuple) -> tuple:
    """
    Normalize [0,255] color to [0,1] space
    """
    # use list comprehension to convert [0,255] color to [0,1] space
    return tuple([x/255 for x in rgb])

def vividity(rgb:tuple) ->tuple:
    """Gets a [0, 255] rgb color's saturation, lightness and product of the two
    :param rgb: RGB color as a list of [0, 255] values
    :return: saturation, relative luminance, and product of the two as a [0, 1] range tuple"""
    r, g, b = rgb
    cmax = max(r,g,b)
    cmin = min(r,g,b)
    if cmax == 0:
        s = 0
    else:
        s = round((cmax - cmin)/(cmax + cmin), 3)
    
    # Relative luminance calculation: https://www.w3.org/TR/WCAG20/#relativeluminancedef
    rlum = round((r*0.2126 + g*0.7152 + b*0.0722) / 255, 3)
    
    
    p = round(s*rlum, 3)
    return (s, rlum, p)

# Define various lightness formulae

def hsl(rgb:tuple) -> tuple:
    """
    Calculate the HSL/HLS of an rgb color in the range [0, 1]
    See https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
    """
    (h, l, s) = colorsys.rgb_to_hls(*rgb) #WHY does colorsys use hls? how many bugs has this caused?
    return (h, s, l)
    
def y_luma(rgb:tuple) -> float:
    """
    Calculate the luma of a color in the range [0, 1], per YIQ theory
    See https://en.wikipedia.org/wiki/YIQ#From_RGB_to_YIQ_2
    """
    return colorsys.rgb_to_yiq(*rgb)[1]

def luminance(rgb:tuple) -> float:
    """
    Calculate the perceived brightness of an r, g, b color tuple in the range [0, 1] using the relative 
    luminance formula
    See https://en.wikipedia.org/wiki/Relative_luminance 
    """
    r, g, b = rgb
    return 0.2126*r + 0.7152*g + 0.0722*b

def perceived_brightness(rgb:tuple) -> float:
    """ 
    Returns the perceived brightness of an r, g, b color tuple based on the 
    "perceived lightness" system by Darel Rex Finley/Photoshop
    See http://alienryderflex.com/hsp.html
    Will return a value in the same [0, N] range as the input tuple
    """
    r, g, b = rgb
    return math.sqrt(0.299 * r * r + 0.587 * g * g + 0.114 * b * b)

def enrich_color(rgb:tuple) -> tuple:
    """
    Enrich a color tuple with the hsl, y_luma, luminance, and hsp values returning a tuple with a layout of 
    (r, g, b, h, s, l, y, lum, p)
    Each of these could probably be vectorized and done individually in generate_color_df 🤷🏻‍♂️
    """
    return rgb + hsl(rgb) + (y_luma(rgb),) + (luminance(rgb),) + (hsp(rgb),)
