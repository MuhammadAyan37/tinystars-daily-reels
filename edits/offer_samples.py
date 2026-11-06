"""Eighteen simple, elegant takes on the Christmas offer, to choose from. Each reads in under five seconds, so the chosen one
can also go on the banner outside.

Every sample says the same few things, in this order of size: $100 off your first 2 months; not happy in the first
month? we'll refund your registration; the phone number; then the small print (the deadline, ages, the website). Each
uses a different modern typeface (Google Fonts, OFL) and a real photo from the daycare's Google page or Drive.

Samples 7 to 12 are photo grids: the kind of page Little Penguins runs (several real photos above, a calm panel
below), with the offer added, more of the daycare shown and captions on the photos.

Samples 13 to 18 put the promise first (not happy in the first month? we'll refund your registration), with the $100
off as a smaller line under it, and wear the logo's own colours: its deep purple, pink and gold, and its star.

Usage: python -I edits/offer_samples.py [1 2 3 ...]   (all eighteen when none is named)
  -> exports/offer_sample_<n>.jpg        1440 x 1800 (4:5)
  -> exports/offer_samples.jpg           samples 1 to 6 side by side, to compare
  -> exports/offer_samples_grids.jpg     samples 7 to 12
  -> exports/offer_samples_brand.jpg     samples 13 to 18
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


def face(name, size, wght, opsz=None, wdth=None):
    """A variable Google font at a weight (and, where it has them, an optical size to match and a width)."""
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), u(size))
    vals = []
    for a in f.get_variation_axes():
        n = a["name"].decode() if isinstance(a["name"], bytes) else str(a["name"])
        n = n.lower()
        if n == "weight":
            vals.append(wght)
        elif "optical" in n:
            vals.append(max(a["minimum"], min(a["maximum"], opsz or size)))
        elif n == "width":
            vals.append(wdth or a["default"])
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


# ---------- photo grids (7 to 12): Little Penguins' kind of page, with the offer, more of the place, and modern type ----
LABELS = {"g02": "Bright classrooms", "IMG_7690": "Turf play yard", "g21": "Indoor play gym", "IMG_8880_S": "Hands-on art",
          "g27": "Learning through play", "IMG_8824_F": "Birthday parties", "g31": "Ocean room", "g28": "Creative corner"}
CROPS = {"g02": (0.56, 0.52, 1.3), "IMG_7690": (0.45, 0.46, 1.25), "g21": (0.55, 0.56, 1.05), "IMG_8880_S": (0.36, 0.46, 1.7),
         "g27": (0.45, 0.55, 1.15), "IMG_8824_F": (0.5, 0.3, 1.45), "g31": (0.5, 0.55, 1.1), "g28": (0.55, 0.6, 1.15)}
LIFT = {}  # a little light for a dim room


def chip(c, x, y, label, size=18, star_col=None):
    """A small white label on a photo, like a caption in an app; optionally led by a little star in the logo's pink."""
    d = ImageDraw.Draw(c)
    f = O.sans(size, 620)
    icon = size * 0.95 if star_col else 0
    w = d.textlength(label, font=f) / O.S + size * 1.5 + (icon + size * 0.35 if star_col else 0)
    h = size * 2.0
    b = Image.new("RGBA", (u(w), u(h)), (255, 255, 255, 255))
    b.putalpha(Image.fromarray((np.asarray(O.rounded(u(w), u(h), u(h / 2)), np.float32) * 0.93).astype(np.uint8)))
    c.alpha_composite(b, (u(x), u(y)))
    if not star_col:
        d.text((u(x + w / 2), u(y + h / 2)), label, font=f, fill=INK, anchor="mm")
        return
    sm = star(icon, 0.5)
    c.paste(star_col + (255,), (u(x + size * 0.7), u(y + h / 2 - icon / 2) - u(1)), sm)
    d.text((u(x + size * 0.7 + icon + size * 0.35), u(y + h / 2)), label, font=f, fill=INK, anchor="lm")


def tile(c, name, x, y, w, h, r=0, label=True, shape="round", star=None):
    """One real photo in its cell of the grid, with its caption."""
    cx, cy, z = CROPS[name]
    im = picture(name, w, h, cx, cy, z, lift=LIFT.get(name, 0))
    if shape == "arch":  # a rounded top, like a window
        m = Image.new("L", im.size, 0)
        dm = ImageDraw.Draw(m)
        rad = im.width // 2
        dm.ellipse((0, 0, im.width - 1, 2 * rad), fill=255)
        dm.rectangle((0, rad, im.width - 1, im.height - 1), fill=255)
        im.putalpha(m)
        c.alpha_composite(im, (u(x), u(y)))
    elif r:
        O.paste_rounded(c, im, u(x), u(y), u(r))
    else:
        c.alpha_composite(im, (u(x), u(y)))
    if label and name in LABELS:
        chip(c, x + 14, y + h - 14 - 36, LABELS[name], star_col=star)


def promise_line(d, cx, y, f_bold, f_light, ink, soft, anchor="ms"):
    """The promise on one line, the question in bold: Not happy in the first month? We'll refund your registration."""
    a, b = PROMISE[0] + " ", PROMISE[1]
    wa, wb = d.textlength(a, font=f_bold) / O.S, d.textlength(b, font=f_light) / O.S
    x = cx - (wa + wb) / 2 if anchor[0] == "m" else cx
    t(d, x, y, a, f_bold, ink)
    t(d, x + wa, y, b, f_light, soft)


