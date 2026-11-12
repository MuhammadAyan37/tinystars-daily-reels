"""Red Nova, our newest room, is open: thirteen picture-ad samples to choose from, seven dressed for Christmas and six
for any time of year.

Every sample says the same few things: the new room is open (Red Nova), the promise (love your first month, or we'll
refund your parent portion), and how to book a tour. The photos are the new room itself, taken the day it opened, with
nobody in them; they still went through photos.py like every other photo.

  Christmas   1 Ornaments: the room hung on the tree as photo baubles, on a snowy night
              2 Christmas card: an arched window onto the room, holly, a red and gold border
              3 Gift wrap: "a new room to unwrap", a satin ribbon and bow, a gift tag
              4 Garland: polaroids hung on a string of fairy lights
              5 Snow globe: the room inside a snow globe
              6 Candy cane: puffy "NOW OPEN" letters on candy stripes
              7 Advent calendar: the room behind numbered doors
  Any time    8 Grand opening: the room with a ribbon and bow across it, ready to cut
              9 Liquid glass over an aurora of red and purple
             10 Magazine cover: the new room issue
             11 Scrapbook: taped polaroids, the promise circled in pen
             12 Clean bento grid: say hello to Red Nova
             13 Room tour: a big photo with what's where pointed out

Usage: python -I edits/rednova_ad.py [1 2 3 ...]   (all thirteen when none is named)
  -> exports/rednova_ad_<n>.jpg          1440 x 1800 (4:5)
  -> exports/rednova_ads_christmas.jpg   samples 1 to 7 side by side
  -> exports/rednova_ads_anytime.jpg     samples 8 to 13
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import offer_samples as S  # noqa: E402
from offer_modern import (aurora, glow_text, heart, holo_star, inflate, liquid, liquid_pill, loop_around,  # noqa: E402
                          doodle_star, dot_grid, pen, polaroid, puffy, puffy_button, round_photo, shade, side_shade)
from offer_samples import (BASE, CROPS, INK, LABELS, LIFT, OUT, PHONE, SIZE, SOFT, SS, WEB, WHITE, accent,  # noqa: E402
                           button, card, die_cut, face, fit, glow, icon, logo, panel, picture, put, ramp, ramp_button,
                           sparkle, star, stick, t, tile, u)

ROOM = "Red Nova"
PROM = ["Love your first month, or we'll", "refund your parent portion."]
LEAD, BIG = "Love your first month,", ["or we'll refund your", "parent portion."]
CTA = f"Book a tour  ·  {PHONE}"
XMAS = "Christmas offer"
ADDRESS = "10629 West Side Drive, Grande Prairie"

CHERRY = (212, 30, 58)
RUBY = (160, 14, 42)
WINE = (84, 8, 30)
PINE = (22, 86, 62)
FOREST = (10, 46, 36)
GOLD = (240, 192, 84)
DEEP_GOLD = (176, 120, 30)
CREAM = (250, 245, 236)
INDIGO = S.INDIGO
GOLD_RAMP = [(0, (255, 228, 146)), (0.5, (232, 178, 64)), (1, (170, 112, 26))]
GOLD_SATIN = [(0, (168, 112, 28)), (0.3, (226, 172, 60)), (0.5, (255, 232, 150)), (0.7, (226, 172, 60)),
              (1, (168, 112, 28))]
RED_SATIN = [(0, (140, 10, 36)), (0.3, (206, 30, 56)), (0.5, (244, 92, 108)), (0.7, (206, 30, 56)), (1, (140, 10, 36))]
RED_PUFF = [(0, (255, 120, 132)), (0.5, (220, 30, 58)), (1, (130, 8, 36))]
GOLD_PUFF = [(0, (255, 236, 160)), (0.5, (238, 184, 70)), (1, (160, 100, 20))]

# the new room, photographed the day it opened (nobody in the photos)
LABELS.update({"IMG_1294": "Play kitchen", "IMG_1291": "Cozy hideout", "IMG_1286": "Sand & diggers",
               "IMG_1308": "Story corner", "IMG_1310": "Circle time", "IMG_1312": "Busy boards",
               "IMG_1297": "Pretend play"})
CROPS.update({"IMG_1294": (0.5, 0.52, 1.0), "IMG_1291": (0.45, 0.56, 1.0), "IMG_1286": (0.5, 0.74, 1.25),
              "IMG_1308": (0.64, 0.5, 1.15), "IMG_1310": (0.45, 0.42, 1.05), "IMG_1312": (0.48, 0.42, 1.15),
              "IMG_1297": (0.42, 0.62, 1.1)})
LIFT.update({n: 0.14 for n in ("IMG_1294", "IMG_1291", "IMG_1286", "IMG_1308", "IMG_1310", "IMG_1312", "IMG_1297")})


# ---------- type ----------
def serif(size, italic=True):
    return ImageFont.truetype(str(O.FONTS / ("InstrumentSerif-Italic.ttf" if italic else "InstrumentSerif-Regular.ttf")),
                              u(size))


def fit_serif(lines, max_w, size, italic=True, track=0.0):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    while size > 12:
        f = serif(size, italic)
        if max(O.width(d, s, f, track) for s in lines) / O.S <= max_w:
            return f
        size -= 2
    return serif(size, italic)


def wid(s, f, track=0.0):
    return O.width(ImageDraw.Draw(Image.new("L", (1, 1))), s, f, track) / O.S


def promise(c, x, y, lead, f, fill, word_fill, track=0.0, anchor="ls", lines=PROM):
    """The promise in two lines with 'refund' picked out."""
    d = ImageDraw.Draw(c)
    t(d, x, y, lines[0], f, fill, track, anchor)
    accent(c, x, y + lead, lines[1], "refund", f, fill, word_fill, track, anchor)


def footer(c, y, f, fill, x=None, items=(WEB, "Grande Prairie")):
    W = BASE[0]
    t(ImageDraw.Draw(c), W / 2 if x is None else x, y, "  ·  ".join(items), f, fill, 0.4, "ms" if x is None else "ls")


def contact_row(c, y, f, ink, cols=(INDIGO, CHERRY), x=None):
    d = ImageDraw.Draw(c)
    items = [("mail", cols[0], "info@tinystars.ca"), ("pin", cols[1], ADDRESS)]
    widths = [42 + wid(s, f) for _, _, s in items]
    x = BASE[0] / 2 - (sum(widths) + 34) / 2 if x is None else x
    for (kind, col, s), w in zip(items, widths):
        icon(c, x + 16, y - 7, 32, col, kind)
        t(d, x + 42, y, s, f, ink)
        x += w + 34


# ---------- Christmas things ----------
def snow(c, n, seed, y0=0, y1=None, alpha=0.9, big=0):
    """Falling snow: many small flakes, a few soft big ones close to the lens."""
    W, H = BASE
    y1 = H if y1 is None else y1
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", c.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(y0, y1)
        r = rng.choice([1.3, 1.8, 2.4, 3.2, 4.3], p=[0.3, 0.3, 0.2, 0.13, 0.07])
        d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=(255, 255, 255, int(255 * alpha * rng.uniform(0.35, 1))))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(u(0.6))))
    if big:
        lay = Image.new("RGBA", c.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(lay)
        for _ in range(big):
            x, y, r = rng.uniform(0, W), rng.uniform(y0, y1), rng.uniform(8, 15)
            d.ellipse((u(x - r), u(y - r), u(x + r), u(y + r)), fill=(255, 255, 255, int(255 * rng.uniform(0.22, 0.4))))
        c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(u(4))))


def bez(p0, p1, p2, s):
    return ((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * p1[0] + s ** 2 * p2[0],
            (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * p1[1] + s ** 2 * p2[1])


def lights(c, p0, p1, p2, n, cols, wire=(26, 34, 28)):
    """A string of fairy lights: a thin wire with little glowing bulbs hanging from it."""
    pen(c, [bez(p0, p1, p2, s) for s in np.linspace(0, 1, 90)], wire, 2.4)
    for i in range(n):
        x, y = bez(p0, p1, p2, (i + 0.5) / n)
        col = cols[i % len(cols)]
        glow(c, x, y + 16, 48, col, 0.5)
        bw, bh = 13, 21
        b = Image.new("RGBA", (u(bw), u(bh)), (0, 0, 0, 0))
        db = ImageDraw.Draw(b)
        db.ellipse((0, 0, u(bw) - 1, u(bh) - 1), fill=col + (255,))
        db.ellipse((u(3.5), u(4), u(bw - 3.5), u(bh - 8)), fill=tuple(min(255, v + 80) for v in col) + (255,))
        b = b.rotate(float(np.random.default_rng(i).uniform(-14, 14)), Image.BICUBIC, expand=True)
        c.alpha_composite(b, (u(x) - b.width // 2, u(y + 6)))
        ImageDraw.Draw(c).rounded_rectangle((u(x - 4), u(y - 1), u(x + 4), u(y + 8)), u(2), fill=wire + (255,))


def ball(c, cx, cy, d, stops, string_top=None, cap=True):
    """A plain shiny Christmas ball, hung on a gold thread."""
    if string_top is not None:
        pen(c, [(cx, string_top), (cx, cy - d / 2 - 8)], (214, 176, 96), 2)
    m = Image.new("L", (u(d), u(d)), 0)
    ImageDraw.Draw(m).ellipse((0, 0, u(d) - 1, u(d) - 1), fill=255)
    b = inflate(m, u(d) * 0.5, stops, 90, gloss=1.0)
    O.shadow(c, m, (u(cx - d / 2), u(cy - d / 2)), u(10), (0, u(8)), 0.3)
    c.alpha_composite(b, (u(cx - d / 2), u(cy - d / 2)))
    if cap:
        cw, ch = d * 0.26, max(8, d * 0.13)
        g = ramp(u(cw), u(ch), [(0, (150, 104, 28)), (0.45, (255, 226, 140)), (1, (150, 104, 28))], 0)
        g.putalpha(O.rounded(u(cw), u(ch), u(3)))
        c.alpha_composite(g, (u(cx - cw / 2), u(cy - d / 2 - ch + 3)))


def bauble(c, name, cx, cy, d, crop=None, string_top=0):
    """A real photo as a Christmas bauble: round, gold-rimmed, glossy, hung from a gold thread with a cap."""
    pen(c, [(cx, string_top), (cx, cy - d / 2 - 30)], (222, 186, 104), 2.4)
    rim = 9
    n = u(d + 2 * rim)
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
    O.shadow(c, m, (u(cx) - n // 2, u(cy) - n // 2), u(18), (0, u(14)), 0.42)
    g = ramp(n, n, GOLD_RAMP, 60)
    g.putalpha(m)
    c.alpha_composite(g, (u(cx) - n // 2, u(cy) - n // 2))
    ph = picture(name, d, d, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    pm = Image.new("L", ph.size, 0)
    ImageDraw.Draw(pm).ellipse((0, 0, ph.width - 1, ph.height - 1), fill=255)
    # glass: a soft highlight up at the top left and a little shade round the bottom, as on a real bauble
    yy, xx = np.mgrid[0:ph.height, 0:ph.width].astype(np.float32) / ph.width
    hi = np.exp(-(((xx - 0.33) / 0.2) ** 2 + ((yy - 0.24) / 0.12) ** 2)) * 0.42
    lo = np.clip(np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / 0.5, 0, 1) ** 4 * 0.38
    a = np.asarray(ph.convert("RGB"), np.float32)
    a = a * (1 - lo[..., None]) + (255 - a * (1 - lo[..., None])) * hi[..., None]
    ph = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")
    ph.putalpha(pm)
    c.alpha_composite(ph, (u(cx) - ph.width // 2, u(cy) - ph.height // 2))
    cw, ch = d * 0.2, 30
    capg = ramp(u(cw), u(ch), [(0, (150, 104, 28)), (0.45, (255, 228, 146)), (1, (150, 104, 28))], 0)
    capg.putalpha(O.rounded(u(cw), u(ch), u(5)))
    ImageDraw.Draw(c).ellipse((u(cx - 10), u(cy - d / 2 - rim - ch - 14), u(cx + 10), u(cy - d / 2 - rim - ch + 6)),
                              outline=(222, 186, 104, 255), width=u(3))
    c.alpha_composite(capg, (u(cx - cw / 2), u(cy - d / 2 - rim - ch + 6)))


def leaf_mask(length, width):
    """A holly leaf, pointing right from (0, h/2): pointed ends and a spiky, scalloped edge."""
    L, Wd = u(length), u(width)
    ts = np.linspace(0, 1, 160)
    half = Wd / 2 * np.sin(np.pi * ts) ** 0.8 * (1 - 0.3 * np.abs(np.sin(4 * np.pi * ts)))
    top = [(t_ * L, Wd / 2 - h) for t_, h in zip(ts, half)]
    bot = [(t_ * L, Wd / 2 + h) for t_, h in zip(ts[::-1], half[::-1])]
    m = Image.new("L", (L, Wd), 0)
    ImageDraw.Draw(m).polygon(top + bot, fill=255)
    return m


def holly(c, cx, cy, s, turn=0):
    """A sprig of holly: two glossy leaves and three red berries."""
    n = u(2.4 * s)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ctr = n // 2
    for ang in (20, 145):
        lm = leaf_mask(s, s * 0.44)
        leaf = inflate(lm, lm.height * 0.28, [(0, (64, 156, 98)), (1, (12, 74, 46))], 90, gloss=0.7)
        dv = ImageDraw.Draw(leaf)
        dv.line((u(6), lm.height // 2, lm.width - u(8), lm.height // 2), fill=(150, 210, 160, 150), width=max(1, u(1.4)))
        big = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        big.alpha_composite(leaf, (ctr, ctr - lm.height // 2))
        lay.alpha_composite(big.rotate(ang, Image.BICUBIC, center=(ctr, ctr)))
    for dx, dy in ((-0.1, -0.06), (0.08, -0.1), (0.0, 0.08)):
        r = s * 0.12
        bm = Image.new("L", (u(2 * r), u(2 * r)), 0)
        ImageDraw.Draw(bm).ellipse((0, 0, bm.width - 1, bm.height - 1), fill=255)
        berry = inflate(bm, bm.width * 0.5, RED_PUFF, 90, gloss=1.0)
        lay.alpha_composite(berry, (ctr + u(dx * s) - bm.width // 2, ctr + u(dy * s) - bm.height // 2))
    lay = lay.rotate(turn, Image.BICUBIC)
    xy = (u(cx) - n // 2, u(cy) - n // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(6), (0, u(4)), 0.25)
    put(c, lay, *xy)


def band(c, x, y, w, h, stops, vertical=False, lift=0.25):
    """A strip of satin ribbon, with the sheen running along it."""
    b = ramp(u(w), u(h), stops, 0 if vertical else 90)
    if lift:
        O.shadow(c, Image.new("L", b.size, 255), (u(x), u(y)), u(8), (0, u(5)), lift)
    put(c, b, u(x), u(y))


def bow(c, cx, cy, s, stops):
    """A satin bow, puffed up and lit: two loops, two notched tails and a knot."""
    n = u(2.6 * s)
    ctr = n // 2
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    k = lambda v: u(v * s)  # noqa: E731
    tm = Image.new("L", (n, n), 0)
    for sx in (-1, 1):
        ImageDraw.Draw(tm).polygon([(ctr + sx * k(0.04), ctr), (ctr + sx * k(0.2), ctr - k(0.02)),
                                    (ctr + sx * k(0.66), ctr + k(0.98)), (ctr + sx * k(0.5), ctr + k(0.86)),
                                    (ctr + sx * k(0.38), ctr + k(1.04))], fill=255)
    lay.alpha_composite(inflate(tm, k(0.07), stops, 90, gloss=0.7))
    lm = Image.new("L", (n, n), 0)
    for sx in (-1, 1):
        e = Image.new("L", (n, n), 0)
        de = ImageDraw.Draw(e)
        de.ellipse((ctr - k(0.52), ctr - k(0.3), ctr + k(0.52), ctr + k(0.3)), fill=255)
        de.ellipse((ctr - k(0.2) + sx * k(0.1), ctr - k(0.09), ctr + k(0.26) + sx * k(0.1), ctr + k(0.1)), fill=0)
        e = e.rotate(sx * 22, Image.BICUBIC).transform(e.size, Image.AFFINE, (1, 0, -sx * k(0.48), 0, 1, k(0.16)))
        lm = ImageChops.lighter(lm, e)
    lay.alpha_composite(inflate(lm, k(0.1), stops, 90, gloss=0.9))
    km = Image.new("L", (n, n), 0)
    ImageDraw.Draw(km).rounded_rectangle((ctr - k(0.17), ctr - k(0.2), ctr + k(0.17), ctr + k(0.18)), k(0.08), fill=255)
    lay.alpha_composite(inflate(km, k(0.09), stops, 90, gloss=0.9))
    xy = (u(cx) - ctr, u(cy) - ctr)
    O.shadow(c, lay.getchannel("A"), xy, u(10), (0, u(8)), 0.35)
    put(c, lay, *xy)


def gift_tag(c, cx, cy, w, h, turn, lines, string_from=None, fill=(244, 228, 200)):
    """A paper gift tag with a gold eyelet, on a string, a few words written on it."""
    W_, H_ = u(w), u(h)
    m = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(m).polygon([(u(h * 0.34), 0), (W_, 0), (W_, H_), (u(h * 0.34), H_), (0, H_ / 2)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(u(3))).point(lambda v: 255 if v > 128 else 0)
    hx, hy = h * 0.3, h / 2
    lay = Image.new("RGBA", (W_, H_), fill + (255,))
    noise = np.random.default_rng(9).normal(0, 5, (H_, W_, 1))
    lay = Image.fromarray(np.clip(np.asarray(lay, np.float32) + np.concatenate([noise] * 3 + [np.zeros_like(noise)], 2),
                                  0, 255).astype(np.uint8))
    d = ImageDraw.Draw(lay)
    d.ellipse((u(hx - 13), u(hy - 13), u(hx + 13), u(hy + 13)), fill=GOLD + (255,))
    d.ellipse((u(hx - 7), u(hy - 7), u(hx + 7), u(hy + 7)), fill=(0, 0, 0, 0))
    m = ImageChops.multiply(m, Image.new("L", m.size, 255))
    ImageDraw.Draw(m).ellipse((u(hx - 7), u(hy - 7), u(hx + 7), u(hy + 7)), fill=0)
    for s, dy, f, col in lines:
        d.text((u((w + h * 0.62) / 2), u(dy)), s, font=f, fill=col, anchor="ms")
    lay.putalpha(m)
    lay = lay.rotate(turn, Image.BICUBIC, expand=True)
    # where the eyelet ends up after the turn, to tie the string to
    th = np.deg2rad(turn)
    lx, ly = hx - w / 2, hy - h / 2
    ex, ey = cx + lx * np.cos(th) + ly * np.sin(th), cy - lx * np.sin(th) + ly * np.cos(th)
    if string_from:
        mid = ((string_from[0] + ex) / 2 - 30, (string_from[1] + ey) / 2 + 40)
        pen(c, [bez(string_from, mid, (ex, ey), s) for s in np.linspace(0, 1, 50)], (232, 214, 170), 2.6)
    xy = (u(cx) - lay.width // 2, u(cy) - lay.height // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(12), (u(2), u(9)), 0.32)
    put(c, lay, *xy)


def globe(c, name, cx, cy, d, crop=None):
    """The room inside a snow globe: a glass ball full of snow on a gold base."""
    bw, bh = d * 0.74, d * 0.2
    base_y = cy + d * 0.42
    bm = Image.new("L", (u(bw), u(bh)), 0)
    ImageDraw.Draw(bm).polygon([(u(bw * 0.08), 0), (u(bw * 0.92), 0), (u(bw), u(bh)), (0, u(bh))], fill=255)
    bm = bm.filter(ImageFilter.GaussianBlur(u(2))).point(lambda v: 255 if v > 128 else 0)
    base = inflate(bm, u(bh) * 0.18, GOLD_PUFF, 90, gloss=0.8)
    O.shadow(c, bm, (u(cx - bw / 2), u(base_y)), u(20), (0, u(14)), 0.5)
    ph = picture(name, d, d, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    n = ph.width
    pm = Image.new("L", (n, n), 0)
    ImageDraw.Draw(pm).ellipse((0, 0, n - 1, n - 1), fill=255)
    inside = ph.copy()
    rng = np.random.default_rng(12)
    sl = Image.new("RGBA", (n, n), (255, 255, 255, 0))
    ds = ImageDraw.Draw(sl)
    for _ in range(170):
        x, y, r = rng.uniform(0, n), rng.uniform(0, n), u(rng.choice([1.6, 2.4, 3.4, 4.6]))
        ds.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(150, 250))))
    inside.alpha_composite(sl.filter(ImageFilter.GaussianBlur(u(0.6))))
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    rr = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) / 0.5
    a = np.asarray(inside.convert("RGB"), np.float32)
    edge = np.clip(rr, 0, 1) ** 5 * 0.5
    a = a * (1 - edge[..., None]) + np.array([200, 220, 255], np.float32) * edge[..., None]
    hi = np.exp(-(((xx - 0.3) / 0.16) ** 2 + ((yy - 0.2) / 0.08) ** 2)) * 0.6
    arc = np.exp(-((rr - 0.9) / 0.03) ** 2) * np.clip(-(xx - 0.5) - (yy - 0.5), 0, 1) * 1.2
    a += (255 - a) * np.clip(hi + arc, 0, 1)[..., None]
    gl = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")
    gl.putalpha(pm)
    O.shadow(c, pm, (u(cx) - n // 2, u(cy) - n // 2), u(24), (0, u(12)), 0.35)
    c.alpha_composite(gl, (u(cx) - n // 2, u(cy) - n // 2))
    c.alpha_composite(base, (u(cx - bw / 2), u(base_y)))
    return base_y + bh


def stripes(w, h, step, a, b, angle=45):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    th = np.deg2rad(angle)
    p = (xx * np.cos(th) + yy * np.sin(th)) / step
    k = ((p % 2) < 1)[..., None]
    img = np.where(k, np.array(a, np.float32), np.array(b, np.float32))
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")


def badge_logo(c, x, y, size):
    O.logo_badge(c, x, y, size)


def number(c, x, y, s, f, col=GOLD):
    """An advent-calendar door number: a little gold circle with a numeral."""
    r = 26
    m = Image.new("L", (u(2 * r), u(2 * r)), 0)
    ImageDraw.Draw(m).ellipse((0, 0, m.width - 1, m.height - 1), fill=255)
    g = ramp(m.width, m.height, GOLD_RAMP, 60)
    g.putalpha(m)
    O.shadow(c, m, (u(x - r), u(y - r)), u(6), (0, u(3)), 0.3)
    c.alpha_composite(g, (u(x - r), u(y - r)))
    ImageDraw.Draw(c).text((u(x), u(y + 1)), s, font=f, fill=WINE, anchor="mm")


def callout(c, x, y, lx, ly, label, f, side="l"):
    """A point on the photo, a line out to a label: what's where in the room."""
    pen(c, [(x, y), (lx, ly)], WHITE, 2.6)
    glow(c, x, y, 34, WHITE, 0.45)
    d = ImageDraw.Draw(c)
    d.ellipse((u(x - 13), u(y - 13), u(x + 13), u(y + 13)), fill=WHITE + (255,))
    d.ellipse((u(x - 7), u(y - 7), u(x + 7), u(y + 7)), fill=CHERRY + (255,))
    w = wid(label, f) + 36
    h = 46
    x0 = lx - w if side == "r" else lx
    panel(c, x0, ly - h / 2, w, h, h / 2, WHITE, lift=0.25)
    t(d, x0 + w / 2, ly + 8, label, f, INK, 0, "ms")


