"""The new-family offer: a picture ad for Meta (feed and Stories/Reels) and a full-screen card for the daycare TV.

One real photograph of the stained-glass classroom carries the picture. Over it lies a printed coupon, perforated like
a ticket you could tear off: $100 off your first 2 months, plus free registration. Under it, a parent's words from the
Google reviews and three small real photos (the play gym, painting, the turf yard), then the button to book a tour.
Every photo comes from the daycare's Google page or its own Drive, blurred where anyone is in the picture (photos.py).

Usage: python -I edits/offer.py [feed|story|tv ...]   (all three when none is named)
  -> exports/offer_feed.jpg   1080 x 1350  Facebook and Instagram feeds
  -> exports/offer_story.jpg  1080 x 1920  Stories and Reels (every word inside the area the apps leave clear)
  -> exports/offer_tv.jpg     1920 x 1080  the daycare TV
  -> work/offer_<format>_zones.jpg          the same with the apps' covered areas shaded, for checking
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "work" / "clean"
FONTS = ROOT / "brand" / "fonts"
OUT = ROOT / "exports"
TILT = 1.1  # degrees, anticlockwise
S = 2  # drawn at twice the size, then scaled down, for clean edges on every shape and letter

INK = (35, 20, 48)
PURPLE = (92, 38, 110)
PLUM = (64, 26, 80)
GOLD = (246, 196, 52)
MAGENTA = (196, 40, 112)
PAPER = (250, 244, 232)
CARD = (255, 252, 246)
GREY = (112, 100, 116)

OFFER = dict(kicker=["NEW", "FAMILY", "OFFER"], price="$100 off", months="your first 2 months", extra="+ FREE REGISTRATION")
QUOTE = "“Hands-down the best choice we ever made for our child.”"
QUOTE_BY = "A Tiny Stars parent, on Google"
TOP = "NOW ENROLLING  ·  AGES 1 TO 12"
CTA = "Book a tour"
PHONE = "(780) 230-1599"
WEB = "tinystars.ca  ·  10629 West Side Dr, Grande Prairie"
HERO = dict(name="g02", cx=0.5, cy=0.52)
THUMBS = [dict(name="g21", label="Indoor play gym", cx=0.55, cy=0.55),
          dict(name="IMG_8880_F", label="Hands-on art", cx=0.36, cy=0.46, zoom=1.5),
          dict(name="g18", label="Turf play yard", cx=0.62, cy=0.55)]

# every position in pixels of the finished picture; the drawing scales them by S
LAYOUT = {
    "feed": dict(size=(1080, 1350), hero=(0, 0, 1080, 724), logo=(40, 40, 188), top=(1040, 58, "right"),
                 coupon=(48, 540, 984, 362), quote=(540, 954), thumbs=(48, 1014, 984, 158), labels=1204,
                 cta=(48, 1238, 372, 78), contact=(452, 1238)),
    "story": dict(size=(1080, 1920), hero=(0, 0, 1080, 1000), logo=(48, 262, 200), top=(1032, 282, "right"),
                  coupon=(48, 712, 984, 392), quote=(540, 1150), cta=(48, 1262, 380, 92), contact=(462, 1264),
                  strip=(0, 1440, 1080, 480)),
    "tv": dict(size=(1920, 1080), hero=(0, 0, 1000, 1080), logo=(48, 48, 184), top=None,
               coupon=(880, 132, 980, 360), quote=(1450, 568), thumbs=(1040, 690, 820, 160), labels=884,
               cta=(1040, 930, 370, 84), contact=(1442, 930), top_tv=(1450, 92)),
}


# ---------- type ----------
def sans(size, weight):
    f = ImageFont.truetype(str(FONTS / "InterTight.ttf"), int(size * S))
    f.set_variation_by_axes([weight])
    return f


def serif(size, italic=False):
    return ImageFont.truetype(str(FONTS / ("InstrumentSerif-Italic.ttf" if italic else "InstrumentSerif-Regular.ttf")),
                              int(size * S))


def tracked_width(d, text, f, track):
    return sum(d.textlength(c, font=f) for c in text) + track * S * (len(text) - 1)


def tracked(d, xy, text, f, fill, track=0, anchor="ls"):
    """Letter-spaced text. anchor: l/m/r horizontally, then the font's own vertical anchor."""
    x, y = xy
    w = tracked_width(d, text, f, track)
    x = x - w / 2 if anchor[0] == "m" else x - w if anchor[0] == "r" else x
    for c in text:
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += d.textlength(c, font=f) + track * S
    return w