def s7(c):
    """Little Penguins' layout, done better: six real photos with captions, then the offer on a calm page. Plus Jakarta Sans."""
    W, H = BASE
    g = 6
    c.paste(WHITE + (255,), (0, 0, u(W), u(H)))
    tile(c, "g02", 0, 0, 712, 474)
    tile(c, "IMG_7690", 712 + g, 0, W - 712 - g, 234)
    tile(c, "g21", 712 + g, 234 + g, W - 712 - g, 474 - 234 - g)
    w3 = (W - 2 * g) / 3
    for i, n in enumerate(["IMG_8880_S", "g27", "IMG_8824_F"]):
        tile(c, n, i * (w3 + g), 474 + g, w3, 240)
    c.paste((249, 245, 239, 255), (0, u(720), u(W), u(H)))
    lg = logo(132)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(748)))
    d = ImageDraw.Draw(c)
    J = "PlusJakartaSans"
    t(d, W / 2, 922, WHEN.upper(), face(J, 19, 700), PURPLE, 3, "ms")
    t(d, W / 2, 1040, PRICE, face(J, 124, 800), INK, -4, "ms")
    t(d, W / 2, 1100, MONTHS, face(J, 46, 500), SOFT, -0.3, "ms")
    promise_line(d, W / 2, 1160, face(J, 25, 700), face(J, 25, 450), INK, SOFT)
    button(c, W / 2 - 290, 1196, 580, 84, f"Book a tour  ·  {PHONE}", PURPLE, WHITE, face(J, 30, 650))
    t(d, W / 2, 1326, f"{WEB}  ·  {AGES}", face(J, 19, 500), SOFT, 0.3, "ms")


def s8(c):
    """Bento: photos and the offer share one grid of rounded tiles, the way modern product pages are laid out. Outfit."""
    W, H = BASE
    c.paste((242, 239, 235, 255), (0, 0, u(W), u(H)))
    r = 26

    def block(x, y, w, h, col):
        b = Image.new("RGBA", (u(w), u(h)), col + (255,))
        b.putalpha(O.rounded(u(w), u(h), u(r)))
        c.alpha_composite(b, (u(x), u(y)))

    tile(c, "g02", 28, 28, 678, 520, r)
    tile(c, "IMG_7690", 720, 28, 332, 253, r)
    tile(c, "IMG_8880_S", 720, 295, 332, 253, r)
    tile(c, "g21", 720, 562, 332, 203, r)
    tile(c, "g27", 720, 779, 332, 203, r, label=False)
    d = ImageDraw.Draw(c)
    block(28, 562, 678, 420, PLUM)
    t(d, 72, 630, WHEN.upper(), face("Outfit", 20, 600), (206, 186, 226), 2.6)
    t(d, 66, 806, PRICE, face("Outfit", 156, 700), WHITE, -4)
    t(d, 72, 880, MONTHS, face("Outfit", 54, 400), (222, 208, 236))
    block(28, 996, 520, 326, WHITE)
    lg = logo(96)
    c.alpha_composite(lg, (u(64), u(1024)))
    t(d, 64, 1214, PROMISE[0], face("Outfit", 31, 600), INK)
    t(d, 64, 1256, PROMISE[1], face("Outfit", 31, 300), SOFT)
    block(562, 996, 490, 326, GOLD)
    t(d, 600, 1080, "Book a tour", face("Outfit", 42, 600), PLUM)
    O.arrow(d, u(600 + 238), u(1066), u(36), PLUM, u(4))
    t(d, 600, 1206, PHONE, face("Outfit", 54, 700), PLUM, -0.5)
    t(d, 600, 1262, f"{WEB}  ·  ages 1 to 12", face("Outfit", 22, 400), (96, 66, 40))


def s9(c):
    """Band: a row of photos, the offer across the middle, another row of photos. Sora."""
    W, H = BASE
    g = 6
    w3 = (W - 2 * g) / 3
    c.paste(WHITE + (255,), (0, 0, u(W), u(H)))
    for i, n in enumerate(["g02", "IMG_7690", "g21"]):
        tile(c, n, i * (w3 + g), 0, w3, 440, label=i != 1)  # the logo sits where the middle caption would be
    for i, n in enumerate(["IMG_8880_S", "g27", "IMG_8824_F"]):
        tile(c, n, i * (w3 + g), 930, w3, 420)
    c.paste(PURPLE + (255,), (0, u(446), u(W), u(924)))
    tsize = 116
    tl = Image.new("RGBA", (u(tsize), u(tsize)), WHITE + (255,))
    tl.putalpha(O.rounded(u(tsize), u(tsize), u(28)))
    O.shadow(c, tl.getchannel("A"), (u(W / 2 - tsize / 2), u(388)), u(14), (0, u(5)), 0.25)
    c.alpha_composite(tl, (u(W / 2 - tsize / 2), u(388)))
    lg = logo(98)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(388 + tsize / 2) - lg.height // 2))
    d = ImageDraw.Draw(c)
    t(d, W / 2, 560, WHEN.upper(), face("Sora", 18, 600), (214, 196, 232), 3, "ms")
    t(d, W / 2, 694, PRICE, face("Sora", 136, 700), WHITE, -4, "ms")
    t(d, W / 2, 750, MONTHS, face("Sora", 42, 400), (226, 214, 238), -0.3, "ms")
    promise_line(d, W / 2, 806, face("Sora", 24, 600), face("Sora", 24, 300), WHITE, (226, 214, 238))
    button(c, W / 2 - 300, 834, 600, 70, f"Book a tour  ·  {PHONE}", GOLD, PLUM, face("Sora", 27, 600))


