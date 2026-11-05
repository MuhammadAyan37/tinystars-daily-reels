# Tiny Stars daily reels

Code that turns a day's phone clips from [Tiny Stars Daycare](https://tinystars.ca) (Grande Prairie, Alberta) into a short, cinematic vertical reel for Instagram, Facebook and TikTok. **Every face is blurred**, kids and staff alike, along with children's names on plates and walls, and every cut lands on the beat of the music.

![The reel's graphics: the paper title card, a watercolour paint wash and the closing card](docs/demo.png)

*The graphics on their own. The finished reel puts them around the classroom footage, which is not in this repo.*

## The first film: "Nothing"

Every parent asks "What did you do at daycare today?" and gets "Nothing." The reel (1080×1920, 30 fps, H.264 + AAC, normalised to −14 LUFS, 25 seconds) opens on that exchange, then:

- a **watercolour paint bleed** opens a paper title card: "Here's what nothing looks like."
- the band comes in on the marshmallows and spaghetti, and the **marshmallow tower** challenge is shown step by step in close-up: push the spaghetti in, add more legs, let go.
- the tower stays up, and only then does "Nothing." get struck through with a brush stroke: *Engineering.*
- the song stops dead while paint spreads across a frozen frame, then comes back on the **washable paint** table: *Fine art.*
- the camera tilts up the whole classroom to its stained-glass window: "Nothing. Just growing up."
- a last paint bleed opens the closing card, with contact details landing on the song's final notes and stars on its last hit.

## Privacy first

The photos, the videos and everything rendered from them stay out of git (see `.gitignore`). Each step has its own script, and the blur is baked in before anything else touches the footage, so no effect can ever work from an unblurred frame:

1. `detect.py` finds faces in every frame with OpenCV's YuNet, at several sizes and four rotations, because a lot of daycare footage is shot from above and faces can be sideways or upside down. It also measures the camera's motion.
2. `track.py` links detections into a smooth track per person. Every track is checked by eye through the film's own framing with `review.py`, and the decisions go in `edits/faces.json`.
3. `blur.py` pixelates and heavily blurs each face inside a feathered ellipse, plus any hand-placed tracks and wall patches for children's names.
4. `verify.py` looks through the finished film for anything that still reads as a face, and puts every hit on a sheet for checking by eye.

## Run it

You need Python 3.12, [uv](https://docs.astral.sh/uv/) and `ffmpeg` on your PATH. None of the media is in the repo, so put the day's clips and photos in the folder named by `RAW` in `edits/content.py` first.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -I tools/fetch_assets.py          # fonts, face model, logo, song
.venv/Scripts/python.exe -I edits/detect.py                # every face in every frame, plus the camera's motion
.venv/Scripts/python.exe -I edits/track.py --sheets        # link them into tracks, with sheets for checking by eye
.venv/Scripts/python.exe -I edits/review.py stand          # one shot's tracks, through the film's framing
.venv/Scripts/python.exe -I edits/blur.py                  # bake the blur into 4K working copies
.venv/Scripts/python.exe -I edits/photos.py IMG_8597       # the same for a photo
.venv/Scripts/python.exe -I edits/film.py --stills 1 9 22  # check frames
.venv/Scripts/python.exe -I edits/film.py                  # the reel, with music and without, plus its cover
.venv/Scripts/python.exe -I edits/verify.py                # the final privacy scan
```

The song, the shots, the timing (in beats) and the words all live in `edits/content.py`. `film.py` writes every frame to `work/frames.rgb` before encoding, so it needs about 5 GB of free disk but little memory. If it stops, run it again and it carries on from the last finished frame.

The logo in `tools/fetch_assets.py` is the small one from the website. Put a larger one at `brand/logo_hd.png` and the film uses that instead.

## Tech stack

- **Python** with NumPy, OpenCV (YuNet face detection, optical-flow slow motion, compositing) and Pillow (lettering and graphics, `pillow-heif` for iPhone photos)
- **FFmpeg** for H.264/AAC encoding and two-pass EBU R128 loudness normalisation
- **Fonts:** Instrument Serif for the big words and Inter Tight for small print, both from Google Fonts (OFL)
- **Music:** "Cinematic Corporate" by alex-morgan on [Pixabay](https://pixabay.com/music/corporate-cinematic-corporate-556231/) (Pixabay Content License). The brush, boom and chime sounds are made in `film.py`.

## License

The code is MIT licensed (see `LICENSE`). The Tiny Stars name and logo belong to Tiny Stars Daycare. The fonts, the face model and the music keep their own licenses.
