# Tiny Stars daily reels

Code that turns a day's phone clips from [Tiny Stars Daycare](https://tinystars.ca) (Grande Prairie, Alberta) into a short, cinematic film in two versions: a vertical reel for Instagram, Facebook and TikTok, and a full-screen widescreen cut for the 55-inch TV at the daycare. **Every face is blurred**, kids and staff alike, along with children's names on plates and walls, and every cut lands on the beat of the music.

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

## The second film: "While you're at work"

A 25-second paid ad, told as the updates a working parent gets from the daycare during the day.

**The hook** opens on the best moment of the day: a teacher's hand swooping in for a high five, with her real "High five!", under "What your kid does while you're at work". The picture stops a hair before the hands meet, then rewinds to the morning, so the viewer waits for the payoff. The day then plays in order, each part arriving as an update on a phone:

- **9:52 AM, Outside time ☀️**: the band comes in on a kick, the ball is caught by the fence, and the toddler walks on across the yard.
- **11:18 AM, Music time 🎶**: a boy claps, then dances, arms flung wide, in two shots.
- **1:34 PM, Little helper 💧**: a girl puts her water bottle back on the table, and the high five from the opening finally lands, in slow motion with its real slap.
- **4:05 PM, Ready for pickup 🎒**: the classroom, quiet again.

Only the steadiest footage is used. `updates.py` measures each clip's shake from the camera motion that `detect.py` records, and smooths the handheld yard clips along that path.

Older updates stack up behind the new one, and the last one is the invitation: **Now enrolling ⭐ Book a tour**. The song is "Acoustic Upbeat" by OctoSound; every cut lands on its beat, and the film ends on the song's own last chord.

`updates.py` makes three versions from one timeline, each laid out for its own screen:

| Version | File | Format |
| --- | --- | --- |
| Reels, Stories, TikTok | `exports/updates_reel.mp4` | 1080×1920, every word inside the 720×1200 band the apps leave clear of their buttons |
| Facebook and Instagram feed | `exports/updates_feed.mp4` | 1080×1350 (4:5) |
| TV | `exports/updates_tv.mp4` | 1920×1080, full screen, every shot framed again |

Ad copy and setup notes are in [`exports/updates_ad.md`](exports/updates_ad.md).

## The picture ad: the new-family offer

A single picture for a paid Meta campaign. The stained-glass classroom fills the frame, graded so lightly that it still reads as a photo. One white card, set like a modern app, carries the words:

- **$100 off** in big, tightly set Inter Tight, then "your first 2 months **+ free registration**"
- three small real photos (indoor play gym, painting, turf play yard)
- a **Book a tour** button

There are no stickers or glows. The painting is the sharpest frame of its clip, picked by measuring each frame's detail.

`offer.py` lays it out three ways:

