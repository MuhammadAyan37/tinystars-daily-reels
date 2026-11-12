"""Red Nova, round nine: six different Christmas layouts (samples 60 to 65), not trees, in the same hand-made style.

Same rules as the flat trees, which the owner preferred: real photos as prints with white borders (the ten brightened
ones from rednova_trees10), flat shapes in a few inks, pen lines, a faint paper texture, no glow, no gloss, no 3D.

  60  Wreath: eight round photos in a ring of flat leaves and berries, a pen-drawn bow, the name in the middle
  61  Postcard: a Christmas postcard with a big photo, a photo stamp, a postmark and a handwritten note
  62  Window: a window at night whose six panes are photos of the room, snow on the sill, a string of bulbs
  63  Photo booth: three photo-booth strips of the room on blush paper, holly drawn by hand
  64  Advent: an advent calendar of numbered doors, ten of them photos of the room
  65  Gingham: polaroids on a red gingham cloth, holly, and a note card with the offer

Usage: python -I edits/rednova_more.py [60 61 ...]   (all six when none is named)
  -> exports/rednova_ad_<n>.jpg            1440 x 1800 (4:5)
  -> exports/rednova_ads_more.jpg          the six side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import rednova_aesthetic as A  # noqa: E402
import rednova_trees10 as T  # noqa: E402
import rednova_trees_flat as F  # noqa: E402
from offer_modern import pen  # noqa: E402
from offer_samples import BASE, CROPS, INK, LIFT, OUT, SIZE, SS, WHITE, face, logo, picture, put, t, u  # noqa: E402
from rednova_ad import fit_serif, leaf_mask, serif  # noqa: E402
from rednova_modern import ring_text  # noqa: E402

I, C = "InterTight", "Caveat"
TITLE = "red nova is open"
SUB = "a new room, just in time for christmas"
CTA = "book a tour  ·  (780) 230-1599"
ASK = "ask us about our first-month promise"
FOOT = "tinystars.ca  ·  10629 west side drive, grande prairie"

CHERRY = (176, 34, 52)
PINE = (34, 84, 62)
LEAF = [(40, 98, 70), (58, 120, 84), (86, 142, 98), (28, 76, 56)]
CREAM = (250, 246, 237)
CROP = {"RC_sand": (0.47, 0.8, 1.6), "RC_kitchen": (0.5, 0.56, 1.25), "RC_books": (0.64, 0.45, 1.3),
        "RC_tent": (0.4, 0.62, 1.15), "RC_rug": (0.45, 0.42, 1.3), "RC_busy": (0.5, 0.45, 1.25),
        "RC_wide": (0.5, 0.5, 1.15), "RC_corner": (0.62, 0.66, 1.5), "RC_mural": (0.56, 0.42, 2.0),
        "RC_play": (0.42, 0.62, 1.2)}


# ---------- words ----------
def promise(c, cx, y, ink, hi, size=26, lead=36, anchor="m", x=None):
    """we're so sure you'll love it, / your first month is worry-free. ('worry-free' in serif, picked out)."""
    d = ImageDraw.Draw(c)
    f, fs = face(I, size, 400), serif(size * 1.2)
    l1, l2 = "we're so sure you'll love it,", "your first month is "
    if anchor == "m":
        t(d, cx, y, l1, f, ink, 0, "ms")
        w = A.wid(l2, f) + A.wid("worry-free", fs) + A.wid(".", f)
        x0 = cx - w / 2
    else:
        t(d, x, y, l1, f, ink)
        x0 = x
    t(d, x0, y + lead, l2, f, ink)
    t(d, x0 + A.wid(l2, f), y + lead, "worry-free", fs, hi)
    t(d, x0 + A.wid(l2, f) + A.wid("worry-free", fs), y + lead, ".", f, ink)


def small(c, y, ink, s=f"{ASK}   ·   tinystars.ca", x=None):
    t(ImageDraw.Draw(c), BASE[0] / 2 if x is None else x, y, s, face(I, 19, 500), ink, 0.4, "ms" if x is None else "ls")


# ---------- hand-made pieces ----------
def round_print(c, name, cx, cy, d, crop=None, border=7, turn=0):
    """A round photo print with a thin white edge and the small shadow paper casts."""
    ph = picture(name, d, d, *(crop or CROP[name]), lift=LIFT.get(name, 0))
    n = ph.width + 2 * u(border)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((0, 0, n - 1, n - 1), fill=(253, 252, 249, 255))
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, ph.width - 1, ph.height - 1), fill=255)
    ph.putalpha(m)
    lay.alpha_composite(ph, (u(border), u(border)))
    xy = (u(cx) - n // 2, u(cy) - n // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(5), (u(1), u(5)), 0.24)
    c.alpha_composite(lay, xy)


def leaf(c, cx, cy, length, width, ang, col):
    """A flat leaf: two arcs meeting in points, one ink, no shading."""
    ts = np.linspace(0, 1, 30)
    half = width / 2 * np.sin(np.pi * ts) ** 0.9
    pts = [(-length / 2 + length * s_, -h) for s_, h in zip(ts, half)] + \
          [(-length / 2 + length * s_, h) for s_, h in zip(ts[::-1], half[::-1])]
    ca, sa = np.cos(ang), np.sin(ang)
    ImageDraw.Draw(c).polygon([(u(cx + x * ca - y * sa), u(cy + x * sa + y * ca)) for x, y in pts], fill=col + (255,))


def holly_flat(c, cx, cy, s, turn=0, green=(40, 98, 70), red=CHERRY):
    """A flat sprig of holly: two spiky leaves in one green and three red berries."""
    for ang in (-25 + turn, 205 + turn):
        m = leaf_mask(s, s * 0.44)
        big = Image.new("L", (u(2.4 * s), u(2.4 * s)), 0)
        big.paste(m, (big.width // 2, big.height // 2 - m.height // 2))
        big = big.rotate(ang, Image.BICUBIC, center=(big.width // 2, big.height // 2))
        lay = Image.new("RGBA", big.size, green + (255,))
        lay.putalpha(big)
        xy = (u(cx) - big.width // 2, u(cy) - big.height // 2)
        F.cast(c, big, xy, dy=2, blur=2, a=0.15)
        put(c, lay, *xy)
    d = ImageDraw.Draw(c)
    for dx, dy in ((-0.08, -0.06), (0.08, -0.08), (0.0, 0.07)):
        r = s * 0.1
        x, y = cx + dx * s, cy + dy * s
        d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=red + (255,))


def stripe_border(c, x, y, w, h, b, cols, step=26):
    """An airmail border: short diagonal stripes in alternating colours all the way round, clipped to a band."""
    lay = Image.new("RGBA", (u(w), u(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    k = 0
    for s_ in np.arange(-h, w + h, step):
        col = cols[k % len(cols)]
        k += 1
        d.polygon([(u(s_), 0), (u(s_ + step * 0.55), 0), (u(s_ + step * 0.55 - h), u(h)), (u(s_ - h), u(h))],
                  fill=col + (255,))
    m = Image.new("L", lay.size, 255)
    ImageDraw.Draw(m).rectangle((u(b), u(b), u(w - b), u(h - b)), fill=0)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
    return lay


def stamp(name, w, h, crop, ink):
    """A postage stamp: a photo inside a white margin with perforated edges and a little caption."""
    W_, H_ = u(w), u(h)
    lay = Image.new("RGBA", (W_, H_), (253, 252, 248, 255))
    ph = picture(name, w - 24, h - 48, *crop, lift=LIFT.get(name, 0))
    lay.alpha_composite(ph, (u(12), u(12)))
    ImageDraw.Draw(lay).text((W_ / 2, H_ - u(14)), "red nova", font=serif(22), fill=ink + (255,), anchor="ms")
    m = Image.new("L", (W_, H_), 255)
    dm = ImageDraw.Draw(m)
    r = u(5)
    for x in np.arange(0, w + 1, 14):
        for y in (0, h):
            dm.ellipse((u(x) - r, u(y) - r, u(x) + r, u(y) + r), fill=0)
    for y in np.arange(0, h + 1, 14):
        for x in (0, w):
            dm.ellipse((u(x) - r, u(y) - r, u(x) + r, u(y) + r), fill=0)
    lay.putalpha(m)
    return lay


def postmark(c, cx, cy, r, ink, text):
    d = ImageDraw.Draw(c)
    for rr in (r, r * 0.66):
        d.ellipse((u(cx - rr), u(cy - rr), u(cx + rr), u(cy + rr)), outline=ink + (190,), width=u(2.2))
    ring_text(c, cx, cy, r * 0.83, text, face(I, 13, 700), ink)
    t(d, cx, cy + 6, "12 · 2026", face(I, 16, 700), ink, 1, "ms")
    for k in range(4):
        pts = [(cx + r + 10 + s_, cy - 30 + k * 18 + 5 * np.sin(s_ / 14)) for s_ in np.linspace(0, 190, 50)]
        pen(c, pts, ink, 2.2)


def gingham(w, h, cell, col, base=(252, 248, 242)):
    yy, xx = np.mgrid[0:h, 0:w]
    a = ((xx // cell) % 2).astype(np.float32)
    b = ((yy // cell) % 2).astype(np.float32)
    k = (a + b) / 2  # 0 white, 0.5 one band, 1 where bands cross
    base_ = np.array(base, np.float32)
    colr = np.array(col, np.float32)
    img = base_ * (1 - k[..., None] * 0.9) + colr * (k[..., None] * 0.9)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def polaroid_flat(c, name, cx, cy, w, turn, caption, crop=None, ink=(70, 46, 46)):
    side, bottom = 14, 64
    ph = picture(name, w, w, *(crop or CROP[name]), lift=LIFT.get(name, 0))
    fw, fh = u(w + 2 * side), u(w + side + bottom)
    lay = Image.new("RGBA", (fw, fh), (253, 252, 248, 255))
    lay.alpha_composite(ph, (u(side), u(side)))
    ImageDraw.Draw(lay).text((fw / 2, u(w + side + bottom * 0.62)), caption, font=face(C, 36, 650), fill=ink,
                             anchor="mm")
    lay = lay.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - lay.width // 2, u(cy) - lay.height // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(6), (u(2), u(7)), 0.28)
    put(c, lay, *xy)


def tape(c, cx, cy, w, h, turn, col=(244, 236, 214), a=210):
    lay = Image.new("RGBA", (u(w), u(h)), col + (a,))
    lay = lay.rotate(turn, Image.BICUBIC, expand=True)
    c.alpha_composite(lay, (u(cx) - lay.width // 2, u(cy) - lay.height // 2))


# ---------- the six ----------
def m60(c):
    """Wreath: eight round photos in a ring of flat leaves and berries, a pen-drawn bow, the name in the middle."""
    W, H = BASE
    F.paper(c, (246, 242, 232), 60)
    c.alpha_composite(logo(86), (u(40), u(26)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 84, SUB, serif(30), (120, 128, 112), 0, "rs")
    cx, cy, R = W / 2, 560, 318
    rng = np.random.default_rng(6)
    for k in range(260):
        a = rng.uniform(0, 2 * np.pi)
        rr = R + rng.normal(0, 40)
        x, y = cx + rr * np.cos(a), cy + rr * np.sin(a)
        leaf(c, x, y, rng.uniform(46, 70), rng.uniform(16, 24), a + np.pi / 2 + rng.normal(0, 0.5),
             LEAF[rng.integers(len(LEAF))])
    for k in range(40):
        a = rng.uniform(0, 2 * np.pi)
        rr = R + rng.normal(0, 50)
        x, y = cx + rr * np.cos(a), cy + rr * np.sin(a)
        r = rng.uniform(6, 9)
        d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=CHERRY + (255,))
    names = ["RC_sand", "RC_kitchen", "RC_books", "RC_rug", "RC_wide", "RC_corner", "RC_tent", "RC_play"]
    for k, n in enumerate(names):
        a = -np.pi / 2 + k * np.pi / 4 + np.pi / 8
        round_print(c, n, cx + R * np.cos(a), cy + R * np.sin(a), 176, CROP[n])
    F.line_bow(c, cx, cy + R + 22, 100, CHERRY, w=6.5)
    t(d, cx, cy - 6, "red nova", fit_serif(["red nova"], 380, 104), (60, 74, 58), -1, "ms")
    t(d, cx, cy + 56, "is open", serif(56), CHERRY, 0, "ms")
    t(d, cx, cy + 108, "come take a peek!", face(C, 36, 600), (110, 118, 100), 0, "ms")
    promise(c, cx, 1066, (60, 60, 52), CHERRY)
    F.flat_pill(c, cx, 1138, 560, 68, CTA, PINE, WHITE, face(I, 25, 600))
    small(c, 1316, (130, 132, 118))


def m61(c):
    """Postcard: a Christmas postcard with a big photo, a photo stamp, a postmark and a handwritten note."""
    W, H = BASE
    F.paper(c, (236, 226, 208), 61)
    c.alpha_composite(logo(86), (u(40), u(26)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 84, SUB, serif(30), (120, 100, 80), 0, "rs")
    t(d, W / 2, 196, TITLE, fit_serif([TITLE], 860, 92), CHERRY, -1, "ms")
    F.print_photo(c, "RC_books", 930, 300, 220, 160, CROP["RC_books"], 9)
    F.print_photo(c, "RC_tent", 150, 900, 220, 160, CROP["RC_tent"], -8)
    cw, ch = 980, 640
    card = Image.new("RGBA", (u(cw), u(ch)), (252, 249, 242, 255))
    card.alpha_composite(stripe_border(c, 0, 0, cw, ch, 16, [CHERRY, (252, 249, 242), PINE, (252, 249, 242)]), (0, 0))
    ph = picture("RC_sand", 440, 520, 0.47, 0.76, 1.3, lift=0)
    fr = Image.new("RGBA", (ph.width + u(16), ph.height + u(16)), (253, 252, 249, 255))
    fr.alpha_composite(ph, (u(8), u(8)))
    card.alpha_composite(fr, (u(40), u(52)))
    dc = ImageDraw.Draw(card)
    dc.line((u(512), u(70), u(512), u(ch - 70)), fill=(200, 190, 176, 255), width=u(1.6))
    st = stamp("RC_kitchen", 150, 180, (0.5, 0.56, 1.5), CHERRY)
    card.alpha_composite(st.rotate(3, Image.BICUBIC, expand=True), (u(cw - 200), u(44)))
    postmark(card, cw - 290, 150, 62, (120, 60, 70), "GRANDE PRAIRIE  ·  ALBERTA  ·  ")
    fc = face(C, 36, 600)
    ink = (70, 46, 46)
    for k, s_ in enumerate(["dear parents,", "our newest room is open,", "just in time for christmas!",
                            "come see it for yourself.", "love, tiny stars"]):
        t(dc, 548, 300 + k * 50, s_, fc, CHERRY if k == 4 else ink)
    for k in range(3):
        dc.line((u(548), u(300 + 5 * 50 + 18 + k * 44), u(cw - 50), u(300 + 5 * 50 + 18 + k * 44)),
                fill=(206, 196, 182, 255), width=u(1.4))
    card = card.rotate(-2, Image.BICUBIC, expand=True)
    xy = (u(W / 2) - card.width // 2, u(578) - card.height // 2)
    O.shadow(c, card.getchannel("A"), xy, u(8), (u(2), u(10)), 0.3)
    put(c, card, *xy)
    holly_flat(c, 120, 300, 70, 10)
    promise(c, W / 2, 1034, (70, 52, 40), CHERRY)
    F.flat_pill(c, W / 2, 1106, 560, 68, CTA, CHERRY, WHITE, face(I, 25, 600))
    small(c, 1316, (130, 112, 92))


def m62(c):
    """Window: a window at night whose six panes are photos of the room, snow on the sill, a string of bulbs."""
    W, H = BASE
    F.paper(c, (30, 64, 52), 62)
    F.flakes(c, (255, 255, 255), 130, seed=62)
    O.logo_badge(c, 34, 26, 84)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 150, "take a peek inside", face(C, 54, 650), (244, 224, 176), 0, "ms")
    x0, y0, w, h, b = 140, 210, 800, 640, 22
    sh = Image.new("L", c.size, 0)
    ImageDraw.Draw(sh).rectangle((u(x0), u(y0), u(x0 + w), u(y0 + h)), fill=255)
    F.cast(c, sh, (0, 0), dy=8, blur=8, a=0.35)
    d.rectangle((u(x0), u(y0), u(x0 + w), u(y0 + h)), fill=(246, 242, 234, 255))
    pw, ph_ = (w - 3 * b) / 2, (h - 4 * b) / 3
    names = ["RC_sand", "RC_kitchen", "RC_books", "RC_tent", "RC_wide", "RC_rug"]
    for k, n in enumerate(names):
        col, row = k % 2, k // 2
        X, Y = x0 + b + col * (pw + b), y0 + b + row * (ph_ + b)
        c.alpha_composite(picture(n, pw, ph_, *CROP[n], lift=0), (u(X), u(Y)))
    sill = Image.new("L", c.size, 0)
    ImageDraw.Draw(sill).rectangle((u(x0 - 40), u(y0 + h), u(x0 + w + 40), u(y0 + h + 34)), fill=255)
    F.cast(c, sill, (0, 0), dy=6, blur=5, a=0.35)
    d.rectangle((u(x0 - 40), u(y0 + h), u(x0 + w + 40), u(y0 + h + 34)), fill=(236, 230, 220, 255))
    pts = [(x0 - 40, y0 + h + 4)]
    rng = np.random.default_rng(3)
    for xx in np.linspace(x0 - 40, x0 + w + 40, 14):
        pts.append((xx, y0 + h - rng.uniform(10, 26)))
    pts.append((x0 + w + 40, y0 + h + 4))
    d.polygon([(u(x), u(y)) for x, y in pts], fill=(255, 255, 255, 255))
    wire = [(x0 - 20 + s_ * (w + 40), y0 - 10 + 26 * np.sin(np.pi * ((s_ * 4) % 1))) for s_ in np.linspace(0, 1, 120)]
    pen(c, wire, (20, 40, 32), 2.4)
    for k, s_ in enumerate(np.linspace(0.04, 0.96, 15)):
        x = x0 - 20 + s_ * (w + 40)
        y = y0 - 10 + 26 * np.sin(np.pi * ((s_ * 4) % 1))
        col = [(236, 196, 96), CHERRY, (246, 240, 226), (80, 150, 110)][k % 4]
        d.rounded_rectangle((u(x - 3.5), u(y), u(x + 3.5), u(y + 6)), u(1), fill=(20, 40, 32, 255))
        d.ellipse((u(x - 7), u(y + 5), u(x + 7), u(y + 24)), fill=col + (255,))
    holly_flat(c, x0 - 10, y0 + h + 6, 64, -10, green=(70, 132, 92))
    t(d, W / 2, 982, TITLE, fit_serif([TITLE], 860, 96), (250, 244, 232), -1, "ms")
    promise(c, W / 2, 1036, (226, 234, 226), (244, 214, 140))
    F.flat_pill(c, W / 2, 1104, 560, 68, CTA, (244, 214, 140), (40, 30, 20), face(I, 25, 600))
    small(c, 1316, (170, 196, 182))


def m63(c):
    """Photo booth: three photo-booth strips of the room on blush paper, holly drawn by hand."""
    W, H = BASE
    F.paper(c, (246, 226, 224), 63)
    c.alpha_composite(logo(86), (u(40), u(26)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 84, SUB, serif(30), (160, 110, 116), 0, "rs")
    strips = [["RC_sand", "RC_kitchen", "RC_books"], ["RC_wide", "RC_tent", "RC_rug"],
              ["RC_mural", "RC_play", "RC_busy"]]
    for k, (names, cx, turn) in enumerate(zip(strips, (238, 540, 842), (-4, 1.5, -2))):
        sw, pw, phh, m_ = 250, 222, 172, 14
        sh_ = m_ + 3 * (phh + m_) + 56
        lay = Image.new("RGBA", (u(sw), u(sh_)), (253, 252, 249, 255))
        for j, n in enumerate(names):
            lay.alpha_composite(picture(n, pw, phh, *CROP[n], lift=0), (u(m_), u(m_ + j * (phh + m_))))
        ImageDraw.Draw(lay).text((u(sw / 2), u(sh_ - 18)), ["tiny stars", "red nova", "dec 2026"][k],
                                 font=face(C, 34, 650), fill=(150, 64, 82), anchor="ms")
        lay = lay.rotate(turn, Image.BICUBIC, expand=True)
        xy = (u(cx) - lay.width // 2, u(150))
        O.shadow(c, lay.getchannel("A"), xy, u(6), (u(2), u(8)), 0.26)
        put(c, lay, *xy)
    tape(c, 238, 150, 110, 30, -6)
    tape(c, 540, 150, 110, 30, 4)
    tape(c, 842, 150, 110, 30, -3)
    holly_flat(c, 80, 900, 72, 20, green=(58, 112, 80))
    holly_flat(c, 1000, 240, 60, 200, green=(58, 112, 80))
    t(d, W / 2, 1010, TITLE, fit_serif([TITLE], 860, 96), (160, 60, 80), -1, "ms")
    promise(c, W / 2, 1062, (90, 52, 58), (176, 60, 82))
    F.flat_pill(c, W / 2, 1130, 560, 68, CTA, (168, 64, 84), WHITE, face(I, 25, 600))
    small(c, 1316, (150, 112, 118))


def m64(c):
    """Advent: an advent calendar of numbered doors, ten of them photos of the room."""
    W, H = BASE
    F.paper(c, (248, 243, 234), 64)
    c.alpha_composite(logo(86), (u(40), u(22)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 80, SUB, serif(30), (130, 100, 96), 0, "rs")
    x0, y0, g, cw, chh = 56, 124, 12, (W - 112 - 24) / 3, 214
    nums = [3, 0, 17, 8, 21, 12, 5, 14, 9, 19, 24, 1]
    names = ["RC_sand", None, "RC_kitchen", "RC_books", "RC_tent", "RC_rug", "RC_wide", "RC_corner", "RC_mural",
             "RC_play", None, "RC_busy"]
    fn = face(I, 20, 800)
    for k in range(12):
        col, row = k % 3, k // 3
        X, Y = x0 + col * (cw + g), y0 + row * (chh + g)
        n = names[k]
        if n:
            c.alpha_composite(picture(n, cw, chh, *CROP[n], lift=0), (u(X), u(Y)))
        elif k == 1:
            d.rectangle((u(X), u(Y), u(X + cw), u(Y + chh)), fill=CHERRY + (255,))
            t(d, X + cw / 2, Y + 104, "red nova", serif(62), (252, 244, 236), -1, "ms")
            t(d, X + cw / 2, Y + 156, "is open", serif(40), (250, 214, 200), 0, "ms")
        else:
            d.rectangle((u(X), u(Y), u(X + cw), u(Y + chh)), fill=PINE + (255,))
            F.flat_star(c, X + cw / 2, Y + 82, 96, (236, 196, 100))
            t(d, X + cw / 2, Y + 178, "come see us!", face(C, 40, 650), (244, 236, 218), 0, "ms")
        d.rectangle((u(X), u(Y), u(X + cw), u(Y + chh)), outline=(176, 34, 52, 255), width=u(2))
        if n:
            r = 22
            d.ellipse((u(X + 14), u(Y + 14), u(X + 14 + 2 * r), u(Y + 14 + 2 * r)), fill=(252, 248, 240, 255))
            t(d, X + 14 + r, Y + 14 + r + 7, str(nums[k]), fn, CHERRY, 0, "ms")
    promise(c, W / 2, 1066, (70, 52, 50), CHERRY)
    F.flat_pill(c, W / 2, 1132, 560, 68, CTA, CHERRY, WHITE, face(I, 25, 600))
    small(c, 1316, (140, 116, 108))


def m65(c):
    """Gingham: polaroids on a red gingham cloth, holly, and a note card with the offer."""
    W, H = BASE
    put(c, gingham(u(W), u(H), u(30), (198, 52, 66)), 0, 0)
    a = np.asarray(c.convert("RGB"), np.float32) + np.random.default_rng(5).normal(0, 2.4, (c.height, c.width, 1))
    c.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"), (0, 0))
    O.logo_badge(c, 34, 26, 84)
    for n, cx, cy, turn, cap in [("RC_sand", 290, 246, -5, "sand + diggers"), ("RC_kitchen", 790, 236, 4, "play kitchen"),
                                 ("RC_books", 280, 616, 3, "story corner"), ("RC_wide", 800, 606, -3, "our new room")]:
        polaroid_flat(c, n, cx, cy, 266, turn, cap)
    holly_flat(c, 540, 430, 80, 0, green=(40, 98, 70))
    card = Image.new("L", c.size, 0)
    ImageDraw.Draw(card).rectangle((u(90), u(830), u(990), u(1300)), fill=255)
    card = card.rotate(-1.2, Image.BICUBIC, center=(u(540), u(1065)))
    F.cast(c, card, (0, 0), dy=8, blur=7, a=0.3)
    lay = Image.new("RGBA", c.size, (252, 249, 242, 255))
    lay.putalpha(card)
    c.alpha_composite(lay)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 930, TITLE, fit_serif([TITLE], 780, 88), CHERRY, -1, "ms")
    t(d, W / 2, 978, SUB, face(C, 36, 600), PINE, 0, "ms")
    promise(c, W / 2, 1034, (70, 52, 46), CHERRY, size=25, lead=34)
    F.flat_pill(c, W / 2, 1098, 540, 66, CTA, CHERRY, WHITE, face(I, 24, 600))
    small(c, 1232, (130, 112, 104))
    small(c, 1262, (150, 132, 124), s="10629 west side drive, grande prairie")


SAMPLES = {60: m60, 61: m61, 62: m62, 63: m63, 64: m64, 65: m65}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"rednova_ad_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"rednova_ad_{i}.jpg", flush=True)
    return out


def main():
    T.prepare()
    picks = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(SAMPLES)
    outs = {i: render(i) for i in picks}
    if all(i in outs for i in SAMPLES):
        cols, tw, th = 3, 540, 675
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 24, 2 * (th + 64) + 24), (236, 233, 228))
        dd = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(SAMPLES):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            dd.text((x, y + th + 10), f"Sample {i}", font=f, fill=INK)
        sheet.save(OUT / "rednova_ads_more.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_more.jpg", flush=True)


if __name__ == "__main__":
    main()
