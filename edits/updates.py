"""While you're at work: a 25-second ad for Tiny Stars Daycare, told as the updates a parent gets during the day.

It opens on the best moment of the day: a teacher's hand swooping in for a high five, with her real "High five!", under
"What your kid does while you're at work". The picture stops a hair before the hands meet and rewinds to the morning, and
the day plays in order, each part arriving like a message on a phone: outside time, music time, a little helper's high
five (the payoff, in slow motion with its real slap, then a fist bump), and the rooms quiet at pickup. The last update is
the invitation: now enrolling, book a tour. The song is "Acoustic Upbeat" by OctoSound (Pixabay); every cut lands on its
beat, the band comes in as the day starts, and the film ends on the song's own last chord.

Only the steadiest footage is used, and the handheld yard clips are smoothed along the camera path detect.py measured.

One timeline, three versions, each laid out for its own screen:
  phone  1080x1920  Reels, Stories and TikTok. Every word sits inside the 720x1200 band those apps leave clear.
  feed   1080x1350  the 4:5 Facebook and Instagram feed.
  tv     1920x1080  the daycare's TV, full screen, with every shot framed again for a wide picture.

Only the blurred working copies from blur.py and photos.py are ever read here, so no effect can touch an unblurred face.

Usage: python -I edits/updates.py [--feed | --tv] [--stills t t ...]
  -> exports/updates_reel.mp4 and updates_cover.jpg, exports/updates_feed.mp4, exports/updates_tv.mp4
     (with no format flag, the phone version is made first and then the other two)
"""
import gc
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from lib import (CREAM, FPS, GOLD, ROOT, SANS, blit, clamp01, decode, ease_in_out, ease_out_back,  # noqa: E402
                 ease_out_cubic, encode, hash01, lettering, logo_image, loudness_normalise, phone_copy, render_frames,
                 rise, rounded_mask, star_image, to_sprite)

FMT = "tv" if "--tv" in sys.argv else "feed" if "--feed" in sys.argv else "phone"
W, H = {"phone": (1080, 1920), "feed": (1080, 1350), "tv": (1920, 1080)}[FMT]
lib.W, lib.H = W, H  # render_frames and encode work at this size

PREVIEW = "--preview" in sys.argv  # half-size blurred clips from work/clean_preview, for a quick look before the full bake
CLEAN = ROOT / "work" / ("clean_preview" if PREVIEW else "clean")
PHOTOS = ROOT / "work" / "clean"
FACES = ROOT / "work" / "faces"
EXPORTS = ROOT / "exports"
FONTS = ROOT / "brand" / "fonts"
EMOJI = Path("C:/Windows/Fonts/seguiemj.ttf")
OUT = {"phone": "updates_reel", "feed": "updates_feed", "tv": "updates_tv"}[FMT] + ("_preview" if PREVIEW else "")

PLUM = (36, 16, 48)
INK_DARK = (28, 20, 34)
GREY = (112, 104, 120)

# ---------- the song ----------
# "Acoustic Upbeat" by OctoSound: 95 BPM, guitar, whistling and handclaps. Its beat grid was measured from the file.
SONG = "acoustic_upbeat_octosound_301015.mp3"
BEAT = 0.6315838
FIRST_BEAT = 0.626057
# (first film beat, first song beat, beats). The film opens on the bar where the bass starts to build, so the band
# comes in on film beat 4. At film beat 28 it jumps from the end of a chorus phrase to the same place in the song's
# last chorus, which runs into the final chord (song beat 174, film beat 34) and its ring.
PARTS = [(0, 12, 28), (28, 168, 12)]
LIFT = 4
HIT = 34
TOTAL_BEATS = 39


def bt(k):
    return k * BEAT


# ---------- what the film shows ----------
# start: seconds into the clip; speed: 1 = real time; zoom (start, end); center or pan: (x, y) as fractions of the
# frame; sat: colour; punch: a small push on the cut; whip: arrives on a whip pan (1 or -1); per-format overrides.
SHOTS = [
    # the hook: a teacher's hand swoops in for a high five and the picture stops a hair before it lands, then the
    # film rewinds to the morning and tells the day in order, so the high five pays off at 1:34 PM
    dict(key="hook", clip="IMG_8714", start=22.95, beats=4, speed=0.55, freeze=bt(3.25), rewind=bt(0.6), steady=6,
         zoom=(1.2, 1.28), center=(0.58, 0.47), sat=1.08, tv=dict(zoom=(1.0, 1.06), center=(0.66, 0.47))),
    # 9:52 AM, outside: the kick, the ball caught by the fence, and on across the yard (the yard clips are handheld,
    # so these three are steadied hardest)
    dict(key="kick", clip="IMG_8697", start=5.95, beats=2, speed=0.6, zoom=(1.62, 1.55), center=(0.48, 0.64), punch=0.06,
         steady=10, tv=dict(zoom=(1.12, 1.06), center=(0.5, 0.6))),
    dict(key="scoop", clip="IMG_8698", start=0.75, beats=2, speed=0.85, zoom=(1.26, 1.2), center=(0.6, 0.5), steady=10,
         tv=dict(zoom=(1.08, 1.05), center=(0.55, 0.36))),
    dict(key="yard", clip="IMG_8697", start=9.7, beats=2, speed=0.8, zoom=(1.22, 1.16), center=(0.5, 0.5), steady=10,
         tv=dict(zoom=(1.1, 1.05), center=(0.5, 0.44))),
    # 11:18 AM, music time: two clips filmed on a steady hand
    dict(key="clap", clip="IMG_8701", start=1.0, beats=2, speed=0.85, zoom=(1.3, 1.26), center=(0.48, 0.47), punch=0.04,
         tv=dict(zoom=(1.08, 1.04), center=(0.47, 0.45))),
    dict(key="dance", clip="IMG_8700", start=9.2, beats=4, speed=0.85, zoom=(1.12, 1.08), center=(0.5, 0.5), sat=1.1,
         tv=dict(zoom=(1.0, 1.0), center=(0.5, 0.44))),
    dict(key="dance2", clip="IMG_8700", start=12.9, beats=4, speed=0.85, zoom=(1.28, 1.22), center=(0.5, 0.46), sat=1.1,
         punch=0.05, tv=dict(zoom=(1.08, 1.04), center=(0.5, 0.42))),
    # 1:34 PM, tidy-up time: the bottle goes back on the table, and the high five lands
    dict(key="bottle", clip="IMG_8714", start=16.9, beats=4, speed=0.8, zoom=(1.16, 1.2), center=(0.5, 0.5), sat=1.08,
         steady=6, tv=dict(zoom=(1.0, 1.04), center=(0.55, 0.45))),
    dict(key="five", clip="IMG_8714", start=23.35, beats=4, speed=0.6, zoom=(1.18, 1.26), center=(0.56, 0.48), sat=1.08,
         steady=6, tv=dict(zoom=(1.0, 1.06), center=(0.66, 0.47))),
    # 4:05 PM, the rooms are quiet again
    dict(key="room", photo="IMG_8711", beats=4, zoom=(1.1, 1.2), pan=((0.5, 0.62), (0.52, 0.58)),
         tv=dict(zoom=(1.0, 1.08), pan=((0.5, 0.52), (0.52, 0.5)))),
    dict(key="end", kind="end", beats=TOTAL_BEATS - 32),
]

