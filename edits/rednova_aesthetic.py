"""Red Nova, round three: eight soft, aesthetic takes (samples 22 to 29), the calm Pinterest look rather than bold
or retro. Oat, linen, dusty rose and sage, with a muted rosewood for Red Nova; lowercase words in a delicate serif
and a light sans; plenty of space; little satin bows; photos with a soft, airy grade and a touch of film grain.

Each uses three to five of the best photos of the new room, with the sand-and-diggers bin as the star.

  22  Mood board: four photos in a soft masonry grid
  23  Bows: three arched photos, each tied with a little satin bow
  24  Dreamy: a pastel cloud gradient, photo widgets and a frosted glass card
  25  Photo dump: printed photos with orange date stamps, scattered on oat
  26  Arch: one big arched photo with two round ones, very clean
  27  Christmas sage: four photos on sage and cream, a bow and pine sprigs
  28  Checklist: photos beside a soft note card listing what's in the room
  29  Fade: the sand bin full width, fading into linen

Usage: python -I edits/rednova_aesthetic.py [22 23 ...]   (all eight when none is named)
  -> exports/rednova_ad_<n>.jpg          1440 x 1800 (4:5)
  -> exports/rednova_ads_aesthetic.jpg   the eight side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import offer_samples as S  # noqa: E402
import rednova_modern as M  # noqa: E402
from offer_modern import aurora, glow_text, heart, inflate, liquid_pill, pen, shade  # noqa: E402
from offer_samples import (BASE, CROPS, LABELS, LIFT, OUT, SIZE, SS, WHITE, face, fit, glow, logo, panel,  # noqa: E402
                           picture, put, ramp, sparkle, t, u)
from rednova_ad import bez, serif, wid  # noqa: E402

I, C = "InterTight", "Caveat"
OAT = (245, 239, 230)
LINEN = (251, 248, 243)
SAND = (236, 228, 217)
COCOA = (72, 54, 48)
TAUPE = (146, 126, 116)
ROSE = (234, 200, 196)
ROSEWOOD = (168, 66, 76)
SAGE = (208, 216, 196)
SAGE_DK = (104, 124, 96)
LAV = (228, 222, 244)
BUTTER = (250, 240, 212)
BLUSH = (250, 230, 228)
CHAMPAGNE = (214, 182, 120)

TITLE = "red nova is open"
PROM = ["love your first month, or we'll", "refund your parent portion."]
CTA = "book a tour  ·  (780) 230-1599"
WEB = "tinystars.ca"
ADDR = "10629 west side drive, grande prairie"

# the best photos again, given a soft, airy grade (see soft)
PHOTOS = {"RA_sand": "IMG_1286", "RA_kitchen": "IMG_1294", "RA_books": "IMG_1308", "RA_tent": "IMG_1291",
          "RA_rug": "IMG_1310", "RA_busy": "IMG_1312"}
for k_, v_ in PHOTOS.items():
    CROPS[k_] = CROPS["RN_" + k_[3:]]
    LABELS[k_] = LABELS["RN_" + k_[3:]].lower().replace("&", "+")
SAND_CLOSE = M.SAND_CLOSE


# ---------- the photos ----------
def soft(im):
    """An airy, slightly faded grade: the yellow of the ceiling lights pulled back, brighter mid-tones, softer
    contrast, matte blacks, colour eased off by a fifth, creamy highlights and a faint glow."""
    im = im.copy()
    im.thumbnail((4000, 4000), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    a = np.clip(a * np.array([0.972, 1.0, 1.04], np.float32), 0, 1)
    a = 1 - (1 - a) ** 1.28
    a = 0.5 + (a - 0.5) * 0.9
    a = 0.04 + a * 0.95
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = lum + (a - lum) * 0.8
    a = a + np.array([0.022, 0.012, -0.004], np.float32) * a ** 2
    base = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
    b = np.asarray(base, np.float32) / 255
    g = np.asarray(base.filter(ImageFilter.GaussianBlur(28)), np.float32) / 255
    im = Image.fromarray((np.clip(1 - (1 - b) * (1 - g * 0.12), 0, 1) * 255 + 0.5).astype(np.uint8))
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=22, threshold=2))


def prepare():
    for new, src in PHOTOS.items():
        out, inp = O.CLEAN / f"{new}.jpg", O.CLEAN / f"{src}.jpg"
        if not out.exists() or out.stat().st_mtime < inp.stat().st_mtime:
            soft(Image.open(inp).convert("RGB")).save(out, quality=95)
            print("soft grade", src, "->", out.name, flush=True)


# ---------- pieces ----------
def paper(c, col):
    c.paste(col + (255,), (0, 0, c.width, c.height))


def grain(c, sigma=5.0, seed=1):
    """A fine, even film grain over the whole picture."""
    a = np.asarray(c.convert("RGB"), np.float32)
    n = np.random.default_rng(seed).normal(0, sigma, a.shape[:2]).astype(np.float32)[..., None]
    c.paste(Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8)).convert("RGBA"), (0, 0))


def soft_shadow(c, m, xy, blur=26, dy=16, a=0.16):
    O.shadow(c, m, xy, u(blur), (0, u(dy)), a)


def photo(c, name, x, y, w, h, r=26, shape="round", crop=None, shadow=True, rim=0, rim_col=LINEN):
    """A softly graded photo with rounded corners (or an arch or circle) and a long, faint shadow."""
    ph = picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    m = M.mask_for(shape, ph.width, ph.height, u(r))
    X, Y = u(x), u(y)
    if rim:
        p = u(rim)
        big = Image.new("L", (ph.width + 2 * p, ph.height + 2 * p), 0)
        big.paste(m, (p, p))
        big = big.filter(ImageFilter.GaussianBlur(p * 0.5)).point(lambda v: 255 if v >= 8 else 0)
        if shadow:
            soft_shadow(c, big, (X - p, Y - p))
        rl = Image.new("RGBA", big.size, rim_col + (255,))
        rl.putalpha(big)
        put(c, rl, X - p, Y - p)
    elif shadow:
        soft_shadow(c, m, (X, Y))
    ph.putalpha(m)
    put(c, ph, X, Y)


def label(c, x, y, s, size=22):
    """A small lowercase caption on a photo, in white with a soft dark haze behind it."""
    glow_text(c, x, y, s, face(I, size, 600), WHITE, 0.2, "ls", col=(30, 20, 18), a=0.45, blur=8)


def pill(c, x, y, w, h, s, bg, fg, f, anchor="l"):
    x0 = x - w / 2 if anchor == "m" else x
    panel(c, x0, y, w, h, h / 2, bg, lift=0.1)
    t(ImageDraw.Draw(c), x0 + w / 2, y + h / 2 + f.size / O.S * 0.34, s, f, fg, 0.3, "ms")


def promise(c, x, y, lead, f, anchor="ls", ink=COCOA, word=ROSEWOOD):
    """The promise in a light sans, with 'refund' in rosewood italic serif."""
    d = ImageDraw.Draw(c)
    t(d, x, y, PROM[0], f, ink, 0, anchor)
    a, b = "refund", PROM[1][len("refund"):]  # b keeps its leading space
    fs = serif(f.size / O.S * 1.18)
    wa, wb = wid(a, fs), wid(b, f)
    x0 = x - (wa + wb) / 2 if anchor[0] == "m" else x
    t(d, x0, y + lead, a, fs, word)
    t(d, x0 + wa, y + lead, b, f, ink)


def footer(c, y, ink=TAUPE, x=None, email=False):
    """The small print: the website and address, or the email and address where the website is already shown."""
    W = BASE[0]
    f = face(I, 19, 500)
    s = f"{'info@tinystars.ca' if email else WEB}   ·   {ADDR}"
    t(ImageDraw.Draw(c), W / 2 if x is None else x, y, s, f, ink, 0.5, "ms" if x is None else "ls")


def small_logo(c, x, y, w=88):
    c.alpha_composite(logo(w), (u(x), u(y)))


def coquette_bow(c, cx, cy, s, col, turn=0):
    """A small satin bow, the flat-ribbon kind: two wide ribbon loops, a little knot and two long tails with notched
    ends, lit softly so the satin catches the light."""
    n = u(3.2 * s)
    ctr = n / 2
    k = lambda v: v * u(s)  # noqa: E731
    m = Image.new("L", (n, n), 0)
    for sx in (-1, 1):
        e = Image.new("L", (n, n), 0)
        de = ImageDraw.Draw(e)
        de.ellipse((ctr - k(0.5), ctr - k(0.31), ctr + k(0.5), ctr + k(0.31)), fill=255)
        de.ellipse((ctr - k(0.26) + sx * k(0.06), ctr - k(0.09), ctr + k(0.3) + sx * k(0.06), ctr + k(0.08)), fill=0)
        e = e.rotate(sx * 20, Image.BICUBIC).transform(e.size, Image.AFFINE, (1, 0, -sx * k(0.46), 0, 1, k(0.1)))
        m = ImageChops.lighter(m, e)
    tl = Image.new("L", (n, n), 0)
    dt = ImageDraw.Draw(tl)
    for sx in (-1, 1):
        p0, p1, p2 = (ctr, ctr + k(0.05)), (ctr + sx * k(0.4), ctr + k(0.6)), (ctr + sx * k(0.26), ctr + k(1.25))
        ss = np.linspace(0, 1, 50)
        pts = np.array([bez(p0, p1, p2, v) for v in ss])
        pts[:, 0] += sx * k(0.05) * np.sin(ss * np.pi * 2)
        dv = np.gradient(pts, axis=0)
        nv = np.stack([-dv[:, 1], dv[:, 0]], 1) / (np.linalg.norm(dv, axis=1)[:, None] + 1e-6)
        hw = (k(0.1) - k(0.02) * ss)[:, None]
        left, right = pts + nv * hw, pts - nv * hw
        tip = pts[-1] - (pts[-1] - pts[-4]) * 0.9
        poly = [tuple(v) for v in left] + [tuple(tip)] + [tuple(v) for v in right[::-1]]
        dt.polygon(poly, fill=255)
    km = Image.new("L", (n, n), 0)
    ImageDraw.Draw(km).rounded_rectangle((ctr - k(0.12), ctr - k(0.12), ctr + k(0.12), ctr + k(0.13)), k(0.06), fill=255)
    hi = tuple(min(255, int(v * 1.25 + 46)) for v in col)
    lo = tuple(int(v * 0.7) for v in col)
    stops = [(0, hi), (0.45, col), (1, lo)]
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    lay.alpha_composite(inflate(tl, k(0.035), stops, 90, gloss=0.55))
    lay.alpha_composite(inflate(m, k(0.04), stops, 90, gloss=0.65))
    lay.alpha_composite(inflate(km, k(0.07), stops, 90, gloss=0.8))
    lay = lay.rotate(turn, Image.BICUBIC)
    xy = (u(cx) - n // 2, u(cy) - n // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(6), (0, u(5)), 0.22)
    put(c, lay, *xy)


def sprig(c, p0, p1, p2, col, needles=16, length=26, width=2.6):
    """A line drawing of a pine sprig: a curved stem with needles getting shorter towards the tip."""
    pts = [bez(p0, p1, p2, s_) for s_ in np.linspace(0, 1, 60)]
    pen(c, pts, col, width)
    for i in range(needles):
        s_ = 0.08 + 0.9 * i / (needles - 1)
        x, y = bez(p0, p1, p2, s_)
        x2, y2 = bez(p0, p1, p2, min(1, s_ + 0.01))
        ang = np.arctan2(y2 - y, x2 - x)
        ln = length * (1 - 0.6 * s_)
        for side in (-1, 1):
            a = ang + side * np.deg2rad(52)
            pen(c, [(x, y), (x + ln * np.cos(a), y + ln * np.sin(a))], col, width * 0.8)


def stamp(c, x, y, s, f, anchor="rs"):
    """A disposable-camera date stamp: orange digits with a soft glow."""
    m = Image.new("L", c.size, 0)
    t(ImageDraw.Draw(m), x, y, s, f, 255, 1.5, anchor)
    bb = m.getbbox()
    pad = u(12)
    box = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    g = m.crop(box).filter(ImageFilter.GaussianBlur(u(4))).point(lambda v: int(v * 0.8))
    gl = Image.new("RGBA", g.size, (255, 120, 40, 0))
    gl.putalpha(g)
    c.alpha_composite(gl, box[:2])
    t(ImageDraw.Draw(c), x, y, s, f, (255, 168, 80), 1.5, anchor)


def print_photo(c, name, cx, cy, w, h, turn, crop=None, date="11 12 '26"):
    """A real print: a thin white border, an orange date stamp in the corner, laid down at a slight angle."""
    b = 14
    ph = picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    lay = Image.new("RGBA", (u(w + 2 * b), u(h + 2 * b)), (253, 251, 247, 255))
    lay.alpha_composite(ph, (u(b), u(b)))
    stamp(lay, w + b - 16, h + b - 16, date, face("DMSans", 22, 700))
    lay.putalpha(O.rounded(lay.width, lay.height, u(4)))
    lay = lay.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - lay.width // 2, u(cy) - lay.height // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(20), (u(2), u(12)), 0.2)
    put(c, lay, *xy)


def check(c, x, y, r=14, col=ROSEWOOD):
    d = ImageDraw.Draw(c)
    d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=col + (255,))
    pen(c, [(x - r * 0.45, y + r * 0.02), (x - r * 0.1, y + r * 0.38), (x + r * 0.5, y - r * 0.36)], WHITE, 3)


# ---------- the eight ----------
def a22(c):
    """Mood board: four softly graded photos in a masonry grid on oat, a lowercase serif title."""
    W, H = BASE
    paper(c, OAT)
    glow(c, 900, 200, 520, (255, 246, 238), 0.8)
    small_logo(c, 56, 38)
    d = ImageDraw.Draw(c)
    t(d, W - 56, 88, "new room  ·  now open", face(I, 22, 500), TAUPE, 0.6, "rs")
    t(d, 50, 252, "red nova", serif(150), COCOA, -2)
    sparkle(c, 62 + wid("red nova", serif(150), -2) + 24, 176, 34, ROSEWOOD)
    sparkle(c, 62 + wid("red nova", serif(150), -2) + 58, 214, 18, CHAMPAGNE)
    t(d, 56, 298, "our newest little room is open", face(I, 26, 400), TAUPE)
    photo(c, "RA_sand", 56, 336, 474, 470, crop=(0.47, 0.8, 1.45))
    photo(c, "RA_rug", 56, 822, 474, 196)
    photo(c, "RA_kitchen", 550, 336, 474, 250)
    photo(c, "RA_tent", 550, 602, 474, 416)
    label(c, 80, 780, LABELS["RA_sand"])
    label(c, 80, 992, LABELS["RA_rug"])
    label(c, 574, 560, LABELS["RA_kitchen"])
    label(c, 574, 992, LABELS["RA_tent"])
    promise(c, 56, 1084, 46, face(I, 34, 400))
    pill(c, 56, 1162, 560, 78, CTA, COCOA, LINEN, face(I, 26, 600))
    t(d, W - 56, 1210, WEB, face(I, 22, 600), COCOA, 0.4, "rs")
    footer(c, 1306, email=True)


def a23(c):
    """Bows: three arched photos, each tied with a little satin bow; a lowercase serif title; lots of linen."""
    W, H = BASE
    paper(c, LINEN)
    glow(c, W / 2, 120, 620, BLUSH, 0.7)
    small_logo(c, W / 2 - 44, 36)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 196, "christmas offer  ·  for new families", face(I, 21, 600), ROSEWOOD, 1.6, "ms")
    t(d, W / 2, 302, TITLE, serif(112), COCOA, -1, "ms")
    for x, n, cr, cap, turn in [(60, "RA_kitchen", (0.5, 0.6, 1.25), "play kitchen", -6),
                                (390, "RA_sand", SAND_CLOSE, "sand + diggers", 4),
                                (720, "RA_books", (0.64, 0.42, 1.4), "story corner", -3)]:
        photo(c, n, x, 360, 300, 450, shape="arch", crop=cr)
        coquette_bow(c, x + 150, 368, 66, ROSEWOOD, turn)
        t(d, x + 150, 860, cap, face(C, 36, 600), TAUPE, 0, "ms")
    promise(c, W / 2, 954, 46, face(I, 34, 400), "ms")
    pill(c, W / 2, 1046, 600, 80, CTA, ROSEWOOD, LINEN, face(I, 27, 600), "m")
    for x, y, s_ in [(120, 1100, 22), (960, 1080, 26), (180, 230, 18), (900, 250, 22)]:
        sparkle(c, x, y, s_, CHAMPAGNE)
    footer(c, 1290)


def a24(c):
    """Dreamy: a pastel cloud gradient, the room as three photo widgets, a frosted glass card with the offer."""
    W, H = BASE
    put(c, aurora(u(W), u(H), LINEN, [(0.05, 0.05, 0.6, BLUSH, 0.95), (0.95, 0.15, 0.55, LAV, 0.95),
                                      (0.15, 0.95, 0.6, BUTTER, 0.9), (0.95, 0.95, 0.55, ROSE, 0.8),
                                      (0.5, 0.5, 0.5, (255, 250, 246), 0.6)]), 0, 0)
    small_logo(c, 56, 34, 84)
    liquid_pill(c, W - 56 - 92, 74, "now open", face(I, 22, 600), h=52, fg=COCOA, tint=(255, 255, 255), alpha=0.5)
    photo(c, "RA_sand", 56, 140, 560, 640, r=40, crop=(0.47, 0.78, 1.4))
    photo(c, "RA_kitchen", 632, 140, 392, 312, r=36)
    photo(c, "RA_tent", 632, 468, 392, 312, r=36)
    label(c, 84, 748, LABELS["RA_sand"])
    S.glass(c, 56, 820, W - 112, 450, 44, alpha=0.6, blur=30)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 930, TITLE, serif(98), COCOA, -1, "ms")
    promise(c, W / 2, 996, 44, face(I, 32, 400), "ms")
    pill(c, W / 2, 1080, 600, 80, CTA, ROSEWOOD, LINEN, face(I, 27, 600), "m")
    footer(c, 1222)


def a25(c):
    """Photo dump: four printed photos with orange date stamps scattered on oat, a lowercase title, little doodles."""
    W, H = BASE
    paper(c, OAT)
    small_logo(c, 56, 36)
    d = ImageDraw.Draw(c)
    t(d, W - 56, 90, "new room photo dump", face(C, 42, 600), ROSEWOOD, 0, "rs")
    t(d, 50, 230, "red nova", serif(128), COCOA, -2)
    print_photo(c, "RA_kitchen", 790, 420, 400, 300, 4)
    print_photo(c, "RA_sand", 330, 520, 540, 405, -3, crop=(0.47, 0.82, 1.55))
    print_photo(c, "RA_tent", 820, 800, 320, 420, -3)
    print_photo(c, "RA_books", 320, 880, 420, 300, 3, crop=(0.64, 0.45, 1.25))
    heart(c, 590, 1000, 22, ROSEWOOD)
    sparkle(c, 980, 270, 30, CHAMPAGNE)
    sparkle(c, 60, 700, 22, CHAMPAGNE)
    promise(c, 56, 1110, 46, face(I, 34, 400))
    pill(c, 56, 1182, 560, 78, CTA, COCOA, LINEN, face(I, 26, 600))
    t(d, W - 56, 1230, WEB, face(I, 22, 600), COCOA, 0.4, "rs")
    footer(c, 1312, email=True)


def a26(c):
    """Arch: one big arched photo of the sand bin with two round ones at its feet; very clean, very calm."""
    W, H = BASE
    paper(c, (242, 235, 226))
    glow(c, W / 2, 500, 600, (250, 244, 236), 0.8)
    small_logo(c, W / 2 - 42, 30, 84)
    photo(c, "RA_sand", 200, 140, 680, 700, shape="arch", crop=(0.47, 0.72, 1.15))
    photo(c, "RA_kitchen", 100, 690, 230, 230, shape="circle", crop=(0.48, 0.62, 1.6), rim=10, rim_col=(242, 235, 226))
    photo(c, "RA_books", 750, 690, 230, 230, shape="circle", crop=(0.64, 0.42, 1.6), rim=10, rim_col=(242, 235, 226))
    sparkle(c, 900, 190, 32, CHAMPAGNE)
    sparkle(c, 940, 240, 16, ROSEWOOD)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1012, TITLE, serif(106), COCOA, -1, "ms")
    promise(c, W / 2, 1070, 44, face(I, 31, 400), "ms", ink=(110, 90, 82))
    pill(c, W / 2, 1150, 580, 78, CTA, ROSEWOOD, LINEN, face(I, 26, 600), "m")
    footer(c, 1306)


def a27(c):
    """Christmas sage: four photos on sage and cream, a satin bow on top, pine sprigs drawn in a fine line."""
    W, H = BASE
    put(c, ramp(u(W), u(H), [(0, (220, 228, 212)), (0.55, (240, 240, 230)), (1, (248, 244, 236))], 90), 0, 0)
    sprig(c, (-10, 120), (90, 60), (210, 30), SAGE_DK)
    sprig(c, (1090, 170), (1000, 110), (880, 96), SAGE_DK)
    small_logo(c, 56, 150, 84)
    d = ImageDraw.Draw(c)
    pill(c, W - 56 - 220, 168, 220, 50, "christmas offer", ROSEWOOD, LINEN, face(I, 21, 600))
    t(d, 56, 296, "a little christmas magic:", serif(46), SAGE_DK, 0)
    t(d, 52, 382, TITLE, serif(108), COCOA, -1)
    for (x, y), n, cr in zip([(56, 420), (548, 420), (56, 722), (548, 722)],
                             ["RA_sand", "RA_kitchen", "RA_books", "RA_tent"],
                             [(0.47, 0.8, 1.6), (0.5, 0.58, 1.15), (0.64, 0.45, 1.2), None]):
        photo(c, n, x, y, 476, 286, r=26, crop=cr)
    coquette_bow(c, W / 2, 704, 96, ROSEWOOD, 0)
    for x, y, s_ in [(980, 360, 26), (1020, 1040, 20), (40, 1020, 18), (520, 300, 16)]:
        sparkle(c, x, y, s_, CHAMPAGNE)
    promise(c, 56, 1088, 46, face(I, 34, 400))
    pill(c, 56, 1160, 580, 80, CTA, ROSEWOOD, LINEN, face(I, 27, 600))
    t(d, W - 56, 1210, WEB, face(I, 22, 600), COCOA, 0.4, "rs")
    footer(c, 1306, ink=(120, 112, 100), email=True)


def a28(c):
    """Checklist: the room in three photos beside a soft note card listing what's inside, the offer on the card."""
    W, H = BASE
    paper(c, LINEN)
    glow(c, 200, 1200, 600, BLUSH, 0.6)
    small_logo(c, 56, 34)
    d = ImageDraw.Draw(c)
    t(d, W - 56, 86, "now open", face(I, 22, 600), ROSEWOOD, 1, "rs")
    t(d, 50, 238, TITLE, serif(104), COCOA, -1)
    t(d, 56, 280, "a peek inside our newest room", face(I, 25, 400), TAUPE)
    photo(c, "RA_sand", 56, 316, 500, 470, crop=(0.47, 0.8, 1.45))
    photo(c, "RA_rug", 56, 802, 242, 220, crop=(0.45, 0.45, 1.4))
    photo(c, "RA_kitchen", 314, 802, 242, 220, crop=(0.48, 0.6, 1.5))
    panel(c, 580, 316, 444, 706, 30, (252, 245, 232), lift=0.1)
    t(d, 616, 380, "new room checklist", face(I, 26, 700), COCOA)
    items = ["sand + diggers", "play kitchen", "story corner", "cozy hideout", "circle-time rug", "busy boards"]
    for k, s_ in enumerate(items):
        y = 446 + k * 56
        check(c, 634, y - 9)
        t(d, 664, y, s_, face(I, 26, 400), COCOA)
    d.line((u(616), u(790), u(988), u(790)), fill=(226, 214, 200, 255), width=u(1.5))
    fs = serif(36)
    for k, s_ in enumerate(["love your first month,", "or we'll refund your", "parent portion."]):
        t(d, 616, 846 + k * 44, s_, fs, ROSEWOOD if k == 1 else COCOA)
    pill(c, 56, 1080, 968, 82, CTA, COCOA, LINEN, face(I, 28, 600))
    footer(c, 1240)