def s10(c):
    """Arches: three photos in arched frames on a warm page, the offer set below in a soft serif. Fraunces + DM Sans."""
    W, H = BASE
    c.paste((246, 240, 231, 255), (0, 0, u(W), u(H)))
    w, gap = 296, 28
    x0 = (W - 3 * w - 2 * gap) / 2
    for i, (n, top) in enumerate([("IMG_7690", 150), ("g02", 80), ("g27", 150)]):
        x = x0 + i * (w + gap)
        tile(c, n, x, top, w, 620 - top, shape="arch", label=False)
    lg = logo(96)
    c.alpha_composite(lg, (u(36), u(28)))
    d = ImageDraw.Draw(c)
    t(d, W / 2, 704, "Bright classrooms  ·  Turf play yard  ·  Learning through play", face("DMSans", 21, 500), SOFT, 0.2, "ms")
    t(d, W / 2, 790, WHEN.upper(), face("DMSans", 19, 700), PURPLE, 3, "ms")
    fp = face("Fraunces", 150, 560, opsz=144)
    a = PRICE[:-1]
    wa = d.textlength(a, font=fp)
    wf = d.textlength("f", font=fp)
    x = u(W / 2) - (wa + u(8) + wf) / 2
    d.text((x, u(940)), a, font=fp, fill=INK, anchor="ls")
    d.text((x + wa + u(8), u(940)), "f", font=fp, fill=INK, anchor="ls")  # the second f set apart, so they don't touch
    t(d, W / 2, 1004, MONTHS, face("DMSans", 46, 450), SOFT, 0, "ms")
    promise_line(d, W / 2, 1068, face("DMSans", 25, 650), face("DMSans", 25, 400), INK, SOFT)
    button(c, W / 2 - 290, 1110, 580, 84, f"Book a tour  ·  {PHONE}", PLUM, WHITE, face("DMSans", 30, 600))
    t(d, W / 2, 1270, f"{WEB}  ·  {AGES}", face("DMSans", 20, 500), SOFT, 0.3, "ms")


def s11(c):
    """Magazine: one big photo, a strip of four more laid over its edge, the offer left-aligned below. Manrope."""
    W, H = BASE
    c.paste((250, 248, 244, 255), (0, 0, u(W), u(H)))
    tile(c, "g02", 0, 0, W, 660, label=False)
    O.logo_badge(c, 40, 40, 108)
    m, gap = 40, 16
    w = (W - 2 * m - 3 * gap) / 4
    d = ImageDraw.Draw(c)
    for i, n in enumerate(["IMG_7690", "g21", "IMG_8880_S", "IMG_8824_F"]):
        x = m + i * (w + gap)
        frame = Image.new("RGBA", (u(w + 12), u(212)), WHITE + (255,))
        frame.putalpha(O.rounded(u(w + 12), u(212), u(22)))
        O.shadow(c, frame.getchannel("A"), (u(x - 6), u(574)), u(16), (0, u(6)), 0.2)
        c.alpha_composite(frame, (u(x - 6), u(574)))
        tile(c, n, x, 580, w, 200, 18, label=False)
        t(d, x + w / 2, 818, LABELS[n].upper(), face("Manrope", 16, 750), SOFT, 1.6, "ms")
    x = 56
    t(d, x, 896, WHEN.upper(), face("Manrope", 20, 750), PURPLE, 2.6)
    t(d, x - 8, 1062, PRICE, face("Manrope", 172, 800), INK, -7)
    t(d, x, 1122, MONTHS, face("Manrope", 48, 500), SOFT, -0.4)
    promise_line(d, x, 1180, face("Manrope", 26, 750), face("Manrope", 26, 500), INK, SOFT, "ls")
    button(c, x, 1222, 390, 84, "Book a tour", PURPLE, WHITE, face("Manrope", 30, 700))
    t(d, x + 420, 1264, PHONE, face("Manrope", 38, 800), INK, -0.3)
    t(d, x + 420, 1298, f"{WEB}  ·  ages 1 to 12", face("Manrope", 19, 500), SOFT)


def s12(c):
    """Sidebar: four photos stacked down the left, the offer in a tall column on the right. DM Sans."""
    W, H = BASE
    c.paste((249, 246, 240, 255), (0, 0, u(W), u(H)))
    g, cw = 6, 400
    h = (H - 3 * g) / 4
    for i, n in enumerate(["IMG_7690", "g21", "IMG_8880_S", "g27"]):
        tile(c, n, 0, i * (h + g), cw, h)
    x = cw + 56
    lg = logo(128)
    c.alpha_composite(lg, (u(x), u(56)))
    d = ImageDraw.Draw(c)
    t(d, x, 290, "CHRISTMAS OFFER", face("DMSans", 21, 700), PURPLE, 3)
    t(d, x, 322, "UNTIL DECEMBER 24", face("DMSans", 21, 500), PURPLE, 3)
    fb = face("DMSans", 236, 800, opsz=40)
    t(d, x - 10, 560, "$100", fb, INK, -9)
    t(d, x - 8, 750, "off", fb, INK, -9)
    t(d, x, 830, "your first", face("DMSans", 52, 450), SOFT)
    t(d, x, 892, "2 months", face("DMSans", 52, 450), SOFT)
    t(d, x, 992, PROMISE[0], face("DMSans", 28, 650), INK)
    t(d, x, 1032, PROMISE[1], face("DMSans", 28, 400), SOFT)
    button(c, x, 1090, W - x - 56, 84, "Book a tour", PLUM, WHITE, face("DMSans", 30, 600))
    t(d, x, 1262, PHONE, face("DMSans", 46, 750), INK, -0.4)
    t(d, x, 1304, f"{WEB}  ·  ages 1 to 12", face("DMSans", 20, 500), SOFT)