# ---------- pictures ----------
def photo(name):
    """A blurred working copy, with any black letterbox bars (Google's vertical frames) cut away."""
    im = Image.open(CLEAN / f"{name}.jpg").convert("RGB")
    a = np.asarray(im.convert("L"), np.float32)
    rows, cols = np.where(a.mean(1) > 14)[0], np.where(a.mean(0) > 14)[0]
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))


def cover(im, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Crop to the box's shape around (cx, cy), then scale to fill it."""
    iw, ih = im.size
    k = max(w / iw, h / ih) * zoom
    cw, ch = w / k, h / k
    x0 = max(0.0, min(cx * iw - cw / 2, iw - cw))
    y0 = max(0.0, min(cy * ih - ch / 2, ih - ch))
    return im.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def grade(im, warm=1.0):
    """A light touch: a little warmth, contrast and saturation, and fine detail brought out. Nothing that looks done."""
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = ImageEnhance.Color(im).enhance(1.06)
    if warm:
        r, g, b = im.split()
        r = r.point(lambda v: min(255, int(v * (1 + 0.025 * warm))))
        b = b.point(lambda v: int(v * (1 - 0.03 * warm)))
        im = Image.merge("RGB", (r, g, b))
    return im.filter(ImageFilter.UnsharpMask(radius=1.4 * S, percent=45, threshold=2))


def rounded(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def grain(size, amount, seed):
    """Paper tooth: a faint, fine noise, so flat colour doesn't look like a screen."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (size[1] // 2 + 1, size[0] // 2 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize(size, Image.BILINEAR))
    return n * amount


def add_grain(im, amount=2.2, seed=1):
    a = np.asarray(im, np.float32)
    a += grain(im.size, amount, seed)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), im.mode)


def shadow(canvas, mask, xy, blur, offset, opacity, col=PLUM):
    """A soft drop shadow for a shape, as if it were lying on the page."""
    pad = blur * 3
    m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
    m.paste(mask, (pad, pad))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    layer = Image.new("RGBA", m.size, col + (0,))
    layer.putalpha(m)
    canvas.alpha_composite(layer, (xy[0] - pad + offset[0], xy[1] - pad + offset[1]))


def star(size, col):
    k = 4
    s = size * k
    pts = []
    for i in range(10):
        r = (0.5 if i % 2 == 0 else 0.21) * s
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * 1.02 * math.sin(a) + s * 0.03))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    out = Image.new("RGBA", (size, size), col + (0,))
    out.putalpha(m.resize((size, size), Image.LANCZOS))
    return out


def logo(width):
    im = Image.open(ROOT / "brand" / "logo_hd.png").convert("RGBA")
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


# ---------- pieces ----------
def coupon(w, h):
    """The offer as a printed coupon: a coloured stub, a perforated tear line with half-circle notches, the offer."""
    stub = int(w * 0.235)
    r_notch = 19 * S
    card = Image.new("RGBA", (w, h), CARD + (255,))
    d = ImageDraw.Draw(card)
    d.rectangle((0, 0, stub, h), fill=PURPLE + (255,))
    # the paper's tooth, a touch stronger on the coloured stub, like ink on card
    card = Image.fromarray(np.dstack([np.clip(np.asarray(card, np.float32)[..., :3] + grain((w, h), 2.4, 7)[..., None], 0, 255),
                                      np.full((h, w), 255, np.float32)]).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(card)
    # perforation: short dashes down the tear line
    dash, gap = 9 * S, 8 * S
    y = r_notch + 10 * S
    while y < h - r_notch - 10 * S:
        d.rounded_rectangle((stub - 2 * S, y, stub + 2 * S, y + dash), 2 * S, fill=PAPER + (255,))
        y += dash + gap
    # stub: a gold star and the words, stacked
    sz = int(stub * 0.30)
    st = star(sz, GOLD)
    card.alpha_composite(st, (stub // 2 - sz // 2, int(h * 0.20)))
    f = sans(25, 800)
    y0 = int(h * 0.20) + sz + 30 * S
    for i, word in enumerate(OFFER["kicker"]):
        tracked(d, (stub / 2, y0 + i * 36 * S), word, f, (255, 246, 228), 4, "ms")
    # the offer
    cx = stub + (w - stub) / 2
    fp = serif(170)
    d.text((cx, h * 0.47), OFFER["price"], font=fp, fill=PURPLE, anchor="ms")
    d.text((cx, h * 0.66), OFFER["months"], font=serif(60, italic=True), fill=INK, anchor="ms")
    fe = sans(26, 800)
    tw = tracked_width(d, OFFER["extra"], fe, 3)
    pw, ph = tw + 56 * S, 58 * S
    px0, py0 = cx - pw / 2, h * 0.76
    d.rounded_rectangle((px0, py0, px0 + pw, py0 + ph), ph / 2, fill=GOLD)
    tracked(d, (cx, py0 + ph / 2 + 1 * S), OFFER["extra"], fe, INK, 3, "mm")
    # corners and notches cut out of the card itself, so whatever lies behind shows through
    m = rounded(w, h, 26 * S)
    md = ImageDraw.Draw(m)
    for ny in (0, h):
        md.ellipse((stub - r_notch, ny - r_notch, stub + r_notch, ny + r_notch), fill=0)
    card.putalpha(ImageChops.multiply(card.getchannel("A"), m))
    return card


def logo_tab(width):
    """The logo on a small white card, like a label stuck to the photo."""
    lg = logo(int(width * 0.86))
    tab = Image.new("RGBA", (width, lg.height + int(width * 0.14)), (0, 0, 0, 0))
    m = rounded(tab.width, tab.height, 24 * S)
    white = Image.new("RGBA", tab.size, (255, 253, 249, 255))
    white.putalpha(m)
    tab.alpha_composite(white)
    tab.alpha_composite(lg, ((tab.width - lg.width) // 2, (tab.height - lg.height) // 2))
    return tab


def frosted_pill(canvas, x, y, text, anchor="right", size=21):
    """Tracked capitals on a dark frosted pill, read clearly over any photo."""
    d = ImageDraw.Draw(canvas)
    f = sans(size, 750)
    tw = tracked_width(d, text, f, 3.2)
    w, h = int(tw + 44 * S), int(54 * S)
    x0 = x - w if anchor == "right" else x - w // 2 if anchor == "center" else x
    region = canvas.crop((x0, y, x0 + w, y + h)).convert("RGB").filter(ImageFilter.GaussianBlur(14 * S))
    glass = Image.blend(region, Image.new("RGB", (w, h), INK), 0.55).convert("RGBA")
    glass.putalpha(rounded(w, h, h // 2))
    canvas.alpha_composite(glass, (x0, y))
    tracked(ImageDraw.Draw(canvas), (x0 + w / 2, y + h / 2 + 1 * S), text, f, (255, 250, 240), 3.2, "mm")


def quote(canvas, cx, y, width_limit):
    d = ImageDraw.Draw(canvas)
    stars = 5
    ss = 30 * S
    gap = 4 * S
    sw = stars * ss + (stars - 1) * gap
    fq = serif(37, italic=True)
    fb = sans(19, 600)
    qw = d.textlength(QUOTE, font=fq)
    total = sw + 18 * S + qw
    if total > width_limit:  # too wide for one line: stars above, the words below
        x = cx - sw / 2
        for i in range(stars):
            canvas.alpha_composite(star(ss, GOLD), (int(x + i * (ss + gap)), int(y - ss)))
        d.text((cx, y + 44 * S), QUOTE, font=fq, fill=INK, anchor="ms")
        tracked(d, (cx, y + 78 * S), QUOTE_BY.upper(), fb, GREY, 2.5, "ms")
        return
    x = cx - total / 2
    for i in range(stars):
        canvas.alpha_composite(star(ss, GOLD), (int(x + i * (ss + gap)), int(y - ss * 0.86)))
    d.text((x + sw + 18 * S, y), QUOTE, font=fq, fill=INK, anchor="ls")
    tracked(d, (cx, y + 34 * S), QUOTE_BY.upper(), fb, GREY, 2.5, "ms")


def button(canvas, x, y, w, h):
    d = ImageDraw.Draw(canvas)
    m = rounded(w, h, h // 2)
    shadow(canvas, m, (x, y), 10 * S, (0, 6 * S), 0.28)
    b = Image.new("RGBA", (w, h), PURPLE + (255,))
    b.putalpha(m)
    canvas.alpha_composite(b, (x, y))
    f = sans(31, 700)
    tw = d.textlength(CTA, font=f)
    aw = 34 * S
    x0 = x + w / 2 - (tw + 16 * S + aw) / 2
    d.text((x0, y + h / 2), CTA, font=f, fill=(255, 250, 240), anchor="lm")
    # an arrow, drawn: the font's own is too thin at this size
    ax, ay = x0 + tw + 16 * S, y + h / 2
    lw = int(4.2 * S)
    d.line([(ax, ay), (ax + aw, ay)], fill=GOLD, width=lw)
    d.line([(ax + aw - 13 * S, ay - 12 * S), (ax + aw, ay), (ax + aw - 13 * S, ay + 12 * S)], fill=GOLD, width=lw,
           joint="curve")


def contact(canvas, x, y, h):
    d = ImageDraw.Draw(canvas)
    d.text((x, y + h * 0.46), PHONE, font=sans(36, 750), fill=INK, anchor="ls")
    d.text((x, y + h * 0.88), WEB, font=sans(21, 500), fill=GREY, anchor="ls")


def thumbs(canvas, x, y, w, h, labels_y=None, gap=16, radius=20, label_size=22):
    n = len(THUMBS)
    tw = (w - gap * S * (n - 1)) // n
    d = ImageDraw.Draw(canvas)
    for i, t in enumerate(THUMBS):
        px = x + i * (tw + gap * S)
        im = grade(cover(photo(t["name"]), tw, h, t["cx"], t["cy"], t.get("zoom", 1.0))).convert("RGBA")
        m = rounded(tw, h, radius * S)
        shadow(canvas, m, (px, y), 8 * S, (0, 4 * S), 0.16)
        im.putalpha(m)
        canvas.alpha_composite(im, (px, y))
        if labels_y is not None:
            tracked(d, (px + tw / 2, labels_y), t["label"].upper(), sans(label_size, 700), INK, 2.2, "ms")
        else:  # labels on the photos themselves, on a small frosted chip
            frosted_pill(canvas, px + tw // 2, y + h - 74 * S, t["label"].upper(), anchor="center", size=19)


# ---------- the picture ----------
def render(fmt):
    L = {k: (tuple(int(v * S) if isinstance(v, (int, float)) else v for v in val) if isinstance(val, tuple) else
             (int(val * S) if isinstance(val, (int, float)) else val)) for k, val in LAYOUT[fmt].items()}
    W, H = L["size"]
    canvas = add_grain(Image.new("RGB", (W, H), PAPER), 1.8, 3).convert("RGBA")
    hx, hy, hw, hh = L["hero"]
    hero = grade(cover(photo(HERO["name"]), hw, hh, HERO["cx"], HERO["cy"])).convert("RGBA")
    # a soft shade at the very top so the label and pill sit cleanly on the window light
    shade = np.linspace(0.30, 0, int(hh * 0.30))[:, None] * np.ones((1, hw))
    sh = Image.fromarray((np.vstack([shade, np.zeros((hh - shade.shape[0], hw))]) * 255).astype(np.uint8), "L")
    dark = Image.new("RGBA", (hw, hh), INK + (0,))
    dark.putalpha(sh)
    hero.alpha_composite(dark)
    canvas.alpha_composite(hero, (hx, hy))

    if "strip" in L:  # the bottom of a Story, under the apps' buttons: more of the rooms, a picture and nothing to read
        sx, sy, sw, shh = L["strip"]
        n = len(THUMBS)
        each = sw // n
        for i, t in enumerate(THUMBS):
            im = grade(cover(photo(t["name"]), each - 4 * S if i < n - 1 else sw - each * i, shh, t["cx"], t["cy"], t.get("zoom", 1.0)))
            canvas.paste(im, (sx + i * each, sy))
        fade = np.linspace(1, 0, 90 * S)[:, None] * np.ones((1, sw))
        f = Image.new("RGBA", (sw, fade.shape[0]), PAPER + (0,))
        f.putalpha(Image.fromarray((fade * 255).astype(np.uint8), "L"))
        canvas.alpha_composite(f, (sx, sy))

    if fmt == "tv":  # the right-hand page
        d = ImageDraw.Draw(canvas)
        tx, ty = L["top_tv"]
        tracked(d, (tx, ty), TOP, sans(22, 750), PURPLE, 3.4, "ms")

    lx, ly, lw = L["logo"]
    tab = logo_tab(lw)
    shadow(canvas, tab.getchannel("A"), (lx, ly), 12 * S, (0, 6 * S), 0.30)
    canvas.alpha_composite(tab, (lx, ly))
    if L["top"]:
        x, y, anchor = L["top"]
        frosted_pill(canvas, x, y, TOP, anchor)

    cx, cy, cw, ch = L["coupon"]
    # laid down by hand: a degree off square, the way a real card never lands quite straight
    cp = coupon(cw, ch).rotate(TILT, resample=Image.BICUBIC, expand=True)
    px, py = cx - (cp.width - cw) // 2, cy - (cp.height - ch) // 2
    shadow(canvas, cp.getchannel("A"), (px, py), 22 * S, (0, 16 * S), 0.34)
    canvas.alpha_composite(cp, (px, py))

    qx, qy = L["quote"]
    quote(canvas, qx, qy, {"feed": 984, "story": 880, "tv": 860}[fmt] * S)  # the story keeps clear of the Reels buttons
    if "thumbs" in L:
        x, y, w, h = L["thumbs"]
        thumbs(canvas, x, y, w, h, L.get("labels"))
    bx, by, bw, bh = L["cta"]
    button(canvas, bx, by, bw, bh)
    ox, oy = L["contact"]
    contact(canvas, ox, oy, bh)

    out = canvas.convert("RGB").resize((W // S, H // S), Image.LANCZOS)
    OUT.mkdir(exist_ok=True)
    out.save(OUT / f"offer_{fmt}.jpg", quality=95, subsampling=0, optimize=True)
    zones(out, fmt).save(ROOT / "work" / f"offer_{fmt}_zones.jpg", quality=88)
    print("wrote", OUT / f"offer_{fmt}.jpg", out.size, flush=True)


def zones(im, fmt):
    """Shade what the apps cover, to check every word sits clear of it."""
    z = im.convert("RGBA")
    d = ImageDraw.Draw(z)
    if fmt == "story":  # Reels: the top 220 px and the bottom 500 px carry the app's own text and buttons
        for box in ((0, 0, 1080, 220), (0, 1420, 1080, 1920), (960, 1000, 1080, 1420)):
            d.rectangle(box, fill=(255, 0, 0, 60))
    return z.convert("RGB")


def main():
    fmts = [a for a in sys.argv[1:] if a in LAYOUT] or list(LAYOUT)
    for fmt in fmts:
        render(fmt)


if __name__ == "__main__":
    main()
