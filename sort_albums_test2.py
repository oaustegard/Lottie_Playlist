# %% Get the albums from the test_covers folder
import os
from typing import Tuple
import webbrowser
import pandas as pd
from PIL import Image

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
    """Determine if a color is 'vivid' based on the saturation and perceived brightness
    Vivid thresholds based on empirical eyeballing of colors using the online tool at
    https://jsfiddle.net/austegard/g1yobd4h/
    :param s: saturation
    :param p: perceived brightness
    :return: True if the color is 'vivid'"""

    return s > 0.15 and p > 0.18 and p < 0.95 
#end def

def get_rainbow_band(hue:float, band_deg:int)->int:
    """
    Get the "rainbow" band for a hue
    for rainbow like color bands
    :param hue: hue in [0, 360]-space
    :param band_size: size of the rainbow band partition in degrees
    :return: the rainbow band index
    """

    # divide the hue 360º into band_deg sized bands. "Correct" for the fact that colors in the 
    # 330º-360º space appear more red than purple, so move those to the other side of the spectrum
    rb_hue = (hue + 30) % 360
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
            #TODO should this be just += 1, += s or += p?  Should all colors contribute equally to define the ranking of the bands?
            vivid_bands[vb] += p  
            vivid_pixels += 1
        #end if
    #end for
    
    # get the bands to use (presumably this will normally be the vivid bands)
    bands, band_pixels = (vivid_bands, vivid_pixels) if sum(vivid_bands.values()) == 0 else (all_bands, len(pixels))
    
    # normalize by dividing each value by the respective number of pixels to get [0,1]-space values
    # if 
    #TODO is this actually necessary? And if so should we use numpy instead of dictionary comprehension for speed?
    #band_pixels = sum(bands.values())
    bands = {k:v/band_pixels for (k,v) in bands.items()}
    perceived_brightness = perceived_brightness / len(pixels)
    
    return bands, perceived_brightness
#end def

#get the primary color band from a bands dictionary
def get_primary_band(bands:dict)->int:
    """
    Get the primary band from a bands dictionary
    :param bands: bands dictionary
    :return: the primary band
    """
    return max(bands, key=bands.get) # I THINK I grok this one
 


# def sort_and_render_images(df:pd.DataFrame, hue_column: str, lightness_column:str)-> pd.DataFrame:
#     """
#     Sort the the dataframe by the chosen hue partition and lightness column then render the images
#     """
#     ldf = df.copy().sort_values(by=[hue_column, lightness_column])

#     #define the html div template
#     div_template = '<img title="prime:{prime_color}, vivid:{vivid_color}, part:{vivid_hue_part}, lum:{prime_lum}, pb:{prime_pb}" src="{image_fqp}" />'
#     # apply the template to each row, return the results as a series, then concatenate the series to a string
#     divs = ldf.apply(div_template.format_map, axis=1, result_type='reduce').str.cat(sep='\n')
#     return divs
# #end def


# %% Test

image_path = 'test_covers/'
image_list = os.listdir(image_path)

image = Image.open(image_path + image_list[0])

bands, pb = get_image_rainbow_bands_and_perceived_brightness(image, 30)
print (bands, pb)
print(sum(bands.values()))
print(max(bands, key=bands.get))

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
for img in image_list:

    image = Image.open(image_path + image)
    bands, pb = get_image_rainbow_bands_and_perceived_brightness(image, band_deg)




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


# output the HTML to a file
with open('sorted_albums_test.html', 'w') as f:
    f.write(ht)
#end with
# open the file in the browser
webbrowser.open('file://' + os.path.realpath('sorted_albums_test.html'))


# %%