"""Red Nova, round four: six samples (30 to 35) in the two styles the owner pointed to.

  30-32  The clean grid: real photos of the room edge to edge in a grid with thin white gutters, then a calm cream
         panel with the logo, a serif headline, one line of offer and a button. The structure many daycare ads use,
         done in Tiny Stars' own colours and type.
  33-34  The daycare's own playful post (Oct 20), done properly: the logo on top, photos in colour frames, chunky
         logo-style lettering, a star buddy, an offer banner and the contact row with icons. 34 is the Christmas one,
         with a Santa hat on the star.
  35     The two together: the clean grid on top, the playful Tiny Stars panel below.

The photos get a natural, bright grade (see natural): clean whites, lifted shadows, true colour.

Usage: python -I edits/rednova_like.py [30 31 ...]   (all six when none is named)
  -> exports/rednova_ad_<n>.jpg          1440 x 1800 (4:5)
  -> exports/rednova_ads_like.jpg        the six side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import offer_samples as S  # noqa: E402
import rednova_ad as R  # noqa: E402
import rednova_modern as M  # noqa: E402
from offer_modern import inflate, puffy  # noqa: E402
from offer_samples import (BASE, CROPS, INDIGO, INK, LABELS, LIFT, MAGENTA, OUT, SIZE, SOFT, SS, SUN, WHITE,  # noqa
                           card, face, fit, glow, icon, logo, logo_type, panel, picture, put, ramp, ramp_button,
                           sparkle, star, stick, t, u)
from rednova_ad import CHERRY, GOLD_PUFF, RED_PUFF, holly, serif, snow, wid  # noqa: E402

F, D, B, UB = "Fraunces", "DMSans", "BricolageGrotesque", "Unbounded"
CREAM = (248, 243, 236)
PLUM = (58, 22, 74)
PURPLE = (84, 38, 120)
ORANGE = S.ORANGE
PHONE = "(780) 230-1599"
EMAIL = "info@tinystars.ca"
ADDR = "10629 West Side Drive, Grande Prairie"
BANNER = ["Red Nova is now open —", "A new space to shine,", "with our first-month", "happiness with Christmas",
          "offer guaranteed!"]

PHOTOS = {"RB_sand": "IMG_1286", "RB_kitchen": "IMG_1294", "RB_books": "IMG_1308", "RB_tent": "IMG_1291",
          "RB_rug": "IMG_1310", "RB_busy": "IMG_1312"}
for k_ in PHOTOS:
    CROPS[k_] = CROPS["RN_" + k_[3:]]
    LABELS[k_] = LABELS["RN_" + k_[3:]]


# ---------- the photos ----------
def natural(im):
    """Bright and true: the yellow of the ceiling lights pulled back, mid-tones lifted, colour just a little richer,
    crisp detail. The look of a well-lit room photographed on a good day."""
    im = im.copy()
    im.thumbnail((4000, 4000), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    a = np.clip(a * np.array([0.962, 1.0, 1.06], np.float32), 0, 1)
    a = 1 - (1 - a) ** 1.22
    im = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    h, s, v = [np.asarray(x, np.float32) / 255 for x in im.convert("HSV").split()]
    s = np.clip(s + 0.2 * s * (1 - s), 0, 1)
    im = Image.merge("HSV", [Image.fromarray((x * 255 + 0.5).astype(np.uint8)) for x in (h, s, v)]).convert("RGB")
    im = im.filter(ImageFilter.UnsharpMask(radius=36, percent=12, threshold=0))
    return im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=30, threshold=2))


def prepare():
    for new, src in PHOTOS.items():
        out, inp = O.CLEAN / f"{new}.jpg", O.CLEAN / f"{src}.jpg"
        if not out.exists() or out.stat().st_mtime < inp.stat().st_mtime:
            natural(Image.open(inp).convert("RGB")).save(out, quality=95)
            print("natural grade", src, "->", out.name, flush=True)


# ---------- pieces ----------
def cell(c, name, x, y, w, h, crop=None):
    """One photo in the grid, edge to edge, square corners."""
    c.alpha_composite(picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0)), (u(x), u(y)))


def grid_a(c, names, crops=None, g=6, top=520, bottom=264):
    """One big photo with two stacked beside it, three in a row below; thin white gutters."""
    W = BASE[0]
    crops = crops or {}
    bw = 712
    rw = W - bw - g
    hh = (top - g) / 2
    cell(c, names[0], 0, 0, bw, top, crops.get(names[0]))
    cell(c, names[1], bw + g, 0, rw, hh, crops.get(names[1]))
    cell(c, names[2], bw + g, hh + g, rw, top - hh - g, crops.get(names[2]))
    cw = (W - 2 * g) / 3
    for i, n in enumerate(names[3:6]):
        cell(c, n, i * (cw + g), top + g, cw, bottom, crops.get(n))
    return top + g + bottom


def phone_icon(c, cx, cy, size, col):
    n = u(size)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse((0, 0, n - 1, n - 1), fill=col + (255,))
    k = n / 100
    d.arc((26 * k, 26 * k, 78 * k, 78 * k), 90, 180, fill=WHITE + (255,), width=int(11 * k))
    d.rounded_rectangle((44 * k, 66 * k, 64 * k, 80 * k), int(4 * k), fill=WHITE + (255,))
    d.rounded_rectangle((20 * k, 36 * k, 34 * k, 56 * k), int(4 * k), fill=WHITE + (255,))
    lay = lay.rotate(-12, Image.BICUBIC)
    c.alpha_composite(lay, (u(cx) - n // 2, u(cy) - n // 2))


def contact_row(c, y, size=20, ink=INK, cols=(MAGENTA, INDIGO, ORANGE), sep=True):
    """Phone, email and address in a row, each with its round icon, split by thin rules, like the daycare's posts."""
    d = ImageDraw.Draw(c)
    f = face(D, size, 600)
    items = [("phone", cols[0], PHONE), ("mail", cols[1], EMAIL), ("pin", cols[2], ADDR)]
    ic = size * 1.6
    gap = 26
    widths = [ic + 9 + wid(s, f) for _, _, s in items]
    x = BASE[0] / 2 - (sum(widths) + gap * 2 * (len(items) - 1)) / 2
    for k, ((kind, col, s), w) in enumerate(zip(items, widths)):
        if kind == "phone":
            phone_icon(c, x + ic / 2, y - size * 0.36, ic, col)
        else:
            icon(c, x + ic / 2, y - size * 0.36, ic, col, kind)
        t(d, x + ic + 9, y, s, f, ink)
        x += w + gap
        if sep and k < len(items) - 1:
            d.line((u(x), u(y - size * 1.05), u(x), u(y + size * 0.3)), fill=(200, 192, 206, 255), width=u(1.5))
        x += gap