# ---------- the Christmas seven ----------
def x1(c):
    """Ornaments: the new room hung on the tree as three photo baubles, on a snowy night. Instrument Serif, Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, aurora(u(W), u(H), (16, 6, 34), [(0.85, 0.02, 0.5, (150, 18, 58), 0.85), (0.08, 0.32, 0.5, (70, 20, 128), 0.8),
                                            (0.5, 1.02, 0.62, (126, 12, 46), 0.8), (0.98, 0.66, 0.4, (64, 16, 112), 0.6)]),
        0, 0)
    snow(c, 300, 3, big=12)
    c.alpha_composite(logo(124), (u(36), u(26)))
    ball(c, 120, 300, 62, RED_PUFF, string_top=170)
    ball(c, 990, 500, 76, GOLD_PUFF, string_top=0)
    bauble(c, "IMG_1294", 300, 340, 258)
    bauble(c, "IMG_1308", 816, 316, 248)
    bauble(c, "IMG_1286", 558, 456, 230)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 650, "NOW OPEN  ·  OUR NEWEST ROOM", face(B, 22, 700), GOLD, 3.2, "ms")
    t(d, W / 2, 800, ROOM, fit_serif([ROOM], 900, 178), WHITE, -1, "ms")
    liquid(c, 44, 846, W - 88, 344, 48, blur=18, bend=32, tint=(26, 6, 40), alpha=0.36)
    S.pill_sticker(c, W / 2, 904, XMAS, face(B, 24, 700), CHERRY, WHITE, -2, h=54)
    f = fit(B, PROM, W - 170, 56, 760, -1.2)
    promise(c, W / 2, 1000, 64, f, WHITE, GOLD, -1.2, "ms")
    button(c, W / 2 - 330, 1088, 660, 82, CTA, WHITE, RUBY, face(B, 30, 700))
    footer(c, 1262, face(B, 21, 500), (226, 214, 236), items=(WEB, ADDRESS))


def x2(c):
    """Christmas card: an arched window onto the room, holly in the corners, a red and gold border. Instrument Serif,
    Fraunces."""
    W, H = BASE
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    grain = np.random.default_rng(4).normal(0, 3.2, (u(H), u(W))).astype(np.float32)
    a = np.asarray(c.convert("RGB"), np.float32) + grain[..., None]
    c.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((u(26), u(26), u(W - 26), u(H - 26)), u(18), outline=CHERRY + (255,), width=u(7))
    d.rounded_rectangle((u(42), u(42), u(W - 42), u(H - 42)), u(10), outline=DEEP_GOLD + (255,), width=u(2))
    lg = logo(118)
    c.alpha_composite(lg, (u(W / 2) - lg.width // 2, u(58)))
    tile(c, "IMG_1294", 170, 178, 740, 540, label=False, shape="arch")
    d.arc((u(170 - 10), u(178 - 10), u(910 + 10), u(178 + 740 + 10)), 180, 360, fill=DEEP_GOLD + (255,), width=u(3))
    d.line((u(160), u(548), u(160), u(718)), fill=DEEP_GOLD + (255,), width=u(3))
    d.line((u(920), u(548), u(920), u(718)), fill=DEEP_GOLD + (255,), width=u(3))
    holly(c, 112, 118, 92, -20)
    holly(c, W - 112, H - 118, 92, 160)
    F = "Fraunces"
    t(d, W / 2, 790, "OUR NEWEST ROOM IS OPEN", face(F, 22, 600, opsz=12), PINE, 3.6, "ms")
    t(d, W / 2, 920, ROOM, fit_serif([ROOM], 820, 168), CHERRY, -1, "ms")
    for x in (W / 2 - 150, W / 2 + 150):
        d.line((u(x - 110), u(962), u(x + 110), u(962)), fill=DEEP_GOLD + (255,), width=u(2))
    sparkle(c, W / 2, 962, 26, DEEP_GOLD)
    t(d, W / 2, 1018, XMAS.upper(), face(F, 20, 700, opsz=12), CHERRY, 3.2, "ms")
    f = fit(F, PROM, W - 200, 44, 500, -0.6, opsz=40)
    promise(c, W / 2, 1072, 54, f, INK, CHERRY, -0.6, "ms")
    S.button(c, W / 2 - 300, 1152, 600, 78, CTA, CHERRY, WHITE, face(F, 27, 650, opsz=24))
    footer(c, 1286, face(F, 19, 500, opsz=12), SOFT, items=(WEB, ADDRESS))


def x3(c):
    """Gift wrap: a new room to unwrap. Red paper with little gold stars, a satin ribbon and a bow, a gift tag.
    Unbounded, Caveat, Bricolage."""
    W, H = BASE
    U, B, C = "Unbounded", "BricolageGrotesque", "Caveat"
    put(c, ramp(u(W), u(H), [(0, (214, 32, 60)), (1, (132, 8, 34))], 90), 0, 0)
    pat = Image.new("RGBA", c.size, (0, 0, 0, 0))
    for j, y in enumerate(range(30, 960, 78)):
        for x in range(30 + (j % 2) * 39, W, 78):
            sparkle(pat, x, y, 16, (255, 214, 130))
    pat.putalpha(pat.getchannel("A").point(lambda v: int(v * 0.22)))
    c.alpha_composite(pat)
    glow(c, 260, 220, 520, (255, 96, 110), 0.3)
    badge_logo(c, 40, 34, 104)
    d = ImageDraw.Draw(c)
    f = fit(U, ["A new room", "to unwrap."], 640, 78, 800, -2)
    stack(d, 48, 258, ["A new room", "to unwrap."], f, WHITE, 92, -2)
    t(d, 52, 388, f"{ROOM} is now open", face(B, 32, 700), GOLD, 0)
    band(c, 0, 438, W, 74, GOLD_SATIN)
    band(c, 762, 0, 74, 920, GOLD_SATIN, vertical=True)
    card(c, "IMG_1294", 352, 690, 560, 400, -4, border=14, r=22)
    gift_tag(c, 846, 742, 330, 156, 10, [("To: your little star", 70, face(C, 34, 700), (90, 40, 30)),
                                         ("From: Tiny Stars", 116, face(C, 34, 700), CHERRY)], string_from=(799, 500))
    bow(c, 799, 475, 120, GOLD_PUFF)
    panel(c, 40, 920, W - 80, 380, 40, CREAM, lift=0.35)
    S.pill_sticker(c, W / 2, 978, XMAS, face(B, 24, 700), CHERRY, WHITE, 0, h=54)
    f = fit(B, PROM, W - 170, 54, 760, -1.2)
    promise(c, W / 2, 1070, 62, f, INK, CHERRY, -1.2, "ms")
    button(c, W / 2 - 320, 1150, 640, 80, CTA, CHERRY, WHITE, face(B, 30, 700))
    footer(c, 1272, face(B, 20, 500), SOFT, items=(WEB, ADDRESS))


def stack(d, x, y, lines, f, fill, lead, track=0.0, anchor="ls"):
    S.stack(d, x, y, lines, f, fill, lead, track, anchor)


def x4(c):
    """Garland: polaroids of the room hung on a string of fairy lights, on deep pine green. Caveat, Instrument Serif,
    Bricolage."""
    W, H = BASE
    B, C = "BricolageGrotesque", "Caveat"
    put(c, aurora(u(W), u(H), (8, 38, 30), [(0.5, 0.0, 0.6, (24, 92, 66), 0.8), (0.0, 0.9, 0.5, (6, 26, 22), 0.9),
                                            (1.0, 0.95, 0.5, (90, 16, 32), 0.55)]), 0, 0)
    snow(c, 160, 8, alpha=0.6, big=6)
    c.alpha_composite(logo(118), (u(36), u(24)))
    d = ImageDraw.Draw(c)
    t(d, W - 50, 86, "Merry Christmas!", face(C, 52, 700), GOLD, 0, "rs")
    p0, p1, p2 = (-30, 196), (540, 360), (1110, 180)
    warm = [(255, 214, 140), (255, 92, 92), (255, 196, 90), (255, 236, 200)]
    for name, x, turn, cap, tape in [("IMG_1294", 210, -6, "play kitchen", (255, 150, 150)),
                                     ("IMG_1286", 540, 2, "sand & diggers", (255, 220, 140)),
                                     ("IMG_1308", 870, 7, "story corner", (170, 220, 180))]:
        s = (x + 30) / 1140
        y = bez(p0, p1, p2, s)[1]
        polaroid(c, name, x, y + 196, 262, turn, cap, tape)
    lights(c, p0, p1, p2, 15, warm)
    t(d, W / 2, 736, "our new room is open!", face(C, 60, 700), (236, 244, 236), 0, "ms")
    t(d, W / 2, 870, ROOM, fit_serif([ROOM], 860, 156), WHITE, -1, "ms")
    t(d, W / 2, 934, XMAS.upper(), face(B, 21, 700), GOLD, 3.4, "ms")
    f = fit(B, PROM, W - 150, 54, 760, -1.2)
    promise(c, W / 2, 1006, 62, f, WHITE, GOLD, -1.2, "ms")
    button(c, W / 2 - 330, 1090, 660, 84, CTA, GOLD, FOREST, face(B, 31, 750))
    footer(c, 1262, face(B, 21, 500), (200, 222, 208), items=(WEB, ADDRESS))


def x5(c):
    """Snow globe: the new room inside a snow globe on a night of falling snow. Instrument Serif, Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, ramp(u(W), u(H), [(0, (14, 10, 44)), (0.6, (48, 12, 64)), (1, (96, 12, 46))], 90), 0, 0)
    glow(c, W / 2, 470, 520, (120, 60, 200), 0.45)
    glow(c, W / 2, 900, 520, (220, 40, 70), 0.3)
    snow(c, 240, 21, big=10)
    c.alpha_composite(logo(118), (u(36), u(24)))
    liquid_pill(c, W - 48 - 120, 84, XMAS, face(B, 24, 650), h=58, alpha=0.12)
    bottom = globe(c, "IMG_1291", W / 2, 452, 540, crop=(0.45, 0.6, 1.0))
    holly(c, W / 2 - 196, bottom - 70, 66, 8)
    holly(c, W / 2 + 200, bottom - 64, 56, 190)
    d = ImageDraw.Draw(c)
    t(d, W / 2, bottom - 30, "R E D   N O V A", face(B, 20, 800), (110, 66, 10), 1, "ms")
    t(d, W / 2, 940, "Our newest room is open", fit_serif(["Our newest room is open"], 940, 92), WHITE, -0.5, "ms")
    f = fit(B, PROM, W - 150, 52, 760, -1.2)
    promise(c, W / 2, 1022, 60, f, (244, 236, 250), GOLD, -1.2, "ms")
    button(c, W / 2 - 330, 1110, 660, 82, CTA, WHITE, RUBY, face(B, 30, 700))
    footer(c, 1262, face(B, 21, 500), (214, 202, 230), items=(WEB, ADDRESS))