def a29(c):
    """Fade: the sand bin full width, fading softly into linen, two small photos floating, the offer below."""
    W, H = BASE
    paper(c, LINEN)
    c.alpha_composite(picture("RA_sand", W, 900, 0.5, 0.7, 1.05), (0, 0))
    shade(c, 560, 900, LINEN, 0.0, 1.0)
    shade(c, 0, 200, (40, 30, 26), 0.28, 0.0)
    small_logo(c, 56, 36)
    liquid_pill(c, W - 56 - 92, 76, "now open", face(I, 22, 600), h=52, fg=COCOA, tint=(255, 255, 255), alpha=0.55)
    photo(c, "RA_kitchen", 56, 690, 300, 220, r=24, rim=8)
    photo(c, "RA_books", 724, 690, 300, 220, r=24, crop=(0.64, 0.45, 1.25), rim=8)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1006, TITLE, serif(110), COCOA, -1, "ms")
    promise(c, W / 2, 1066, 46, face(I, 33, 400), "ms")
    pill(c, W / 2, 1148, 600, 80, CTA, ROSEWOOD, LINEN, face(I, 27, 600), "m")
    footer(c, 1306)


SAMPLES = {22: a22, 23: a23, 24: a24, 25: a25, 26: a26, 27: a27, 28: a28, 29: a29}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    grain(c, 5.5, i)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"rednova_ad_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"rednova_ad_{i}.jpg", flush=True)
    return out


def main():
    prepare()
    picks = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(SAMPLES)
    outs = {i: render(i) for i in picks}
    if all(i in outs for i in SAMPLES):
        cols, tw, th = 4, 540, 675
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 24, 2 * (th + 64) + 24), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(SAMPLES):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 10), f"Sample {i}", font=f, fill=(40, 30, 30))
        sheet.save(OUT / "rednova_ads_aesthetic.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_aesthetic.jpg", flush=True)


if __name__ == "__main__":
    main()