def star_buddy(c, cx, cy, size, turn=-8, hat=False):
    """A chubby 3D star with a happy face, the daycare's little mascot; optionally in a Santa hat."""
    n = u(size)
    m = star(size, 0.56)
    body = inflate(m, n * 0.22, [(0, (255, 238, 150)), (0.55, (252, 196, 58)), (1, (226, 138, 22))], 90, gloss=0.9)
    lay = Image.new("RGBA", (int(n * 1.5), int(n * 1.5)), (0, 0, 0, 0))
    ox = (lay.width - n) // 2
    oy = int(n * 0.32)
    lay.alpha_composite(body, (ox, oy))
    d = ImageDraw.Draw(lay)
    k = n / 100
    fx, fy = ox + 50 * k, oy + 55 * k
    cheeks = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(cheeks)
    for sx in (-1, 1):
        dc.ellipse((fx + sx * 17 * k - 6 * k, fy + 6 * k - 3.6 * k, fx + sx * 17 * k + 6 * k, fy + 6 * k + 3.6 * k),
                   fill=(255, 120, 140, 190))
    lay.alpha_composite(cheeks.filter(ImageFilter.GaussianBlur(1.6 * k)))
    for sx in (-1, 1):
        ex = fx + sx * 9.5 * k
        d.ellipse((ex - 3.6 * k, fy - 9 * k, ex + 3.6 * k, fy + 1 * k), fill=(48, 26, 30, 255))
        d.ellipse((ex - 1.9 * k, fy - 7.6 * k, ex + 0.4 * k, fy - 5.2 * k), fill=WHITE + (255,))
    d.chord((fx - 7 * k, fy + 1 * k, fx + 7 * k, fy + 13 * k), 0, 180, fill=(120, 36, 40, 255))
    d.ellipse((fx - 3.6 * k, fy + 7.5 * k, fx + 3.6 * k, fy + 12.4 * k), fill=(255, 128, 140, 255))
    if hat:
        hm = Image.new("L", lay.size, 0)
        tip = (ox + 70 * k, oy - 22 * k)
        ImageDraw.Draw(hm).polygon([(ox + 33 * k, oy + 20 * k), (ox + 67 * k, oy + 20 * k), tip], fill=255)
        hm = hm.filter(ImageFilter.GaussianBlur(1.2 * k)).point(lambda v: 255 if v > 128 else 0)
        lay.alpha_composite(inflate(hm, 7 * k, RED_PUFF, 90, gloss=0.6))
        fm = Image.new("L", lay.size, 0)
        ImageDraw.Draw(fm).rounded_rectangle((ox + 29 * k, oy + 15 * k, ox + 71 * k, oy + 27 * k), 6 * k, fill=255)
        fur = [(0, (255, 255, 255)), (1, (214, 214, 226))]
        lay.alpha_composite(inflate(fm, 5 * k, fur, 90, gloss=0.3))
        pm = Image.new("L", lay.size, 0)
        ImageDraw.Draw(pm).ellipse((tip[0] - 7 * k, tip[1] - 7 * k, tip[0] + 7 * k, tip[1] + 7 * k), fill=255)
        lay.alpha_composite(inflate(pm, 7 * k, fur, 90, gloss=0.3))
    lay = lay.rotate(turn, Image.BICUBIC)
    xy = (u(cx) - lay.width // 2, u(cy) - lay.height // 2 - int(n * 0.07))
    O.shadow(c, lay.getchannel("A"), xy, u(10), (0, u(10)), 0.3)
    put(c, lay, *xy)


def one_line(c, y, ink, hi, size=27):
    """The promise in two lines, 'Christmas offer' picked out, a sparkle before it and a star after it."""
    f = fit(D, R.PROM_FIT, BASE[0] - 110, size, 600)
    R.promise(c, BASE[0] / 2, y, 34, f, ink, hi, 0, "ms")


def offer_banner(c, x, y, w, h, lines, stops, f, lead, marks=False):
    """The offer on a bright ramp banner with rounded ends, in white."""
    b = ramp(u(w), u(h), stops, 0)
    b.putalpha(O.rounded(u(w), u(h), u(28)))
    O.shadow(c, b.getchannel("A"), (u(x), u(y)), u(14), (0, u(8)), 0.25)
    c.alpha_composite(b, (u(x), u(y)))
    d = ImageDraw.Draw(c)
    y0 = y + h / 2 - (len(lines) - 1) * lead / 2 + f.size / O.S * 0.34
    for k, s in enumerate(lines):
        t(d, x + w / 2, y0 + k * lead, s, f, WHITE, -0.3, "ms")
    if marks:
        R.marks(c, x + w / 2, y0, lead, lines, f, -0.3, "ms", (255, 226, 130))


def banner_font(w):
    """Bold type for the four-line offer banner, as big as fits with the sparkle and the star."""
    return fit(B, ["M  " + s + "  M" for s in BANNER], w - 30, 28, 750)


def tag(c, cx, cy, s, bg, fg, f, h=52, turn=0):
    S.pill_sticker(c, cx, cy, s, f, bg, fg, turn, h=h)


# ---------- the six ----------
def l30(c):
    """The clean grid: six photos of the room edge to edge, a cream panel with the logo, a serif headline, one line
    of offer and a button. Fraunces and DM Sans."""
    W, H = BASE
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    c.paste(WHITE + (255,), (0, 0, u(W), u(796)))
    grid_a(c, ["RB_kitchen", "RB_sand", "RB_tent", "RB_books", "RB_rug", "RB_busy"],
           {"RB_sand": (0.47, 0.8, 1.5), "RB_tent": (0.42, 0.62, 1.2), "RB_books": (0.64, 0.45, 1.2)})
    lg = logo(150)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(826)))
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1046, "Red Nova, our newest room.", fit(F, ["Red Nova, our newest room."], W - 120, 52,
                                                                    500, -0.6, opsz=72), PLUM, -0.6, "ms")
    one_line(c, 1096, (84, 70, 92), MAGENTA)
    t(d, W / 2, 1166, "Grande Prairie  ·  tinystars.ca", face(D, 19, 500), (150, 140, 150), 1, "ms")
    S.button(c, W / 2 - 280, 1194, 560, 74, f"Book a tour  ·  {PHONE}", PURPLE, WHITE, face(D, 24, 700))


