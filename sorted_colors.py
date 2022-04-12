# %% [markdown]
# # Sorting Colors
# Naive question: *If given a bunch of random colors, can we sort them like a rainbow?*
# 
# (see ColorPlay.ipynb for the original ask)
# 
# 

# %% [markdown]
# ## (Naive) Attempt 1: Sort by Hex Value
# 
# Let's start with basic hex colors, as commonly used in HTML/CSS - they're strings, ordered by color; should work, right?:

# %%
import random
from IPython.core.display import display, HTML

# %%
# generate 100 hex colors and simply sort by RRGGBB hex values
hex_colors = []
for i in range(100):
    hex_color = '#' + ''.join([random.choice('0123456789ABCDEF') for i in range(6)])
    hex_colors.append(hex_color)

# sort the list by the hex code
hex_colors.sort()

#ouput the list as a set of html divs with the hex code as the background color and the code as the string in the div
html = '\n'.join([f'<div style="background-color: {hex_color}; zoom:30%;">{hex_color}</div>' for hex_color in hex_colors])
display(HTML(html))

# %% [markdown]
# Ok, if you squint that is sort of a gradient, but far too noisy to feel "sorted". And definitely not a "rainbow" feel.
# 
# Need to do some actual research.

# %% [markdown]
# # ... Many websites later...
# Oh boy. **Color**. It's a whole _thing_. Renewed respect for Pantone, Behr, van Gogh and TV makers!
# 
# Ok, main issue: color is a 3D space and we're trying to somehow flatten it into a list: 1D space. There's going to have to be compromises.
# 
# Let's start by what we most often think of as "the color" - the Hue.

# %% [markdown]
# ## Hue
# 
# We're taught as kids that the rainbow is ROYGBIV - 7 colors (but they forgot to teach us about Cyan and nobody gets the difference between Indigo and Violet). Of course we know there are infinitely many more (also, aside, where is brown? gray? black?) but can we do something similar?  
# 
# The 3D color space can be represented as Hue, Saturation and Lightness - HSL (or sometimes HLS). Hue is often represented as the angle around a color wheel, with Red at 0 (and 360), Yellow at 60, Green at 120 and so on. A list of different hues with same saturation and lightness does indeed look like what we're after:

# %%
display(HTML('''
    <div style="background-color:hsl(0, 100%, 50%)">Red</div>
    <div style="background-color:hsl(60, 100%, 50%">Yellow</div>
    <div style="background-color:hsl(120, 100%, 50%">Green</div>
    <div style="background-color:hsl(180, 100%, 50%">Cyan</div>
    <div style="background-color:hsl(240, 100%, 50%">Blue</div>
    <div style="background-color:hsl(300, 100%, 50%">Magenta</div>
'''))

# %% [markdown]
# ### Attempt 2: Sort by Hue
# 
# Ok, rather than hex colors, let's generate a bunch of random HSL colors and then sort those by Hue:

# %%
hsl_colors = []
for i in range(100):
    hsl = (random.random()*360, random.random()*100, random.random()*100)
    hsl_colors.append(hsl)

# sort the list by the first tuple value, the hue
hsl_colors.sort(key=lambda x: x[0])

html = '\n'.join([f'<div style="background-color: hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%); zoom:30%" title="hsl({hsl[0]}, {hsl[1]}%, {hsl[1]}%)">&nbsp;</div>' for hsl in hsl_colors])
display(HTML(html))

# %% [markdown]
# Hmmm, yeah, closer, I guess? But it's very stripy, lots of mixing of light and dark inbetween the more 
# saturated colors. _Shockingly_ simply using one of the three dimensions is not enough here. 
# 
# _Next._

# %% [markdown]
# ## Lightness 
# 
# The main problem with simply sorting by Hue seems to be the mix of light and dark bands between colors 
# with relatively similar hues. No cler rainbow pattern.
# 
# The rainbow above was 6 colors, same saturation and lightness separated by 60 degreees of Hue. What if 
# we partitioned by Hue and then sorted by Lightness?

