"""Red Nova, round seven: the six photo trees again (samples 48 to 53), made by hand rather than rendered.

The owner said the glossy trees (42 to 47) look AI-made. What gives that away is the computer-graphics finish: puffy
3D shapes, shiny baubles, glows everywhere, a 3D mascot. So these are built the way a designer would make them:

  - the tree is three tiers of flat paper, cut and stacked, with only the small shadow real paper casts;
  - ornaments, beads, stars and presents are flat shapes in two or three inks, no shine, no glow;
  - bows are drawn with a pen line, slightly uneven, like a hand-drawn illustration;
  - the photos are prints: real, natural colour, thin white borders, laid on the page;
  - the page is paper, with a faint fibre texture, and the type is set plainly.

Same six colours as before: blush, sage, ice, champagne, velvet and lavender.

Usage: python -I edits/rednova_trees_flat.py [48 49 ...]   (all six when none is named)
  -> exports/rednova_ad_<n>.jpg            1440 x 1800 (4:5)
  -> exports/rednova_ads_trees_flat.jpg    the six side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import rednova_aesthetic as A  # noqa: E402
import rednova_like as L  # noqa: E402
from offer_modern import pen  # noqa: E402
from offer_samples import BASE, INK, LIFT, OUT, SIZE, SS, WHITE, face, logo, picture, put, star, t, u  # noqa: E402
from rednova_ad import bez, fit_serif, serif  # noqa: E402

I = "InterTight"
TITLE = "red nova is now open"
SUB = "a new room, just in time for christmas"
CTA = "book a tour  ·  (780) 230-1599"

SPOTS = [("RB_sand", 540, 372, 250, 176, (0.47, 0.8, 1.6), 0),
         ("RB_kitchen", 394, 594, 262, 176, (0.5, 0.56, 1.25), -2),
         ("RB_books", 686, 594, 262, 176, (0.64, 0.45, 1.3), 2),
         ("RB_tent", 244, 816, 262, 180, (0.42, 0.62, 1.25), -2),
         ("RB_rug", 540, 822, 262, 180, (0.45, 0.42, 1.3), 1),
         ("RB_busy", 836, 816, 262, 180, (0.5, 0.45, 1.25), 2)]
TIERS = [(190, 476, 236), (310, 706, 388), (480, 936, 526)]
GARLANDS = [((334, 456), (560, 512), (758, 438)), ((214, 684), (540, 754), (876, 668)),
            ((122, 912), (540, 972), (978, 904))]

PAL = {
    48: dict(name="blush", bg=(246, 228, 224), tiers=[(238, 184, 190), (228, 164, 174), (214, 144, 158)],
             acc=(170, 60, 82), acc2=(255, 255, 255), gold=(206, 166, 98), ink=(86, 42, 50), soft=(150, 110, 116),
             cta_fg=(255, 246, 244), top="bow", gifts=[((255, 252, 250), (170, 60, 82)), ((222, 150, 162),
                                                                                          (255, 255, 255))],
             snow=False),
    49: dict(name="sage", bg=(240, 238, 226), tiers=[(176, 196, 166), (152, 176, 144), (128, 154, 122)],
             acc=(164, 38, 52), acc2=(255, 252, 244), gold=(204, 160, 84), ink=(46, 58, 44), soft=(116, 126, 108),
             cta_fg=(250, 248, 240), top="star", gifts=[((255, 252, 244), (164, 38, 52)), ((164, 38, 52),
                                                                                           (255, 252, 244))],
             snow=False),
    50: dict(name="ice", bg=(220, 231, 242), tiers=[(252, 253, 255), (234, 241, 249), (212, 226, 240)],
             acc=(44, 70, 116), acc2=(160, 186, 220), gold=(176, 186, 202), ink=(36, 52, 84), soft=(96, 114, 144),
             cta_fg=WHITE, top="star", gifts=[((255, 255, 255), (44, 70, 116)), ((160, 186, 220), (255, 255, 255))],
             snow=True),
    51: dict(name="champagne", bg=(245, 239, 226), tiers=[(230, 210, 168), (216, 192, 146), (198, 172, 122)],
             acc=(122, 30, 46), acc2=(255, 252, 244), gold=(186, 146, 74), ink=(70, 54, 34), soft=(138, 120, 96),
             cta_fg=(255, 250, 240), top="star", gifts=[((255, 252, 244), (122, 30, 46)), ((122, 30, 46),
                                                                                           (230, 210, 168))],
             snow=False),
    52: dict(name="velvet", bg=(108, 24, 42), tiers=[(40, 112, 84), (30, 96, 72), (22, 80, 60)],
             acc=(226, 190, 118), acc2=(250, 240, 226), gold=(226, 190, 118), ink=(250, 238, 228),
             soft=(222, 186, 190), cta_fg=(90, 16, 34), top="star",
             gifts=[((250, 240, 226), (176, 30, 54)), ((226, 190, 118), (108, 24, 42))], snow=True),
    53: dict(name="lavender", bg=(238, 231, 248), tiers=[(204, 186, 238), (184, 162, 226), (162, 138, 212)],
             acc=(86, 40, 132), acc2=(255, 255, 255), gold=(214, 172, 92), ink=(58, 34, 88), soft=(128, 110, 154),
             cta_fg=WHITE, top="star", gifts=[((255, 255, 255), (86, 40, 132)), ((86, 40, 132), (255, 255, 255))],
             snow=False),
}


# ---------- paper and print ----------
def paper(c, col, seed=0):
    """A flat sheet of coloured paper: a faint, uneven fibre texture, nothing more."""
    h, w = c.height, c.width
    rng = np.random.default_rng(seed)
    low = Image.fromarray((rng.random((h // 90 + 1, w // 90 + 1)) * 255).astype(np.uint8)).resize((w, h),
                                                                                                   Image.BICUBIC)
    low = (np.asarray(low, np.float32) / 255 - 0.5) * 3
    fine = rng.normal(0, 2.2, (h, w)).astype(np.float32)
    a = np.ones((h, w, 3), np.float32) * np.array(col, np.float32) + (low + fine)[..., None]
    c.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"), (0, 0))


def cast(c, m, xy, dy=4, blur=3, a=0.2):
    """The small, tight shadow a sheet of paper casts on the one under it."""
    O.shadow(c, m, xy, u(blur), (0, u(dy)), a)


def wobble(pts, amp=1.2, seed=0):
    rng = np.random.default_rng(seed)
    n = len(pts)
    noise = np.cumsum(rng.normal(0, 1, (n, 2)), 0)
    noise -= np.linspace(noise[0], noise[-1], n)
    noise *= amp / (np.abs(noise).max() + 1e-6)
    return [(x + dx, y + dy) for (x, y), (dx, dy) in zip(pts, noise)]


def print_photo(c, name, cx, cy, w, h, crop, turn, border=8):
    """A real photo printed with a thin white border, laid on the page at a slight angle."""
    ph = picture(name, w, h, *crop, lift=LIFT.get(name, 0))
    fr = Image.new("RGBA", (ph.width + 2 * u(border), ph.height + 2 * u(border)), (253, 252, 249, 255))
    fr.alpha_composite(ph, (u(border), u(border)))
    fr.putalpha(O.rounded(fr.width, fr.height, u(2)))
    fr = fr.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - fr.width // 2, u(cy) - fr.height // 2)
    O.shadow(c, fr.getchannel("A"), xy, u(5), (u(1), u(5)), 0.24)
    put(c, fr, *xy)


# ---------- flat pieces ----------
def paper_tiers(c, cx, cols):
    for (apex, base, half), col in zip(TIERS, cols):
        m = Image.new("L", c.size, 0)
        ImageDraw.Draw(m).polygon([(u(cx), u(apex)), (u(cx + half), u(base)), (u(cx - half), u(base))], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(u(3))).point(lambda v: 255 if v > 128 else 0)
        cast(c, m, (0, 0), dy=5, blur=4, a=0.22)
        lay = Image.new("RGBA", c.size, col + (255,))
        lay.putalpha(m)
        c.alpha_composite(lay)


def flat_star(c, cx, cy, size, col, turn=0):
    m = star(size, 0.42, turn)
    lay = Image.new("RGBA", m.size, col + (255,))
    lay.putalpha(m)
    xy = (u(cx) - m.width // 2, u(cy) - m.height // 2)
    cast(c, m, xy, dy=3, blur=2, a=0.18)
    c.alpha_composite(lay, xy)


def dots(c, p0, p1, p2, col, step=17, r=4.0):
    """A bead garland: plain flat dots along a gently sagging line."""
    d = ImageDraw.Draw(c)
    pts = [bez(p0, p1, p2, s_) for s_ in np.linspace(0, 1, 400)]
    acc, last = step, pts[0]
    for x, y in pts:
        acc += np.hypot(x - last[0], y - last[1])
        last = (x, y)
        if acc >= step:
            acc = 0
            d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=col + (255,))


def bauble(c, x, y, dd, col, cap):
    """A flat ornament: a thread, a small cap and a plain disc."""
    d = ImageDraw.Draw(c)
    d.line((u(x), u(y), u(x), u(y + 12)), fill=cap + (255,), width=max(1, u(1.6)))
    d.rectangle((u(x - 4), u(y + 10), u(x + 4), u(y + 16)), fill=cap + (255,))
    d.ellipse((u(x - dd / 2), u(y + 15), u(x + dd / 2), u(y + 15 + dd)), fill=col + (255,))


def line_bow(c, cx, cy, s, col, w=5.0, seed=3):
    """A bow drawn with a pen: two loops, a knot and two tails, the line a little uneven as a hand draws it."""
    for k, side in enumerate((-1, 1)):
        ts = np.linspace(0, 2 * np.pi, 90)
        lx, ly = 0.46 * s * (1 - np.cos(ts)) / 2, 0.2 * s * np.sin(ts)  # a loop running out from the knot
        ang = np.deg2rad(-20)  # tipped up a little
        rx, ry = lx * np.cos(ang) - ly * np.sin(ang), lx * np.sin(ang) + ly * np.cos(ang)
        pts = [(cx + side * x, cy + y) for x, y in zip(rx, ry)]
        pen(c, wobble(pts, 1.4, seed + k), col, w)
        p0, p1, p2 = (cx, cy + s * 0.02), (cx + side * s * 0.34, cy + s * 0.45), (cx + side * s * 0.26, cy + s * 0.92)
        tail = [bez(p0, p1, p2, v) for v in np.linspace(0, 1, 40)]
        pen(c, wobble(tail, 1.2, seed + 5 + k), col, w)
    r = s * 0.07
    ImageDraw.Draw(c).ellipse((u(cx - r), u(cy - r), u(cx + r), u(cy + r)), fill=col + (255,))


def present(c, x, y, w, h, box, ribbon):
    """A flat present: a box and lid in one ink, a ribbon in another, and a small pen-drawn bow."""
    lid = tuple(max(0, int(v * 0.93)) for v in box)
    m = Image.new("L", c.size, 0)
    ImageDraw.Draw(m).rectangle((u(x), u(y), u(x + w), u(y + h)), fill=255)
    cast(c, m, (0, 0), dy=4, blur=3, a=0.2)
    d = ImageDraw.Draw(c)
    d.rectangle((u(x), u(y), u(x + w), u(y + h)), fill=box + (255,))
    d.rectangle((u(x - w * 0.04), u(y), u(x + w * 1.04), u(y + h * 0.22)), fill=lid + (255,))
    rw = w * 0.14
    d.rectangle((u(x + w / 2 - rw / 2), u(y), u(x + w / 2 + rw / 2), u(y + h)), fill=ribbon + (255,))
    line_bow(c, x + w / 2, y - 2, w * 0.42, ribbon, w=4.4, seed=int(x))


def flakes(c, col, n=160, seed=8):
    """Snow as flat dots of a few sizes, the way it's printed, not glowing."""
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    for _ in range(n):
        x, y = rng.uniform(0, BASE[0]), rng.uniform(0, 1030)  # none over the words
        r = rng.choice([1.6, 2.2, 3.0, 4.0])
        d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=col + (int(rng.uniform(150, 255)),))