def l31(c):
    """The clean grid at Christmas: the sand bin big, a cream panel with holly, a Christmas tag and a red button.
    Fraunces and DM Sans."""
    W, H = BASE
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    c.paste(WHITE + (255,), (0, 0, u(W), u(796)))
    grid_a(c, ["RB_sand", "RB_kitchen", "RB_books", "RB_tent", "RB_rug", "RB_busy"],
           {"RB_sand": (0.47, 0.76, 1.2), "RB_books": (0.64, 0.45, 1.2), "RB_tent": (0.42, 0.62, 1.15)})
    holly(c, 70, 840, 70, -20)
    holly(c, W - 70, 1300, 70, 160)
    lg = logo(140)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(818)))
    tag(c, W / 2, 976, "Christmas offer", CHERRY, WHITE, face(D, 21, 700), h=46, turn=-2)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 1060, "Red Nova, our newest room.", fit(F, ["Red Nova, our newest room."], W - 120, 52,
                                                                    500, -0.6, opsz=72), PLUM, -0.6, "ms")
    one_line(c, 1108, (84, 70, 92), CHERRY)
    S.button(c, W / 2 - 280, 1170, 560, 74, f"Book a tour  ·  {PHONE}", CHERRY, WHITE, face(D, 24, 700))
    t(d, W / 2, 1270, "Grande Prairie  ·  tinystars.ca", face(D, 19, 500), (150, 140, 150), 1, "ms")
    for x, y, s_ in [(180, 1000, 18), (900, 960, 22), (300, 1250, 14)]:
        sparkle(c, x, y, s_, (226, 180, 90))


