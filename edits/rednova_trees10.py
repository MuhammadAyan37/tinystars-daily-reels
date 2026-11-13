"""Red Nova, round eight: the flat, hand-made photo tree with ten photos (samples 54 to 59), in the six colours.

The owner sent four more photos of the room that were taken in low light (IMG_1289, 1290, 1291 and 1292) and asked
for them to be used too. Every photo here gets the same treatment first (bright, below): the exposure brought up to
a normal daylight level, shadows lifted, then the natural grade. With ten photos the tree stacks one, two, three,
four.

The look is the flat one from 48 to 53, which the owner preferred to the glossy one: paper-cut tiers, flat dots and
discs, pen-drawn bows, white-bordered prints, a faint paper texture, no glow.

Usage: python -I edits/rednova_trees10.py [54 55 ...]   (all six when none is named)
  -> exports/rednova_ad_<n>.jpg            1440 x 1800 (4:5)
  -> exports/rednova_ads_trees10.jpg       the six side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import rednova_aesthetic as A  # noqa: E402
import rednova_like as L  # noqa: E402
import rednova_trees_flat as F  # noqa: E402
from offer_samples import BASE, CROPS, INK, OUT, SIZE, SS, WHITE, face, logo, t, u  # noqa: E402
from rednova_ad import fit_serif, serif  # noqa: E402

I = "InterTight"

# the ten photos: the six from before and the four low-light ones the owner sent (1289 to 1292)
PHOTOS = {"RC_sand": "IMG_1286", "RC_kitchen": "IMG_1294", "RC_books": "IMG_1308", "RC_rug": "IMG_1310",
          "RC_busy": "IMG_1312", "RC_tent": "IMG_1291", "RC_wide": "IMG_1292", "RC_corner": "IMG_1290",
          "RC_mural": "IMG_1289", "RC_play": "IMG_1297"}

# rows of the tree, top to bottom: (name, crop)
ROWS = [[("RC_sand", (0.47, 0.8, 1.6))],
        [("RC_kitchen", (0.5, 0.56, 1.25)), ("RC_books", (0.64, 0.45, 1.3))],
        [("RC_tent", (0.4, 0.62, 1.15)), ("RC_mural", (0.56, 0.42, 2.0)), ("RC_rug", (0.45, 0.42, 1.3))],
        [("RC_wide", (0.5, 0.5, 1.15)), ("RC_corner", (0.62, 0.66, 1.5)), ("RC_play", (0.42, 0.62, 1.2)),
         ("RC_busy", (0.5, 0.45, 1.25))]]
ROW_Y = [318, 494, 670, 846]
ROW_W = [252, 240, 236, 226]
PH_H = 150
TIERS = [(176, 404, 176), (300, 582, 300), (440, 760, 420), (600, 940, 536)]
GARLANDS = [((376, 404), (560, 446), (708, 392)), ((260, 582), (540, 636), (830, 572)),
            ((150, 760), (540, 818), (938, 750)), ((50, 940), (540, 994), (1032, 932))]
TIPS = [(372, 400), (708, 400), (248, 578), (832, 578), (128, 756), (952, 756), (34, 936), (1046, 936)]


def bright(im, target=0.54):
    """A photo taken in low light, brought up to a normal daylight level: exposure set from the photo's own median
    brightness (only ever brightened), shadows lifted a touch, then the natural grade."""
    im = im.copy()
    im.thumbnail((4000, 4000), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    m = float(np.median(a @ np.array([0.299, 0.587, 0.114], np.float32)))
    g = float(np.clip(np.log(target) / np.log(max(m, 1e-3)), 0.55, 1.0))
    a = a ** g
    a = a + 0.06 * (1 - a) ** 2 * (1 - (1 - a) ** 2)
    return L.natural(Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)))


def prepare():
    for new, src in PHOTOS.items():
        out, inp = O.CLEAN / f"{new}.jpg", O.CLEAN / f"{src}.jpg"
        if not out.exists() or out.stat().st_mtime < inp.stat().st_mtime:
            bright(Image.open(inp).convert("RGB")).save(out, quality=95)
            print("brightened", src, "->", out.name, flush=True)
        CROPS.setdefault(new, (0.5, 0.5, 1.0))


def paper_tiers(c, cx, cols):
    for (apex, base, half), col in zip(TIERS, cols + [cols[-1]]):
        m = Image.new("L", c.size, 0)
        ImageDraw.Draw(m).polygon([(u(cx), u(apex)), (u(cx + half), u(base)), (u(cx - half), u(base))], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(u(3))).point(lambda v: 255 if v > 128 else 0)
        F.cast(c, m, (0, 0), dy=5, blur=4, a=0.22)
        lay = Image.new("RGBA", c.size, col + (255,))
        lay.putalpha(m)
        c.alpha_composite(lay)


def tree10(c, i):
    p = F.PAL[i - 6]
    W, H = BASE
    F.paper(c, p["bg"], i)
    dark = p["name"] == "velvet"
    if p["snow"]:
        F.flakes(c, (255, 255, 255), 150 if dark else 120, seed=i)
    if dark:
        O.logo_badge(c, 34, 28, 88)
    else:
        c.alpha_composite(logo(88), (u(40), u(28)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 86, F.SUB, serif(30), p["soft"], 0, "rs")
    tiers = p["tiers"] + [tuple(max(0, int(v * 0.9)) for v in p["tiers"][-1])]
    paper_tiers(c, W / 2, tiers)
    for k, g in enumerate(GARLANDS):
        F.dots(c, *g, col=p["acc2"] if k % 2 == 0 else p["gold"], step=17, r=3.6)
    rng = np.random.default_rng(i)
    for row, y, w in zip(ROWS, ROW_Y, ROW_W):
        n = len(row)
        gap = 14
        x0 = W / 2 - (n * w + (n - 1) * gap) / 2 + w / 2
        for k, (name, crop) in enumerate(row):
            F.print_photo(c, name, x0 + k * (w + gap), y, w, PH_H, crop, float(rng.uniform(-2.2, 2.2)), border=7)
    for k, (x, y) in enumerate(TIPS):
        F.bauble(c, x, y, 26, p["acc"] if k % 2 == 0 else p["gold"], p["gold"])
    if p["top"] == "bow":
        F.line_bow(c, W / 2, 150, 110, p["acc"], w=6.5)
    else:
        F.flat_star(c, W / 2, 140, 104, p["gold"], 0)
    (b1, r1), (b2, r2) = p["gifts"]
    F.present(c, 330, 948, 118, 74, b1, r1)
    F.present(c, 640, 958, 92, 64, b2, r2)
    accent = p["acc"] if not dark else p["gold"]
    t(d, W / 2, 1112, F.TITLE, fit_serif([F.TITLE], 860, 92), accent, -1, "ms")
    A.promise(c, W / 2, 1158, 36, face(I, 26, 400), "ms", p["ink"], accent)
    F.flat_pill(c, W / 2, 1220, 560, 68, F.CTA, accent, p["cta_fg"], face(I, 25, 600))
    t(d, W / 2, 1322, f"tinystars.ca   ·   {A.ADDR}", face(I, 19, 500), p["soft"], 0.4, "ms")


SAMPLES = {i: (lambda c, i=i: tree10(c, i)) for i in range(54, 60)}


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
        dd = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(SAMPLES):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            dd.text((x, y + th + 10), f"Sample {i}  ·  {F.PAL[i - 6]['name']}", font=f, fill=INK)
        sheet.save(OUT / "rednova_ads_trees10.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_trees10.jpg", flush=True)


if __name__ == "__main__":
    main()
