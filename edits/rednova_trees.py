"""Red Nova, round six: six more photo trees (samples 42 to 47), softer and more aesthetic than sample 38, each in
its own colours.

The room's six best photos are stacked one, two, three into a Christmas tree, dressed with tinsel beads, small
baubles and warm fairy lights, a topper, and wrapped presents underneath. The photos have the soft, airy grade of the
aesthetic set; the words are lowercase in Instrument Serif and Inter Tight; there is a fine film grain over it all.
The offer is said gently: "a new space to shine, with our first-month happiness with christmas offer guaranteed".

  42  blush: pink tiers, pearl beads, a satin bow on top
  43  sage: soft sage tiers on cream, champagne beads, a gold star
  44  ice: frosted white and blue tiers in falling snow, a silver star
  45  champagne: a tree drawn in fairy lights on ivory, a gold star
  46  velvet: an emerald tree on deep burgundy, gold beads, a gold star
  47  lavender: the brand's purple, silver beads, the star buddy on top

Usage: python -I edits/rednova_trees.py [42 43 ...]   (all six when none is named)
  -> exports/rednova_ad_<n>.jpg          1440 x 1800 (4:5)
  -> exports/rednova_ads_trees.jpg       the six side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import rednova_aesthetic as A  # noqa: E402
import rednova_christmas as X  # noqa: E402
import rednova_like as L  # noqa: E402
from offer_modern import inflate  # noqa: E402
from offer_samples import BASE, CROPS, INK, LIFT, OUT, SIZE, SS, WHITE, face, glow, logo, panel, picture, put, ramp, \
    sparkle, star, t, u  # noqa: E402
from rednova_ad import ball, bez, fit_serif, lights, serif, snow  # noqa: E402

I = "InterTight"
TITLE = "red nova is now open"
SUB = "a new room, just in time for christmas"
CTA = "book a tour  ·  (780) 230-1599"
FOOT = "tinystars.ca  ·  10629 west side drive, grande prairie"

# where the six photos sit on the tree: (name, centre x, centre y, width, height, crop, turn)
SPOTS = [("RA_sand", 540, 370, 250, 180, (0.47, 0.8, 1.6), 0),
         ("RA_kitchen", 392, 594, 270, 182, (0.5, 0.56, 1.25), -2),
         ("RA_books", 688, 594, 270, 182, (0.64, 0.45, 1.3), 2),
         ("RA_tent", 240, 816, 270, 186, (0.42, 0.62, 1.25), -2),
         ("RA_rug", 540, 822, 270, 186, (0.45, 0.42, 1.3), 0),
         ("RA_busy", 840, 816, 270, 186, (0.5, 0.45, 1.25), 2)]
TIERS = [(178, 470, 240), (304, 700, 392), (474, 930, 530)]
BEADS = [((330, 452), (560, 520), (760, 430)), ((210, 680), (540, 760), (880, 660)), ((120, 910), (540, 980), (980, 900))]

PAL = {
    42: dict(name="blush", bg=[(0, (252, 242, 240)), (1, (244, 222, 222))],
             tiers=[(0, (250, 210, 214)), (0.6, (230, 168, 178)), (1, (196, 124, 140))],
             rim=[(0, (250, 232, 206)), (1, (208, 170, 120))], beads=(255, 248, 242), lights=(255, 236, 214),
             balls=[[(0, (255, 255, 255)), (1, (226, 214, 214))], [(0, (250, 214, 190)), (1, (200, 144, 110))]],
             ink=(92, 52, 58), title=(160, 72, 90), cta=(166, 78, 96), cta_fg=(255, 246, 244), soft=(150, 116, 120),
             gifts=[([(0, (255, 255, 255)), (1, (236, 226, 224))], (226, 160, 172), (196, 92, 112)),
                    ([(0, (244, 196, 202)), (1, (216, 150, 162))], (255, 246, 240), (255, 250, 246))],
             topper="bow", topper_col=(196, 84, 106), glow=(255, 214, 220), snow=0),
    43: dict(name="sage", bg=[(0, (248, 246, 238)), (1, (230, 236, 222))],
             tiers=[(0, (200, 216, 192)), (0.6, (152, 176, 148)), (1, (104, 130, 104))],
             rim=[(0, (250, 236, 200)), (1, (196, 160, 96))], beads=(232, 200, 140), lights=(255, 232, 196),
             balls=[[(0, (255, 252, 244)), (1, (222, 214, 196))], [(0, (250, 226, 160)), (1, (190, 146, 70))]],
             ink=(56, 66, 54), title=(70, 98, 72), cta=(84, 110, 84), cta_fg=(250, 248, 240), soft=(118, 128, 114),
             gifts=[([(0, (255, 252, 244)), (1, (232, 226, 210))], (196, 160, 96), (196, 160, 96)),
                    ([(0, (176, 196, 170)), (1, (130, 156, 128))], (252, 246, 232), (252, 248, 238))],
             topper="star", topper_col=[(0, (255, 236, 168)), (0.5, (232, 186, 82)), (1, (176, 128, 40))],
             glow=(255, 232, 170), snow=0),
    44: dict(name="ice", bg=[(0, (236, 243, 250)), (0.7, (206, 222, 240)), (1, (186, 206, 232))],
             tiers=[(0, (255, 255, 255)), (0.55, (222, 234, 246)), (1, (170, 192, 222))],
             rim=[(0, (255, 255, 255)), (1, (176, 190, 212))], beads=(246, 250, 255), lights=(236, 246, 255),
             balls=[[(0, (255, 255, 255)), (1, (196, 206, 222))], [(0, (206, 226, 250)), (1, (110, 146, 196))]],
             ink=(40, 56, 86), title=(52, 82, 130), cta=(60, 92, 140), cta_fg=WHITE, soft=(96, 116, 146),
             gifts=[([(0, (255, 255, 255)), (1, (220, 230, 242))], (150, 182, 222), (120, 156, 206)),
                    ([(0, (176, 204, 238)), (1, (120, 156, 206))], (255, 255, 255), (250, 252, 255))],
             topper="star", topper_col=[(0, (255, 255, 255)), (0.5, (214, 222, 236)), (1, (140, 156, 182))],
             glow=(220, 236, 255), snow=1),
    45: dict(name="champagne", bg=[(0, (251, 248, 240)), (1, (238, 228, 210))],
             tiers=None, rim=[(0, (252, 238, 204)), (1, (200, 164, 104))], beads=(255, 250, 240),
             lights=(255, 224, 170),
             balls=[[(0, (255, 252, 244)), (1, (226, 216, 196))], [(0, (250, 226, 170)), (1, (196, 150, 76))]],
             ink=(76, 60, 40), title=(146, 108, 50), cta=(132, 98, 50), cta_fg=(255, 250, 240), soft=(140, 122, 100),
             gifts=[([(0, (255, 252, 244)), (1, (234, 224, 206))], (214, 180, 120), (196, 156, 90)),
                    ([(0, (236, 210, 160)), (1, (200, 164, 104))], (255, 250, 240), (255, 252, 246))],
             topper="star", topper_col=[(0, (255, 240, 180)), (0.5, (236, 192, 96)), (1, (180, 132, 48))],
             glow=(255, 226, 160), snow=0),
    46: dict(name="velvet", bg=[(0, (104, 22, 42)), (1, (52, 8, 22))],
             tiers=[(0, (52, 132, 98)), (0.6, (22, 86, 64)), (1, (8, 46, 36))],
             rim=[(0, (252, 230, 170)), (1, (190, 146, 70))], beads=(240, 204, 128), lights=(255, 220, 160),
             balls=[[(0, (255, 236, 168)), (1, (190, 140, 50))], [(0, (255, 250, 240)), (1, (220, 210, 196))]],
             ink=(250, 238, 228), title=(244, 214, 150), cta=(236, 200, 128), cta_fg=(70, 12, 28), soft=(220, 186, 190),
             gifts=[([(0, (255, 248, 236)), (1, (230, 218, 200))], (190, 30, 56), (200, 40, 66)),
                    ([(0, (236, 200, 128)), (1, (190, 146, 70))], (120, 20, 44), (150, 24, 52))],
             topper="star", topper_col=[(0, (255, 240, 180)), (0.5, (236, 192, 96)), (1, (180, 132, 48))],
             glow=(255, 214, 140), snow=1),
    47: dict(name="lavender", bg=[(0, (247, 242, 252)), (1, (228, 218, 246))],
             tiers=[(0, (222, 206, 248)), (0.6, (176, 148, 226)), (1, (124, 92, 190))],
             rim=[(0, (255, 255, 255)), (1, (196, 190, 214))], beads=(250, 250, 255), lights=(255, 236, 214),
             balls=[[(0, (255, 255, 255)), (1, (210, 206, 224))], [(0, (250, 186, 220)), (1, (210, 90, 150))]],
             ink=(56, 34, 86), title=(96, 52, 150), cta=(98, 52, 152), cta_fg=WHITE, soft=(130, 112, 156),
             gifts=[([(0, (255, 255, 255)), (1, (230, 226, 240))], (196, 150, 230), (160, 100, 210)),
                    ([(0, (206, 184, 244)), (1, (156, 120, 214))], (255, 255, 255), (250, 250, 255))],
             topper="buddy", topper_col=None, glow=(255, 226, 160), snow=0),
}


# ---------- pieces ----------
def tiers(c, cx, stops):
    for apex, base, half in TIERS:
        m = Image.new("L", c.size, 0)
        ImageDraw.Draw(m).polygon([(u(cx), u(apex)), (u(cx + half), u(base)), (u(cx - half), u(base))], fill=255)
        bb = m.getbbox()
        mk = m.crop(bb).filter(ImageFilter.GaussianBlur(u(12))).point(lambda v: 255 if v > 128 else 0)
        lay = inflate(mk, u(44), stops, 90, gloss=0.2)
        O.shadow(c, mk, bb[:2], u(20), (0, u(12)), 0.22)
        c.alpha_composite(lay, bb[:2])


def light_tree(c, cx, col):
    """A tree drawn only in fairy lights: two curving sides and strings draped across, on a fine champagne wire."""
    wire = (196, 168, 120)
    cols = [col, (255, 246, 226)]
    lights(c, (cx, 196), (cx - 200, 560), (cx - 500, 930), 16, cols, wire)
    lights(c, (cx, 196), (cx + 200, 560), (cx + 500, 930), 16, cols, wire)
    for (p0, p1, p2), n in zip(BEADS, (8, 12, 16)):
        lights(c, p0, p1, p2, n, cols, wire)


def frame(c, name, cx, cy, w, h, crop, turn, rim_stops, rim=5, r=18):
    ph = picture(name, w, h, *crop, lift=LIFT.get(name, 0))
    ph.putalpha(O.rounded(ph.width, ph.height, u(r)))
    fr = ramp(ph.width + 2 * u(rim), ph.height + 2 * u(rim), rim_stops, 45)
    fr.putalpha(O.rounded(fr.width, fr.height, u(r + rim)))
    fr.alpha_composite(ph, (u(rim), u(rim)))
    fr = fr.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - fr.width // 2, u(cy) - fr.height // 2)
    O.shadow(c, fr.getchannel("A"), xy, u(18), (0, u(12)), 0.25)
    put(c, fr, *xy)


def topper_star(c, cx, cy, size, stops, glow_col):
    glow(c, cx, cy, size * 1.2, glow_col, 0.6)
    m = star(size, 0.5)
    lay = inflate(m, u(size) * 0.2, stops, 90, gloss=1.0)
    xy = (u(cx) - m.width // 2, u(cy) - m.height // 2)
    O.shadow(c, m, xy, u(8), (0, u(6)), 0.2)
    c.alpha_composite(lay, xy)
    for dx, dy, s_ in [(-size * 0.75, -size * 0.3, 22), (size * 0.8, -size * 0.1, 16), (size * 0.55, size * 0.55, 12)]:
        sparkle(c, cx + dx, cy + dy, s_, (255, 244, 214))


def gift(c, x, y, w, h, stops, ribbon, bow_col):
    """A present wrapped in soft paper, a satin ribbon down the middle and a little satin bow."""
    box = ramp(u(w), u(h), stops, 90)
    box.putalpha(O.rounded(u(w), u(h), u(6)))
    O.shadow(c, box.getchannel("A"), (u(x), u(y)), u(12), (0, u(8)), 0.22)
    c.alpha_composite(box, (u(x), u(y)))
    lw, lh = w * 1.08, h * 0.24
    ld = ramp(u(lw), u(lh), [(0, tuple(min(255, int(v * 1.06)) for v in stops[0][1])), (1, stops[0][1])], 90)
    ld.putalpha(O.rounded(u(lw), u(lh), u(5)))
    c.alpha_composite(ld, (u(x - (lw - w) / 2), u(y)))
    rw = w * 0.15
    hi = tuple(min(255, int(v * 1.15 + 20)) for v in ribbon)
    c.alpha_composite(ramp(u(rw), u(h), [(0, ribbon), (0.5, hi), (1, ribbon)], 0), (u(x + w / 2 - rw / 2), u(y)))
    A.coquette_bow(c, x + w / 2, y + 4, w * 0.36, bow_col)


def snowfall(c, light_bg):
    if light_bg:  # on a pale sky, white flakes with a faint blue edge so they show
        rng = np.random.default_rng(4)
        lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for _ in range(220):
            x, y, r = rng.uniform(0, BASE[0]), rng.uniform(0, BASE[1]), rng.choice([2, 2.6, 3.4, 4.6])
            d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=(255, 255, 255, int(rng.uniform(170, 255))))
        sh = lay.getchannel("A").filter(ImageFilter.GaussianBlur(u(2))).point(lambda v: int(v * 0.25))
        edge = Image.new("RGBA", c.size, (120, 150, 196, 0))
        edge.putalpha(sh)
        c.alpha_composite(edge)
        c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(u(0.5))))
    else:
        snow(c, 220, 9, alpha=0.8, big=10)


# ---------- the tree ----------
def photo_tree(c, i):
    p = PAL[i]
    W, H = BASE
    put(c, ramp(u(W), u(H), p["bg"], 90), 0, 0)
    glow(c, W / 2, 560, 640, p["glow"], 0.22 if i == 46 else 0.35)
    dark = i == 46
    if p["snow"]:
        snowfall(c, light_bg=not dark)
    if dark:
        O.logo_badge(c, 34, 28, 88)
    else:
        c.alpha_composite(logo(88), (u(40), u(28)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 86, SUB, serif(34), p["soft"], 0, "rs")
    if p["tiers"]:
        tiers(c, W / 2, p["tiers"])
        for (p0, p1, p2) in BEADS:
            X.beads(c, p0, p1, p2, col=p["beads"], step=14, r=4.2)
    else:
        light_tree(c, W / 2, p["lights"])
    for name, cx, cy, w, h, cr, turn in SPOTS:
        frame(c, name, cx, cy, w, h, cr, turn, p["rim"])
    if p["tiers"]:
        for k, (x, y) in enumerate([(300, 474), (780, 474), (176, 704), (904, 704), (86, 936), (994, 936),
                                    (540, 488), (540, 716)]):
            glow(c, x, y, 30, p["lights"], 0.7)
            ImageDraw.Draw(c).ellipse((u(x - 5), u(y - 5), u(x + 5), u(y + 5)), fill=p["lights"] + (255,))
        for k, (x, y, dd) in enumerate([(372, 470, 30), (708, 470, 30), (248, 700, 32), (832, 700, 32),
                                        (150, 930, 34), (930, 930, 34)]):
            ball(c, x, y + 20, dd, p["balls"][k % 2], string_top=y)
    top = p["topper"]
    if top == "bow":
        glow(c, W / 2, 140, 140, p["glow"], 0.6)
        A.coquette_bow(c, W / 2, 136, 98, p["topper_col"])
    elif top == "buddy":
        glow(c, W / 2, 150, 150, p["glow"], 0.6)
        L.star_buddy(c, W / 2, 160, 150, 0)
    else:
        topper_star(c, W / 2, 150, 124, p["topper_col"], p["glow"])
    (g1, r1, b1), (g2, r2, b2) = p["gifts"]
    gift(c, 330, 912, 130, 92, g1, r1, b1)
    gift(c, 636, 924, 104, 80, g2, r2, b2)
    t(d, W / 2, 1100, TITLE, fit_serif([TITLE], 860, 96), p["title"], -1, "ms")
    A.promise(c, W / 2, 1150, 38, face(I, 27, 400), "ms", p["ink"], p["title"])
    A.pill(c, W / 2, 1214, 560, 72, CTA, p["cta"], p["cta_fg"], face(I, 25, 600), "m")
    t(d, W / 2, 1320, f"tinystars.ca   ·   {A.ADDR}", face(I, 19, 500), p["soft"], 0.4, "ms")


SAMPLES = {i: (lambda c, i=i: photo_tree(c, i)) for i in PAL}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    A.grain(c, 5.0, i)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"rednova_ad_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"rednova_ad_{i}.jpg", flush=True)
    return out


def main():
    A.prepare()
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
        sheet.save(OUT / "rednova_ads_trees.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_trees.jpg", flush=True)


if __name__ == "__main__":
    main()