def l32(c):
    """The clean grid, wide: the room across the top, four squares below, the name big in serif on the cream panel.
    Instrument Serif and DM Sans."""
    W, H = BASE
    g = 6
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    c.paste(WHITE + (255,), (0, 0, u(W), u(747)))
    cell(c, "RB_kitchen", 0, 0, W, 470, (0.5, 0.55, 1.0))
    cw = (W - 3 * g) / 4
    for i, (n, cr) in enumerate([("RB_sand", (0.47, 0.8, 1.6)), ("RB_books", (0.64, 0.45, 1.3)),
                                 ("RB_tent", (0.42, 0.62, 1.2)), ("RB_rug", (0.45, 0.42, 1.4))]):
        cell(c, n, i * (cw + g), 470 + g, cw, 265, cr)
    d = ImageDraw.Draw(c)
    lg = logo(120)
    c.alpha_composite(lg, (u(60), u(784)))
    t(d, W - 60, 840, "NOW OPEN", face(D, 20, 800), MAGENTA, 3.4, "rs")
    t(d, W - 60, 870, "Grande Prairie", face(D, 19, 500), SOFT, 0.5, "rs")
    t(d, W / 2, 1042, "Red Nova", serif(150, italic=False), PLUM, -2, "ms")
    t(d, W / 2, 1090, "our newest room is open", serif(44), (130, 100, 140), 0, "ms")
    one_line(c, 1142, (84, 70, 92), MAGENTA)
    S.button(c, W / 2 - 280, 1204, 560, 74, f"Book a tour  ·  {PHONE}", PURPLE, WHITE, face(D, 24, 700))
    t(d, W / 2, 1306, "tinystars.ca", face(D, 19, 600), (150, 140, 150), 1, "ms")