# when each update arrives (film beat), and what it says. The times are a dramatisation of one day.
NOTES = [
    dict(at=4.15, time="9:52 AM", title="Outside time", emoji="\u2600", body="Chasing the ball all morning."),
    dict(at=10.1, time="11:18 AM", title="Music time", emoji="\U0001F3B6", body="Someone brought their best dance moves."),
    dict(at=20.1, time="1:34 PM", title="Little helper", emoji="\U0001F4A7", body="Helped put the water bottles away. High five!"),
    dict(at=28.1, time="4:05 PM", title="Ready for pickup", emoji="\U0001F392", body="Big day, lots of smiles. See you soon!"),
]
CTA = dict(at=32.6, time="now", title="Now enrolling", emoji="\u2B50", body="Book a tour: (780) 230-1599")
HOOK = ["What your kid does", "while you\u2019re at work"]
TAGLINE = ["Little stars today,", "bright futures tomorrow."]
ROWS = ["10629 West Side Drive, Grande Prairie", "tinystars.ca  \u00b7  @tinystarsgp"]

LAYOUT = {
    "phone": dict(note=dict(cx=540, top=250, w=1004, s=1.16), stack=28, hook=dict(size=82, ys=(1170, 1266)),
                  end=dict(logo=(330, 520), tag=(80, 812, 902), cta=1092, rows=(34, 1296, 1346))),
    "feed": dict(note=dict(cx=540, top=48, w=1004, s=1.16), stack=28, hook=dict(size=82, ys=(1010, 1106)),
                 end=dict(logo=(270, 300), tag=(72, 556, 638), cta=820, rows=(32, 1010, 1056))),
    "tv": dict(note=dict(cx=1920 - 64 - 500, top=56, w=1000, s=0.98), stack=24, hook=dict(size=96, ys=(830, 940)),
               end=dict(logo=(280, 205), tag=(76, 440, 526), cta=690, rows=(34, 880, 928))),
}[FMT]

for _sh in SHOTS:
    _sh.update(_sh.get(FMT, {}))


# ---------- footage ----------
class Source:
    """A baked clip, read one frame at a time, keeping just a few frames in memory."""

    def __init__(self, name, want_w=None):
        data = json.loads((FACES / f"{name}.json").read_text())
        self.name, self.n = name, data["n"]
        w, h = data["w"], data["h"]
        k = min(1.0, want_w / w) if want_w else 1.0
        self.w, self.h = int(w * k) // 2 * 2, int(h * k) // 2 * 2
        self.k = self.w / w
        self.cap, self.pos, self.cache = None, 0, {}
        m = np.array(data["motion"])
        self.path = np.c_[np.cumsum(m[:, 0, 2]), np.cumsum(m[:, 1, 2]), np.cumsum(np.arctan2(m[:, 1, 0], m[:, 0, 0]))]

    def correction(self, sigma):
        """How far each frame sits from a smooth version of the camera's path, in this source's pixels."""
        r = int(sigma * 3)
        g = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
        g /= g.sum()
        pad = np.pad(self.path, ((r, r), (0, 0)), mode="edge")
        c = np.stack([np.convolve(pad[:, i], g, "valid") for i in range(3)], 1) - self.path
        c[:, :2] *= self.k
        return c

    def frame(self, i):
        i = int(max(0, min(self.n - 1, i)))
        if i in self.cache:
            return self.cache[i]
        if self.cap is None or i < self.pos:
            if self.cap is not None:
                self.cap.release()
            self.cap, self.pos = cv2.VideoCapture(str(CLEAN / f"{self.name}.mp4")), 0
        while self.pos < i:
            self.cap.grab()
            self.pos += 1
        ok, fr = self.cap.read()
        self.pos += 1
        if not ok:
            raise SystemExit(f"could not read frame {i} of {self.name}")
        if fr.shape[1] != self.w:
            fr = cv2.resize(fr, (self.w, self.h), interpolation=cv2.INTER_AREA)
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        self.cache[i] = fr
        for k in sorted(self.cache)[:-4]:
            del self.cache[k]
        return fr

    def close(self):
        if self.cap is not None:
            self.cap.release()
        self.cap, self.cache = None, {}