# %%
# partition the list by Hue, then sort the list by the lightness value
hsl_colors.sort(key=lambda x: x[0]//60+ x[2]/100)

html = '\n'.join([f'<div style="background-color: hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%); zoom:30%" title="hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)">&nbsp;</div>' for hsl in hsl_colors])
display(HTML(html))

# %% [markdown]
# Ok, we have _something_ here. But the Hue bands may be too broad? There seems to be similar looking colors 
# in different bands. And red shows up again in the last one?  If we're looking for a "rainbow" we need red 
# just on the top. Let's try smaller bands and shifting the axis a bit to get the tail-end Reds up top:

# %%
# partition the list by 30 degrees of Hue with axis shifted 30 degrees, then sort the list by the lightness value
hsl_colors.sort(key=lambda x: ((x[0]+30)%360)//30+ x[2]/100)

html = '\n'.join([f'<div style="background-color: hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%); zoom:30%" title="hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%) =&gt; {((hsl[0]+30)%360)//30+hsl[2]/100}">&nbsp;</div>' for hsl in hsl_colors])
display(HTML(html))

# %% [markdown]
# Ok the bands are now in "proper" rainbow order, but the lightness sort doesn't quite work.

# %% [markdown]
# ## Many more websites later...

# %% [markdown]
# ## _Perceived_ Lightness
# Turns out Red, Green and Blue, the ingredients from which we can generate 16,581,375 colors (plus transparency) 
# are quite different from a human perception standpoint. We've evolved on land, to survive among grass and 
# forests, and there's not a ton of blue things in nature that looked edible or threatened to kill us; meanwhile 
# the right plants provided nourishment. 
# 
# So, assuming normal color vision, the same amounts of R, G and B light don't look the same from a brightness 
# standpoint, as is clear from the below: the text is the same white in all three colors, but while it's legible 
# for Blue and Red, it's almost impossible to read for Green - there is not enough _perceptible_ contrast betwen 
# the white and green, i.e. the same amount of green is _perceived to be lighter_ than the other two colors:

# %%
display(HTML('''
    <div style="background-color:#f00">Red</div>
    <div style="background-color:#0f0">Green</div>
    <div style="background-color:#00f">Blue</div>
'''))

# %% [markdown]
# There's been a [_lot_ of research in this area](https://culorijs.org/color-spaces/) and several formulae have been arrived at for calculating the 
# lightness of a color, as perceived by humans. None of them are perfect, so let's empirically compare a few of them by 
# trying each.
# 
# But first, that lambda for sorting is getting out of hand, and the html is getting complex, let's clean up 
# the code, and why not -- use Pandas for the data structure:

# %%
import math
import colorsys 
import pandas as pd
import numpy as np

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

def hsp(rgb:tuple) -> float:
    """ 
    Returns the perceived brightness of an r, g, b color tuple in the range [0, 1] based on the 
    "perceived lightness" system by Darel Rex Finley/Photoshop
    See http://alienryderflex.com/hsp.html
    """
    r, g, b = rgb
    return math.sqrt(0.299 * r * r + 0.587 * g * g + 0.114 * b * b)


def generate_random_colors(n:int)-> list:
    """
    Generate a list of n random colors in the range [0, 1] as a r, g, b, tuple
    """
    return [tuple(np.random.rand(3)) for i in range(n)]

def enrich_color(rgb:tuple) -> tuple:
    """
    Enrich a color tuple with the hsl, y_luma, luminance, and hsp values returning a tuple with a layout of 
    (r, g, b, h, s, l, y, lum, p)
    Each of these could probably be vectorized and done individually in generate_color_df 🤷🏻‍♂️
    """
    return rgb + hsl(rgb) + (y_luma(rgb),) + (luminance(rgb),) + (hsp(rgb),)

def generate_color_df(colors:list, partition_degrees: int)-> pd.DataFrame:
    """
    Convert a list of [0, 1] enriched color tuples with a (r, g, b, h, s, l, y, lum, p) layout to a fleshed out 
    dataframe with [0, 255] rgb values, hsl, "corrected" hue, hue partition index, and various lightness values
    """
    df = pd.DataFrame(colors, columns=['r', 'g', 'b', 'h', 's', 'l', 'y', 'lum', 'p'])
    # convert rgb to [0, 255] space and hue to degrees
    df['r'] = df['r'] * 255
    df['g'] = df['g'] * 255
    df['b'] = df['b'] * 255
    df['h'] = df['h'] * 360
    # round the values in the columns since they carry too much precision to be useful
    df = df.round(3).round({"r": 1, "g": 1, "b": 1, "h": 1})
    
    # shift the hue 30 degrees to group reds at top, store in a new column, ch
    df['ch'] = (df['h'] + 30) % 360 
    # partition the hues into 360/partition_degrees bands
    df['h_part'] = (df['ch'] // partition_degrees).astype(int)

    return df

def sort_and_render_colors(df:pd.DataFrame, lightness_column:str)-> pd.DataFrame:
    """
    Sort the the dataframe by the hue partition and the chosen lightness column then render the colors as html divs
    """
    ldf = df.copy().sort_values(by=['h_part', lightness_column])

    #define the html div template
    div_template = '<div style="background-color:rgb({r},{g},{b});" title="hsl({h},{s},{l}) =&gt; {h_part}.{' \
        + lightness_column + '}">&nbsp;</div>'
    # apply the template to each row, return the results as a series, then concatenate the series to a string
    divs = ldf.apply(div_template.format_map, axis=1, result_type='reduce').str.cat(sep='\n')
    return divs

# %% [markdown]
# ## Let the Sorting now begin!
# Left as mental exercise: Insert sorting-hat gif here...
# 
# Ok, that's all the logic moved into functions, let's generate a new set of colors and display them in a table, 
# with each column partitioned and sorted 
# by the various lightness formulae

# %%
rgbs = generate_random_colors(400)
# enrich the tuples THEN generate the dataframe - this would likely be faster to do as vectorized functions in 
# the dataframe conversion process but favoring simplicity over performance here
enriched_colors = [enrich_color(rgb) for rgb in rgbs]
cdf = generate_color_df(enriched_colors, partition_degrees=40)

# generate the HTML table
ht = \
'''<style>td {width: 150px;} td>div {height: 5px;}</style>
<table>
    <tr><th>YIQ Luma</th><th>HSL Lightness</th><th>Luminance</th><th>HSP Lightness</th></tr>
    <tr>''' \
    + f'<td>{sort_and_render_colors(cdf, "y")}</td>' \
    + f'<td>{sort_and_render_colors(cdf, "l")}</td>' \
    + f'<td>{sort_and_render_colors(cdf, "lum")}</td>' \
    + f'<td>{sort_and_render_colors(cdf, "p")}</td>' \
    + '''
    </tr>
</table>'''

display(HTML(ht))


# %% [markdown]
# ## Conclusion?
# I placed these in order of -- in my opinion -- from worst to best. YIQ clearly has its place in television, 
# but as far as for this use case its Luma does not work well.
# The "out of the box" lightness value of HSL works moderately better, but the luminance and perceived lightness 
# of the HSP formula are the best, with HSP's "perceived lightness" eeking out a win. Luminance has the benefit 
# of being an accepted standard thoug