def x6(c):
    """Candy cane: big puffy 'NOW OPEN' letters on soft candy stripes, photo stickers, a holographic star. Unbounded,
    Instrument Serif, Bricolage."""
    W, H = BASE
    U, B = "Unbounded", "BricolageGrotesque"
    put(c, stripes(u(W), u(H), u(44), (255, 230, 234), (255, 250, 250)), 0, 0)
    glow(c, W / 2, 1230, 760, (255, 255, 255), 0.85)
    c.alpha_composite(logo(118), (u(36), u(24)))
    S.pill_sticker(c, 850, 84, f"{XMAS}  ·  new families", face(B, 23, 700), CHERRY, WHITE, 3)
    puffy(c, W / 2, 322, ["NOW OPEN"], fit(U, ["NOW OPEN"], 940, 150, 900, -2), 0, RED_PUFF, drop=(120, 10, 34))
    d = ImageDraw.Draw(c)
    t(d, W / 2, 410, f"{ROOM}, our newest room", fit_serif([f"{ROOM}, our newest room"], 800, 66), RUBY, -0.4, "ms")
    card(c, "IMG_1291", 240, 660, 300, 360, -6, border=12, r=26)
    card(c, "IMG_1294", 552, 622, 360, 290, 2, border=12, r=26)
    card(c, "IMG_1286", 860, 668, 290, 340, 7, border=12, r=26)
    holo_star(c, 996, 860, 132, 14)
    holly(c, 90, 860, 74, 10)
    f = fit(B, PROM, W - 150, 54, 800, -1.2)
    promise(c, W / 2, 970, 64, f, INK, CHERRY, -1.2, "ms")
    puffy_button(c, W / 2 - 340, 1068, 680, 94, CTA, [(0, (236, 50, 74)), (1, (150, 10, 40))], face(B, 32, 700))
    footer(c, 1262, face(B, 21, 500), SOFT, items=(WEB, ADDRESS))


