# %% Test ColorThief on a few test images
import os
from IPython.display import display, HTML, Image
from colorthief import ColorThief

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


# the images are in "../Lottie_Playlist/test_covers/"
# get a list of the available images
image_path = "/Users/austegard/Projects/Lottie_Playlist/test_covers/"
image_list = os.listdir(image_path)


#for each image, display the image and the top 5 dominant colors
for image in image_list:
    print("\nImage: " + image)
    display(Image(filename=image_path + image))
    # create a ColorThief object for the image
    color_thief = ColorThief(image_path + image)
    # get the dominant colors
    palette = color_thief.get_palette(quality=25, color_count=10) 
    # display the colors
    print ("\nPalette:")
    for c in palette:
        (s,l,p) = vividity(c)
        display(HTML(f'<div style="background-color: rgb{c};">{c} s:{s} l:{l} p:{p}</div>'))

    # filter the palette to only include vivid colors, those with a saturation and lightness 
    # product greater than 0.15
    print ("\nVivid Palette:")
    for v in palette:
        (s,l,p) = vividity(v)
        if p > 0.1 and p < 0.9:
            display(HTML(f'<div style="background-color: rgb{v};">{v} s:{s} l:{l} p:{p}</div>'))
# %%




