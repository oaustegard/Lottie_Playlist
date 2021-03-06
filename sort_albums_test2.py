# %% Get the albums from the test_covers folder
import os
from IPython.display import display
from typing import Tuple
import webbrowser
import pandas as pd
from PIL import Image
import pprint

#%%

def append_row(df:pd.DataFrame, row:list)->None:
    '''Append a row to a dataframe
    :param df: dataframe to append to
    :param row: row to append'''
    df.loc[len(df.index)] = row

def normalize_color(rgb:tuple) -> tuple:
    """
    Normalize [0,255] color to [0,1] space
    """
    # use list comprehension to convert [0,255] color to [0,1] space
    return tuple([x/255 for x in rgb])


def rgb_to_hsp(rgb:tuple)->Tuple[int, float, float]:
    """Convert an RGB color to Hue, Saturation, and Perceived Brightness
    Use the HSL algorithm from ColorSys and the Perceived Brightness
    algorithm from http://alienryderflex.com/hsp.html by Darel Rex Finley
    :param rgb: RGB color as a tuple of [0, N]-space values
    :return: a tuple with the hue in [0, 360]-space, saturation 
    and perceived brightness in the same [0, N]-space as the input color"""
    #TODO import rgb_to_hls from ColorSys instead of hardcoding it here?
    r, g, b = rgb
    maxc = max(r, g, b)
    minc = min(r, g, b)
    sumc = (maxc+minc)
    rangec = (maxc-minc)
    l = sumc/2.0
    if minc == maxc:
        return 0.0, l, 0.0
    if l <= 0.5:
        s = rangec / sumc
    else:
        s = rangec / (2.0-sumc)
    rc = (maxc-r) / rangec
    gc = (maxc-g) / rangec
    bc = (maxc-b) / rangec
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = int((h/6.0) % 1.0 * 360.0) # I don't quite grok the %1.0 part, but it seems to work

    p = (0.299 * r * r + 0.587 * g * g + 0.114 * b * b)**0.5
    
    return h, s, p
#end def

def is_vivid(s:float, p:float)->bool:
    """Determine if a color is 'vivid' based on the saturation and perceived brightness.
    Vivid thresholds based on the super-scientific approach of one person empirically 
    eyeballing colors of various saturation and brightnesss on an uncalibrated monitor, 
    using his own created online tool at https://jsfiddle.net/austegard/g1yobd4h/
    :param s: saturation
    :param p: perceived brightness
    :return: True if the color is 'vivid'"""

    return s > 0.15 and p > 0.18 and p < 0.95 
#end def

def get_rainbow_band(hue:float, band_deg:int)->int:
    """
    Get the "rainbow" band for a hue by dividing the hue color wheel into band_deg-sized partitions.
    Since the last 30?? of the hue appears to this developer as more red than violet, 
    shift the hue wheel by 30?? so they appear with the other reds at the beginning of the wheel 
    for rainbow like color bands
    :param hue: hue in [0, 360]-space
    :param band_size: size of the rainbow band partition in degrees
    :return: the rainbow band index
    """
    # apply the 30?? shift
    rb_hue = (hue + 30) % 360
    # return the band index
    return rb_hue // band_deg


