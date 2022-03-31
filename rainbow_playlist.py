# %% 🌈 sorted playlist
""" '🌈 I have too many songs in my playlist. Could you come up with a way to sort them by the color of their album cover? 🌈'

Expectations:
--------------
The source of the data is Spotify
The user can authenticate to access a playlist - or maybe make it public?
Songs from the same album will be ordered by the track number
The user's auth allows uploading the new playlist
"""

# %% Authenticate to Spotify

# %% Get the playlist


# %% Sort the playlist by color - use hex code?

# %% Import the python modules we need for this script
import random
from IPython.core.display import display, HTML
import math


# %%

# generate 100 random hex colors and add them to a list
hex_colors = []
for i in range(100):
    hex_color = '#' + ''.join([random.choice('0123456789ABCDEF') for i in range(6)])
    hex_colors.append(hex_color)

# sort the list by the hex code
hex_colors.sort()

#ouput the list as a set of html divs with the hex code as the background color and the code as the string in the div
html = '<h1>Hex</h1>' + \
    '\n'.join(['<div style="background-color: {};">{}</div>'.format(hex_color, hex_color) for hex_color in hex_colors])
display(HTML(html))

# %%
from typing import NamedTuple
from colorsys import rgb_to_hls, rgb_to_yiq

def luminance(r, g, b):
    """
    Returns the perceived brightness of an r, g, b color tuple in the range [0, 1] using the relative 
    luminance formula
    See https://en.wikipedia.org/wiki/Relative_luminance 
    """
    return 0.2126*r + 0.7152*g + 0.0722*b

def hsp(r, g, b):
    """ 
    Returns the perceived brightness of an r, g, b color tuple in the range [0, 1] based on the "perceived lightness" proposal
    See http://alienryderflex.com/hsp.html
    """
    return math.sqrt(0.299 * r * r + 0.587 * g * g + 0.114 * b * b)

Color = NamedTuple('Color', [
    ('r', float), ('g', float), ('b', float), # rgb values [0-1]
    ('h', float), ('l', float), ('s', float), ('ch', float), #hls and "corrected hue" [0-360, 0-100, 0-100]
    ('lum', float), ('y', float), ('p', float) # "lightness" alternatives to HSL's l
])


def generate_random_colors(num):
    """
    Returns a list of Color objects with random rgb values and associated hls, "corrected" hue, and assorted lightness values
    """
    cols = []
    for i in range(num):
        r, g, b = random.random(), random.random(), random.random()
        h, l, s = rgb_to_hls(r, g, b)
        h *= 360 #convert to degrees
        # spin the hue wheel 30 degrees to lump the reds together for a 'corrected' hue
        ch = (h + 30) % 360
        # alternate lightness calculations taking human percetion into account
        lum = luminance(r, g, b)
        y, _, _ = rgb_to_yiq(r, g, b) #yiq lightness
        p = hsp(r, g, b)

        # round each value to 3 decimal places
        col = Color([round(i, 3) for i in [r, g, b, h, l, s, ch, lum, y, p]])

        cols.append(col)
    return cols

def display_colors(sorted_cols):
    """
    Displays a list of Color objects as a set of html divs with the rgb values as the background color 
    and also as the title of the div
    """
    html = '\n'.join([f'<div style="background-color: rgb({c.r*255},{c.g*255}, {c.b*255}); zoom:30%" title="({c.r*255},{c.g*255}, {c.b*255}) =&gt; {c.sort}">&nbsp;</div>' for c in sorted_cols])
    display(HTML(html))



# %%
cols = generate_random_colors(100)

# %% sort the list by the HSL lightness


cols.sort(key=lambda x: x.l)

html = '<h1>HSL Lightness</h1>' + \
    '\n'.join([f'<div style="background-color: rgb({c.r*255},{c.g*255}, {c.b*255});">L: {c.l}</div>' for c in cols])
display(HTML(html))

# %% partition by corrected hue then sort by lightness
cols.sort(key=lambda x: x.ch//30 + x.l)
html = '<h1>Hue + Lightness</h1>' + \
    '\n'.join([f'<div style="background-color: rgb({c.r*255},{c.g*255}, {c.b*255});">H: {c.h}, L: {c.l}</div>' for c in cols])
display(HTML(html))

# %% partition by corrected hue, then sort by luminance
cols.sort(key=lambda x: x.ch//30 + x.lum)
html = '<h1>Hue + Luminance</h1>' + \
    '\n'.join([f'<div style="background-color: rgb({c.r*255},{c.g*255}, {c.b*255});">H: {c.h}, Lum: {c.lum}</div>' for c in cols])
display(HTML(html))


# %% partition by corrected hue, then sort by YIQ lightness
# see https://en.wikipedia.org/wiki/YIQ
cols.sort(key=lambda x: x.ch//30 + x.y)
html = '<h1>Hue + YIQ Lightness</h1>' + \
    '\n'.join([f'<div style="background-color: rgb({c.r*255},{c.g*255}, {c.b*255});">H: {c.h}, P: {c.y}</div>' for c in cols])
display(HTML(html))

# %% partition by corrected hue, then sort by perceived lightness
cols.sort(key=lambda x: x.ch//30 + x.p)
html = '<h1>Hue + Perceived Lightness</h1>' + \
    '\n'.join([f'<div style="background-color: rgb({c.r*255},{c.g*255}, {c.b*255});">H: {c.h}, P: {c.p}</div>' for c in cols])
display(HTML(html))
# %%

hsl_colors = []
for i in range(100):
    hsl = (random.random()*360, random.random()*100, random.random()*100)
    hsl_colors.append(hsl)

# sort the list by the first tuple value, the hue
hsl_colors.sort(key=lambda x: x[0])

html = '\n'.join([f'<div style="background-color: hsl({hsl[0]}, {hsl[1]}%, {hsl[1]}%); zoom:30%" title="hsl({hsl[0]}, {hsl[1]}%, {hsl[1]}%)">&nbsp;</div>' for hsl in hsl_colors])
display(HTML(html))

# %%