def x7(c):
    """Advent calendar: the room behind numbered doors, a title door and a promise door, on deep wine red.
    Instrument Serif, Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, ramp(u(W), u(H), [(0, (112, 12, 40)), (1, (58, 6, 24))], 90), 0, 0)
    snow(c, 120, 30, alpha=0.5)
    badge_logo(c, 40, 30, 96)
    liquid_pill(c, W - 48 - 120, 80, XMAS, face(B, 24, 650), h=58, alpha=0.12)
    x0, gap, cw, rh, y0 = 40, 14, (W - 80 - 28) / 3, 222, 160
    fn = face(B, 26, 800)

    def cell(col, row, span=1, rows=1):
        return x0 + col * (cw + gap), y0 + row * (rh + gap), cw * span + gap * (span - 1), rh * rows + gap * (rows - 1)

    x, y, w, h = cell(0, 0, 2)
    tl = ramp(u(w), u(h), [(0, (230, 44, 70)), (1, (150, 12, 40))], 30)
    tl.putalpha(O.rounded(u(w), u(h), u(26)))
    c.alpha_composite(tl, (u(x), u(y)))
    d = ImageDraw.Draw(c)
    t(d, x + 34, y + 62, "NOW OPEN", face(B, 22, 800), GOLD, 3.2)
    t(d, x + 30, y + 170, ROOM, fit_serif([ROOM], w - 70, 132), WHITE, -1)
    t(d, x + 34, y + 204, "our newest room", face(B, 24, 600), (255, 222, 226))
    for name, (cc, rr, sp), num in [("IMG_1286", (2, 0, 1), "1"), ("IMG_1294", (0, 1, 2), "7"),
                                    ("IMG_1308", (2, 1, 1), "12"), ("IMG_1310", (0, 2, 1), "18"),
                                    ("IMG_1291", (2, 2, 1), "24")]:
        x, y, w, h = cell(cc, rr, sp)
        tile(c, name, x, y, w, h, 26, label=True, star=None)
        number(c, x + w - 38, y + 38, num, fn)
    x, y, w, h = cell(1, 2)
    panel(c, x, y, w, h, 26, (255, 240, 214), lift=0)
    st = Image.new("RGBA", (u(130), u(130)), GOLD + (255,))
    st.putalpha(star(130, 0.52))
    c.alpha_composite(st, (u(x + w / 2 - 65), u(y + 26)))
    t(d, x + w / 2, y + 196, "brand new!", face("Caveat", 44, 700), RUBY, 0, "ms")
    x, y, w, h = cell(0, 3, 3)
    panel(c, x, y, w, h, 26, CREAM, lift=0)
    t(d, W / 2, y + 62, f"{XMAS.upper()}  ·  FOR NEW FAMILIES", face(B, 21, 800), CHERRY, 3, "ms")
    f = fit(B, PROM, w - 70, 54, 800, -1.2)
    promise(c, W / 2, y + 132, 62, f, INK, CHERRY, -1.2, "ms")
    button(c, W / 2 - 330, 1124, 660, 82, CTA, WHITE, RUBY, face(B, 30, 700))
    footer(c, 1268, face(B, 21, 500), (246, 214, 222), items=(WEB, ADDRESS))


# ---------- the six for any time ----------
def r1(c):
    """Grand opening: the room with a red satin ribbon and bow across it, ready to cut; the offer on warm white below.
    Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    c.alpha_composite(picture("IMG_1294", W, 740, 0.5, 0.5, 1.0, lift=0.16), (0, 0))
    shade(c, 0, 230, (20, 8, 16), 0.42, 0.0)
    badge_logo(c, 40, 34, 104)
    band(c, 0, 706, W, 70, RED_SATIN, lift=0.35)
    bow(c, W / 2, 738, 128, RED_PUFF)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 958, "GRAND OPENING  ·  OUR NEWEST ROOM", face(B, 22, 800), CHERRY, 3.2, "ms")
    t(d, W / 2, 1050, f"{ROOM} is open.", fit(B, [f"{ROOM} is open."], W - 120, 92, 800, -3), INK, -3, "ms")
    f = fit(B, PROM, W - 170, 40, 500, -0.4)
    t(d, W / 2, 1114, PROM[0], f, SOFT, -0.4, "ms")
    accent(c, W / 2, 1162, PROM[1], "refund", f, SOFT, CHERRY, -0.4, "ms")
    button(c, W / 2 - 320, 1196, 640, 80, CTA, CHERRY, WHITE, face(B, 29, 700))
    footer(c, 1318, face(B, 19, 500), SOFT, items=(WEB, ADDRESS))