# for a given PIL Image object, extract the pixels, then for each get the HSP color, 
# increment the image's perceived brightness value, then check the vividness of the color; 
# if vivid get the hue partition and increment the hue counter. Finally divide counters by the pixel count to get [0,1]-space values.
def get_image_rainbow_bands_and_perceived_brightness(image:Image, band_deg:int)->Tuple[dict[int, float], float]:
    """
    Get the rainbow bands (aka hue partitions) as a list of relative saturation for vivid colors 
    as well as the perceived brightness for an image
    :param image: PIL Image object
    :return: a tuple with the hue partitions as a list of floats and perceived brightness as a float
    """
    # convert the image to RGB and read the pixels
    pixels = image.convert('RGB').getdata()
    #TODO: for large images probably do some sampling to avoid memory issues, for now count on the images being small enough
    
    band_cnt = 360 // band_deg
    all_bands = dict.fromkeys(range(band_cnt), 0) 
    vivid_bands = dict.fromkeys(range(band_cnt), 0) 
    perceived_brightness = 0.0
    vivid_pixels = 0
    # for each pixel, get the HSP color, increment the perceived brightness...
    for pixel in pixels:
        rgb = normalize_color(pixel)
        h, s, p = rgb_to_hsp(rgb)
        perceived_brightness += p
        # also capture the band just in the exceedingly rare case there are NO vivid colors
        ab = get_rainbow_band(h, band_deg)
        all_bands[ab] += p

        # ...and check if the color is vivid, if so get the rainbow band...
        if is_vivid(s, p):
            vb = get_rainbow_band(h, band_deg)
            # ... and increment the band value by the perceived brightness of the color
            #TODO should this be just += 1, += s or += p? Should all colors contribute 
            # equally to define the ranking of the bands? 
            vivid_bands[vb] += s  
            vivid_pixels += 1
        #end if
    #end for
    
    # get the bands to use (presumably this will normally be the vivid bands)
    if sum(vivid_bands.values()) > 0:
        bands = vivid_bands
        band_pixels = vivid_pixels
    else:
        bands = all_bands
        band_pixels = len(pixels)
    
    # normalize by dividing each value by the respective number of pixels to get [0,1]-space 
    # values to allow accurate comparison of different-sized images
    bands = {k:v/band_pixels for (k,v) in bands.items()}
    perceived_brightness = perceived_brightness / len(pixels)
    
    return bands, perceived_brightness
#end def

#get the primary color band from a bands dictionary to use for the hue partition
def get_primary_band(bands:dict)->int:
    """
    Get the primary band from a bands dictionary
    :param bands: bands dictionary
    :return: the primary band
    """
    return max(bands, key=bands.get) # I THINK I grok this one
 

def render_images(df:pd.DataFrame)->str:
    """
    Render the images from the dataframe
    """
    
    #define the html div template
    div_template = '<img title="band: {band}, pb: {pb}" src="{image_fqp}" />'
    # apply the template to each row, return the results as a series, then concatenate the series to a string
    divs = df.apply(div_template.format_map, axis=1, result_type='reduce').str.cat(sep='\n')
    return divs
#end def

# %%

# the images are in "../Lottie_Playlist/test_covers/"
# get a list of the available images
#image_path = '/Users/austegard/Projects/Lottie_Playlist/test_covers/'
image_path = 'test_covers/'
image_list = os.listdir(image_path)

df = pd.DataFrame(
    columns=['image_fqp', 'band', 'pb'])

band_deg = 30

# for each image, filter out the vivid pixels and extract the hue band for each
# then get the hue and perceived lightness of each colors
# and add to the dataframe
for image_file in image_list:
    image_fqp = image_path + image_file
    image = Image.open(image_fqp)
    bands, pb = get_image_rainbow_bands_and_perceived_brightness(image, band_deg)
    primary_band = get_primary_band(bands)
    row = [image_fqp, primary_band, pb]
    append_row(df, row)
# end for

#sort the dataframe by the hue band and perceived brightness
df = df.sort_values(by=['band', 'pb'])

# %%
# generate the HTML

#define the html div template
div_template = '<img title="band: {band}, pb: {pb}" src="{image_fqp}" />'
# apply the template to each row, return the results as a series, then concatenate the series to a string
divs = df.apply(div_template.format_map, axis=1, result_type='reduce').str.cat(sep='\n')

ht = \
'''<style>img {width: 200px; display:block;}</style>
<h2>Arrange by Primary Vivid Hue Band, then Sort by Perceived Brightness</h2>
''' + divs

# output the HTML to a file
with open('sorted_albums_test.html', 'w') as f:
    f.write(ht)
#end with
# open the file in the browser
webbrowser.open('file://' + os.path.realpath('sorted_albums_test.html'))

# %%