# %% Connect to Spotify and get the album covers for a given playlist

import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint


#sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="9fcca0731fa949d1845b9adae235e120",
                                                           client_secret="2356010b9886436b88d287aa0e5256c8"))

offset = 0

fields = ['item.track.uri', 'item.track.name', 'item.track.artists.name', 'item.track.album.name']


playlist_id = 'spotify:user:spotifycharts:playlist:6h0WIgq1l6s9MJMbXvmJaJ'
results = sp.playlist(playlist_id)
print(json.dumps(results, indent=2))


# while True:
#     response = sp.playlist_items(pl_id,
#                                  offset=offset,
#                                  fields=','.join(fields),
#                                  #additional_types=['track']
#                                  )
    
#     if len(response['item']) == 0:
#         break
    
#     pprint(response['items'])
#     offset = offset + len(response['items'])
#     print(offset, "/", response['total'])

# # for debugging just use the first item
#     break

# %%
