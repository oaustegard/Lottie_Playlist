# %% Get the albums from the test_covers folder
import os
from typing import Tuple
from IPython.display import display, HTML, Image
from colorthief import ColorThief
from numpy import partition
from color_utility import perceived_brightness, perceived_brightness_255, vividity
import pandas as pd

#%%

def append_row(df:pd.DataFrame, row:list)->None:
    '''Append a row to a dataframe
    :param df: dataframe to append to
    :param row: row to append'''
    df.loc[len(df.index)] = row


def get_dominant_colors(image:str)->Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    '''Get the dominant colors from an image using the ColorThief library
    :param image: full path to the image or the image file itself
    :return: a tuple of the dominant and dominant "vivid" colors as RGB tuples'''
    color_thief = ColorThief(image)
    # get the dominant colors
    palette = color_thief.get_palette(quality=5, color_count=5) 
    prime_color = palette[0]
    # Find the first "vivid" color: saturation and relative luminance product between 0.1 and 0.9
    vivid_color = None
    for v in palette:
        (_,_,p) = vividity(v)
        if p > 0.1 and p < 0.9:
            vivid_color = v
            break
    #end for
    # if we didn't find a "vivid" color, use prime_color for both
    return prime_color, vivid_color or prime_color
#end def

def rgb_to_hue_luminance_brightness(rgb:tuple)->Tuple[float, float, float]:
    '''Convert an RGB color to a hue, luminance and perceived brightness as per 
    standard HSV/HSL theory (https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB), 
    relative luminance theory (https://en.wikipedia.org/wiki/Relative_luminance),
    and perceived brightness theory (http://alienryderflex.com/hsp.html)

    :param rgb: RGB color as a list of [0, N]-space values
    :return: a tuple with the hue in [0, 360]-space and luminance and perceived 
    brightness in the same [0, N]-space as the input color
    '''
    r, g, b = rgb
    
    # extract the hue-bit from ColorSys' rgb_to_hsl
    maxc = max(r, g, b)
    minc = min(r, g, b)
    if maxc == minc:
        h = 0.0
    else:
        rangec = (maxc-minc)

        rc = (maxc-r) / rangec
        gc = (maxc-g) / rangec
        bc = (maxc-b) / rangec
        if r == maxc:
            h = bc-gc
        elif g == maxc:
            h = 2.0+rc-bc
        else:
            h = 4.0+gc-rc
        h = ((h/6.0) % 1.0) * 360
    #end ifelse

    # Relative Luminance
    lum = 0.2126*r + 0.7152*g + 0.0722*b

    # perceived brightness by Darel Rex Finley/Adobe Photoshop
    pb = (0.299 * r * r + 0.587 * g * g + 0.114 * b * b)**0.5
    
    return h, lum, pb
#end def

def sort_and_render_images(df:pd.DataFrame, color:str, hue_column: str, lightness_column:str)-> pd.DataFrame:
    """
    Sort the the dataframe by the chosen hue partition and lightness column then render the images
    """
    ldf = df.copy().sort_values(by=[hue_column, lightness_column])

    #define the html div template
    div_template = '<img title="prime:{prime_color}, vivid:{vivid_color}, part:{vivid_hue_part}, lum:{prime_lum}, pb:{prime_pb}" src="{image_fqp}" />'
    # apply the template to each row, return the results as a series, then concatenate the series to a string
    divs = ldf.apply(div_template.format_map, axis=1, result_type='reduce').str.cat(sep='\n')
    return divs
#end def

# %%

# the images are in "../Lottie_Playlist/test_covers/"
# get a list of the available images
#image_path = '/Users/austegard/Projects/Lottie_Playlist/test_covers/'
image_path = 'test_covers/'
image_list = os.listdir(image_path)

df = pd.DataFrame(
    columns=['image_fqp', 
        'prime_color', 'prime_hue', 'prime_lum', 'prime_pb', 
        'vivid_color', 'vivid_hue', 'vivid_lum', 'vivid_pb'])

# for each image, extract the top color as well as the top "vivid" color 
# then get the hue and perceived lightness of each colors
# and add to the dataframe
for image in image_list:
    #get the image file object
    image_fqp = image_path + image
    prime_color, vivid_color = get_dominant_colors(image_fqp)
    prime_hue, prime_lum, prime_pb = rgb_to_hue_luminance_brightness(prime_color)
    vivid_hue, vivid_lum, vivid_pb = rgb_to_hue_luminance_brightness(vivid_color)
    row = [image_fqp, 
        prime_color, prime_hue, prime_lum, prime_pb, 
        vivid_color, vivid_hue, vivid_lum, vivid_pb]
    append_row(df, row)

# The color wheel is centered on red at 0 degrees, but some of the colors near 360 
# are also closer to red than violet, so shift the hue to capture these as 'red'
hue_shift = 30
# partition the hue into 360/partition_degrees bands
partition_degrees = 60
# get the hue partition for both the prime and vivid colors
df['prime_hue_part'] = ((df['prime_hue'] + hue_shift) % 360) // partition_degrees
df['vivid_hue_part'] = ((df['vivid_hue'] + hue_shift) % 360) // partition_degrees


# %%
# generate the HTML table
ht = \
f'''<style>img {{max-height: 50px; display:block;}}</style>
<table>
    <tr><th>Vivid/Lum</th><th>Vivid/PB</th>
        <th>Viv hue/Prim Lum</th><th>Viv hue/Prim PB</th></tr>
    <tr>
        <td>{sort_and_render_images(df, "vivid_color", "vivid_hue_part", "vivid_lum")}</td>
        <td>{sort_and_render_images(df, "vivid_color", "vivid_hue_part", "vivid_pb")}</td>
        <td>{sort_and_render_images(df, "vivid_color", "vivid_hue_part", "prime_lum")}</td>
        <td>{sort_and_render_images(df, "vivid_color", "vivid_hue_part", "prime_pb")}</td>
    </tr>
</table>'''

print(ht)

#display(HTML(ht))
#<th>Prime/Lum</th><th>Prime/PB</th>
#        <td>{sort_and_render_images(df, "prime_color", "prime_hue", "prime_lum")}</td>
#        <td>{sort_and_render_images(df, "prime_color", "prime_hue", "prime_pb")}</td>


# %%
