# %% Connect to Spotify and get the album covers for a given playlist

import os
import requests
import spotipy
import spotipy.util as util
import pprint
from PIL import Image
from IPython.display import display
from rainbow_util import *
import webbrowser
import creds

pp = pprint.PrettyPrinter(indent=2)


# %% Authenticate with Spotify
# TODO move this to environment variables
client_id = creds.spotify_client_id
client_secret = creds.spotify_client_secret
# TODO prompt the user for this
user_id = '122543813'
scope = 'playlist-modify-private playlist-modify-public'
redirect_uri = 'https://webhook.site/f4ca85af-de35-4d03-9e78-1ef042aef58d'

token = util.prompt_for_user_token(
            user_id, scope, client_id=client_id, client_secret=client_secret,
            redirect_uri=redirect_uri)
sp = spotipy.Spotify(auth=token)

# %% Get the source playlist
fields = 'name,tracks.total'
#TODO: make user input
source_playlist_id = 'spotify:user:spotifycharts:playlist:6h0WIgq1l6s9MJMbXvmJaJ'

pl_results = sp.playlist(source_playlist_id, fields='name,tracks.total')
pp.pprint(pl_results)

playlist_name = pl_results['name']
playlist_length = pl_results['tracks']['total']
# %% Get the tracks from the playlist
offset = 0
playlist_items = []
# loop through the playlist until we get all the tracks
while offset < playlist_length:
    # get the tracks from the playlist
    batch = sp.playlist_tracks(source_playlist_id, offset=offset, 
                fields='items(track(id,track_number,album(images)))')
    batch_items = batch['items']
    pp.pprint(batch_items)
    offset += len(batch_items)
    playlist_items.extend(batch_items)
#end while

# %% Get the album covers for the tracks, extract color info and sort the tracks
df = pd.DataFrame(columns=['track_id', 'band', 'pb', 'track_number', 'img_url'])
# loop through the tracks in the playlist and get the smallest album cover for each track
#TODO: make this parallel to speed up the process?
for item in playlist_items:
    track = item['track']
    track_id = track['id']
    track_number = track['track_number']

    # conveniently the album cover images are always sorted by size, so we can just get 
    # the last one's url
    cover_image_url = track['album']['images'][-1]['url']
    # load the it as a PIL image
    track_image = Image.open(requests.get(cover_image_url, stream=True).raw)

    # get the bands and perceived brightness
    bands, pb = get_image_rainbow_bands_and_perceived_brightness(track_image, band_deg=60)
    primary_band = get_primary_band(bands)
    # add the track to the dataframe
    append_row(df, [track_id, primary_band, pb, track_number, cover_image_url])
#end for

# sort the dataframe by the hue band and perceived brightness and finally track number 
# for multiple tracks from the same album
df = df.sort_values(by=['band', 'pb', 'track_number'])

#extract the resorted track_ids
sorted_track_ids = df['track_id'].tolist()

# %%
# create a Spotify Playlist
new_playlist_name = f'🌈  {playlist_name} 🌈 '
new_playlist_description = f'The {playlist_name} playlist, sorted like a 🌈'
playlist = sp.user_playlist_create(user=user_id, public=False, 
                name=new_playlist_name, description=new_playlist_description)
#get the playlist external url
playlist_external_url = playlist['external_urls']['spotify']

pp.pprint(playlist)

# %% add the tracks to the playlist
offset = 0
while offset < playlist_length:
    # Add the next batch of track ids - conveniently Python doesn't mind you asking for more than is available
    batch = sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=sorted_track_ids[offset:offset+100])
    offset += 100
#end while
# %% open the playlist in a browser
webbrowser.open(playlist_external_url)
# %% Local copy of the playlist - album-deduplified
img_df = df.drop_duplicates(subset=['img_url'])

img_template = '<img title="band: {band}, pb: {pb}" src="{img_url}" />'
# apply the template to each row, return the results as a series, then concatenate the series to a string (phew)
imgs = img_df.apply(img_template.format_map, axis=1, result_type='reduce').str.cat(sep='\n')

ht = \
f'''<html><head><title>{new_playlist_name}</title>
<style>
  body {{font-family:Arial; color:#fff; background-color:#000;text-align:center}}
  div {{margin:0 auto; width:384px; max-width:384px}} 
  img {{width: 64px; height:64px;}}
</style>
</head>
<body><h1>{new_playlist_name}</h1>
<div>
{imgs}
</div>
</body></html>
''' 

# output the HTML to a file
safe_name = ''.join(filter(str.isalnum, playlist_name))
file_name = f'{safe_name}_rainbow.html'
with open(file_name, 'w') as f:
    f.write(ht)
#end with
# open the file in the browser
webbrowser.open('file://' + os.path.realpath(file_name))
# %%