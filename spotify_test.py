# %% Connect to Spotify and get the album covers for a given playlist
# import spotipy
# import spotipy.util as util

# from pprint import pprint

# token = util.prompt_for_user_token('122543813', show_dialog=True)
# sp = spotipy.Spotify(token)


# pprint(sp.me())
# # %% get playlist

# pl_id = 'spotify:playlist:5RIbzhG2QqdkaP24iXLnZX'
# offset = 0

# while True:
#     response = sp.playlist_items(pl_id,
#                                  offset=offset,
#                                  fields='items.track.id,total',
#                                  additional_types=['track'])
    
#     if len(response['items']) == 0:
#         break
    
#     pprint(response['items'])
#     offset = offset + len(response['items'])
#     print(offset, "/", response['total'])

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

pl_id = 'spotify:playlist:6h0WIgq1l6s9MJMbXvmJaJ'
offset = 0

if 1==1:
#while True:
    response = sp.playlist_items(pl_id, limit=2,
                                 offset=offset, 
                                 fields='items.track.uri,items.track.name,items.track.album.images,total',
                                 #additional_types=['track']
                                 )
    
    if len(response['items']) == 0:
    #    break
        pass
    
    pprint(response['items'])
    offset = offset + len(response['items'])
    print(offset, "/", response['total'])