def r2(c):
    """Liquid glass over an aurora of red and purple, a bento of the room. Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, aurora(u(W), u(H), (30, 6, 30), [(0.9, 0.08, 0.55, (226, 34, 64), 0.9), (0.05, 0.3, 0.5, (124, 40, 200), 0.85),
                                            (0.15, 1.0, 0.6, (250, 150, 80), 0.75), (0.98, 0.92, 0.5, (210, 30, 90), 0.7),
                                            (0.55, 0.6, 0.4, (90, 20, 120), 0.6)]), 0, 0)
    tile(c, "IMG_1291", 48, 196, 500, 556, 38, label=False)
    tile(c, "IMG_1294", 562, 196, 470, 270, 38, star=CHERRY)
    tile(c, "IMG_1286", 562, 480, 470, 272, 38, label=False)
    c.alpha_composite(logo(124), (u(44), u(34)))
    liquid_pill(c, W - 48 - 176, 98, "New room  ·  now open", face(B, 24, 600), h=62, alpha=0.12)
    liquid(c, 36, 690, W - 72, 524, 54, blur=20, bend=36, tint=(40, 6, 30), alpha=0.34)
    d = ImageDraw.Draw(c)
    x = 80
    t(d, x, 790, "Say hello to", face(B, 46, 500), (250, 230, 236), -0.4)
    t(d, x - 4, 912, f"{ROOM}.", face(B, 132, 800), WHITE, -4)
    f = fit(B, PROM, W - 2 * x, 42, 600, -0.6)
    t(d, x, 984, PROM[0], f, (248, 232, 240), -0.6)
    accent(c, x, 1034, PROM[1], "refund", f, (248, 232, 240), GOLD, -0.6)
    button(c, x, 1084, W - 2 * x, 92, CTA, WHITE, RUBY, face(B, 33, 700))
    for cx, s in zip([W / 2 - 300, W / 2, W / 2 + 290], ["Now enrolling", "Grande Prairie", WEB]):
        liquid_pill(c, cx, 1276, s, face(B, 22, 600), h=54, alpha=0.1)


def r3(c):
    """Cover: the new room as a magazine cover, cover lines with round photos, a star badge, a barcode. Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    c.alpha_composite(picture("IMG_1291", W, H, 0.45, 0.55, 1.0, lift=0.16), (0, 0))
    shade(c, 0, 420, (24, 6, 20), 0.66, 0.0)
    side_shade(c, 330, 980, 620, (24, 6, 20), 0.6)
    shade(c, 700, H, (24, 6, 20), 0.0, 0.94)
    d = ImageDraw.Draw(c)
    mast = fit(B, ["TINY STARS"], W - 80, 240, 800, -5, wdth=75)
    t(d, W / 2, 228, "TINY STARS", mast, WHITE, -5, "ms")
    t(d, W / 2, 274, "THE NEW ROOM ISSUE   ·   RED NOVA   ·   NOW OPEN", face(B, 18, 700), WHITE, 2.4, "ms")
    lg = logo(112)
    c.alpha_composite(lg, (u(W - 44) - lg.width, u(300)))
    for i, n in enumerate(["IMG_1294", "IMG_1308", "IMG_1286", "IMG_1312"]):
        y = 372 + i * 100
        round_photo(c, n, 92, y, 76)
        glow_text(c, 148, y + 12, LABELS[n], face(B, 34, 750), WHITE, -0.3)
    S.sticker(c, 870, 610, 300, [("NOW", -14, face(B, 52, 800, wdth=75)), ("OPEN", 38, face(B, 52, 800, wdth=75))],
              -10, fill=CHERRY)
    glow_text(c, 52, 966, LEAD, face(B, 46, 500), (246, 234, 240), -0.4)
    f = fit(B, BIG, W - 96, 116, 800, -3)
    accent(c, 46, 1076, BIG[0], "refund", f, WHITE, GOLD, -3)
    t(d, 46, 1176, BIG[1], f, WHITE, -3)
    button(c, 52, 1222, 640, 88, CTA, WHITE, RUBY, face(B, 31, 700))
    bx, by, bw, bh = 742, 1222, 290, 88
    panel(c, bx, by, bw, bh, 10, WHITE, lift=0)
    rng = np.random.default_rng(31)
    xx = bx + 16
    while xx < bx + bw - 18:
        wbar = float(rng.choice([2, 2, 3, 4, 6]))
        d.rectangle((u(xx), u(by + 12), u(xx + wbar), u(by + bh - 30)), fill=INK)
        xx += wbar + float(rng.choice([2, 3, 4]))
    t(d, bx + bw / 2, by + bh - 9, WEB, face(B, 18, 700), INK, 1.2, "ms")


