"""Six simple, elegant takes on the Christmas offer, to choose from. Each reads in under five seconds, so the chosen one
can also go on the banner outside.

Every sample says the same few things, in this order of size: $100 off your first 2 months; not happy in the first
month? we'll refund your registration; the phone number; then the small print (the deadline, ages, the website). Each
uses a different modern typeface (Google Fonts, OFL) and a real photo from the daycare's Google page or Drive.

Usage: python -I edits/offer_samples.py [1 2 3 ...]   (all six when none is named)
  -> exports/offer_sample_<n>.jpg  1440 x 1800 (4:5)
  -> exports/offer_samples.jpg     all six side by side, to compare
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402  (photo, crop, grade and drawing helpers)

ROOT = O.ROOT
FONTS = ROOT / "brand" / "fonts"
OUT = ROOT / "exports"
BASE, SIZE, SS = (1080, 1350), (1440, 1800), 2.0

PRICE = "$100 off"
MONTHS = "your first 2 months"
PROMISE = ["Not happy in the first month?", "We'll refund your registration."]
PHONE = "(780) 230-1599"
WEB = "tinystars.ca"
WHEN = "Christmas offer  ·  until December 24"
AGES = "Ages 1 to 12  ·  Grande Prairie"

INK = (22, 18, 30)
SOFT = (98, 92, 106)
PURPLE = (84, 38, 120)
PLUM = (48, 22, 70)
GOLD = (244, 196, 70)
CREAM = (248, 244, 237)
WHITE = (255, 255, 255)


def u(v):
    return O.u(v)


def face(name, size, wght, opsz=None):
    """A variable Google font at a weight (and, where it has one, an optical size to match)."""
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), u(size))
    vals = []
    for a in f.get_variation_axes():
        n = a["name"].decode() if isinstance(a["name"], bytes) else str(a["name"])
        n = n.lower()
        if n == "weight":
            vals.append(wght)
        elif "optical" in n:
            vals.append(max(a["minimum"], min(a["maximum"], opsz or size)))
        elif n in ("softness", "wonky"):
            vals.append(0)
        else:
            vals.append(a["default"])
    f.set_variation_by_axes(vals)
    return f


def t(d, x, y, s, f, fill, track=0.0, anchor="ls"):
    return O.text(d, u(x), u(y), s, f, fill, track, anchor)


def picture(name, w, h, cx=0.5, cy=0.5, zoom=1.0, lift=0.0):
    """A real photo cropped to a box, lightly graded; lift brightens a dark room a little."""
    im = O.grade(O.cover(O.photo(name), u(w), u(h), cx, cy, zoom))
    if lift:
        a = np.asarray(im, np.float32) / 255
        a = 1 - (1 - a) ** (1 + lift)
        im = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    return im.convert("RGBA")


def logo(width):
    lg = Image.open(ROOT / "brand" / "logo_hd.png").convert("RGBA")
    k = u(width) / lg.width
    return lg.resize((u(width), round(lg.height * k)), Image.LANCZOS)


def button(canvas, x, y, w, h, label, bg, fg, f):
    b = Image.new("RGBA", (u(w), u(h)), bg + (255,))
    b.putalpha(O.rounded(u(w), u(h), u(h / 2)))
    canvas.alpha_composite(b, (u(x), u(y)))
    ImageDraw.Draw(canvas).text((u(x + w / 2), u(y + h / 2)), label, font=f, fill=fg, anchor="mm")


# ---------- the six ----------
def s1(c):
    """Split: the stained-glass room above, the offer set large on warm white below. Manrope."""
    W, H = BASE
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    c.alpha_composite(picture("g02", W, 690, 0.55, 0.52, 1.28), (0, 0))
    O.logo_badge(c, 40, 40, 108)
    d = ImageDraw.Draw(c)
    x = 72
    t(d, x, 776, WHEN.upper(), face("Manrope", 21, 750), PURPLE, 2.6)
    t(d, x - 8, 960, PRICE, face("Manrope", 196, 800), INK, -7)
    t(d, x, 1032, MONTHS, face("Manrope", 54, 500), SOFT, -0.5)
    d.line((u(x), u(1082), u(W - x), u(1082)), fill=(226, 220, 212), width=u(2))
    t(d, x, 1140, PROMISE[0], face("Manrope", 33, 750), INK)
    t(d, x, 1184, PROMISE[1], face("Manrope", 33, 500), SOFT)
    t(d, x, 1282, PHONE, face("Manrope", 40, 800), PURPLE, -0.3)
    t(d, W - x, 1282, WEB, face("Manrope", 26, 600), SOFT, 0, "rs")


def s2(c):
    """Editorial: the forest-mural room fills the frame, white type sits in the shade at the bottom. Plus Jakarta Sans."""
    W, H = BASE
    c.alpha_composite(picture("IMG_7697", W, H, 0.55, 0.62, 1.3, lift=0.35), (0, 0))
    # a long, soft shade, like the light falling off in a photo, so the white type reads
    hgt = u(820)
    g = np.clip((np.arange(hgt) / hgt - 0.05) / 0.95, 0, 1) ** 1.35 * 0.86
    shade = Image.new("RGBA", (u(W), hgt), (12, 8, 16, 0))
    shade.putalpha(Image.fromarray((np.repeat(g[:, None], u(W), 1) * 255).astype(np.uint8), "L"))
    c.alpha_composite(shade, (0, u(H) - hgt))
    O.logo_badge(c, 44, 44, 108)
    d = ImageDraw.Draw(c)
    x = 72
    t(d, x, 870, WHEN, face("PlusJakartaSans", 25, 600), (236, 228, 244))
    t(d, x - 6, 1046, PRICE, face("PlusJakartaSans", 182, 800), WHITE, -6)
    t(d, x, 1112, MONTHS, face("PlusJakartaSans", 52, 500), (240, 236, 244))
    t(d, x, 1184, PROMISE[0], face("PlusJakartaSans", 30, 700), WHITE)
    t(d, x, 1224, PROMISE[1], face("PlusJakartaSans", 30, 450), (226, 220, 232))
    t(d, x, 1296, PHONE, face("PlusJakartaSans", 36, 750), WHITE)
    t(d, W - x, 1296, WEB, face("PlusJakartaSans", 25, 600), (226, 220, 232), 0, "rs")


def s3(c):
    """Brand colour: deep plum, one rounded photo of the rainbow over the yard, white type. Outfit."""
    W, H = BASE
    c.paste(PLUM + (255,), (0, 0, u(W), u(H)))
    O.paste_rounded(c, picture("IMG_7690", W - 112, 560, 0.47, 0.42, 1.25), u(56), u(56), u(30))
    O.logo_badge(c, 84, 84, 104)
    d = ImageDraw.Draw(c)
    x = 72
    t(d, x, 700, WHEN.upper(), face("Outfit", 22, 600), (206, 186, 226), 3)
    t(d, x - 6, 890, PRICE, face("Outfit", 208, 700), WHITE, -5)
    t(d, x, 962, MONTHS, face("Outfit", 56, 400), (222, 208, 236))
    t(d, x, 1052, PROMISE[0], face("Outfit", 34, 600), WHITE)
    t(d, x, 1098, PROMISE[1], face("Outfit", 34, 300), (222, 208, 236))
    button(c, x, 1176, 936, 104, f"Book a tour   {PHONE}", GOLD, PLUM, face("Outfit", 38, 600))
    t(d, W / 2, 1322, f"{WEB}  ·  {AGES}", face("Outfit", 21, 400), (190, 170, 210), 0.4, "ms")


def s4(c):
    """Swiss: white page, one huge line, a strip of three real photos. Inter Tight."""
    W, H = BASE
    c.paste(WHITE + (255,), (0, 0, u(W), u(H)))
    c.alpha_composite(logo(150), (u(64), u(56)))
    d = ImageDraw.Draw(c)
    f = O.sans
    t(d, W - 64, 96, "Christmas offer", f(24, 700), PURPLE, 0, "rs")
    t(d, W - 64, 128, "until December 24", f(24, 500), SOFT, 0, "rs")
    t(d, 54, 470, "$100", f(330, 820), INK, -14)
    t(d, 64, 552, "off " + MONTHS, f(62, 640), INK, -1.2)
    gap, top, h = 12, 610, 330
    w = (W - 128 - 2 * gap) / 3
    for i, (n, cx, cy, z) in enumerate([("g02", 0.6, 0.5, 1.6), ("IMG_7690", 0.44, 0.5, 1.6), ("g27", 0.45, 0.55, 1.3)]):
        O.paste_rounded(c, picture(n, w, h, cx, cy, z), u(64 + i * (w + gap)), u(top), u(16))
    t(d, 64, 1040, PROMISE[0], f(36, 700), INK, -0.3)
    t(d, 64, 1088, PROMISE[1], f(36, 450), SOFT, -0.3)
    d.line((u(64), u(1150), u(W - 64), u(1150)), fill=(230, 228, 234), width=u(2))
    t(d, 64, 1262, PHONE, f(58, 780), INK, -1)
    t(d, W - 64, 1226, WEB, f(26, 600), PURPLE, 0, "rs")
    t(d, W - 64, 1262, AGES, f(22, 500), SOFT, 0, "rs")


def s5(c):
    """Framed print: the photo hung with a wide cream border, the offer in a soft modern serif. Fraunces + DM Sans."""
    W, H = BASE
    c.paste((244, 239, 230, 255), (0, 0, u(W), u(H)))
    m = 64
    ph = picture("g27", W - 2 * m, 700, 0.48, 0.55, 1.12)
    O.shadow(c, Image.new("L", ph.size, 255), (u(m), u(m)), u(14), (0, u(6)), 0.16)
    c.alpha_composite(ph, (u(m), u(m)))
    d = ImageDraw.Draw(c)
    lg = logo(118)
    c.alpha_composite(lg, (u(W - m) - lg.width, u(800)))
    t(d, m, 836, WHEN, face("DMSans", 24, 600), PURPLE, 0.3)
    # Fraunces' f reaches over the next letter, so the second f is set a little apart from the first
    fp = face("Fraunces", 168, 560, opsz=144)
    w = t(d, m - 6, 1000, PRICE[:-1], fp, INK)
    d.text((u(m - 6) + w + u(10), u(1000)), PRICE[-1], font=fp, fill=INK, anchor="ls")
    t(d, m, 1066, MONTHS, face("DMSans", 50, 450), SOFT)
    t(d, m, 1150, PROMISE[0], face("DMSans", 31, 650), INK)
    t(d, m, 1192, PROMISE[1], face("DMSans", 31, 400), SOFT)
    t(d, m, 1282, PHONE, face("DMSans", 40, 750), INK, -0.3)
    t(d, W - m, 1282, f"{WEB}  ·  ages 1 to 12", face("DMSans", 24, 500), SOFT, 0, "rs")


def s6(c):
    """Centred, like a sign: the rainbow over the yard on top, everything centred and short below. Sora."""
    W, H = BASE
    c.paste(WHITE + (255,), (0, 0, u(W), u(H)))
    c.alpha_composite(picture("IMG_7690", W, 640, 0.47, 0.44, 1.0), (0, 0))
    lg = logo(150)
    tile = 176
    O.shadow(c, O.rounded(u(tile), u(tile), u(40)), (u(W / 2 - tile / 2), u(640 - tile / 2)), u(16), (0, u(6)), 0.2)
    tl = Image.new("RGBA", (u(tile), u(tile)), WHITE + (255,))
    tl.putalpha(O.rounded(u(tile), u(tile), u(40)))
    c.alpha_composite(tl, (u(W / 2 - tile / 2), u(640 - tile / 2)))
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(640) - lg.height // 2))
    d = ImageDraw.Draw(c)
    cx = W / 2
    t(d, cx, 790, WHEN.upper(), face("Sora", 20, 600), PURPLE, 3, "ms")
    t(d, cx, 930, PRICE, face("Sora", 150, 700), INK, -5, "ms")
    t(d, cx, 998, MONTHS, face("Sora", 48, 400), SOFT, -0.5, "ms")
    t(d, cx, 1080, PROMISE[0], face("Sora", 29, 600), INK, 0, "ms")
    t(d, cx, 1120, PROMISE[1], face("Sora", 29, 300), SOFT, 0, "ms")
    button(c, cx - 330, 1170, 660, 96, f"Book a tour  ·  {PHONE}", PURPLE, WHITE, face("Sora", 32, 600))
    t(d, cx, 1318, f"{WEB}  ·  {AGES}", face("Sora", 19, 400), SOFT, 0.4, "ms")


SAMPLES = [s1, s2, s3, s4, s5, s6]


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i - 1](c)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"offer_sample_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"offer_sample_{i}.jpg", flush=True)
    return out


def main():
    picks = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(range(1, len(SAMPLES) + 1))
    outs = [render(i) for i in picks]
    if len(outs) == len(SAMPLES):
        tw, th = 720, 900
        sheet = Image.new("RGB", (3 * tw + 4 * 30, 2 * th + 3 * 30 + 80), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 30, 700)
        for k, im in enumerate(outs):
            x, y = 30 + (k % 3) * (tw + 30), 30 + (k // 3) * (th + 70)
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 12), f"Sample {k + 1}", font=f, fill=INK)
        sheet.save(OUT / "offer_samples.jpg", quality=90)
        print("wrote", OUT / "offer_samples.jpg", flush=True)


if __name__ == "__main__":
    main()