# ---------- on-brand (13 to 18): the promise first, in the logo's own deep purple, pink and gold ----------------------
NIGHT = (30, 8, 60)
INDIGO = (60, 14, 108)
MAGENTA = (228, 58, 132)
SUN = (252, 182, 84)
LILAC = (216, 198, 240)
Q = PROMISE[0]
A2 = ["We'll refund your", "registration."]
EXTRA = "Plus $100 off your first 2 months"
LOGO_RAMP = [(0.0, SUN), (0.5, MAGENTA), (1.0, INDIGO)]  # the gold-to-pink-to-purple running through the logo's letters
PINK_RAMP = [(0.0, MAGENTA), (1.0, INDIGO)]
# the newest photos: the class painting (faces blurred), the block city with its smiley chairs, the rocket playroom
LABELS.update({"IMG_8598": "Hands-on art", "IMG_8711": "Block city", "IMG_8707": "Rocket playroom"})
CROPS.update({"IMG_8598": (0.45, 0.36, 1.9), "IMG_8711": (0.45, 0.68, 1.15), "IMG_8707": (0.6, 0.56, 1.12)})
LIFT.update({"IMG_8598": 0.22})


def put(c, im, x, y):
    """alpha_composite that also takes a layer hanging off the edge of the canvas."""
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(im.width, c.width - x), min(im.height, c.height - y)
    if x1 > x0 and y1 > y0:
        c.alpha_composite(im.crop((x0, y0, x1, y1)), (x + x0, y + y0))


def ramp(w, h, stops, angle=90.0):
    """A smooth colour ramp over w x h pixels (90 runs top to bottom, 0 left to right), dithered so it never bands."""
    th = np.deg2rad(angle)
    p = np.arange(w, dtype=np.float32)[None, :] * np.cos(th) + np.arange(h, dtype=np.float32)[:, None] * np.sin(th)
    p = (p - p.min()) / max(1e-6, float(p.max() - p.min()))
    rng = np.random.default_rng(7)
    out = np.empty((h, w, 3), np.float32)
    for k in range(3):
        out[..., k] = np.interp(p, [s[0] for s in stops], [s[1][k] for s in stops]) + rng.random((h, w), np.float32) - 0.5
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")


def glow(c, cx, cy, r, col, opacity):
    """A soft pool of coloured light, the way the logo's neon would light a wall."""
    n = u(2 * r)
    yy, xx = np.ogrid[0:n, 0:n]
    dist = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    a = np.exp(-4 * dist ** 2) * opacity * 255 + np.random.default_rng(3).random((n, n)) - 0.5
    layer = Image.new("RGBA", (n, n), col + (0,))
    layer.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    put(c, layer, u(cx - r), u(cy - r))


def star(size, inner=0.5, turn=0.0):
    """The logo's chubby five-point star with softly rounded points, as a mask."""
    n = max(4, u(size))
    big = n / 2 * 0.985
    pts = []
    for k in range(10):
        a = -np.pi / 2 + k * np.pi / 5 + np.deg2rad(turn)
        r = big if k % 2 == 0 else big * inner
        pts.append((n / 2 + r * np.cos(a), n / 2 + r * np.sin(a)))
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(n * 0.045)).point(lambda v: 255 if v >= 128 else 0)