def r4(c):
    """Scrapbook: taped polaroids of the room with handwritten captions, 'refund' circled in pen, a sticky note.
    Caveat, Bricolage."""
    W, H = BASE
    B, C = "BricolageGrotesque", "Caveat"
    PEN = (58, 30, 50)
    c.paste((252, 248, 242, 255), (0, 0, u(W), u(H)))
    glow(c, 900, 140, 520, (255, 222, 226), 0.6)
    glow(c, 120, 1250, 520, (255, 232, 214), 0.55)
    dot_grid(c, 34, (230, 214, 214, 255))
    c.alpha_composite(logo(118), (u(42), u(30)))
    d = ImageDraw.Draw(c)
    t(d, W - 56, 92, "new room alert!", face(C, 48, 700), CHERRY, 0, "rs")
    pen(c, [(W - 330 + i * 7, 108 + 4 * np.sin(i * 0.9)) for i in range(40)], CHERRY, 3.5)
    polaroid(c, "IMG_1294", 220, 400, 290, -7, "play kitchen!", (255, 190, 196))
    polaroid(c, "IMG_1308", 540, 372, 290, 3, "story corner", (206, 226, 255))
    polaroid(c, "IMG_1286", 860, 410, 290, 8, "sand & diggers", (255, 230, 150))
    doodle_star(c, 72, 640, 46, S.SUN, seed=1)
    doodle_star(c, 1020, 660, 38, CHERRY, seed=2)
    heart(c, 400, 640, 26, CHERRY)
    t(d, 56, 744, f"{ROOM} is open! love your first month, or...", fit(C, [f"{ROOM} is open! love your first month, or..."],
                                                                      W - 110, 60, 700), PEN, 0)
    BIG2 = ["we'll  refund  your", "parent portion."]
    f = fit(B, BIG2, 880, 112, 800, -3)
    t(d, 50, 862, BIG2[0], f, RUBY, -3)
    pre = wid("we'll  ", f, -3)
    wr = wid("refund", f, -3)
    sz = f.size / O.S
    loop_around(c, 50 + pre + 12, 862 - sz * 0.7, 50 + pre + wr - 16, 862 + sz * 0.02, CHERRY, 5.5)
    t(d, 50, 966, BIG2[1], f, RUBY, -3)
    ramp_button(c, 56, 1030, 560, 90, CTA, [(0, (236, 50, 74)), (1, (150, 10, 40))], WHITE, face(B, 30, 650))
    note = Image.new("RGBA", (u(290), u(250)), (255, 234, 128, 255))
    nd = ImageDraw.Draw(note)
    for k, s in enumerate(["come take", "a peek", "this week!"]):
        nd.text((note.width / 2, u(80 + k * 60)), s, font=face(C, 54, 700), fill=PEN, anchor="ms")
    curl = Image.new("RGBA", note.size, (0, 0, 0, 0))
    ImageDraw.Draw(curl).polygon([(note.width, note.height - u(40)), (note.width, note.height),
                                  (note.width - u(40), note.height)], fill=(236, 206, 96, 255))
    note.alpha_composite(curl)
    stick(c, note, 852, 1120, 5)
    heart(c, 980, 1006, 22, CHERRY)
    pen_arrow(c, (690, 1210), (640, 1250), (560, 1150), PEN)
    t(d, 58, 1186, f"{WEB}  ·  Grande Prairie", face(C, 40, 650), PEN)
    contact_row(c, 1307, face("DMSans", 21, 600), INK, cols=(RUBY, S.ORANGE), x=56)