def blend_flow(a, b, q):
    """A frame between a and b by optical flow, for slow motion."""
    if q < 0.03:
        return a
    if q > 0.97:
        return b
    ga = cv2.cvtColor(cv2.resize(a, (W // 2, H // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, (W // 2, H // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    f_ab = cv2.resize(dis.calc(ga, gb, None), (W, H), interpolation=cv2.INTER_LINEAR) * 2
    f_ba = cv2.resize(dis.calc(gb, ga, None), (W, H), interpolation=cv2.INTER_LINEAR) * 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wa = cv2.remap(a, xx + f_ba[..., 0] * q, yy + f_ba[..., 1] * q, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.remap(b, xx + f_ab[..., 0] * (1 - q), yy + f_ab[..., 1] * (1 - q), cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(wa, 1 - q, wb, q, 0)


# ---------- the look: clean and bright, warm in the highlights ----------
def make_curve():
    x = np.arange(256, dtype=np.float32) / 255
    s = x + 0.07 * (x - 0.5) * (1 - np.abs(2 * x - 1)) * 2
    s = np.where(s > 0.82, 0.82 + (s - 0.82) * 0.86, s)
    return (np.clip(s / s[-1], 0, 1) * 255).astype(np.uint8)


CURVE = make_curve()
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (np.clip(np.sqrt(((_xx - W / 2) / (W * 0.8)) ** 2 + ((_yy - H / 2) / (H * 0.8)) ** 2) - 0.5, 0, 1) ** 1.8)[..., None]
del _yy, _xx
WARM = np.array([1.0, 0.7, 0.42], np.float32)


def grade(img, sat=1.04):
    x = cv2.LUT(img, CURVE).astype(np.float32) / 255
    lum = (x @ LUMA)[..., None]
    x = lum + (x - lum) * sat
    x = x + lum ** 2 * np.array([0.018, 0.006, -0.022], np.float32) + (1 - lum) ** 2 * np.array([-0.006, 0.0, 0.014], np.float32)
    hi = cv2.resize(np.clip(lum[..., 0] - 0.78, 0, 1), (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    hi = cv2.resize(cv2.GaussianBlur(hi, (0, 0), 6), (W, H), interpolation=cv2.INTER_LINEAR)
    x = x + hi[..., None] * WARM * 0.35
    return np.clip(x, 0, 1.2) * (1 - VIG * 0.3)


def sharpen(img, amount=0.35):
    soft = cv2.GaussianBlur(img, (0, 0), 1.2)
    return cv2.addWeighted(img, 1 + amount, soft, -amount, 0)


def flash(img, k):
    return img + (np.array([1.0, 0.97, 0.9], np.float32) - img) * k


def dir_blur(img, length):
    if length < 3:
        return img
    return cv2.blur(img, (int(length) | 1, 1), borderType=cv2.BORDER_REFLECT)


def slide(img, dx):
    if abs(dx) < 0.5:
        return img
    M = np.array([[1, 0, dx], [0, 1, 0]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


def light_leak(img, q, strength=1.0):
    """Warm sunlight sweeping across the frame (q 0..1)."""
    if not 0 < q < 1:
        return img
    x = np.linspace(0, 1, W // 8, dtype=np.float32)[None, :]
    y = np.linspace(0, 1, H // 8, dtype=np.float32)[:, None]
    c = -0.3 + 1.6 * q + 0.25 * (y - 0.5)
    band = np.exp(-((x - c) / 0.32) ** 2) * math.sin(math.pi * q) * strength
    band = cv2.resize(band, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    col = np.array([1.0, 0.72, 0.36], np.float32)
    return 1 - (1 - img) * (1 - np.clip(band * col, 0, 1))


# ---------- type ----------
def sans(size, weight):
    f = ImageFont.truetype(str(FONTS / SANS), size)
    f.set_variation_by_axes([weight])
    return f


def serif_italic(size):
    f = ImageFont.truetype(str(FONTS / "CrimsonPro-Italic.ttf"), size)
    try:
        f.set_variation_by_axes([400])  # the variable font from Google Fonts; the static one has no axes
    except OSError:
        pass
    return f


def plain(text, f, fill, track=0):
    """Flat text with no shadow, as an RGBA image cropped to its ink (for the cards)."""
    return lettering(text, f, track, fill=fill, shadow=0)


def emoji_image(ch, size):
    f = ImageFont.truetype(str(EMOJI), 109)  # the colour glyphs are drawn at their native size, then scaled
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, round(im.height * size / im.width)), Image.LANCZOS)


def wrap(text, f, width):
    words, lines, cur = text.split(" "), [], ""  # a no-break space keeps words together
    for w in words:
        nxt = (cur + " " + w).strip()
        if f.getlength(nxt) <= width or not cur:
            cur = nxt
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


class Card:
    """A notification from the Tiny Stars app: frosted glass, the app's icon, the time, a title and a line or two."""

    def __init__(self, note, width, s):
        self.w = int(width)
        pad, icon = round(30 * s), round(88 * s)
        f_app, f_title, f_body = sans(round(26 * s), 600), sans(round(41 * s), 680), sans(round(37 * s), 430)
        x_text = pad + icon + round(24 * s)
        text_w = self.w - x_text - pad
        app = plain("TINY STARS", f_app, GREY, track=round(2.2 * s))
        when = plain(note["time"], f_app, GREY)
        title = plain(note["title"], f_title, INK_DARK)
        body_lines = [plain(t, f_body, (50, 42, 56)) for t in wrap(note["body"], f_body, text_w)]
        emo = emoji_image(note["emoji"], round(40 * s))
        gap = round(12 * s)
        y_app, y_title = pad + 2, pad + app.height + gap
        y_body = y_title + title.height + round(10 * s)
        lead = round(46 * s)
        self.h = max(y_body + (len(body_lines) - 1) * lead + body_lines[0].height + pad + 4, pad * 2 + icon)
        self.r = round(40 * s)
        canvas = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        # the app icon: the logo on a white rounded tile with a hairline edge
        tile = Image.new("RGBA", (icon * 4, icon * 4), (0, 0, 0, 0))
        ImageDraw.Draw(tile).rounded_rectangle((0, 0, icon * 4 - 1, icon * 4 - 1), round(icon * 0.24) * 4,
                                               fill=(255, 255, 255, 255), outline=(220, 214, 226, 255), width=6)
        tile = tile.resize((icon, icon), Image.LANCZOS)
        logo = logo_image(round(icon * 0.86))
        tile.alpha_composite(logo, ((icon - logo.width) // 2, (icon - logo.height) // 2))
        canvas.alpha_composite(tile, (pad, (self.h - icon) // 2))
        canvas.alpha_composite(app, (x_text, y_app))
        canvas.alpha_composite(when, (self.w - pad - when.width, y_app))
        canvas.alpha_composite(title, (x_text, y_title))
        canvas.alpha_composite(emo, (x_text + title.width + round(12 * s), y_title + (title.height - emo.height) // 2 + 1))
        for i, line in enumerate(body_lines):
            canvas.alpha_composite(line, (x_text, y_body + i * lead))
        self.content = to_sprite(canvas)
        self.mask = rounded_mask(self.w, self.h, self.r)
        m = 48
        sh = np.zeros((self.h + 2 * m, self.w + 2 * m), np.float32)
        sh[m:m + self.h, m:m + self.w] = self.mask
        self.shadow = cv2.GaussianBlur(sh, (0, 0), 18 * s)
        self.m = m
        self.s = s

    def draw(self, img, cx, top, alpha=1.0, content=1.0, narrow=1.0, glass=1.0, white=0.74):
        """Draw in place: the card's shadow, then its frosted glass over whatever is under it, then its content."""
        if alpha <= 0.004:
            return
        w = int(self.w * narrow) // 2 * 2
        mask = self.mask if narrow == 1.0 else cv2.resize(self.mask, (w, self.h), interpolation=cv2.INTER_AREA)
        x0, y0 = int(round(cx - w / 2)), int(round(top))
        x1, y1 = x0 + w, y0 + self.h
        if x0 < 0 or x1 > W or y1 <= 0 or y0 >= H:
            return
        # shadow
        m = self.m
        shadow = self.shadow if narrow == 1.0 else cv2.resize(self.shadow, (w + 2 * m, self.h + 2 * m))
        sy0 = y0 - m + round(12 * self.s)
        a0, b0 = max(0, sy0), min(H, sy0 + shadow.shape[0])
        c0, d0 = max(0, x0 - m), min(W, x0 - m + shadow.shape[1])
        sub = shadow[a0 - sy0:b0 - sy0, c0 - (x0 - m):d0 - (x0 - m)]
        img[a0:b0, c0:d0] *= (1 - 0.26 * alpha * sub)[..., None]
        # glass
        ya, yb = max(0, y0), min(H, y1)
        mk = mask[ya - y0:yb - y0][..., None] * alpha * glass
        pad = 40
        Y0, Y1, X0, X1 = max(0, ya - pad), min(H, yb + pad), max(0, x0 - pad), min(W, x1 + pad)
        small = cv2.resize(img[Y0:Y1, X0:X1], None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        soft = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_LINEAR)
        soft = soft[ya - Y0:yb - Y0, x0 - X0:x1 - X0]
        frost = soft * (1 - white) + np.array([0.965, 0.955, 0.975], np.float32) * white
        region = img[ya:yb, x0:x1]
        region[:] = region * (1 - mk) + frost * mk
        # content
        if content > 0.004 and narrow == 1.0:
            blit(img[ya:yb], self.content[ya - y0:yb - y0], w / 2 + x0, (yb - ya) / 2, 1.0, 0, alpha * content)


# ---------- the timeline ----------
def build_timeline():
    segs, b = [], 0
    for i, sh in enumerate(SHOTS):
        segs.append(dict(i=i, shot=sh, key=sh["key"], kind=sh.get("kind", "photo" if "photo" in sh else "clip"),
                         b0=b, b1=b + sh["beats"]))
        b += sh["beats"]
    for s in segs:
        s["t0"], s["t1"] = bt(s["b0"]), bt(s["b1"])
    return segs


class Renderer:
    def __init__(self):
        self.segs = build_timeline()
        self.total = self.segs[-1]["t1"]
        self.by_key = {s["key"]: s for s in self.segs}
        self.clips, self.cache = {}, {}
        ln = LAYOUT["note"]
        self.cards = [Card(n, ln["w"], ln["s"]) for n in NOTES]
        self.cta = Card(CTA, ln["w"] if FMT != "tv" else 960, 1.08)
        f_hook = sans(LAYOUT["hook"]["size"], 760)
        self.hook = [to_sprite(lettering(t, f_hook, 0, fill=(255, 255, 255), shadow=0.9)) for t in HOOK]
        le = LAYOUT["end"]
        self.logo = to_sprite(logo_image(le["logo"][0]))
        f_tag = serif_italic(le["tag"][0])
        self.tag = [to_sprite(lettering(t, f_tag, 0, fill=CREAM, shadow=0)) for t in TAGLINE]
        f_row = sans(le["rows"][0], 500)
        self.rows = [to_sprite(lettering(t, f_row, round(le["rows"][0] * 0.03), fill=(236, 226, 240), shadow=0)) for t in ROWS]
        self.stars = [to_sprite(star_image(s, GOLD)) for s in (18, 26, 34)]

    def release(self):
        for c in self.clips.values():
            c.close()
        self.clips.clear()

    # ----- a shot's camera -----
    def source(self, sh):
        name = sh["clip"]
        if name not in self.clips:
            data = json.loads((FACES / f"{name}.json").read_text())
            zmax = max(sh.get("zoom", (1.0, 1.0)))
            cover = max(W / data["w"], H / data["h"]) * zmax  # how big the clip is drawn
            self.clips[name] = Source(name, min(data["w"], data["w"] * cover * 1.25))
        return self.clips[name]

    @staticmethod
    def src_frame(sh, tau):
        f0, sp = sh.get("start", 0) * FPS, sh.get("speed", 1.0)
        if "freeze" in sh:
            # the hook: play, stop on the frame before the hands meet, then rewind fast to where it began
            r0 = sh["beats"] * BEAT - sh["rewind"]
            ff = f0 + sh["freeze"] * FPS * sp
            if tau >= r0:
                return ff - (ff - f0) * ease_in_out((tau - r0) / sh["rewind"])
            tau = min(tau, sh["freeze"])
        return f0 + tau * FPS * sp

    def matrix(self, sh, src, tau, dur, f=0.0):
        z0, z1 = sh.get("zoom", (1.04, 1.0))
        e = ease_in_out(tau / dur)
        z = z0 + (z1 - z0) * e
        if sh.get("punch"):
            z *= 1 + sh["punch"] * math.exp(-tau / 0.16)
        if sh.get("pan"):
            (x0, y0), (x1, y1) = sh["pan"]
            cx, cy = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
        else:
            cx, cy = sh.get("center", (0.5, 0.5))
        s = max(W / src.w, H / src.h) * z
        half_w, half_h = W / 2 / s, H / 2 / s
        px, py = min(max(cx * src.w, half_w), src.w - half_w), min(max(cy * src.h, half_h), src.h - half_h)
        ox, oy, ang = 0.0, 0.0, 0.0
        if sh.get("steady"):
            key = ("cor", src.name, sh["steady"])
            if key not in self.cache:
                self.cache[key] = src.correction(sh["steady"])
            cor = self.cache[key]
            ox, oy, ang = cor[int(min(len(cor) - 1, max(0, f)))]
        # never reveal the edge of the frame
        ox = max(px + half_w - src.w, min(px - half_w, ox))
        oy = max(py + half_h - src.h, min(py - half_h, oy))
        ca, sa = math.cos(ang) * s, math.sin(ang) * s
        return np.array([[ca, -sa, W / 2 - ca * px + sa * py + ox * s],
                         [sa, ca, H / 2 - sa * px - ca * py + oy * s]], np.float32)

    def sample(self, sh, tau, dur):
        src = self.source(sh)
        f = min(self.src_frame(sh, tau), src.n - 1.001)
        M = self.matrix(sh, src, tau, dur, f)
        i0 = int(math.floor(f))
        interp = cv2.INTER_CUBIC if M[0, 0] > 0.6 else cv2.INTER_AREA
        a = cv2.warpAffine(src.frame(i0), M, (W, H), flags=interp, borderMode=cv2.BORDER_REPLICATE)
        q = f - i0
        if q < 0.03:
            return a
        b = cv2.warpAffine(src.frame(i0 + 1), M, (W, H), flags=interp, borderMode=cv2.BORDER_REPLICATE)
        return blend_flow(a, b, q)

    def photo(self, name):
        if name not in self.cache:
            im = cv2.imread(str(PHOTOS / f"{name}.jpg"))
            k = max(W, H) * 1.6 / max(im.shape[:2])
            im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            self.cache[name] = sharpen(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), 0.4)
        return self.cache[name]

    def photo_picture(self, sg, t):
        sh = sg["shot"]
        pic = self.photo(sh["photo"])
        ph, pw = pic.shape[:2]
        e = ease_in_out((t - sg["t0"]) / (sg["t1"] - sg["t0"]))
        z0, z1 = sh["zoom"]
        s = max(W / pw, H / ph) * (z0 + (z1 - z0) * e)
        (x0, y0), (x1, y1) = sh["pan"]
        cx, cy = (x0 + (x1 - x0) * e) * pw, (y0 + (y1 - y0) * e) * ph
        half_w, half_h = W / 2 / s, H / 2 / s
        cx, cy = min(max(cx, half_w), pw - half_w), min(max(cy, half_h), ph - half_h)
        M = np.array([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]], np.float32)
        return grade(cv2.warpAffine(pic, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE), 1.06)

    def clip_picture(self, sg, t):
        sh = sg["shot"]
        tau = max(0.0, t - sg["t0"])
        return grade(self.sample(sh, tau, sg["t1"] - sg["t0"]), sh.get("sat", 1.02))

    def end_ground(self):
        """The closing card's ground: the last room, softly out of focus under a deep plum."""
        if "ground" not in self.cache:
            room = self.segs[-2]
            pic = self.photo_picture(room, room["t1"] - 1e-3)
            small = cv2.resize(pic, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
            soft = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (W, H), interpolation=cv2.INTER_CUBIC)
            plum = np.array(PLUM, np.float32) / 255
            yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
            ground = soft * 0.3 + plum * 0.7
            ground = ground * (0.92 + 0.12 * (1 - yy))  # a little lighter at the top, where the logo sits
            self.cache["ground"] = (np.clip(ground, 0, 1), soft)
        return self.cache["ground"]

    def end_picture(self, sg, t):
        since = t - sg["t0"]
        ground, _ = self.end_ground()
        img = ground.copy()
        le = LAYOUT["end"]
        cx = W / 2
        _, y_logo = le["logo"]
        after = t - bt(HIT)
        pl = (since - 0.05) / 0.5
        pop = 1 + 0.045 * math.exp(-after / 0.18) if after > 0 else 1.0
        if pl > 0:
            blit(img, self.logo, cx, y_logo, (0.9 + 0.1 * ease_out_back(pl)) * pop, 0, clamp01(pl * 2))
        # a few small stars catch the light on the last chord
        if after > 0:
            for i in range(7):
                q = (after - 0.06 * i) / 1.4
                if 0 < q < 1:
                    a0 = (i / 7 + 0.08 * hash01(i, 1)) * 2 * math.pi
                    d = self.logo.shape[1] * (0.58 + 0.16 * hash01(i, 2))
                    spr = self.stars[i % 3]
                    blit(img, spr, cx + math.cos(a0) * d, y_logo + math.sin(a0) * d * 0.9, 0.6 + 0.5 * math.sin(math.pi * q),
                         0, math.sin(math.pi * q) * 0.9)
        _, y1, y2 = le["tag"]
        rise(img, self.tag[0], cx, y1, (since - 0.35) / 0.55)
        rise(img, self.tag[1], cx, y2, (since - 0.48) / 0.55)
        _, r1, r2 = le["rows"]
        for i, (spr, y) in enumerate(zip(self.rows, (r1, r2))):
            q = (t - bt(HIT) - 0.15 - 0.12 * i) / 0.45
            if q > 0:
                blit(img, spr, cx, y + 14 * (1 - ease_out_cubic(q)), 1.0, 0, clamp01(q * 2))
        return img

    def picture(self, sg, t):
        if sg["kind"] == "clip":
            return self.clip_picture(sg, t)
        if sg["kind"] == "photo":
            return self.photo_picture(sg, t)
        return self.end_picture(sg, t)

    # ----- the updates -----
    def notes(self, img, t):
        ln = LAYOUT["note"]
        end0 = bt(32)
        if t >= end0 + 0.45:
            return
        gone = ease_in_out((t - end0) / 0.45) if t > end0 else 0.0
        arrived = [k for k, n in enumerate(NOTES) if t >= bt(n["at"])]
        for k in arrived:
            # how far back in the stack this card has gone: one step for every update that arrived after it
            depth = sum(ease_out_cubic((t - bt(NOTES[j]["at"])) / 0.4) for j in arrived if j > k)
            if depth > 2.95:
                continue
            q = (t - bt(NOTES[k]["at"])) / 0.5
            drop = (1 - ease_out_back(q, 1.3)) * 80 * ln["s"]
            alpha = clamp01(q * 3) * clamp01(2.95 - depth) * (1 - gone)
            top = ln["top"] - drop + depth * LAYOUT["stack"] - gone * 60
            # its words fade first, at full width; then it narrows into the stack
            narrow = 1.0 if depth < 0.5 else 1 - 0.05 * min(depth, 2.4)
            self.cards[k].draw(img, ln["cx"], top, alpha * (1 - 0.15 * min(depth, 2)), content=clamp01(1 - depth * 2),
                               narrow=narrow)

    def hook_text(self, img, t):
        ys = LAYOUT["hook"]["ys"]
        out = clamp01((bt(3.4) - t) / 0.12)
        if out <= 0:
            return
        # a soft shade behind the words, so they read on bright grass
        if "hook_shade" not in self.cache:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            cy = (ys[0] + ys[1]) / 2
            d = ((xx - W / 2) / (W * 0.66)) ** 2 + ((yy - cy) / (LAYOUT["hook"]["size"] * 2.4)) ** 2
            self.cache["hook_shade"] = (np.exp(-d * 1.6) * 0.5)[..., None].astype(np.float32)
        img *= 1 - self.cache["hook_shade"] * out * clamp01(t / 0.25)
        for i, spr in enumerate(self.hook):
            q = (t - 0.04 - 0.14 * i) / 0.55
            if q > 0:
                if out < 1:
                    blit(img, spr, W / 2, ys[i], 1.0, 0, out)
                else:
                    rise(img, spr, W / 2, ys[i], q)

    def cta_card(self, img, t):
        q = (t - bt(CTA["at"])) / 0.5
        if q <= 0:
            return
        drop = (1 - ease_out_back(q, 1.3)) * 70
        card = self.cta
        card.draw(img, W / 2, LAYOUT["end"]["cta"] - card.h / 2 - drop, clamp01(q * 3), white=0.88)

    # ----- one frame -----
    def composed(self, sg, t):
        return self.picture(sg, t)

    def frame(self, t):
        t = min(t, self.total - 1e-4)
        i = next(k for k, s in enumerate(self.segs) if s["t0"] <= t < s["t1"])
        sg = self.segs[i]
        nxt = self.segs[i + 1] if i + 1 < len(self.segs) else None
        keep = {sg["shot"].get("clip"), nxt["shot"].get("clip") if nxt else None}
        for name in [n for n in self.clips if n not in keep]:
            self.clips.pop(name).close()
        img = self.composed(sg, t)
        since, until = t - sg["t0"], sg["t1"] - t
        # whip pans across a cut
        span = 3.5 / FPS
        if nxt and nxt["shot"].get("whip") and until < span:
            q = 1 - until / span
            img = dir_blur(slide(img, -nxt["shot"]["whip"] * 0.3 * W * q * q), 1 + q * 200)
        if sg["shot"].get("whip") and since < span:
            q = 1 - since / span
            img = dir_blur(slide(img, sg["shot"]["whip"] * 0.3 * W * q * q), 1 + q * 200)
        # the band comes in: a little flash of sun
        d = t - bt(LIFT)
        if 0 <= d < 0.28:
            img = flash(img, 0.38 * math.exp(-d / 0.07))
        if 0 <= d < 0.8:
            img = light_leak(img, d / 0.8, 0.55)
        # the hook stops, then rewinds: the picture smears as it runs back to the morning
        hk = self.by_key["hook"]
        sh = hk["shot"]
        r0 = hk["t0"] + sh["beats"] * BEAT - sh["rewind"]
        if hk["t0"] + sh["freeze"] <= t < r0:
            img = flash(img, 0.06)
        if r0 <= t < hk["t1"]:
            q = (t - r0) / sh["rewind"]
            img = cv2.blur(img, (1, int(3 + 60 * math.sin(math.pi * q)) | 1))
            lum = (img @ LUMA)[..., None]
            img = lum + (img - lum) * (1 - 0.5 * math.sin(math.pi * q))
        # sunlight carries the film indoors
        q = (t - (bt(10) - 0.35)) / 0.8
        if 0 < q < 1:
            img = light_leak(img, q, 0.9)
        # a soft dissolve into the rooms, and the rooms melt into the closing card
        room, end = self.by_key["room"], self.by_key["end"]
        if room["t0"] - 0.18 < t < room["t0"]:
            k = (t - (room["t0"] - 0.18)) / 0.18
            img = img * (1 - k) + self.composed(room, room["t0"]) * k
        if end["t0"] - 0.4 < t < end["t0"]:
            k = ease_in_out((t - (end["t0"] - 0.4)) / 0.4)
            ground, soft = self.end_ground()
            img = img * (1 - k) + (soft * 0.5 + ground * 0.5) * k
        if sg["key"] == "end" and since < 0.3:
            _, soft = self.end_ground()
            k = since / 0.3
            img = (soft * 0.5 + self.end_ground()[0] * 0.5) * (1 - k) + img * k
        self.hook_text(img, t)
        self.notes(img, t)
        if sg["key"] == "end":
            self.cta_card(img, t)
        return img


# ---------- sound ----------
def chime(sr, seed=0):
    """The update arriving: two soft bell notes, G6 then D7, in the song's key."""
    n = int(1.4 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    y = np.zeros(n, np.float32)
    for at, f, g in ((0.0, 1567.98, 1.0), (0.085, 2349.32, 0.8)):
        k = np.clip(t - at, 0, None)
        env = np.exp(-k * 7.0) * np.clip(k / 0.003, 0, 1) * (t >= at)
        tone = np.sin(2 * np.pi * f * k) + 0.18 * np.sin(2 * np.pi * f * 2.76 * k) * np.exp(-k * 14) + 0.06 * np.sin(2 * np.pi * f * 5.4 * k) * np.exp(-k * 22)
        y += (tone * env * g).astype(np.float32)
    y /= np.abs(y).max() + 1e-9
    # a touch of room
    rng = np.random.default_rng(seed)
    ir = (rng.normal(0, 1, int(0.25 * sr)) * np.exp(-np.arange(int(0.25 * sr)) / (0.06 * sr))).astype(np.float32)
    wet = np.convolve(y, ir)[:n] * 0.02
    left, right = y + wet, y + np.roll(wet, 240)
    return np.stack([left, right], 1).astype(np.float32) * 0.5


def shimmer(sr):
    n = int(1.8 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    y = np.zeros(n, np.float32)
    rng = np.random.default_rng(4)
    for f in (1567.98, 1975.53, 2349.32, 3135.96):
        at = rng.uniform(0, 0.3)
        k = np.clip(t - at, 0, None)
        y += np.sin(2 * np.pi * f * k).astype(np.float32) * np.exp(-k * 4.5).astype(np.float32) * (t > at)
    y /= np.abs(y).max() + 1e-9
    return np.stack([y, y], 1) * 0.4


def rewind_sound(sr, length):
    """Tape running backwards: noise whose pitch sweeps down and back up, with a fast flutter."""
    n = int(length * sr)
    t = np.arange(n, dtype=np.float32) / sr
    q = t / length
    rng = np.random.default_rng(12)
    spec = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / sr)
    out = np.zeros(n, np.float32)
    for j, centre in enumerate((3200, 2200, 1500, 1100, 1500, 2600)):
        band = np.fft.irfft(spec * np.exp(-((np.log(f + 1) - np.log(centre)) / 0.45) ** 2), n).astype(np.float32)
        w = np.exp(-((q - j / 5) / 0.16) ** 2)
        out += band * w
    out *= (0.75 + 0.25 * np.sin(2 * np.pi * (40 + 50 * q) * t)) * np.sin(np.pi * q) ** 0.8
    out /= np.abs(out).max() + 1e-9
    return np.stack([out, out], 1) * 0.7


def clip_audio(name, start, dur, fade=0.04):
    x = decode(next((ROOT / "source").glob(f"*_raw/{name}.MOV")), start, dur)
    f = int(fade * 48000)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    return x


def build_audio(r):
    sr = 48000
    n = int(math.ceil(r.total * sr))
    mix = np.zeros((n, 2), np.float32)
    song = ROOT / "source" / "music" / SONG
    xf = int(0.03 * sr)
    for b_film, b_song, beats in PARTS:
        start = FIRST_BEAT + b_song * BEAT - 0.012
        m = decode(song, start, beats * BEAT + 0.05)[:int(beats * BEAT * sr) + xf]
        m[:xf] *= np.linspace(0, 1, xf)[:, None]
        m[-xf:] *= np.linspace(1, 0, xf)[:, None]
        i = int(bt(b_film) * sr)
        j = min(n, i + len(m))
        mix[i:j] += m[:j - i]
    # the hook is the teacher's own voice over a quiet bar; the band comes in as the day starts
    k = int(bt(LIFT) * sr)
    mix[:k] *= np.linspace(0.42, 0.62, k)[:, None]
    hook = r.by_key["hook"]
    hs = hook["shot"]
    voice = clip_audio("IMG_8714", 20.25, 0.85)
    voice = voice / (np.abs(voice).max() + 1e-9)
    i = int(0.12 * sr)
    mix[i:i + len(voice)] += voice[:n - i] * 0.5 * 10 ** (-1 / 20)
    # the stop, and the tape running back to the morning
    r0 = hook["t0"] + hs["beats"] * BEAT - hs["rewind"]
    rw = rewind_sound(sr, hs["rewind"] + 0.05)
    i = int(r0 * sr)
    mix[i:i + len(rw)] += rw[:n - i] * 10 ** (-7 / 20)
    # the real yard under the morning, very low
    yard = clip_audio("IMG_8697", 6.0, bt(6) + 0.3)
    rms = np.sqrt((yard ** 2).mean()) + 1e-9
    yard = yard / rms * 10 ** (-34 / 20)
    i = int(bt(LIFT) * sr)
    f = int(0.2 * sr)
    yard[:f] *= np.linspace(0, 1, f)[:, None]
    yard[-f:] *= np.linspace(1, 0, f)[:, None]
    mix[i:i + len(yard)] += yard[:n - i]
    # the payoff: the slap of the high five, right as the slow-motion hands meet
    five = r.by_key["five"]
    sh = five["shot"]
    contact = five["t0"] + (24.05 - sh["start"]) / sh["speed"]
    slap = clip_audio("IMG_8714", 23.72, 0.32, 0.01)
    slap = slap / (np.abs(slap).max() + 1e-9)
    a_, b_ = int((contact - 0.15) * sr), int((contact + 0.45) * sr)
    ramp = int(0.08 * sr)
    env = np.ones(n, np.float32)
    env[a_:b_] = 0.72
    env[a_ - ramp:a_] = np.linspace(1, 0.72, ramp)
    env[b_:b_ + ramp] = np.linspace(0.72, 1, ramp)
    mix *= env[:, None]
    i = int((contact - 0.06) * sr)
    mix[i:i + len(slap)] += slap[:n - i] * 0.5 * 10 ** (-3 / 20)
    sp = shimmer(sr)
    i = int((contact + 0.05) * sr)
    mix[i:i + len(sp)] += sp[:n - i] * 10 ** (-22 / 20)
    # an update arriving
    for k_, note in enumerate(NOTES + [CTA]):
        c = chime(sr, k_)
        i = int((bt(note["at"]) + 0.05) * sr)
        j = min(n, i + len(c))
        mix[i:j] += c[:j - i] * 10 ** (-13 / 20)
    s = shimmer(sr)
    i = int(bt(HIT) * sr)
    mix[i:i + len(s)] += s[:n - i] * 10 ** (-16 / 20)
    tail = int(0.6 * sr)
    mix[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 1.5
    raw = ROOT / "work" / f"{OUT}_mix_raw.wav"
    sf.write(str(raw), mix, sr, subtype="FLOAT")
    out = raw.with_name(f"{OUT}_mix.wav")
    loudness_normalise(raw, out)
    return out


def main():
    r = Renderer()
    print(f"{FMT}: {len(r.segs)} segments, {r.total:.2f} s", flush=True)
    if "--stills" in sys.argv:
        out = ROOT / "work" / f"stills_{FMT}{'_preview' if PREVIEW else ''}"
        out.mkdir(parents=True, exist_ok=True)
        for arg in sys.argv[sys.argv.index("--stills") + 1:]:
            if arg.startswith("--"):
                continue
            t = float(arg)
            fr = (np.clip(r.frame(t), 0, 1) * 255 + 0.5).astype(np.uint8)
            Image.fromarray(fr).save(out / f"t{t:06.2f}.jpg", quality=92)
            print("wrote", t, flush=True)
        return
    if "--audio" in sys.argv:
        print(build_audio(r))
        return
    EXPORTS.mkdir(exist_ok=True)
    if FMT == "phone" and not PREVIEW:
        cover = (np.clip(r.frame(bt(2.6)), 0, 1) * 255 + 0.5).astype(np.uint8)
        Image.fromarray(cover).save(EXPORTS / "updates_cover.jpg", quality=95)
    raw = ROOT / "work" / f"{OUT}.rgb"
    render_frames(r, raw)
    audio, dur = build_audio(r), r.total
    del r
    gc.collect()
    video = EXPORTS / f"{OUT}.mp4"
    encode(raw, video, audio, dur)
    raw.unlink()
    if FMT == "phone" and not PREVIEW:
        if video.stat().st_size > 29 * 2 ** 20:
            phone_copy(video, EXPORTS / f"{OUT}_phone.mp4")
        for flag in ("--feed", "--tv"):
            subprocess.run([sys.executable, "-I", __file__, flag], check=True)


if __name__ == "__main__":
    main()
