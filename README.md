# The Lottie Playlist
 "Could you find a way to sort my Spotify playlist by the color of the album cover, like a rainbow?" -- Lottie

### Expected Workflow
1. App displays instructions
1. User logs in
    1. App authenticates user
1. App Lists user's Playlists: Displays Name and ID
1. App asks user for Playlist Id
    a. User enters Id
1. App loads playlist's first 100 tracks with track name, id, # (on album), artist name, album name, album cover urls into dataframe
    1. For each track: 
        1. App downloads 64x64 album cover
        1. App gets dominant color(s?) of album cover, adds to dataframe
    1. App loads next 100 tracks into dataframe, repeat
1. App sorts dataframe by album dominant color(s)
1. App displays list of tracks/album/artist with cover as 
1. App asks user for new playlist name
    1. User enters name
1. App creates playlist
1. App uploads tracks, 100 at a time in the order of the new playlist
1. App displays link to new playlist
    1. User opens playlist in Spotify


### Things to figure out/do
See [Project Kanban Board](https://github.com/users/oaustegard/projects/2)

## Results(!)

See [Color Sorting](https://colab.research.google.com/drive/1s1hMtukMIRjDmGApmSHvUSr_rnbC2tA7#scrollTo=Ehy6s_Z_8CXz) and [🌈 Playlist](https://colab.research.google.com/drive/1gXRzjjXaY0-zDXoggZs49jmIIxr9NLAX?usp=sharing#scrollTo=nZwzuKawZqw8) Colab Notebooks