| Version | File | Format |
| --- | --- | --- |
| Facebook and Instagram feed | `exports/offer_feed.jpg` | 1440×1800 (4:5, Meta's recommended size) |
| Stories and Reels | `exports/offer_story.jpg` | 1440×2560, every word clear of the apps' buttons (`work/offer_story_zones.jpg` shades them) |
| TV | `exports/offer_tv.jpg` | 3840×2160 (4K), with a parent's words from Google |

Each picture is drawn at 1.5 to 2 times its final size and scaled down, so type and edges stay crisp.

`offer_samples.py` sets the same short message six ways, for choosing a look that also works on the banner outside. Each one reads in under five seconds:

- $100 off your first 2 months
- not happy in the first month? we'll refund your registration
- the phone number

Each sample uses a different modern Google font: Manrope, Plus Jakarta Sans, Outfit, Inter Tight, Fraunces with DM Sans, and Sora. They're written to `exports/offer_sample_1.jpg` through `exports/offer_sample_6.jpg`, plus `exports/offer_samples.jpg` side by side.

Samples 7 to 12 are photo grids, the kind of page Little Penguins runs, taken further:

- 5 to 9 captioned real photos (classrooms, the turf yard, the play gym, art, birthdays)
- laid out as a classic grid, a bento, a band, arches, a magazine strip or a sidebar
- the offer and the promise set clearly in each

They're written to `exports/offer_sample_7.jpg` through `exports/offer_sample_12.jpg`, plus `exports/offer_samples_grids.jpg` side by side.

Samples 13 to 18 lead with the promise ("Not happy in the first month? We'll refund your registration."), with the $100 off as a smaller line, and wear the logo's own colours, its deep purple, pink and gold, and its star:

- 13: a photo dump of tilted prints on lilac, with star and pill stickers and 'refund' in gold highlighter
- 14: the logo's purple-to-gold ramp as the whole page
- 15: the promise as a chat between a parent and Tiny Stars
- 16: a night-purple page with the promise lit in gold to pink
- 17: a wall of photos with a star sticker on it
- 18: the look of the daycare's own Oct 20 post, done properly: colour-framed photos, logo-style lettering, ribbons and the contact line

They use the newest photos too: the class painting (every child's face blurred), the block city with its smiley chairs and the rocket playroom. They're written to `exports/offer_sample_13.jpg` through `exports/offer_sample_18.jpg`, plus `exports/offer_samples_brand.jpg`. Fonts: Bricolage Grotesque and Unbounded, both from Google Fonts (OFL).

`offer_modern.py` makes samples 19 to 22, each built on a look people like right now:

- 19, liquid glass: real photos under panes of glass that bend the light at their edges, over an aurora of the logo's colours, with a sparkle trail
- 20, puffy 3D: the promise blown up into glossy balloon letters, photo stickers on a pastel check, a holographic star
- 21, cover: the stained-glass classroom as a magazine cover, with round-photo cover lines, a star badge and a barcode
- 22, scrapbook: taped polaroids with handwritten captions on dot-grid paper, 'refund' circled in pen, the $100 off on a sticky note

The glass, the balloon shading and the foil are computed from the image itself (OpenCV distance fields and remapping), not pasted in. They're written to `exports/offer_sample_19.jpg` through `exports/offer_sample_22.jpg`, plus `exports/offer_samples_modern.jpg`. Caveat (OFL) is the handwriting. The photos come from the daycare's Google page and its Drive, and go through `photos.py` first like every other photo. Ad copy and the campaign plan are in [`exports/offer_ad.md`](exports/offer_ad.md).

## The picture ad: Red Nova, the new room

`rednova_ad.py` makes thirteen samples announcing Red Nova, the daycare's newest room, with the owner's line "Red Nova is now open, a new space to shine, with our first-month happiness with Christmas offer guaranteed", a flat sparkle before it and a flat star after it. Every Red Nova sample (1 to 65) carries this line; it replaced the earlier refund wording on Nov 12. They use the photos of the room taken the day it opened, before any children were in it. Seven are dressed for Christmas:

- 1, ornaments: the room hung on the tree as gold-rimmed photo baubles, on a snowy night
- 2, Christmas card: an arched window onto the room, holly in the corners, a red and gold border
- 3, gift wrap: "a new room to unwrap", a satin ribbon and bow, a gift tag
- 4, garland: polaroids hung on a string of fairy lights
- 5, snow globe: the room inside a snow globe on a gold base
- 6, candy cane: puffy "NOW OPEN" letters on candy stripes, photo stickers, a holographic star
- 7, advent calendar: the room behind numbered doors

Six work at any time of year:

- 8, grand opening: the room with a ribbon and bow across it, ready to cut
- 9, liquid glass over an aurora of red and purple
- 10, magazine cover: the new room issue
- 11, scrapbook: taped polaroids, "Christmas" circled in pen, a sticky note
- 12, clean bento grid: "Say hello to Red Nova."
- 13, room tour: a big photo with the play kitchen, mural, hideout and tables pointed out

The bow, the holly and the baubles are drawn and lit in code like the balloon letters (no clip art). They're written to `exports/rednova_ad_1.jpg` through `exports/rednova_ad_13.jpg`, plus `exports/rednova_ads_christmas.jpg` and `exports/rednova_ads_anytime.jpg` to compare.

`rednova_modern.py` makes eight more (14 to 21), each built on three to five of the best photos with the sand-and-diggers bin as the star. It first cleans the photos up (`enhance`): the yellow of the ceiling lights pulled back, shadows lifted, colours richer, detail crisper. The eight:

- 14, hero and strip: the sand bin big, three more photos in a row, a spinning "new room" badge
- 15, bento on red: five photos under a giant condensed "RED NOVA"
- 16, shapes: photos cut into an arch, a circle, a pill and a star, each on its own colour block
- 17, photo letters: "NEW" spelled in three photos of the room, two more below
- 18, story: the room as a stack of story cards, with progress bars and a puffy heart
- 19, Christmas gift: the sand bin wrapped with a satin ribbon and bow, three more photos beside it
- 20, editorial: a big serif title, three numbered photos in a magazine grid
- 21, now showing: the room on a strip of 35 mm film, on a snowy red night

They're written to `exports/rednova_ad_14.jpg` through `exports/rednova_ad_21.jpg`, plus `exports/rednova_ads_modern.jpg`.

`rednova_aesthetic.py` makes eight soft, aesthetic ones (22 to 29), the calm Pinterest look rather than bold or retro:
- **Palette:** oat, linen, dusty rose and sage, with a muted rosewood for Red Nova.
- **Type:** lowercase words in Instrument Serif and Inter Tight.
- **Details:** thin satin "coquette" bows, and a fine film grain over everything.
- **Photos:** a soft, airy grade (`soft`): brighter, matte blacks, colour eased off, creamy highlights.

The eight:

- 22, mood board: four photos in a soft masonry grid
- 23, bows: three arched photos, each tied with a satin bow
- 24, dreamy: a pastel cloud gradient, photo widgets, a frosted glass card
- 25, photo dump: printed photos with orange date stamps, scattered on oat
- 26, arch: one big arched photo with two round ones
- 27, Christmas sage: four photos on sage and cream, a bow at the centre, pine sprigs in a fine line
- 28, checklist: photos beside a soft note card listing what's in the room
- 29, fade: the sand bin full width, fading into linen

They're written to `exports/rednova_ad_22.jpg` through `exports/rednova_ad_29.jpg`, plus `exports/rednova_ads_aesthetic.jpg`.

`rednova_like.py` makes six more (30 to 35) in two styles the owner pointed to.
- **30–32, the clean grid:** photos of the room edge to edge with thin white gutters, then a cream panel with the logo, a serif headline, the offer and a button. 31 is the Christmas version.
- **33–34, the daycare's own Oct 20 post done properly:**
  - the logo on top and photos in colour frames;
  - "Red Nova" in logo-style lettering and the offer on a bright banner;
  - the contact row with icons;
  - a 3D star buddy drawn in code, which wears a Santa hat in 34.
- **35, both together.**

The photos get a natural, bright grade (`natural`). They're written to `exports/rednova_ad_30.jpg` through `exports/rednova_ad_35.jpg`, plus `exports/rednova_ads_like.jpg`.

`rednova_christmas.py` makes six that are Christmas through and through (36 to 41). They put the promise gently, as the owner's Christmas-offer line, so it reads as confident rather than desperate.
- **Pieces drawn in code:** pine garlands with lights and baubles, a woven red tartan, wrapped presents, a fir tree of photos, gold bead tinsel, polaroids pegged to a garland, and the star buddy in a Santa hat.
- **The six:** a pine grid, tartan, a photo tree, a red panel, a card edged in lights, and a garland at night.

They're written to `exports/rednova_ad_36.jpg` through `exports/rednova_ad_41.jpg`, plus `exports/rednova_ads_christmas2.jpg`.

`rednova_trees.py` makes six more photo trees (42 to 47), softer and more aesthetic, each in its own colours. All of them:
- stack the room's six photos into a tree;
- add tinsel beads, small baubles, warm lights and presents with satin bows;
- set lowercase serif titles and the gentle offer;
- carry a fine film grain.

| Sample | Colours | Topper |
| --- | --- | --- |
| 42 | blush | a satin bow |
| 43 | sage | a gold star |
| 44 | ice, in falling snow | a silver star |
| 45 | champagne, a tree drawn in fairy lights | a gold star |
| 46 | velvet: emerald on burgundy | a gold star |
| 47 | lavender (the brand's purple) | the star buddy |

They're written to `exports/rednova_ad_42.jpg` through `exports/rednova_ad_47.jpg`, plus `exports/rednova_ads_trees.jpg`.

`rednova_trees_flat.py` makes the same six trees again (48 to 53), made by hand rather than rendered, because the glossy ones read as AI-made. It uses:
- flat paper-cut tiers with only a real paper shadow;
- flat ornaments, beads and stars, with no shine and no glow;
- bows drawn with a slightly uneven pen line;
- the photos as prints with thin white borders, on a page with a faint paper texture.

They're written to `exports/rednova_ad_48.jpg` through `exports/rednova_ad_53.jpg`, plus `exports/rednova_ads_trees_flat.jpg`.

`rednova_trees10.py` makes the flat tree with ten photos (54 to 59) in the same six colours. It adds the four low-light shots the owner sent (IMG_1289 to 1292). Every photo is brought up to a normal daylight level first (`bright`: exposure set from the photo's own median, shadows lifted, then the natural grade), and the ten stack one, two, three, four. They're written to `exports/rednova_ad_54.jpg` through `exports/rednova_ad_59.jpg`, plus `exports/rednova_ads_trees10.jpg`.

`rednova_more.py` makes six different Christmas layouts that aren't trees (60 to 65). They keep the same hand-made style and use the ten brightened photos. They're written to `exports/rednova_ad_60.jpg` through `exports/rednova_ad_65.jpg`, plus `exports/rednova_ads_more.jpg`.

| Sample | Layout |
| --- | --- |
| 60 | a wreath of round photos with flat leaves and berries |
| 61 | a Christmas postcard with a photo stamp, a postmark and a handwritten note |
| 62 | a window at night whose panes are photos of the room |
| 63 | photo-booth strips on blush paper |
| 64 | an advent calendar |
| 65 | polaroids on a red gingham cloth with a note card |

## Two versions of every film

| Version | File | Format |
| --- | --- | --- |
| Phone | `exports/nothing_reel.mp4` | 1080×1920, H.264 |
| TV | `exports/nothing_tv.mp4` | 1920×1080, H.264 High 4.2, full screen with no bars or side panels |

`film.py` makes both. The TV version is a real re-edit rather than a resize: the story, the timing and the music are the same, but every shot is framed again and every title is laid out again for a wide screen, through `FRAMING` and `LAYOUT` in `edits/content.py`.

Wide shots show more of the room, so `review_wide.py` shows each landscape clip's whole frame for checking by eye, and anything the phone crop used to hide gets blurred too. The vertical clips stay at the phone film's zoom, which keeps them inside what was already checked.

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
.venv/Scripts/python.exe -I edits/review_wide.py           # every shot's whole frame, for what the TV version will reveal
.venv/Scripts/python.exe -I edits/blur.py                  # bake the blur into 4K working copies
.venv/Scripts/python.exe -I edits/photos.py IMG_8597       # the same for a photo
.venv/Scripts/python.exe -I edits/film.py --stills 1 9 22  # check frames
.venv/Scripts/python.exe -I edits/film.py                  # the reel, with music and without, its cover and the TV version
.venv/Scripts/python.exe -I edits/film.py --tv             # just the TV version (add --stills 1 9 22 to check frames)
.venv/Scripts/python.exe -I edits/verify.py                # the final privacy scan (name a video to scan the TV version)
.venv/Scripts/python.exe -I edits/updates.py --stills 1 9 22  # the ad: check frames (add --feed or --tv for the other layouts)
.venv/Scripts/python.exe -I edits/updates.py               # the ad in all three versions
.venv/Scripts/python.exe -I edits/photos.py g02 g21 g18 IMG_8880_S  # the picture ad's photos, blurred where anyone is in them
.venv/Scripts/python.exe -I edits/offer.py                 # the picture ad: feed, story and TV
.venv/Scripts/python.exe -I edits/photos.py IMG_1294 IMG_1291 IMG_1286 IMG_1308 IMG_1310  # the new room's photos
.venv/Scripts/python.exe -I edits/rednova_ad.py            # the Red Nova samples (name numbers to draw only those)
.venv/Scripts/python.exe -I edits/rednova_modern.py        # Red Nova samples 14 to 21, with the photos cleaned up
.venv/Scripts/python.exe -I edits/rednova_aesthetic.py     # Red Nova samples 22 to 29, the soft aesthetic set
.venv/Scripts/python.exe -I edits/rednova_like.py          # Red Nova samples 30 to 35: the clean grid and the daycare's own style
.venv/Scripts/python.exe -I edits/rednova_christmas.py     # Red Nova samples 36 to 41: fully Christmas, the offer said gently
.venv/Scripts/python.exe -I edits/rednova_trees.py         # Red Nova samples 42 to 47: aesthetic photo trees in six colours
.venv/Scripts/python.exe -I edits/rednova_trees_flat.py    # Red Nova samples 48 to 53: the same trees, flat and hand-made
.venv/Scripts/python.exe -I edits/photos.py IMG_1289 IMG_1290 IMG_1292 IMG_1297  # the low-light shots
.venv/Scripts/python.exe -I edits/rednova_trees10.py       # Red Nova samples 54 to 59: ten-photo flat trees, low light fixed
.venv/Scripts/python.exe -I edits/rednova_more.py          # Red Nova samples 60 to 65: wreath, postcard, window, photo booth, advent, gingham
```

The privacy scripts look for originals in every `source/*_raw` folder, so each film's clips can stay in the folder for the day they were filmed.

The song, the shots, the timing (in beats) and the words all live in `edits/content.py`. `film.py` writes every frame to `work/frames.rgb` before encoding, so it needs about 5 GB of free disk but little memory. If it stops, run it again and it carries on from the last finished frame.

The logo in `tools/fetch_assets.py` is the small one from the website. Put a larger one at `brand/logo_hd.png` and the film uses that instead.

## Tech stack

- **Python** with NumPy, OpenCV (YuNet face detection, optical-flow slow motion, compositing) and Pillow (lettering and graphics, `pillow-heif` for iPhone photos)
- **FFmpeg** for H.264/AAC encoding and two-pass EBU R128 loudness normalisation
- **Fonts:** Instrument Serif for the big words and Inter Tight for small print (plus Manrope, Plus Jakarta Sans, Outfit, Sora, DM Sans, Fraunces, Bricolage Grotesque, Unbounded and Caveat for the offer samples), plus Crimson Pro Italic for the ad's closing line, all from Google Fonts (OFL). The ad's emoji come from Segoe UI Emoji, which ships with Windows.
- **Music:** "Cinematic Corporate" by alex-morgan on [Pixabay](https://pixabay.com/music/corporate-cinematic-corporate-556231/) for "Nothing", and "Acoustic Upbeat" by OctoSound on [Pixabay](https://pixabay.com/music/happy-childrens-tunes-acoustic-upbeat-301015/) for the ad (Pixabay Content License). The brush, boom and chime sounds are made in `film.py` and `updates.py`.

## License

The code is MIT licensed (see `LICENSE`). The Tiny Stars name and logo belong to Tiny Stars Daycare. The fonts, the face model and the music keep their own licenses.