def pen_arrow(c, p0, p1, p2, col):
    from offer_modern import arrow
    arrow(c, p0, p1, p2, col)


def r5(c):
    """Clean bento: say hello to Red Nova, five photos of the room in a tidy grid, the promise on a soft card.
    Inter Tight."""
    W, H = BASE
    I = "InterTight"
    c.paste((251, 250, 248, 255), (0, 0, u(W), u(H)))
    c.alpha_composite(logo(112), (u(40), u(30)))
    d = ImageDraw.Draw(c)
    pw = wid("Now open", face(I, 24, 700)) + 64
    panel(c, W - 40 - pw, 62, pw, 52, 26, (255, 232, 236), lift=0)
    d.ellipse((u(W - 40 - pw + 24), u(82), u(W - 40 - pw + 36), u(94)), fill=CHERRY + (255,))
    t(d, W - 40 - pw + 46, 96, "Now open", face(I, 24, 700), RUBY)
    f = face(I, 96, 800)
    t(d, 40, 262, "Say hello to", f, INK, -3.5)
    t(d, 40, 360, f"{ROOM}.", f, CHERRY, -3.5)
    tile(c, "IMG_1294", 40, 404, 648, 384, 28, star=CHERRY)
    tile(c, "IMG_1291", 702, 404, 338, 590, 28)
    tile(c, "IMG_1286", 40, 802, 317, 192, 28)
    tile(c, "IMG_1308", 371, 802, 317, 192, 28)
    panel(c, 40, 1012, W - 80, 160, 28, (255, 236, 238), lift=0)
    fp = fit(I, PROM, W - 160, 42, 700, -1)
    t(d, 80, 1078, PROM[0], fp, INK, -1)
    accent(c, 80, 1130, PROM[1], "refund", fp, INK, CHERRY, -1)
    button(c, 40, 1190, W - 80, 86, CTA, CHERRY, WHITE, face(I, 31, 700))
    footer(c, 1320, face(I, 19, 500), SOFT, items=(WEB, ADDRESS))