def sparkle(c, cx, cy, size, col):
    """A four-point twinkle like the ones around the logo."""
    n = u(size)
    k, w = n / 2, n * 0.12
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).polygon([(k, 0), (k + w, k - w), (n, k), (k + w, k + w), (k, n), (k - w, k + w), (0, k),
                               (k - w, k - w)], fill=255)
    lay = Image.new("RGBA", (n, n), col + (255,))
    lay.putalpha(m)
    c.alpha_composite(lay, (u(cx) - n // 2, u(cy) - n // 2))


def fit(name, lines, max_w, size, wght, track=0.0, **kw):
    """The biggest size, up to `size`, at which every line fits in max_w."""
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    while True:
        f = face(name, size, wght, **kw)
        if max(O.width(d, s, f, track) for s in lines) / O.S <= max_w or size <= 12:
            return f
        size -= 2


def stack(d, x, y, lines, f, fill, lead, track=0.0, anchor="ls"):
    for k, s in enumerate(lines):
        t(d, x, y + k * lead, s, f, fill, track, anchor)


def accent(c, x, y, s, word, f, fill, word_fill, track=0.0, anchor="ls", marker=None):
    """A line of type with one word picked out: in its own colour, or over a stroke of highlighter."""
    d = ImageDraw.Draw(c)
    i = s.index(word)
    pre, post = s[:i], s[i + len(word):]
    wp = O.width(d, pre, f, track) / O.S if pre else 0
    ww = O.width(d, word, f, track) / O.S
    if anchor[0] == "m":
        x -= O.width(d, s, f, track) / O.S / 2
    sz = f.size / O.S
    if marker:
        hl = Image.new("RGBA", (u(ww + 0.16 * sz), u(0.44 * sz)), marker + (255,))
        hl.putalpha(O.rounded(hl.width, hl.height, u(0.1 * sz)))
        c.alpha_composite(hl.rotate(-1.2, Image.BICUBIC, expand=True, fillcolor=marker + (0,)),
                          (u(x + wp + track - 0.08 * sz), u(y - 0.36 * sz)))
    t(d, x, y, pre, f, fill, track)
    t(d, x + wp + track, y, word, f, word_fill, track)
    t(d, x + wp + ww + 2 * track, y, post, f, fill, track)


def ramp_text(c, x, y, lines, f, stops, lead=0, track=0.0, anchor="ls"):
    """Type filled with a colour ramp, like the lettering of the logo."""
    m = Image.new("L", c.size, 0)
    stack(ImageDraw.Draw(m), x, y, lines, f, 255, lead, track, anchor)
    bb = m.getbbox()
    g = ramp(bb[2] - bb[0], bb[3] - bb[1], stops, 0)
    g.putalpha(m.crop(bb))
    c.alpha_composite(g, bb[:2])


def ramp_button(c, x, y, w, h, label, stops, fg, f):
    b = ramp(u(w), u(h), stops, 0)
    b.putalpha(O.rounded(u(w), u(h), u(h / 2)))
    O.shadow(c, b.getchannel("A"), (u(x), u(y)), u(12), (0, u(6)), 0.22)
    c.alpha_composite(b, (u(x), u(y)))
    ImageDraw.Draw(c).text((u(x + w / 2), u(y + h / 2)), label, font=f, fill=fg, anchor="mm")


def panel(c, x, y, w, h, r, col, lift=0.18):
    b = Image.new("RGBA", (u(w), u(h)), col + (255,))
    b.putalpha(O.rounded(u(w), u(h), u(r)))
    if lift:
        O.shadow(c, b.getchannel("A"), (u(x), u(y)), u(18), (0, u(8)), lift)
    c.alpha_composite(b, (u(x), u(y)))


def glass(c, x, y, w, h, r, alpha=0.8, blur=24, ring=None):
    """Frosted glass: the photo behind, blurred and washed with white; optionally edged in the logo's colours."""
    box = (u(x), u(y), u(x) + u(w), u(y) + u(h))
    pane = c.crop(box).filter(ImageFilter.GaussianBlur(u(blur)))
    pane.alpha_composite(Image.new("RGBA", pane.size, (255, 255, 255, round(255 * alpha))))
    m = O.rounded(pane.width, pane.height, u(r))
    O.shadow(c, m, box[:2], u(20), (0, u(10)), 0.28)
    if ring:
        bw = u(ring[0])
        g = ramp(pane.width + 2 * bw, pane.height + 2 * bw, ring[1], 0)
        g.putalpha(O.rounded(g.width, g.height, u(r) + bw))
        c.alpha_composite(g, (box[0] - bw, box[1] - bw))
    pane.putalpha(m)
    c.alpha_composite(pane, box[:2])


def bubble(c, x, y, w, h, fill, corner):
    """A message bubble, one bottom corner squared off on the side of whoever is speaking."""
    r = 40
    b = ramp(u(w), u(h), fill, 0) if isinstance(fill, list) else Image.new("RGBA", (u(w), u(h)), fill + (255,))
    m = O.rounded(u(w), u(h), u(r))
    sq = (0, u(h - r), u(r), u(h) - 1) if corner == "left" else (u(w - r), u(h - r), u(w) - 1, u(h) - 1)
    ImageDraw.Draw(m).rounded_rectangle(sq, u(8), fill=255)
    b.putalpha(m)
    O.shadow(c, m, (u(x), u(y)), u(12), (0, u(6)), 0.12)
    c.alpha_composite(b, (u(x), u(y)))


def die_cut(shape, fill, edge=5):
    """A sticker: the shape in a colour, on a white die-cut border, on a clear layer."""
    pad = u(edge * 3)
    full = Image.new("L", (shape.width + 2 * pad, shape.height + 2 * pad), 0)
    full.paste(shape, (pad, pad))
    rim = full.filter(ImageFilter.GaussianBlur(u(edge))).point(lambda v: 255 if v >= 8 else 0)
    layer = Image.new("RGBA", full.size, (255, 255, 255, 0))
    layer.paste(WHITE + (255,), (0, 0) + full.size, rim)
    layer.paste(fill + (255,), (0, 0) + full.size, full)
    return layer


def stick(c, layer, cx, cy, turn):
    layer = layer.rotate(turn, Image.BICUBIC, expand=True, fillcolor=(255, 255, 255, 0))
    xy = (u(cx) - layer.width // 2, u(cy) - layer.height // 2)
    O.shadow(c, layer.getchannel("A"), xy, u(12), (0, u(7)), 0.3)
    put(c, layer, *xy)


def sticker(c, cx, cy, size, lines, turn, fill=MAGENTA, inner=0.56):
    """The logo's star as a sticker, turned a little, with a few words on it."""
    layer = die_cut(star(size, inner), fill)
    d = ImageDraw.Draw(layer)
    for s, dy, f in lines:
        d.text((layer.width / 2, layer.height / 2 + u(dy)), s, font=f, fill=WHITE, anchor="ms")
    stick(c, layer, cx, cy, turn)


def pill_sticker(c, cx, cy, s, f, fill, fg, turn, h=58):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = d.textlength(s, font=f) / O.S + 56
    layer = die_cut(O.rounded(u(w), u(h), u(h / 2)), fill)
    ImageDraw.Draw(layer).text((layer.width / 2, layer.height / 2), s, font=f, fill=fg, anchor="mm")
    stick(c, layer, cx, cy, turn)


def card(c, name, cx, cy, w, h, turn, border=10, r=20, rim=None):
    """A real photo printed with a white edge (or a colour-ramp frame, rim) and its caption, turned a little and laid
    on the page."""
    ph = picture(name, w, h, *CROPS[name], lift=LIFT.get(name, 0))
    ph.putalpha(O.rounded(ph.width, ph.height, u(r)))
    bw = u(border)
    full = Image.new("RGBA", (ph.width + 2 * bw, ph.height + 2 * bw), (255, 255, 255, 0))
    edge = ramp(full.width, full.height, rim, 45) if rim else Image.new("RGBA", full.size, WHITE + (255,))
    full.paste(edge, (0, 0), O.rounded(full.width, full.height, u(r) + bw))
    full.alpha_composite(ph, (bw, bw))
    chip(full, border + 14, border + h - 50, LABELS[name], star_col=MAGENTA)
    full = full.rotate(turn, Image.BICUBIC, expand=True, fillcolor=(255, 255, 255, 0))
    xy = (u(cx) - full.width // 2, u(cy) - full.height // 2)
    O.shadow(c, full.getchannel("A"), xy, u(18), (0, u(12)), 0.24)
    put(c, full, *xy)


def s13(c):
    """Photo dump: three real photos laid down as prints on soft lilac, a star sticker, and the promise large with
    'refund' run over in gold highlighter. Bricolage Grotesque."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, ramp(u(W), u(H), [(0, (240, 231, 253)), (1, (253, 236, 244))], 100), 0, 0)
    c.alpha_composite(logo(112), (u(40), u(28)))
    pill_sticker(c, 452, 88, "Christmas offer  ·  until Dec 24", face(B, 24, 650), INDIGO, WHITE, -3)
    card(c, "IMG_8598", 392, 456, 590, 428, -3)
    card(c, "IMG_8711", 846, 344, 312, 376, 6)
    card(c, "IMG_8707", 838, 654, 340, 232, -5)
    sticker(c, 962, 158, 250, [("NOW", -4, face(B, 46, 800, wdth=75)), ("ENROLLING", 28, face(B, 25, 800, wdth=75))],
            12, inner=0.6)
    d = ImageDraw.Draw(c)
    t(d, 56, 870, Q, face(B, 46, 500), (104, 66, 146), -0.4)
    f = fit(B, A2, 940, 116, 800, -3)
    accent(c, 50, 980, A2[0], "refund", f, INDIGO, INDIGO, -3, marker=(255, 200, 92))
    t(d, 50, 1082, A2[1], f, INDIGO, -3)
    w2 = O.width(d, A2[1], f, -3) / O.S
    sparkle(c, 50 + w2 + 40, 1030, 46, MAGENTA)
    sparkle(c, 50 + w2 + 82, 1074, 26, SUN)
    t(d, 56, 1150, EXTRA, face(B, 34, 700), MAGENTA, -0.3)
    ramp_button(c, 56, 1184, 620, 90, f"Book a tour  ·  {PHONE}", PINK_RAMP, WHITE, face(B, 31, 650))
    t(d, 56, 1320, f"{WEB}  ·  {AGES}", face(B, 19, 450), SOFT)


def s14(c):
    """Sunset: the logo's purple-pink-gold as the whole page, the promise in white with 'refund' in gold, three photos,
    a white card. Bricolage Grotesque."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, ramp(u(W), u(H), [(0, INDIGO), (0.55, MAGENTA), (1, SUN)], 100), 0, 0)
    c.alpha_composite(logo(120), (u(48), u(40)))
    d = ImageDraw.Draw(c)
    t(d, W - 52, 92, "Christmas offer", face(B, 28, 700), WHITE, 0, "rs")
    t(d, W - 52, 126, "until December 24", face(B, 28, 400), LILAC, 0, "rs")
    t(d, 52, 266, Q, face(B, 54, 500), (242, 230, 250), -0.5)
    f = fit(B, A2, 980, 124, 800, -3)
    accent(c, 46, 382, A2[0], "refund", f, WHITE, SUN, -3)
    t(d, 46, 494, A2[1], f, WHITE, -3)
    gap = 16
    w = (W - 96 - 2 * gap) / 3
    for i, n in enumerate(["IMG_8598", "IMG_8711", "IMG_7690"]):
        tile(c, n, 48 + i * (w + gap), 552, w, 356, 26, star=MAGENTA)
    panel(c, 48, 934, W - 96, 368, 34, WHITE)
    d = ImageDraw.Draw(c)
    t(d, 88, 1012, EXTRA, face(B, 42, 750), INK, -0.4)
    t(d, 88, 1054, AGES, face(B, 27, 450), SOFT)
    d.line((u(88), u(1092), u(W - 88), u(1092)), fill=(232, 226, 236), width=u(2))
    button(c, 88, 1126, 360, 88, "Book a tour", INDIGO, WHITE, face(B, 32, 650))
    t(d, W - 88, 1186, PHONE, face(B, 52, 800), INDIGO, -0.5, "rs")
    t(d, 88, 1264, WEB, face(B, 24, 500), SOFT)


def s15(c):
    """Chat: the question a parent has and Tiny Stars' answer as two message bubbles, under four photos. Manrope."""
    W, H = BASE
    M = "Manrope"
    put(c, ramp(u(W), u(H), [(0, (246, 240, 253)), (1, (253, 238, 246))], 90), 0, 0)
    g = 6
    w2, h2 = (W - g) / 2, 262
    for k, n in enumerate(["IMG_8598", "IMG_8711", "IMG_8707", "IMG_7690"]):
        tile(c, n, (k % 2) * (w2 + g), (k // 2) * (h2 + g), w2, h2, star=MAGENTA)
    c.alpha_composite(logo(112), (u(26), u(22)))
    d = ImageDraw.Draw(c)
    x = 56
    t(d, x, 604, WHEN.upper(), face(M, 19, 750), MAGENTA, 2.6)
    t(d, x + 6, 664, "You", face(M, 20, 650), SOFT)
    fq = face(M, 42, 650)
    qw = O.width(d, Q, fq) / O.S + 80
    bubble(c, x, 680, qw, 104, WHITE, "left")
    d.text((u(x + 40), u(680 + 52)), Q, font=fq, fill=INK, anchor="lm")
    fa = face(M, 62, 800)
    aw = max(O.width(d, s, fa, -1) for s in A2) / O.S + 92
    ax = W - x - aw
    t(d, W - x - 6, 838, "Tiny Stars", face(M, 20, 650), SOFT, 0, "rs")
    bubble(c, ax, 854, aw, 196, PINK_RAMP, "right")
    stack(d, ax + 46, 854 + 86, A2, fa, WHITE, 74, -1)
    # a reaction on the answer, the way people tap one on a message they like
    react = die_cut(Image.new("L", (u(58), u(58)), 0), WHITE, 1)
    rd = ImageDraw.Draw(react)
    rd.ellipse((0, 0, react.width - 1, react.height - 1), fill=WHITE + (255,))
    sm = star(34, 0.5)
    react.paste(MAGENTA + (255,), ((react.width - sm.width) // 2, (react.height - sm.height) // 2 + u(1)), sm)
    stick(c, react, ax + 6, 854 + 4, 0)
    t(d, x, 1124, EXTRA, face(M, 34, 750), INDIGO, -0.3)
    button(c, x, 1160, 360, 86, "Book a tour", INDIGO, WHITE, face(M, 31, 700))
    t(d, x + 390, 1218, PHONE, face(M, 44, 800), INK, -0.3)
    t(d, x, 1310, f"{WEB}  ·  {AGES}", face(M, 19, 550), SOFT)


def s16(c):
    """Night: six captioned photos, the promise lit in the logo's gold-to-pink, on deep night purple. Sora."""
    W, H = BASE
    S_ = "Sora"
    c.paste(NIGHT + (255,), (0, 0, u(W), u(H)))
    glow(c, W / 2, 930, 640, MAGENTA, 0.30)
    m, g, h = 36, 12, 248
    w = (W - 2 * m - 2 * g) / 3
    for k, n in enumerate(["IMG_8598", "IMG_8711", "IMG_7690", "IMG_8707", "g02", "IMG_8824_F"]):
        tile(c, n, m + (k % 3) * (w + g), m + (k // 3) * (h + g), w, h, 22, label=k != 4, star=MAGENTA)
    lg = logo(146)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(m + 2 * h + g) - lg.height // 2 + u(8)))
    d = ImageDraw.Draw(c)
    t(d, W / 2, 716, WHEN.upper(), face(S_, 18, 600), LILAC, 3, "ms")
    t(d, W / 2, 790, Q, face(S_, 42, 400), WHITE, -0.5, "ms")
    ramp_text(c, W / 2, 902, A2, fit(S_, A2, 990, 100, 800, -4), [(0, SUN), (1, MAGENTA)], 106, -4, "ms")
    t(d, W / 2, 1076, EXTRA, face(S_, 30, 500), LILAC, 0, "ms")
    button(c, W / 2 - 320, 1118, 640, 94, f"Book a tour  ·  {PHONE}", WHITE, NIGHT, face(S_, 30, 600))
    t(d, W / 2, 1306, f"{WEB}  ·  {AGES}", face(S_, 18, 400), (170, 150, 200), 0.3, "ms")


def s17(c):
    """Sticker wall: real photos edge to edge with the logo's star stuck on them, the promise large below with 'refund'
    in highlighter. Bricolage Grotesque."""
    W, H = BASE
    B = "BricolageGrotesque"
    c.paste(WHITE + (255,), (0, 0, u(W), u(H)))
    g = 6
    tile(c, "IMG_8598", 0, 0, 640, 360, star=MAGENTA)
    tile(c, "IMG_7690", 640 + g, 0, W - 640 - g, 360, star=MAGENTA)
    w3 = (W - 2 * g) / 3
    for i, n in enumerate(["IMG_8711", "IMG_8707", "g27"]):
        tile(c, n, i * (w3 + g), 360 + g, w3, 330, label=i != 2, star=MAGENTA)
    sticker(c, 846, 676, 420, [("CHRISTMAS", -34, face(B, 40, 800, wdth=75)), ("OFFER", 36, face(B, 74, 800, wdth=75)),
                               ("until Dec 24", 80, face(B, 28, 500))], 8)
    c.alpha_composite(logo(108), (u(48), u(722)))
    d = ImageDraw.Draw(c)
    t(d, 52, 904, Q, face(B, 46, 500), SOFT, -0.5)
    f = fit(B, A2, 980, 110, 800, -3)
    accent(c, 46, 1008, A2[0], "refund", f, INDIGO, INDIGO, -3, marker=(255, 200, 92))
    t(d, 46, 1108, A2[1], f, INDIGO, -3)
    t(d, 52, 1170, EXTRA, face(B, 34, 700), MAGENTA, -0.3)
    button(c, 52, 1204, 360, 86, "Book a tour", INDIGO, WHITE, face(B, 32, 650))
    t(d, 440, 1262, PHONE, face(B, 48, 800), INK, -0.5)
    t(d, 52, 1330, f"{WEB}  ·  {AGES}", face(B, 19, 450), SOFT)


ORANGE = (246, 124, 52)
LETTERING = [(0.0, (255, 216, 96)), (0.5, (250, 150, 62)), (1.0, (236, 72, 140))]  # the logo's letters, top to bottom


def logo_type(c, x, y, lines, f, lead, stroke=5, anchor="ms"):
    """Chunky lettering drawn the way the logo is: a gold-to-pink fill, a deep purple outline and a drop shadow."""
    sw = u(stroke)
    for k, s in enumerate(lines):
        masks = []
        for w in (sw, 0):
            m = Image.new("L", c.size, 0)
            ImageDraw.Draw(m).text((u(x), u(y + k * lead)), s, font=f, fill=255, anchor=anchor, stroke_width=w,
                                   stroke_fill=255)
            masks.append(m)
        out, inner = masks
        bb = out.getbbox()
        size = (bb[2] - bb[0], bb[3] - bb[1])
        for col, dy in (((40, 8, 74), u(7)), (INDIGO, 0)):
            lay = Image.new("RGBA", size, col + (255,))
            lay.putalpha(out.crop(bb))
            put(c, lay, bb[0], bb[1] + dy)
        g = ramp(size[0], size[1], LETTERING, 90)
        g.putalpha(inner.crop(bb))
        c.alpha_composite(g, bb[:2])


def icon(c, cx, cy, size, col, kind):
    """A round contact icon: an envelope or a map pin, white on a colour."""
    n = u(size)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    dr.ellipse((0, 0, n - 1, n - 1), fill=col + (255,))
    if kind == "mail":
        w, h = n * 0.52, n * 0.36
        x0, y0 = (n - w) / 2, (n - h) / 2
        dr.rounded_rectangle((x0, y0, x0 + w, y0 + h), n * 0.05, fill=WHITE + (255,))
        dr.line((x0 + n * 0.04, y0 + n * 0.05, n / 2, y0 + h * 0.6, x0 + w - n * 0.04, y0 + n * 0.05), fill=col + (255,),
                width=max(2, int(n * 0.06)), joint="curve")
    else:
        r, px, py = n * 0.2, n / 2, n * 0.42
        dr.ellipse((px - r, py - r, px + r, py + r), fill=WHITE + (255,))
        dr.polygon([(px - r * 0.93, py + r * 0.36), (px + r * 0.93, py + r * 0.36), (px, n * 0.82)], fill=WHITE + (255,))
        dr.ellipse((px - r * 0.42, py - r * 0.42, px + r * 0.42, py + r * 0.42), fill=col + (255,))
    c.alpha_composite(lay, (u(cx) - n // 2, u(cy) - n // 2))


def s18(c):
    """Our own post, done properly: the look of the Oct 20 post (the logo on top, real photos in colour frames, chunky
    logo-style lettering, ribbons, the contact line), in full HD with real photos and fewer, crisper sparkles. Unbounded."""
    W, H = BASE
    U = "Unbounded"
    c.paste((255, 252, 248, 255), (0, 0, u(W), u(H)))
    glow(c, 160, 300, 560, (226, 210, 255), 0.7)
    glow(c, 940, 1120, 560, (255, 222, 200), 0.7)
    card(c, "IMG_8598", 300, 500, 520, 380, -3, border=14, r=30, rim=[(0, (124, 58, 200)), (1, MAGENTA)])
    card(c, "IMG_8711", 800, 400, 420, 270, 3, border=14, r=30, rim=[(0, MAGENTA), (1, ORANGE)])
    card(c, "IMG_8707", 792, 680, 392, 228, -2, border=14, r=30, rim=[(0, SUN), (1, ORANGE)])
    lg = logo(232)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(20)))
    for x, y, sz, col in [(352, 72, 44, SUN), (382, 182, 22, MAGENTA), (712, 56, 28, MAGENTA), (738, 168, 40, SUN),
                          (46, 932, 30, SUN), (1036, 1030, 26, MAGENTA)]:
        sparkle(c, x, y, sz, col)
    for x, y, sz, col, turn in [(58, 300, 58, MAGENTA, -12), (1030, 812, 50, SUN, 10)]:
        stick(c, die_cut(star(sz, 0.5), col, 3), x, y, turn)
    button(c, W / 2 - 330, 818, 660, 60, Q, INDIGO, WHITE, face(U, 26, 600))
    logo_type(c, W / 2, 958, A2, fit(U, A2, 930, 84, 900), 88)
    ramp_button(c, W / 2 - 330, 1083, 660, 58, EXTRA, [(0, (250, 152, 52)), (1, (238, 88, 72))], WHITE, face(U, 22, 600))
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1176, "Christmas offer for new families  ·  until December 24", face(U, 16, 500), INDIGO, 0.2, "ms")
    ramp_button(c, W / 2 - 360, 1198, 720, 86, f"Book a tour  ·  {PHONE}", PINK_RAMP, WHITE, face(U, 26, 600))
    f = face("DMSans", 21, 600)
    items = [("mail", INDIGO, "info@tinystars.ca"), ("pin", ORANGE, "10629 West Side Drive, Grande Prairie")]
    widths = [32 + 10 + O.width(d, s, f) / O.S for _, _, s in items]
    x = W / 2 - (sum(widths) + 36) / 2
    for (kind, col, s), w in zip(items, widths):
        icon(c, x + 16, 1320, 32, col, kind)
        t(d, x + 42, 1327, s, f, INK)
        x += w + 36


SAMPLES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18]
SHEETS = {"offer_samples.jpg": range(1, 7), "offer_samples_grids.jpg": range(7, 13), "offer_samples_brand.jpg": range(13, 19)}


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
    outs = {i: render(i) for i in picks}
    for name, group in SHEETS.items():  # a side-by-side sheet for each set that was drawn in full
        if not all(i in outs for i in group):
            continue
        tw, th = 720, 900
        sheet = Image.new("RGB", (3 * tw + 4 * 30, 2 * th + 3 * 30 + 80), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 30, 700)
        for k, i in enumerate(group):
            x, y = 30 + (k % 3) * (tw + 30), 30 + (k // 3) * (th + 70)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 12), f"Sample {i}", font=f, fill=INK)
        sheet.save(OUT / name, quality=90)
        print("wrote", OUT / name, flush=True)


if __name__ == "__main__":
    main()
