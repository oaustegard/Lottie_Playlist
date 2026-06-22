# 🌈 The Lottie Playlist

> "Could you find a way to sort my Spotify playlist by the color of the album cover, like a rainbow?" — Lottie

A one-question favor that turned into a small exercise in color science: take a
Spotify playlist, look at every track's album cover, and re-order the songs so the
covers run through the spectrum like a rainbow — reds, oranges, yellows, greens,
blues, violets — with the grayscale covers gathered into their own gradient.

The working artifact is the [`🌈_Playlist.ipynb`](./🌈_Playlist.ipynb) notebook
(open it in Colab — link below). The loose `*.py` files are the exploratory
scratch work that fed into it.

## How it works

1. **Authenticate** to Spotify via `spotipy` (OAuth). Pick a source: a playlist id,
   or your **Liked Songs**.
2. **Pull the tracks**, paging through the full source, keeping each track's id,
   track number, and album-cover URL.
3. **Read each cover.** The cover is downsized to 10×10 px — we want the *gist* of
   the color, not the detail — and every pixel is converted to hue, saturation and
   perceived luminance.
4. **Classify the cover.** Pixels are bucketed into 30°-wide hue *bands* around the
   color wheel (shifted 30° so the trailing reds rejoin the leading reds). Only
   *vivid* pixels vote, so a logo on a busy cover doesn't hijack the result. A
   cover whose pixels are mostly grayscale (fewer than 10% vivid) is sent to a
   dedicated **gray band** instead of being assigned a meaningless hue.
5. **Sort** by `(band, perceived luminance, track number)`: grays first as a
   black→white run, then each hue band light-to-dark, with same-album tracks held
   in album order.
6. **Write** the result back as a new Spotify playlist and hand back a link.

### The color bits

- **Hue / saturation** come from the standard HSL conversion.
- **Perceived luminance** uses the [relative-luminance](https://en.wikipedia.org/wiki/Relative_luminance)
  weighting (`0.2126·R + 0.7152·G + 0.0722·B`, gamma-corrected) rather than naïve
  lightness, because the eye is far more sensitive to green than to blue.
- **"Vivid"** is a saturation/luminance threshold, hand-tuned with
  [this little jsfiddle](https://jsfiddle.net/austegard/g1yobd4h/) — the
  super-scientific approach of eyeballing swatches on an uncalibrated monitor.

## Running it

```bash
pip install spotipy pillow pandas requests
```

You need a Spotify developer app (client id + secret). Keep them out of the repo —
put them in a gitignored `creds.py` (or environment variables); never commit the
`.cache*` token files spotipy writes. Then open the notebook and run the cells, or
launch it straight in Colab:

- [Color Sorting notebook](https://colab.research.google.com/drive/1s1hMtukMIRjDmGApmSHvUSr_rnbC2tA7#scrollTo=Ehy6s_Z_8CXz)
- [🌈 Playlist notebook](https://colab.research.google.com/drive/1gXRzjjXaY0-zDXoggZs49jmIIxr9NLAX?usp=sharing#scrollTo=nZwzuKawZqw8)

## Status & ideas

The core pipeline — auth → fetch → color-extract → rainbow-sort → create playlist —
works end to end. Remaining ideas live in the issues: parallelizing the cover
downloads (#25) and a better whole-image "perceived color" than the dominant band
(open-ended). See also the [project board](https://github.com/users/oaustegard/projects/2).
