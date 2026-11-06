"""The new-family offer: a picture ad for Meta (feed and Stories/Reels) and a full-screen picture for the daycare TV.

A real photograph does the work: the stained-glass classroom, full bleed, graded only lightly so it still looks like a
photo. One white card carries everything to read, set the way a modern app sets it: who it's for, $100 off your first
2 months plus free registration in big type, three small real photos (the play gym, painting, the turf yard) and the
button to book a tour. No stickers, glows or stars: nothing that looks generated.

Every photo comes from the daycare's Google page or its own Drive, blurred wherever anyone is in the picture
(photos.py). Each version is drawn at well over its final size and scaled down, so edges and type stay crisp.

Usage: python -I edits/offer.py [feed|story|tv ...]   (all three when none is named)
  -> exports/offer_feed.jpg   1440 x 1800  Facebook and Instagram feeds (Meta's recommended size for 4:5)
  -> exports/offer_story.jpg  1440 x 2560  Stories and Reels (every word inside the area the apps leave clear)
  -> exports/offer_tv.jpg     3840 x 2160  the daycare TV, in 4K
  -> work/offer_story_zones.jpg            the story with the apps' covered areas shaded, for checking
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "work" / "clean"
FONTS = ROOT / "brand" / "fonts"
OUT = ROOT / "exports"

INK = (24, 19, 32)
SOFT = (92, 86, 100)
PURPLE = (84, 38, 120)
CARD = (255, 255, 255)
LINE = (232, 228, 236)

EYEBROW = "Christmas offer for new families  ·  Enrol by December 24"
PROMISE = "30-day happiness promise"
TAGS = ["Ages 1 to 12", "Grande Prairie"]
PRICE = "$100 off"
MONTHS = "your first 2 months"
EXTRA = "+ free registration"
CTA = "Book a tour"
PHONE = "(780) 230-1599"
WEB = "tinystars.ca  ·  10629 West Side Drive"
QUOTE = ["“Hands-down the best choice", "we ever made for our child.”"]
QUOTE_BY = "A Tiny Stars parent, on Google"
HERO = "g02"
PLACES = [dict(name="g21", label=["Indoor", "play gym"], cx=0.55, cy=0.56, zoom=1.0),
          dict(name="IMG_8880_S", label=["Hands-on", "art"], cx=0.36, cy=0.5, zoom=1.9),
          dict(name="IMG_7690", label=["Turf", "play yard"], cx=0.44, cy=0.5, zoom=2.3)]

# positions in "base" pixels (the 1080-wide frame for the phone pictures, 1920-wide for the TV); out is the delivered
# size, and ss how much bigger than that it is drawn before scaling down
FORMATS = {
    "feed": dict(base=(1080, 1350), out=(1440, 1800), ss=2.0, hero=(0.55, 0.57, 1.42), logo=(32, 32, 112),
                 card=(28, 680, 1024, 642), pad=52),
    "story": dict(base=(1080, 1920), out=(1440, 2560), ss=2.0, hero=(0.62, 0.56, 1.3), logo=(40, 236, 120),
                  card=(40, 760, 1000, 652), pad=48, right=940),
    "tv": dict(base=(1920, 1080), out=(3840, 2160), ss=1.5, hero=(0.36, 0.47, 1.06), logo=(48, 48, 132),
               card=(1150, 44, 726, 992), pad=60),
}
S = 1.0  # pixels per base pixel while drawing; set per format


def u(v):
    return int(round(v * S))


# ---------- type ----------
def sans(size, weight):
    f = ImageFont.truetype(str(FONTS / "InterTight.ttf"), u(size))
    f.set_variation_by_axes([weight])
    return f


def serif_italic(size):
    return ImageFont.truetype(str(FONTS / "InstrumentSerif-Italic.ttf"), u(size))


def width(d, s, f, track=0.0):
    return sum(d.textlength(c, font=f) for c in s) + u(track) * (len(s) - 1) if track else d.textlength(s, font=f)


def text(d, x, y, s, f, fill, track=0.0, anchor="ls"):
    """Text at a baseline, with optional letter-spacing (negative tightens big type, the way it's set in print)."""
    w = width(d, s, f, track)
    x = x - w / 2 if anchor[0] == "m" else x - w if anchor[0] == "r" else x
    if not track:
        d.text((x, y), s, font=f, fill=fill, anchor="l" + anchor[1])
        return w
    for c in s:
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += d.textlength(c, font=f) + u(track)
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
    k = max(w / iw, h / ih) * max(1.0, zoom)  # never wider than the photo itself
    cw, ch = w / k, h / k
    x0 = max(0.0, min(cx * iw - cw / 2, iw - cw))
    y0 = max(0.0, min(cy * ih - ch / 2, ih - ch))
    return im.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def grade(im):
    """Barely there: a touch of contrast and warmth, colour left as the camera saw it, highlights held a little."""
    a = np.asarray(im, np.float32) / 255
    a = a - 0.06 * np.clip(a - 0.82, 0, None) / 0.18 * a  # roll off the brightest windows and skies
    a = 0.5 + (a - 0.5) * 1.04
    a *= np.array([1.012, 1.0, 0.985], np.float32)
    im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
    return im.filter(ImageFilter.UnsharpMask(radius=max(1.0, S * 0.5), percent=28, threshold=3))


def rounded(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def shadow(canvas, mask, xy, blur, offset, opacity):
    """A wide, faint shadow: just enough to lift the card off the photo."""
    pad = blur * 3
    m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
    m.paste(mask, (pad, pad))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    layer = Image.new("RGBA", m.size, (20, 12, 28, 0))
    layer.putalpha(m)
    canvas.alpha_composite(layer, (xy[0] - pad + offset[0], xy[1] - pad + offset[1]))


def paste_rounded(canvas, im, x, y, r):
    im = im.convert("RGBA")
    im.putalpha(rounded(im.width, im.height, r))
    canvas.alpha_composite(im, (x, y))


def logo_badge(canvas, x, y, size):
    """The logo on a small white tile in the corner of the photo."""
    s = u(size)
    tile = Image.new("RGBA", (s, s), CARD + (255,))
    tile.putalpha(rounded(s, s, u(size * 0.24)))
    lg = Image.open(ROOT / "brand" / "logo_hd.png").convert("RGBA")
    k = s * 0.84 / max(lg.size)
    lg = lg.resize((round(lg.width * k), round(lg.height * k)), Image.LANCZOS)
    tile.alpha_composite(lg, ((s - lg.width) // 2, (s - lg.height) // 2))
    shadow(canvas, tile.getchannel("A"), (u(x), u(y)), u(16), (0, u(6)), 0.22)
    canvas.alpha_composite(tile, (u(x), u(y)))


def arrow(d, x, y, length, col, lw):
    d.line([(x, y), (x + length, y)], fill=col, width=lw)
    k = length * 0.42
    d.line([(x + length - k, y - k), (x + length, y), (x + length - k, y + k)], fill=col, width=lw, joint="curve")


def button(canvas, x, y, w, h, size=30):
    """The call to action: a solid pill, label and arrow centred."""
    d = ImageDraw.Draw(canvas)
    b = Image.new("RGBA", (u(w), u(h)), PURPLE + (255,))
    b.putalpha(rounded(u(w), u(h), u(h / 2)))
    canvas.alpha_composite(b, (u(x), u(y)))
    f = sans(size, 680)
    tw = d.textlength(CTA, font=f)
    al = u(size * 0.8)
    x0 = u(x + w / 2) - (tw + u(14) + al) / 2
    d.text((x0, u(y + h / 2)), CTA, font=f, fill=CARD, anchor="lm")
    arrow(d, x0 + tw + u(14), u(y + h / 2) + u(1), al, CARD, max(2, u(size * 0.1)))


def place(canvas, d, x, y, p, size, label_size):
    """One small real photo with its two-line label beside it."""
    im = grade(cover(photo(p["name"]), u(size), u(size), p["cx"], p["cy"], p["zoom"]))
    paste_rounded(canvas, im, u(x), u(y), u(size * 0.2))
    f = sans(label_size, 620)
    lx = u(x + size + 16)
    mid = y + size / 2
    text(d, lx, u(mid - 4), p["label"][0], f, INK)
    text(d, lx, u(mid - 4 + label_size * 1.18), p["label"][1], f, INK)


def tag(canvas, x, y, label, size=22, tick=False):
    """A small rounded tag, the way an app shows a feature. Returns its width in base pixels."""
    d = ImageDraw.Draw(canvas)
    f = sans(size, 640 if tick else 560)
    h = size * 2.2
    tw = d.textlength(label, font=f) / S
    iw = size * 0.95 if tick else 0
    w = tw + 2 * size * 0.85 + (iw + size * 0.42 if tick else 0)
    t = Image.new("RGBA", (u(w), u(h)), ((240, 233, 247) if tick else (241, 239, 243)) + (255,))
    t.putalpha(rounded(u(w), u(h), u(h / 2)))
    canvas.alpha_composite(t, (u(x), u(y)))
    tx = x + size * 0.85
    if tick:  # a drawn tick, crisper than any font's
        cx, cy, k = tx + iw / 2, y + h / 2, iw / 2
        d.line([(u(cx - k * 0.8), u(cy + k * 0.02)), (u(cx - k * 0.22), u(cy + k * 0.6)), (u(cx + k * 0.85), u(cy - k * 0.62))],
               fill=PURPLE, width=max(2, u(size * 0.14)), joint="curve")
        tx += iw + size * 0.42
    text(d, u(tx), u(y + h / 2), label, f, PURPLE if tick else SOFT, anchor="lm")
    return w


# ---------- the card ----------
def white_card(canvas, x, y, w, h, r, blur):
    m = rounded(u(w), u(h), u(r))
    shadow(canvas, m, (u(x), u(y)), u(blur), (0, u(blur * 0.3)), 0.20)
    c = Image.new("RGBA", (u(w), u(h)), CARD + (255,))
    c.putalpha(m)
    canvas.alpha_composite(c, (u(x), u(y)))


def card_phone(canvas, x, y, w, h, pad, right=None):
    """Feed and story: the offer, the places, the button."""
    white_card(canvas, x, y, w, h, 36, 34)
    d = ImageDraw.Draw(canvas)
    x0 = x + pad
    x1 = right if right is not None else x + w - pad
    # who it's for
    yy = y + pad + 20
    d.ellipse((u(x0), u(yy - 15), u(x0 + 12), u(yy - 3)), fill=PURPLE)
    text(d, u(x0 + 24), u(yy), EYEBROW, sans(23, 600), PURPLE, 0.2)
    # the offer, in big type
    yy += 158
    text(d, u(x0 - 7), u(yy), PRICE, sans(172, 820), INK, -7)
    yy += 60
    wm = text(d, u(x0), u(yy), MONTHS, sans(40, 520), SOFT)
    text(d, u(x0) + wm + u(12), u(yy), EXTRA, sans(40, 760), PURPLE)
    # the promise and the plain facts
    yy += 30
    tx = x0
    for i, label in enumerate([PROMISE] + TAGS):
        tx += tag(canvas, tx, yy, label, 22, tick=i == 0) + 12
    yy += 48 + 32
    col = (x1 - x0) / len(PLACES)
    for i, p in enumerate(PLACES):
        place(canvas, d, x0 + i * col, yy, p, 96, 24)
    # the button and the phone number
    yy += 96 + 34
    bw = 400
    button(canvas, x0, yy, bw, 86)
    tx = x0 + bw + 32
    text(d, u(tx), u(yy + 42), PHONE, sans(36, 720), INK, -0.4)
    text(d, u(tx), u(yy + 74), WEB, sans(19, 500), SOFT)


def card_tv(canvas, x, y, w, h, pad):
    """The TV: the same card, stood up beside the photo, with a parent's words, read from across the room."""
    white_card(canvas, x, y, w, h, 40, 40)
    d = ImageDraw.Draw(canvas)
    x0 = x + pad
    yy = y + pad + 22
    d.ellipse((u(x0), u(yy - 16), u(x0 + 13), u(yy - 3)), fill=PURPLE)
    text(d, u(x0 + 26), u(yy), "Christmas offer  ·  Enrol by December 24", sans(25, 600), PURPLE, 0.2)
    yy += 168
    text(d, u(x0 - 6), u(yy), PRICE, sans(158, 820), INK, -6)
    yy += 64
    text(d, u(x0), u(yy), MONTHS, sans(44, 520), SOFT)
    yy += 54
    text(d, u(x0), u(yy), EXTRA, sans(44, 760), PURPLE)
    yy += 30
    tx = x0
    for i, label in enumerate([PROMISE, TAGS[0]]):
        tx += tag(canvas, tx, yy, label, 23, tick=i == 0) + 12
    yy += 51
    # a parent's words
    yy += 36
    d.line((u(x0), u(yy), u(x + w - pad), u(yy)), fill=LINE, width=max(1, u(2)))
    yy += 66
    fq = serif_italic(44)
    text(d, u(x0), u(yy), QUOTE[0], fq, INK)
    text(d, u(x0), u(yy + 48), QUOTE[1], fq, INK)
    text(d, u(x0), u(yy + 88), QUOTE_BY, sans(20, 560), SOFT, 0.2)
    # the places, side by side
    yy += 128
    col = (w - 2 * pad) / len(PLACES)
    for i, p in enumerate(PLACES):
        px = x0 + i * col
        im = grade(cover(photo(p["name"]), u(col - 18), u(126), p["cx"], p["cy"], p["zoom"] * 0.9))
        paste_rounded(canvas, im, u(px), u(yy), u(20))
        text(d, u(px), u(yy + 126 + 32), " ".join(p["label"]), sans(21, 620), INK)
    # the button and the number
    yy += 126 + 64
    button(canvas, x0, yy, 300, 84, 29)
    tx = x0 + 300 + 26
    text(d, u(tx), u(yy + 40), PHONE, sans(34, 720), INK, -0.4)
    text(d, u(tx), u(yy + 70), "tinystars.ca", sans(19, 500), SOFT)


# ---------- the picture ----------
def render(fmt):
    global S
    F = FORMATS[fmt]
    bw, bh = F["base"]
    S = F["out"][0] / bw * F["ss"]
    W, H = u(bw), u(bh)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    cx, cy, zoom = F["hero"]
    canvas.alpha_composite(grade(cover(photo(HERO), W, H, cx, cy, zoom)).convert("RGBA"))
    logo_badge(canvas, *F["logo"])
    if fmt == "tv":
        card_tv(canvas, *F["card"], F["pad"])
    else:
        card_phone(canvas, *F["card"], F["pad"], F.get("right"))
    out = canvas.convert("RGB").resize(F["out"], Image.LANCZOS)
    OUT.mkdir(exist_ok=True)
    out.save(OUT / f"offer_{fmt}.jpg", quality=95, subsampling=0, optimize=True)
    if fmt == "story":
        zones(out).save(ROOT / "work" / "offer_story_zones.jpg", quality=88)
    print("wrote", OUT / f"offer_{fmt}.jpg", out.size, flush=True)


def zones(im):
    """Shade what Reels covers (the top 220 and bottom 500 of a 1080 x 1920 frame, and the buttons on the right)."""
    z = im.convert("RGBA")
    k = im.width / 1080
    d = ImageDraw.Draw(z)
    for box in ((0, 0, 1080, 220), (0, 1420, 1080, 1920), (960, 1000, 1080, 1420)):
        d.rectangle(tuple(int(v * k) for v in box), fill=(255, 0, 0, 70))
    return z.convert("RGB")


def main():
    for fmt in [a for a in sys.argv[1:] if a in FORMATS] or list(FORMATS):
        render(fmt)


if __name__ == "__main__":
    main()