def own_post(c, names, xmas=False):
    """The daycare's own post, done properly (33 and 34)."""
    W, H = BASE
    c.paste((255, 253, 250, 255), (0, 0, u(W), u(H)))
    glow(c, 140, 260, 520, (232, 218, 255), 0.75)
    glow(c, 960, 1100, 560, (255, 226, 206), 0.75)
    if xmas:
        M.snowflakes_bg(c, (190, 170, 230), 0.16, step=150)
    lg = logo(250)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(22)))
    for x, y, sz, col in [(330, 70, 40, SUN), (356, 170, 20, MAGENTA), (746, 52, 26, MAGENTA), (770, 160, 38, SUN),
                          (40, 640, 26, SUN), (1044, 600, 22, MAGENTA)]:
        sparkle(c, x, y, sz, col)
    rims = [[(0, (124, 58, 200)), (1, MAGENTA)], [(0, MAGENTA), (1, ORANGE)], [(0, SUN), (1, ORANGE)]]
    card(c, names[0], 300, 430, 470, 320, -3, border=12, r=26, rim=rims[0])
    card(c, names[1], 790, 410, 430, 300, 3, border=12, r=26, rim=rims[1])
    card(c, names[2], 310, 784, 430, 300, 2, border=12, r=26, rim=rims[2])
    lab = "Christmas offer  ·  new room opened:" if xmas else "New room opened:"
    S.button(c, 790 - 210, 610, 420, 54, lab, PURPLE, WHITE, face(D, 22 if xmas else 25, 700))
    logo_type(c, 790, 760, ["Red Nova"], fit(UB, ["Red Nova"], 440, 96, 900), 0, stroke=5)
    stops = [(0, CHERRY), (1, MAGENTA)] if xmas else [(0, MAGENTA), (1, (250, 136, 56))]
    offer_banner(c, 566, 790, 450, 170, BANNER, stops, banner_font(450), 29, marks=True)
    if xmas:
        holly(c, 1000, 806, 60, 20)
    star_buddy(c, 84 if xmas else 96, 1046 if xmas else 1022, 186, 8 if xmas else -10, hat=xmas)
    ramp_button(c, W / 2 - 330, 1064, 660, 84, "Book a tour today", S.PINK_RAMP, WHITE, face(B, 32, 700))
    contact_row(c, 1250, 19)


def l33(c):
    own_post(c, ["RB_kitchen", "RB_sand", "RB_books"])


def l34(c):
    own_post(c, ["RB_sand", "RB_tent", "RB_kitchen"], xmas=True)


def l35(c):
    """The two together: the clean grid on top, the playful Tiny Stars panel below with logo lettering, the offer
    on a purple pill and the contact row."""
    W, H = BASE
    g = 6
    c.paste((255, 253, 250, 255), (0, 0, u(W), u(H)))
    cell(c, "RB_sand", 0, 0, 712, 470, (0.47, 0.78, 1.25))
    cell(c, "RB_kitchen", 718, 0, W - 718, 232, (0.5, 0.56, 1.3))
    cell(c, "RB_tent", 718, 238, W - 718, 232, (0.42, 0.6, 1.3))
    cell(c, "RB_books", 0, 476, 537, 230, (0.64, 0.45, 1.2))
    cell(c, "RB_rug", 543, 476, W - 543, 230, (0.45, 0.42, 1.2))
    glow(c, 160, 1200, 520, (232, 218, 255), 0.6)
    glow(c, 940, 1250, 520, (255, 226, 206), 0.6)
    lg = logo(150)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(718)))
    for x, y, sz, col in [(400, 760, 26, SUN), (680, 790, 30, MAGENTA), (90, 900, 22, SUN), (990, 920, 24, MAGENTA)]:
        sparkle(c, x, y, sz, col)
    logo_type(c, W / 2, 976, ["Red Nova!"], fit(UB, ["Red Nova!"], W - 120, 74, 900), 0,
              stroke=5)
    S.button(c, W / 2 - 400, 1008, 800, 90, "", PURPLE, WHITE, face(D, 24, 700))
    d = ImageDraw.Draw(c)
    fp = face(B, 27, 700)
    R.promise(c, W / 2, 1044, 36, fp, WHITE, (255, 214, 110), -0.2, "ms")
    ramp_button(c, W / 2 - 300, 1124, 600, 78, "Book a tour today", S.PINK_RAMP, WHITE, face(B, 29, 700))
    star_buddy(c, 1000, 1150, 120, 10)
    contact_row(c, 1290, 18)


SAMPLES = {30: l30, 31: l31, 32: l32, 33: l33, 34: l34, 35: l35}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"rednova_ad_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"rednova_ad_{i}.jpg", flush=True)
    return out


def main():
    prepare()
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
        sheet.save(OUT / "rednova_ads_like.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_like.jpg", flush=True)


if __name__ == "__main__":
    main()