def r6(c):
    """Room tour: a big photo of the room with what's where pointed out, then the offer on deep plum. Bricolage."""
    W, H = BASE
    B = "BricolageGrotesque"
    c.paste((28, 12, 26, 255), (0, 0, u(W), u(H)))
    glow(c, W / 2, 1200, 700, (120, 14, 44), 0.6)
    c.alpha_composite(picture("IMG_1294", W, 810, 0.5, 0.5, 1.0, lift=0.16), (0, 0))
    shade(c, 0, 220, (20, 8, 16), 0.45, 0.0)
    shade(c, 610, 812, (28, 12, 26), 0.0, 1.0)
    badge_logo(c, 40, 34, 100)
    f = face(B, 23, 700)
    callout(c, 540, 500, 700, 600, "Play kitchen", f)
    callout(c, 742, 140, 880, 250, "Sunny mural", f)
    callout(c, 442, 336, 300, 420, "Cozy hideout", f, side="r")
    callout(c, 676, 404, 860, 440, "Little tables", f)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 870, "TAKE A PEEK INSIDE OUR NEWEST ROOM", face(B, 21, 800), GOLD, 3.2, "ms")
    t(d, W / 2, 970, f"{ROOM} is open.", fit(B, [f"{ROOM} is open."], W - 120, 96, 800, -3), WHITE, -3, "ms")
    fp = fit(B, PROM, W - 170, 42, 600, -0.6)
    t(d, W / 2, 1040, PROM[0], fp, (236, 222, 232), -0.6, "ms")
    accent(c, W / 2, 1090, PROM[1], "refund", fp, (236, 222, 232), GOLD, -0.6, "ms")
    button(c, W / 2 - 330, 1132, 660, 84, CTA, CHERRY, WHITE, face(B, 31, 700))
    footer(c, 1280, face(B, 21, 500), (200, 182, 196), items=(WEB, ADDRESS))


SAMPLES = {1: x1, 2: x2, 3: x3, 4: x4, 5: x5, 6: x6, 7: x7, 8: r1, 9: r2, 10: r3, 11: r4, 12: r5, 13: r6}
SHEETS = {"rednova_ads_christmas.jpg": range(1, 8), "rednova_ads_anytime.jpg": range(8, 14)}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"rednova_ad_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"rednova_ad_{i}.jpg", flush=True)
    return out


def main():
    picks = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(SAMPLES)
    outs = {}
    for i in picks:
        outs[i] = render(i)
    for name, group in SHEETS.items():
        group = list(group)
        if not all(i in outs for i in group):
            continue
        cols = 4 if len(group) > 6 else 3
        rows = (len(group) + cols - 1) // cols
        tw, th = 540, 675
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 24, rows * (th + 64) + 24), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(group):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 10), f"Sample {i}", font=f, fill=INK)
        sheet.save(OUT / name, quality=90)
        print("wrote", OUT / name, flush=True)


if __name__ == "__main__":
    main()
