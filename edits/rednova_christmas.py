"""Red Nova, round five: six fully Christmas samples (36 to 41), with the offer said gently instead of outright.

The owner asked for everything to be Christmas, and for the promise not to sound desperate. On Nov 12 they gave the
line to use everywhere: "Red Nova is now open, a new space to shine, with our first-month happiness with Christmas
offer guaranteed", with
a sparkle before it and a star after it (drawn flat, see rednova_ad.promise).

  36  Pine grid: the room in a photo grid, a pine garland with lights and baubles, a deep green panel
  37  Tartan: the daycare's own post style on red tartan, gold frames, the star buddy in a Santa hat, gifts
  38  Photo tree: the room's photos stacked into a Christmas tree with the star buddy on top and gifts below
  39  Red panel: the grid on top, a cranberry panel with a garland, logo lettering and the star buddy
  40  Lights: a cream card with a string of lights all round its edge, an arched photo and two round ones
  41  Garland night: polaroids pegged to a pine garland on a snowy green night

Usage: python -I edits/rednova_christmas.py [36 37 ...]   (all six when none is named)
  -> exports/rednova_ad_<n>.jpg          1440 x 1800 (4:5)
  -> exports/rednova_ads_christmas2.jpg  the six side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import offer_samples as S  # noqa: E402
import rednova_ad as R  # noqa: E402
import rednova_like as L  # noqa: E402
from offer_modern import aurora, inflate  # noqa: E402
from rednova_modern import shaped  # noqa: E402
from offer_samples import (BASE, CROPS, INK, LABELS, LIFT, OUT, SIZE, SS, WHITE, card, face, fit, glow, logo,  # noqa
                           logo_type, panel, picture, put, ramp, sparkle, star, t, u)
from rednova_ad import (GOLD_PUFF, GOLD_RAMP, RED_PUFF, ball, bez, bow, fit_serif, holly, lights, serif, snow,  # noqa
                        wid)

F, D, B, C = "Fraunces", "DMSans", "BricolageGrotesque", "Caveat"
PINE = (22, 78, 58)
FOREST = (10, 44, 34)
XRED = (196, 30, 50)
CRANBERRY = (140, 14, 38)
GOLD = (236, 192, 98)
SNOWY = (250, 246, 238)
CREAM = (250, 244, 232)
WARM = [(255, 214, 140), (255, 96, 96), (255, 200, 92), (255, 238, 200), (140, 220, 160)]

LINE = R.GUAR
TITLE = "Red Nova is now open"
SUB = "a new room, just in time for Christmas"
CTA = "Book a tour  ·  (780) 230-1599"
WEB = "tinystars.ca"
ADDR = "10629 West Side Drive, Grande Prairie"


# ---------- words ----------
def line(c, x, y, lead, f, ink, hi, anchor="ms"):
    """The promise in two lines, 'Christmas offer' picked out, a sparkle before it and a star after it."""
    R.promise(c, x, y, lead, f, ink, hi, -0.2, anchor)


def foot(c, y, ink, x=None, items=(WEB, ADDR)):
    t(ImageDraw.Draw(c), BASE[0] / 2 if x is None else x, y, "  ·  ".join(items), face(D, 19, 500), ink, 0.4,
      "ms" if x is None else "ls")


# ---------- Christmas pieces ----------
def garland(c, p0, p1, p2, thick=46, seed=0, baubles=7, bulbs=13, bauble_cols=None):
    """A pine garland along a curve: hundreds of needles in five greens, lights glowing in it and baubles hanging
    from it."""
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    greens = [[(10, 48, 32), (16, 64, 42), (22, 80, 52)], [(30, 104, 66), (44, 126, 80), (70, 150, 98)]]
    for tier in greens:
        for _ in range(1400):
            s_ = rng.uniform(-0.02, 1.02)
            x, y = bez(p0, p1, p2, np.clip(s_, 0, 1))
            x2, y2 = bez(p0, p1, p2, np.clip(s_ + 0.003, 0, 1))
            ang = np.arctan2(y2 - y, x2 - x) if s_ < 1 else 0
            off = rng.normal(0, thick * 0.2)
            cx_, cy_ = x - np.sin(ang) * off, y + np.cos(ang) * off
            a = rng.uniform(0, 2 * np.pi)
            ln = rng.uniform(thick * 0.22, thick * 0.5)
            col = tier[rng.integers(len(tier))]
            d.line((u(cx_), u(cy_), u(cx_ + ln * np.cos(a)), u(cy_ + ln * np.sin(a))), fill=col + (255,),
                   width=max(2, u(2.4)))
    O.shadow(c, lay.getchannel("A"), (0, 0), u(8), (0, u(8)), 0.45)
    c.alpha_composite(lay)
    for i in range(bulbs):
        x, y = bez(p0, p1, p2, (i + 0.5) / bulbs)
        y += rng.normal(0, thick * 0.12)
        col = WARM[i % len(WARM)]
        glow(c, x, y, 40, col, 0.55)
        ImageDraw.Draw(c).ellipse((u(x - 6), u(y - 8), u(x + 6), u(y + 8)), fill=col + (255,))
        ImageDraw.Draw(c).ellipse((u(x - 3), u(y - 5), u(x + 3), u(y + 2)),
                                  fill=tuple(min(255, v + 70) for v in col) + (255,))
    cols = bauble_cols or [RED_PUFF, GOLD_PUFF]
    for i in range(baubles):
        x, y = bez(p0, p1, p2, (i + 0.75) / (baubles + 0.5))
        dd = rng.uniform(34, 48)
        ball(c, x, y + thick * 0.45 + dd / 2, dd, cols[i % len(cols)], string_top=y + thick * 0.1)


def tartan(w, h, unit):
    """Red Christmas tartan: a repeating sett of red, green, dark and thin gold stripes, woven both ways, with a
    faint twill."""
    sett = [(64, (176, 22, 40)), (16, (18, 70, 46)), (6, (34, 12, 18)), (16, (18, 70, 46)), (36, (176, 22, 40)),
            (3, (232, 190, 96)), (36, (176, 22, 40)), (10, (34, 12, 18))]
    total = sum(s[0] for s in sett)
    lut = np.zeros((total, 3), np.float32)
    p = 0
    for wdt, col in sett:
        lut[p:p + wdt] = col
        p += wdt
    xs = lut[(np.arange(w) / unit).astype(int) % total]
    ys = lut[(np.arange(h) / unit).astype(int) % total]
    img = (xs[None, :, :] + ys[:, None, :]) / 2
    yy, xx = np.mgrid[0:h, 0:w]
    twill = (((xx + yy) // max(1, int(unit * 2))) % 2).astype(np.float32) * 0.06 + 0.94
    img *= twill[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def gift(c, x, y, w, h, stops, ribbon, bow_stops, lid=0.24):
    """A wrapped present: a box and lid in paper, a ribbon down the middle and a puffed-up bow on top."""
    box = ramp(u(w), u(h), stops, 90)
    box.putalpha(O.rounded(u(w), u(h), u(6)))
    O.shadow(c, box.getchannel("A"), (u(x), u(y)), u(10), (0, u(8)), 0.35)
    c.alpha_composite(box, (u(x), u(y)))
    lw, lh = w * 1.08, h * lid
    ld = ramp(u(lw), u(lh), [(0, tuple(min(255, int(v * 1.12)) for v in stops[0][1])), (1, stops[0][1])], 90)
    ld.putalpha(O.rounded(u(lw), u(lh), u(5)))
    c.alpha_composite(ld, (u(x - (lw - w) / 2), u(y)))
    rw = w * 0.17
    rb = ramp(u(rw), u(h), ribbon, 0)
    c.alpha_composite(rb, (u(x + w / 2 - rw / 2), u(y)))
    bow(c, x + w / 2, y - w * 0.06, w * 0.32, bow_stops)


def tree_tiers(c, cx, tiers):
    """A stylised fir tree: stacked rounded tiers, lit softly from the top left."""
    for apex, base, half in tiers:
        m = Image.new("L", c.size, 0)
        ImageDraw.Draw(m).polygon([(u(cx), u(apex)), (u(cx + half), u(base)), (u(cx - half), u(base))], fill=255)
        bb = m.getbbox()
        mk = m.crop(bb).filter(ImageFilter.GaussianBlur(u(10))).point(lambda v: 255 if v > 128 else 0)
        lay = inflate(mk, u(40), [(0, (52, 132, 86)), (0.6, (24, 92, 60)), (1, (12, 58, 38))], 90, gloss=0.25)
        O.shadow(c, mk, bb[:2], u(16), (0, u(12)), 0.4)
        c.alpha_composite(lay, bb[:2])


def beads(c, p0, p1, p2, col=(240, 200, 110), step=15, r=4.4):
    """A string of little gold beads along a curve, like tinsel on a tree."""
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pts = [bez(p0, p1, p2, s_) for s_ in np.linspace(0, 1, 400)]
    acc, last = 0.0, pts[0]
    for x, y in pts:
        acc += np.hypot(x - last[0], y - last[1])
        last = (x, y)
        if acc >= step:
            acc = 0
            d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=col + (255,))
            d.ellipse((u(x - r * 0.45), u(y - r * 0.6), u(x), u(y - r * 0.1)), fill=(255, 246, 214, 255))
    O.shadow(c, lay.getchannel("A"), (0, 0), u(3), (0, u(3)), 0.35)
    c.alpha_composite(lay)


def framed(c, name, cx, cy, w, h, crop=None, rim=6, r=16, turn=0):
    """A photo in a thin gold frame."""
    ph = picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    ph.putalpha(O.rounded(ph.width, ph.height, u(r)))
    fr = ramp(ph.width + 2 * u(rim), ph.height + 2 * u(rim), GOLD_RAMP, 45)
    fr.putalpha(O.rounded(fr.width, fr.height, u(r + rim)))
    fr.alpha_composite(ph, (u(rim), u(rim)))
    fr = fr.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - fr.width // 2, u(cy) - fr.height // 2)
    O.shadow(c, fr.getchannel("A"), xy, u(14), (0, u(10)), 0.45)
    put(c, fr, *xy)


def hang(c, name, cx, top, w, turn, caption, crop=None):
    """A polaroid hung from a garland by a little wooden peg."""
    side, bottom = 16, 70
    ph = picture(name, w, w, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    fw, fh = u(w + 2 * side), u(w + side + bottom)
    fr = Image.new("RGBA", (fw, fh + u(30)), (0, 0, 0, 0))
    card_ = Image.new("RGBA", (fw, fh), (253, 251, 246, 255))
    card_.alpha_composite(ph, (u(side), u(side)))
    ImageDraw.Draw(card_).text((fw / 2, u(w + side + bottom * 0.56)), caption, font=face(C, 38, 650),
                               fill=(70, 40, 40), anchor="mm")
    fr.alpha_composite(card_, (0, u(30)))
    pw, ph_ = u(20), u(52)
    peg = ramp(pw, ph_, [(0, (226, 186, 132)), (1, (176, 128, 80))], 0)
    peg.putalpha(O.rounded(pw, ph_, u(5)))
    ImageDraw.Draw(peg).line((pw // 2, u(6), pw // 2, ph_ - u(6)), fill=(130, 90, 56, 255), width=max(1, u(1.6)))
    fr.alpha_composite(peg, (fw // 2 - pw // 2, 0))
    hh = fr.height
    fr = fr.rotate(turn, Image.BICUBIC, expand=True)
    th = np.deg2rad(turn)  # where the top of the peg lands after the turn, so it sits on the garland
    px, py = fr.width / 2 - hh / 2 * np.sin(th), fr.height / 2 - hh / 2 * np.cos(th)
    xy = (int(u(cx) - px), int(u(top) - py))
    O.shadow(c, fr.getchannel("A"), xy, u(14), (u(3), u(12)), 0.4)
    put(c, fr, *xy)


def gold_button(c, x, y, w, h, s, f, fg=FOREST):
    S.ramp_button(c, x, y, w, h, s, [(0, (250, 214, 122)), (1, (214, 160, 58))], fg, f)


def cream_badge_logo(c, cx, cy, d):
    """The logo on a round cream badge with a gold rim."""
    n = u(d)
    rim = ramp(n + u(10), n + u(10), GOLD_RAMP, 45)
    m = Image.new("L", rim.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, m.width - 1, m.height - 1), fill=255)
    rim.putalpha(m)
    O.shadow(c, m, (u(cx) - m.width // 2, u(cy) - m.height // 2), u(14), (0, u(10)), 0.4)
    c.alpha_composite(rim, (u(cx) - m.width // 2, u(cy) - m.height // 2))
    b = Image.new("RGBA", (n, n), CREAM + (255,))
    bm = Image.new("L", (n, n), 0)
    ImageDraw.Draw(bm).ellipse((0, 0, n - 1, n - 1), fill=255)
    lg = logo(d * 0.78)
    b.alpha_composite(lg, ((n - lg.width) // 2, (n - lg.height) // 2))
    b.putalpha(bm)
    c.alpha_composite(b, (u(cx) - n // 2, u(cy) - n // 2))


# ---------- the six ----------
def x36(c):
    """Pine grid: the room in a photo grid, a pine garland with lights and baubles over a deep green panel."""
    W, H = BASE
    c.paste(SNOWY + (255,), (0, 0, u(W), u(800)))
    put(c, ramp(u(W), u(H - 790), [(0, PINE), (1, FOREST)], 90), 0, u(790))
    L.grid_a(c, ["RB_kitchen", "RB_sand", "RB_tent", "RB_books", "RB_rug", "RB_busy"],
             {"RB_sand": (0.47, 0.8, 1.5), "RB_tent": (0.42, 0.62, 1.2), "RB_books": (0.64, 0.45, 1.2)})
    O.logo_badge(c, 26, 26, 100)
    snow(c, 160, 36, y0=800, alpha=0.7, big=4)
    garland(c, (-40, 788), (540, 870), (1120, 788), seed=3)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1002, TITLE, fit_serif([TITLE], 860, 104), GOLD, -1, "ms")
    t(d, W / 2, 1046, SUB.upper(), face(D, 18, 700), (214, 232, 218), 2.8, "ms")
    line(c, W / 2, 1100, 40, face(D, 28, 600), SNOWY, GOLD)
    gold_button(c, W / 2 - 300, 1170, 600, 76, CTA, face(D, 25, 700))
    foot(c, 1310, (170, 200, 180))


def x37(c):
    """Tartan: the daycare's own post style on red tartan: a string of lights, the logo on a gold-rimmed badge,
    photos in gold frames, 'Red Nova' in logo lettering, the star buddy in a Santa hat, presents."""
    W, H = BASE
    put(c, tartan(u(W), u(H), O.S * 1.0), 0, 0)
    shade_ = Image.new("RGBA", c.size, (30, 6, 12, 70))
    c.alpha_composite(shade_)
    lights(c, (-30, 30), (540, 110), (1110, 30), 16, WARM)
    cream_badge_logo(c, W / 2, 196, 190)
    rim = [(0, (255, 228, 146)), (1, (196, 140, 40))]
    card(c, "RB_kitchen", 300, 470, 450, 300, -3, border=12, r=22, rim=rim)
    card(c, "RB_sand", 788, 450, 420, 290, 3, border=12, r=22, rim=rim)
    card(c, "RB_books", 306, 800, 420, 280, 2, border=12, r=22, rim=rim)
    S.button(c, 790 - 210, 640, 420, 52, "Christmas offer  ·  new room opened:", CREAM, CRANBERRY, face(D, 20, 700))
    logo_type(c, 790, 790, ["Red Nova"], fit("Unbounded", ["Red Nova"], 440, 96, 900), 0, stroke=5)
    L.offer_banner(c, 566, 822, 450, 154, L.BANNER, [(0, (26, 96, 64)), (1, (14, 60, 42))], L.banner_font(450), 32,
                   marks=True)
    holly(c, 1004, 832, 58, 20)
    L.star_buddy(c, 90, 1048, 180, 8, hat=True)
    gift(c, 860, 1020, 120, 96, [(0, (60, 140, 96)), (1, (22, 86, 58))], GOLD_RAMP, GOLD_PUFF)
    gift(c, 960, 1046, 90, 70, [(0, (255, 248, 236)), (1, (230, 220, 206))], [(0, (220, 40, 60)), (1, (160, 16, 40))],
         RED_PUFF)
    gold_button(c, W / 2 - 300, 1060, 600, 80, "Book a tour today", face(B, 31, 700))
    panel(c, 0, 1182, W, 200, 0, CREAM, lift=0.3)
    L.contact_row(c, 1272, 18, ink=INK, cols=(XRED, (22, 86, 58), (196, 140, 40)))


def x38(c):
    """Photo tree: the room's photos stacked into a Christmas tree, tinsel and lights on it, the star buddy on top
    and presents underneath, on a snowy night."""
    W, H = BASE
    put(c, ramp(u(W), u(H), [(0, (14, 22, 46)), (0.6, (16, 46, 42)), (1, (10, 32, 30))], 90), 0, 0)
    glow(c, W / 2, 560, 620, (255, 214, 140), 0.18)
    snow(c, 260, 11, alpha=0.8, big=10)
    O.logo_badge(c, 30, 26, 92)
    tree_tiers(c, W / 2, [(170, 470, 250), (300, 700, 400), (470, 930, 540)])
    beads(c, (330, 452), (560, 520), (760, 430))
    beads(c, (210, 680), (540, 760), (880, 660))
    beads(c, (120, 910), (540, 980), (980, 900))
    framed(c, "RB_sand", W / 2, 370, 250, 180, (0.47, 0.8, 1.6))
    framed(c, "RB_kitchen", 392, 594, 270, 182, (0.5, 0.56, 1.25), turn=-2)
    framed(c, "RB_books", 688, 594, 270, 182, (0.64, 0.45, 1.3), turn=2)
    framed(c, "RB_tent", 240, 816, 270, 186, (0.42, 0.62, 1.25), turn=-2)
    framed(c, "RB_rug", W / 2, 822, 270, 186, (0.45, 0.42, 1.3))
    framed(c, "RB_busy", 840, 816, 270, 186, (0.5, 0.45, 1.25), turn=2)
    for x, y, col in [(300, 470, WARM[0]), (780, 470, WARM[1]), (180, 700, WARM[2]), (900, 700, WARM[3]),
                      (90, 932, WARM[1]), (990, 932, WARM[0]), (540, 486, WARM[2]), (540, 712, WARM[0])]:
        glow(c, x, y, 34, col, 0.6)
        ImageDraw.Draw(c).ellipse((u(x - 6), u(y - 6), u(x + 6), u(y + 6)), fill=col + (255,))
    glow(c, W / 2, 150, 150, (255, 220, 120), 0.6)
    L.star_buddy(c, W / 2, 160, 150, 0)
    panel(c, W / 2 - 34, 926, 68, 48, 6, (110, 70, 42), lift=0.2)
    gift(c, 330, 906, 130, 92, [(0, (220, 40, 60)), (1, (150, 14, 38))], GOLD_RAMP, GOLD_PUFF)
    gift(c, 640, 918, 104, 82, [(0, (60, 140, 96)), (1, (22, 86, 58))], [(0, (240, 60, 76)), (1, (170, 16, 40))],
         RED_PUFF)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1104, TITLE, fit_serif([TITLE], 860, 92), SNOWY, -1, "ms")
    line(c, W / 2, 1152, 38, face(D, 27, 600), (232, 238, 232), GOLD)
    gold_button(c, W / 2 - 300, 1212, 600, 74, CTA, face(D, 25, 700))
    foot(c, 1324, (170, 196, 186))


def x39(c):
    """Red panel: the grid on top, a cranberry panel with a garland across its top, 'Red Nova is now open!' in logo
    lettering, the offer on a cream pill, the star buddy in a Santa hat and the contact row."""
    W, H = BASE
    c.paste(SNOWY + (255,), (0, 0, u(W), u(720)))
    L.cell(c, "RB_sand", 0, 0, 712, 470, (0.47, 0.78, 1.25))
    L.cell(c, "RB_kitchen", 718, 0, W - 718, 232, (0.5, 0.56, 1.3))
    L.cell(c, "RB_tent", 718, 238, W - 718, 232, (0.42, 0.6, 1.3))
    L.cell(c, "RB_books", 0, 476, 537, 230, (0.64, 0.45, 1.2))
    L.cell(c, "RB_rug", 543, 476, W - 543, 230, (0.45, 0.42, 1.2))
    put(c, ramp(u(W), u(H - 706), [(0, (176, 22, 46)), (1, (110, 10, 32))], 90), 0, u(706))
    O.logo_badge(c, 26, 26, 100)
    snow(c, 140, 52, y0=720, alpha=0.7, big=4)
    garland(c, (-40, 704), (540, 780), (1120, 704), seed=9, bauble_cols=[GOLD_PUFF, [(0, (255, 255, 255)),
                                                                                     (1, (210, 214, 226))]])
    logo_type(c, W / 2, 922, ["Red Nova is now open!"], fit("Unbounded", ["Red Nova is now open!"], W - 130, 74, 900), 0,
              stroke=5)
    S.button(c, W / 2 - 400, 960, 800, 96, "", CREAM, CREAM, face(D, 24, 700))
    line(c, W / 2, 999, 38, face(B, 28, 700), CRANBERRY, (22, 110, 70))
    gold_button(c, W / 2 - 300, 1086, 600, 78, "Book a tour today", face(B, 30, 700), fg=CRANBERRY)
    L.star_buddy(c, 990, 1130, 130, 8, hat=True)
    holly(c, 96, 1120, 64, -14)
    L.contact_row(c, 1300, 18, ink=SNOWY, cols=((236, 192, 98), (40, 130, 86), (236, 192, 98)), sep=False)


def x40(c):
    """Lights: a cream card with a string of lights all round its edge, a big arched photo of the sand bin and two
    round ones, holly in the corners, the offer in red and green."""
    W, H = BASE
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    glow(c, W / 2, 480, 600, (255, 248, 236), 0.8)
    m = 26
    lights(c, (m, m), (W / 2, m + 40), (W - m, m), 14, WARM)
    lights(c, (m, H - m), (W / 2, H - m - 30), (W - m, H - m), 14, WARM)
    lights(c, (m, m), (m + 30, H / 2), (m, H - m), 16, WARM)
    lights(c, (W - m, m), (W - m - 30, H / 2), (W - m, H - m), 16, WARM)
    holly(c, 96, 104, 76, -20)
    holly(c, W - 96, 104, 76, 200)
    lg = logo(108)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(64)))
    shaped(c, "RB_sand", 230, 200, 620, 600, "arch", crop=(0.47, 0.74, 1.2), lift=0.25)
    d = ImageDraw.Draw(c)
    d.arc((u(218), u(188), u(862), u(832)), 180, 360, fill=(196, 150, 60, 255), width=u(3))
    for cx_, n, cr in [(230, "RB_kitchen", (0.48, 0.62, 1.6)), (850, "RB_books", (0.64, 0.42, 1.6))]:
        shaped(c, n, cx_ - 105, 640, 210, 210, "circle", crop=cr, rim=9, lift=0.25)
    t(d, W / 2, 940, TITLE, fit_serif([TITLE], 820, 100), XRED, -1, "ms")
    t(d, W / 2, 984, SUB.upper(), face(D, 18, 700), PINE, 2.8, "ms")
    line(c, W / 2, 1036, 40, face(D, 28, 600), INK, XRED)
    S.button(c, W / 2 - 300, 1098, 600, 76, CTA, XRED, WHITE, face(D, 25, 700))
    foot(c, 1240, (120, 110, 100))


def x41(c):
    """Garland night: polaroids of the room pegged to a pine garland on a snowy green night, the star buddy in a
    Santa hat waving below."""
    W, H = BASE
    put(c, aurora(u(W), u(H), (8, 34, 28), [(0.5, 0.0, 0.6, (24, 92, 66), 0.8), (0.0, 0.9, 0.5, (6, 24, 20), 0.9),
                                            (1.0, 0.95, 0.5, (100, 16, 34), 0.5)]), 0, 0)
    snow(c, 240, 77, alpha=0.8, big=10)
    p0, p1, p2 = (-40, 120), (540, 250), (1120, 120)
    for name, x, turn, cap, cr in [("RB_kitchen", 210, 4, "play kitchen", (0.5, 0.6, 1.3)),
                                   ("RB_sand", 540, -2, "sand + diggers", (0.47, 0.8, 1.6)),
                                   ("RB_books", 870, -4, "story corner", (0.64, 0.45, 1.3))]:
        y = bez(p0, p1, p2, (x + 40) / 1160)[1]
        hang(c, name, x, y + 6, 292, turn, cap, cr)
    garland(c, p0, p1, p2, seed=21, baubles=6)
    O.logo_badge(c, 30, 20, 88)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 800, TITLE, fit_serif([TITLE], 860, 104), SNOWY, -1, "ms")
    t(d, W / 2, 860, SUB, face(C, 48, 650), GOLD, 0, "ms")
    line(c, W / 2, 930, 40, face(D, 28, 600), (236, 242, 236), GOLD)
    gold_button(c, W / 2 - 300, 1000, 600, 78, CTA, face(D, 25, 700))
    L.star_buddy(c, 120, 1130, 160, 8, hat=True)
    foot(c, 1300, (170, 196, 186))


SAMPLES = {36: x36, 37: x37, 38: x38, 39: x39, 40: x40, 41: x41}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"rednova_ad_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"rednova_ad_{i}.jpg", flush=True)
    return out


def main():
    L.prepare()
    picks = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(SAMPLES)
    outs = {i: render(i) for i in picks}
    if all(i in outs for i in SAMPLES):
        cols, tw, th = 3, 540, 675
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 24, 2 * (th + 64) + 24), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(SAMPLES):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 10), f"Sample {i}", font=f, fill=INK)
        sheet.save(OUT / "rednova_ads_christmas2.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_christmas2.jpg", flush=True)


if __name__ == "__main__":
    main()