def flat_pill(c, cx, y, w, h, s, bg, fg, f):
    ImageDraw.Draw(c).rounded_rectangle((u(cx - w / 2), u(y), u(cx + w / 2), u(y + h)), u(h / 2), fill=bg + (255,))
    t(ImageDraw.Draw(c), cx, y + h / 2 + f.size / O.S * 0.34, s, f, fg, 0.3, "ms")


# ---------- the tree ----------
def tree(c, i):
    p = PAL[i]
    W, H = BASE
    paper(c, p["bg"], i)
    dark = i == 52
    if p["snow"]:
        flakes(c, (255, 255, 255), 150 if dark else 120, seed=i)
    if dark:
        O.logo_badge(c, 34, 28, 88)
    else:
        c.alpha_composite(logo(88), (u(40), u(28)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 86, SUB, serif(34), p["soft"], 0, "rs")
    paper_tiers(c, W / 2, p["tiers"])
    for k, g in enumerate(GARLANDS):
        dots(c, *g, col=p["acc2"] if k % 2 == 0 else p["gold"], step=17, r=3.8)
    for name, cx, cy, w, h, cr, turn in SPOTS:
        print_photo(c, name, cx, cy, w, h, cr, turn)
    for k, (x, y) in enumerate([(326, 470), (754, 470), (178, 700), (902, 700), (58, 930), (1022, 930)]):
        bauble(c, x, y, 28, p["acc"] if k % 2 == 0 else p["gold"], p["gold"])
    if p["top"] == "bow":
        line_bow(c, W / 2, 132, 140, p["acc"], w=7)
    else:
        flat_star(c, W / 2, 150, 112, p["gold"], 0)
    (b1, r1), (b2, r2) = p["gifts"]
    present(c, 336, 922, 124, 84, b1, r1)
    present(c, 628, 934, 98, 72, b2, r2)
    t(d, W / 2, 1100, TITLE, fit_serif([TITLE], 860, 96), p["acc"] if not dark else p["gold"], -1, "ms")
    A.promise(c, W / 2, 1150, 38, face(I, 27, 400), "ms", p["ink"], p["acc"] if not dark else p["gold"])
    flat_pill(c, W / 2, 1216, 560, 70, CTA, p["acc"] if not dark else p["gold"], p["cta_fg"], face(I, 25, 600))
    t(d, W / 2, 1322, f"tinystars.ca   ·   {A.ADDR}", face(I, 19, 500), p["soft"], 0.4, "ms")


SAMPLES = {i: (lambda c, i=i: tree(c, i)) for i in PAL}


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
        dd = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(SAMPLES):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            dd.text((x, y + th + 10), f"Sample {i}  ·  {PAL[i]['name']}", font=f, fill=INK)
        sheet.save(OUT / "rednova_ads_trees_flat.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_trees_flat.jpg", flush=True)


if __name__ == "__main__":
    main()
