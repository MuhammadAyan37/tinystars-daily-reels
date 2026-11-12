"""Four all-out modern takes on the offer (samples 19 to 22), each built on a look people like right now.

  19  Liquid glass: real photos under panes of glass that bend the light at their edges, over a soft aurora of the
      logo's colours, with a trail of sparkles like a wand has passed.
  20  Puffy 3D: the promise blown up into glossy balloon letters, photo stickers on a pastel check, a holographic star.
  21  Cover: the stained-glass classroom as a magazine cover, cover lines with little round photos, a star badge and a
      barcode.
  22  Scrapbook: taped polaroids with handwritten captions on dot-grid paper, the word "refund" circled by hand and the
      $100 off on a sticky note.

Every one says the same thing in the same order as samples 13 to 18: the promise (not happy in the first month? we'll
refund your registration) biggest, then $100 off your first 2 months, then how to book. The photos are the daycare's
own, blurred wherever a face shows (photos.py). Drawn at well over the delivered size and scaled down, so it stays sharp.

Usage: python -I edits/offer_modern.py [19 20 21 22]   (all four when none is named)
  -> exports/offer_sample_<n>.jpg     1440 x 1800 (4:5)
  -> exports/offer_samples_modern.jpg the four side by side
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import offer_samples as S  # noqa: E402
from offer_samples import (A2, AGES, BASE, CROPS, EXTRA, INDIGO, INK, LABELS, LIFT, LILAC, MAGENTA, OUT, PHONE,  # noqa
                           PINK_RAMP, Q, SIZE, SOFT, SS, SUN, WEB, WHITE, accent, button, card, chip, die_cut, face, fit,
                           glow, icon, logo, panel, picture, put, ramp, sparkle, stack, star, stick, sticker, t, tile, u)

VIOLET = (124, 58, 220)
CORAL = (255, 122, 118)
PEN = (58, 34, 86)
CROPS.update({"g02_cover": (0.62, 0.5, 1.0)})


# ---------- effects ----------
def aurora(w, h, base, blobs):
    """A soft mesh of coloured light: big, blurred pools of colour over a base (positions and sizes as fractions)."""
    sw, sh = max(8, w // 8), max(8, h // 8)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    img = np.ones((sh, sw, 3), np.float32) * np.array(base, np.float32)
    for bx, by, r, col, a in blobs:
        k = np.exp(-(((xx - bx * sw) ** 2 + (yy - by * sh) ** 2) / (r * sw) ** 2) * 2.2)[..., None] * a
        img = img * (1 - k) + np.array(col, np.float32) * k
    big = np.asarray(Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                     np.float32)
    big += np.random.default_rng(5).random(big.shape, np.float32) - 0.5  # dither, so the soft ramps never band
    return Image.fromarray(np.clip(big + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")


def liquid(c, x, y, w, h, r, blur=16, bend=30, tint=(255, 255, 255), alpha=0.14, shade=0.25):
    """A pane of liquid glass: what's behind it, softened, and bent at the rounded edge the way thick glass bends light,
    with a hint of colour fringing, a bright rim where the edge faces the light and a soft shadow."""
    X, Y, Wp, Hp = u(x), u(y), u(w), u(h)
    m = u(bend)
    x0, y0, x1, y1 = max(0, X - m), max(0, Y - m), min(c.width, X + Wp + m), min(c.height, Y + Hp + m)
    src = np.asarray(c.crop((x0, y0, x1, y1)).convert("RGB").filter(ImageFilter.GaussianBlur(u(blur))), np.float32)
    mask = np.asarray(O.rounded(Wp, Hp, u(r)), np.uint8)
    dist = cv2.distanceTransform((mask > 127).astype(np.uint8), cv2.DIST_L2, 5)
    gx = cv2.Sobel(dist, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(dist, cv2.CV_32F, 0, 1, ksize=5)
    n = np.sqrt(gx * gx + gy * gy) + 1e-6
    gx, gy = gx / n, gy / n
    k = np.clip(1 - dist / m, 0, 1) ** 2.2
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
    out = np.empty((Hp, Wp, 3), np.float32)
    for ch, s in zip(range(3), (1.07, 1.0, 0.93)):
        mx = xx + (X - x0) - gx * k * m * 0.85 * s
        my = yy + (Y - y0) - gy * k * m * 0.85 * s
        out[..., ch] = cv2.remap(src[..., ch], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    out = out * (1 - alpha) + np.array(tint, np.float32) * alpha
    facing = np.clip(-(gx * -0.55 + gy * -0.83), 0, 1)  # the top-left edge catches the light
    rim = np.exp(-(dist / u(1.5)) ** 2) * (0.3 + 0.7 * facing) * 0.9 + k * 0.09 * (0.4 + 0.6 * facing)
    out += (255 - out) * np.clip(rim, 0, 1)[..., None]
    pane = Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")
    pane.putalpha(Image.fromarray(mask))
    if shade:
        O.shadow(c, Image.fromarray(mask), (X, Y), u(22), (0, u(12)), shade)
    c.alpha_composite(pane, (X, Y))


def liquid_pill(c, cx, cy, label, f, h=58, pad=30, fg=WHITE, **kw):
    w = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(label, font=f) / O.S + 2 * pad
    liquid(c, cx - w / 2, cy - h / 2, w, h, h / 2, blur=10, bend=14, shade=0.14, **kw)
    ImageDraw.Draw(c).text((u(cx), u(cy)), label, font=f, fill=fg, anchor="mm")
    return w


def inflate(mask, depth, stops, angle=90, gloss=0.95):
    """Shade a flat shape as if it were blown up like a balloon: a rounded height from its distance to the edge, lit
    from the top left, with a glossy highlight. mask: an L image; returns an RGBA image of the same size."""
    M = np.asarray(mask, np.uint8)
    dist = cv2.distanceTransform((M > 127).astype(np.uint8), cv2.DIST_L2, 5)
    tt = np.clip(dist / depth, 0, 1)
    hgt = np.sqrt(np.clip(1 - (1 - tt) ** 2, 0, 1)) * depth
    hgt = cv2.GaussianBlur(hgt, (0, 0), max(1.0, depth * 0.22))
    nx = -cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) / 8
    ny = -cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) / 8
    nn = np.sqrt(nx * nx + ny * ny + 1)
    nx, ny, nz = nx / nn, ny / nn, 1 / nn
    L = np.array([-0.45, -0.7, 0.56], np.float32)
    L /= np.linalg.norm(L)
    Hv = L + np.array([0, 0, 1], np.float32)
    Hv /= np.linalg.norm(Hv)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    nh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)
    base = np.asarray(ramp(M.shape[1], M.shape[0], stops, angle).convert("RGB"), np.float32)
    col = base * (0.55 + 0.75 * diff)[..., None] * (0.74 + 0.26 * np.sqrt(tt))[..., None]
    col += (base * 1.15 - col) * (np.clip(ny, 0, 1) * (1 - nz) * 0.5)[..., None]  # light bouncing up under the curve
    col += (255 - col) * np.clip(nh ** 50 * gloss + nh ** 10 * 0.2, 0, 1)[..., None]
    out = Image.fromarray(np.clip(col + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(mask)
    return out


def puffy(c, x, y, lines, f, lead, stops, anchor="ms", depth=0.12, drop=(70, 20, 104)):
    """Big balloon lettering: each line inflated and lit, on a soft shadow."""
    m = Image.new("L", c.size, 0)
    d = ImageDraw.Draw(m)
    for k, s in enumerate(lines):
        d.text((u(x), u(y + k * lead)), s, font=f, fill=255, anchor=anchor)
    bb = m.getbbox()
    pad = u(30)
    box = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(c.width, bb[2] + pad), min(c.height, bb[3] + pad))
    mk = m.crop(box)
    sh = Image.new("RGBA", mk.size, drop + (0,))
    sh.putalpha(mk.filter(ImageFilter.GaussianBlur(u(5))).point(lambda v: int(v * 0.42)))
    put(c, sh, box[0], box[1] + u(9))
    c.alpha_composite(inflate(mk, f.size * depth, stops), box[:2])


def puffy_button(c, x, y, w, h, label, stops, f, fg=WHITE):
    mk = O.rounded(u(w), u(h), u(h / 2))
    sh = Image.new("RGBA", mk.size, (90, 30, 120, 0))
    sh.putalpha(mk.filter(ImageFilter.GaussianBlur(u(10))).point(lambda v: int(v * 0.35)))
    put(c, sh, u(x), u(y + 10))
    c.alpha_composite(inflate(mk, u(h) * 0.42, stops, angle=0, gloss=0.6), (u(x), u(y)))
    ImageDraw.Draw(c).text((u(x + w / 2), u(y + h / 2)), label, font=f, fill=fg, anchor="mm")


def holo(w, h):
    """Holographic foil: pastel colours that shift across the surface, with a band of sheen."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    hue = ((xx / w) * 0.9 + (yy / h) * 0.55 + 0.07 * np.sin(xx / w * 9 + yy / h * 5)) % 1.0
    sat = 0.34 + 0.08 * np.sin(yy / h * 7)
    val = 0.97 - 0.04 * np.cos(xx / w * 11)
    img = np.asarray(Image.fromarray(np.clip(np.stack([hue * 255, sat * 255, val * 255], -1), 0, 255).astype(np.uint8),
                                     "HSV")
                     .convert("RGB"), np.float32)
    sheen = np.exp(-(((xx - yy * 0.7) - w * 0.25) / (w * 0.09)) ** 2) * 0.55
    img += (255 - img) * sheen[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def holo_star(c, cx, cy, size, turn, text=None, f=None):
    shape = star(size, 0.56)
    layer = die_cut(shape, WHITE)
    pad = (layer.width - shape.width) // 2
    foil = holo(shape.width, shape.height)
    layer.paste(foil, (pad, pad), shape)
    if text:
        ImageDraw.Draw(layer).text((layer.width / 2, layer.height / 2 + u(8)), text, font=f, fill=INDIGO, anchor="mm")
    stick(c, layer, cx, cy, turn)


def trail(c, p0, p1, p2, n, s0, s1, cols):
    """A curving trail of sparkles, big at the start and fading to dust, as if a wand has just passed."""
    for i in range(n):
        tt = i / (n - 1)
        x = (1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * p1[0] + tt ** 2 * p2[0]
        y = (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * p1[1] + tt ** 2 * p2[1]
        s = s0 + (s1 - s0) * tt
        glow(c, x, y, s * 0.9, cols[i % len(cols)], 0.35)
        sparkle(c, x, y, s, cols[i % len(cols)])


def checker(w, h, cell, a, b):
    yy, xx = np.mgrid[0:h, 0:w]
    k = ((xx // cell + yy // cell) % 2).astype(bool)
    img = np.where(k[..., None], np.array(b, np.uint8), np.array(a, np.uint8))
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")


def dot_grid(c, step, col, r=1.6):
    d = ImageDraw.Draw(c)
    rr = u(r)
    for y in np.arange(step / 2, BASE[1], step):
        for x in np.arange(step / 2, BASE[0], step):
            d.ellipse((u(x) - rr, u(y) - rr, u(x) + rr, u(y) + rr), fill=col)


def pen(c, pts, col, width):
    """A line drawn by hand with a felt pen: round joins and round ends."""
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    p = [(u(x), u(y)) for x, y in pts]
    d.line(p, fill=col + (255,), width=u(width), joint="curve")
    rr = u(width) / 2
    for x, y in (p[0], p[-1]):
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (255,))
    c.alpha_composite(lay)


def loop_around(c, x0, y0, x1, y1, col, width=5, seed=2):
    """A loop drawn twice round a word, the way you'd circle something on paper."""
    rng = np.random.default_rng(seed)
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 22, (y1 - y0) / 2 + 18
    ts = np.linspace(0, 2 * np.pi * 1.15, 220) + np.deg2rad(205)
    a, b = rng.uniform(0, 6, 2)
    wob = 1 + 0.035 * np.sin(ts * 3 + a) + 0.02 * np.sin(ts * 5 + b)
    grow = np.linspace(0, 1, len(ts))
    pts = [(cx + rx * wob[i] * (1 + 0.05 * grow[i]) * np.cos(v), cy + ry * wob[i] * (1 + 0.08 * grow[i]) * np.sin(v)
            - 6 * grow[i]) for i, v in enumerate(ts)]
    pen(c, pts, col, width)


def arrow(c, p0, p1, p2, col, width=4.5):
    pts = [((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * p1[0] + s ** 2 * p2[0],
            (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * p1[1] + s ** 2 * p2[1]) for s in np.linspace(0, 1, 60)]
    pen(c, pts, col, width)
    (ax, ay), (bx, by) = pts[-6], pts[-1]
    ang = np.arctan2(by - ay, bx - ax)
    for da in (2.55, -2.55):
        pen(c, [(bx, by), (bx + 26 * np.cos(ang + da), by + 26 * np.sin(ang + da))], col, width)


def doodle_star(c, cx, cy, size, col, width=3.5, seed=0):
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(11):
        a = -np.pi / 2 + k * np.pi / 5
        r = (size / 2 if k % 2 == 0 else size / 4.4) * (1 + rng.uniform(-0.06, 0.06))
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    pen(c, pts, col, width)


def heart(c, cx, cy, size, col):
    ts = np.linspace(0, 2 * np.pi, 120)
    xs = 16 * np.sin(ts) ** 3
    ys = -(13 * np.cos(ts) - 5 * np.cos(2 * ts) - 2 * np.cos(3 * ts) - np.cos(4 * ts))
    k = size / 34
    ImageDraw.Draw(c).polygon([(u(cx + x * k), u(cy + y * k)) for x, y in zip(xs, ys)], fill=col + (255,))


def polaroid(c, name, cx, cy, w, turn, caption, tape, crop=None):
    """A real photo as a polaroid, its caption written in pen and a strip of washi tape across the top."""
    side, bottom, over = 18, 78, 26
    ph = picture(name, w, w, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    fw, fh = u(w + 2 * side), u(w + side + bottom)
    lay = Image.new("RGBA", (fw, fh + u(over)), (255, 255, 255, 0))
    fr = Image.new("RGBA", (fw, fh), (253, 252, 248, 255))
    fr.alpha_composite(ph, (u(side), u(side)))
    ImageDraw.Draw(fr).text((fw / 2, u(w + side + bottom * 0.52)), caption, font=face("Caveat", 42, 650), fill=PEN,
                            anchor="mm")
    lay.alpha_composite(fr, (0, u(over)))
    tw, th = u(150), u(40)
    tm = Image.new("L", (tw, th), 0)
    teeth = 6
    poly = [(0, 0)] + [(tw, 0)] + [(tw - u(5) * (i % 2), th * i / teeth) for i in range(teeth + 1)] + [(0, th)] + \
           [(u(5) * (i % 2), th * (teeth - i) / teeth) for i in range(teeth + 1)]
    ImageDraw.Draw(tm).polygon(poly, fill=200)
    strip = Image.new("RGBA", (tw, th), tape + (0,))
    strip.putalpha(tm)
    strip = strip.rotate(-4, Image.BICUBIC, expand=True, fillcolor=tape + (0,))
    lay.alpha_composite(strip, (fw // 2 - strip.width // 2, u(over) - th // 2 - u(6)))
    lay = lay.rotate(turn, Image.BICUBIC, expand=True, fillcolor=(255, 255, 255, 0))
    xy = (u(cx) - lay.width // 2, u(cy) - lay.height // 2)
    O.shadow(c, lay.getchannel("A"), xy, u(14), (u(3), u(10)), 0.26)
    put(c, lay, *xy)


def shade(c, y0, y1, col, a0, a1):
    """A soft fall of shadow over a photo, from opacity a0 at y0 to a1 at y1, so white type reads."""
    h = u(y1 - y0)
    g = np.linspace(0, 1, h, dtype=np.float32)
    g = a0 + (a1 - a0) * (g * g * (3 - 2 * g))
    lay = Image.new("RGBA", (c.width, h), col + (0,))
    lay.putalpha(Image.fromarray((np.repeat(g[:, None], c.width, 1) * 255).astype(np.uint8)))
    c.alpha_composite(lay, (0, u(y0)))


def glow_text(c, x, y, s, f, fill, track=0.0, anchor="ls", col=(14, 4, 30), a=0.75, blur=9):
    """Type with a soft dark glow behind it, the way magazine cover lines sit on a busy photo."""
    m = Image.new("L", c.size, 0)
    t(ImageDraw.Draw(m), x, y, s, f, 255, track, anchor)
    bb = m.getbbox()
    pad = u(blur * 3)
    box = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(c.width, bb[2] + pad), min(c.height, bb[3] + pad))
    sh = m.crop(box).filter(ImageFilter.GaussianBlur(u(blur))).point(lambda v: min(255, int(v * a * 1.8)))
    lay = Image.new("RGBA", sh.size, col + (0,))
    lay.putalpha(sh)
    c.alpha_composite(lay, box[:2])
    t(ImageDraw.Draw(c), x, y, s, f, fill, track, anchor)


def side_shade(c, y0, y1, w, col, a):
    """A soft shadow from the left edge, under a column of cover lines."""
    W_, H_ = u(w), u(y1 - y0)
    gx = np.clip(1 - np.linspace(0, 1, W_, dtype=np.float32), 0, 1) ** 1.6
    gy = np.clip(np.sin(np.linspace(0, np.pi, H_, dtype=np.float32)), 0, 1) ** 0.6
    lay = Image.new("RGBA", (W_, H_), col + (0,))
    lay.putalpha(Image.fromarray((np.outer(gy, gx) * a * 255).astype(np.uint8)))
    c.alpha_composite(lay, (0, u(y0)))


def round_photo(c, name, cx, cy, d, crop=None):
    ph = picture(name, d, d, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, ph.width - 1, ph.height - 1), fill=255)
    ring = Image.new("RGBA", (ph.width + u(8), ph.height + u(8)), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, ring.width - 1, ring.height - 1), fill=WHITE + (255,))
    ph.putalpha(m)
    ring.alpha_composite(ph, (u(4), u(4)))
    c.alpha_composite(ring, (u(cx) - ring.width // 2, u(cy) - ring.height // 2))


# ---------- the four ----------
def s19(c):
    """Liquid glass over an aurora of the logo's colours, a bento of real photos, a sparkle trail. Bricolage Grotesque."""
    W, H = BASE
    B = "BricolageGrotesque"
    put(c, aurora(u(W), u(H), (24, 7, 52), [(0.9, 0.08, 0.55, MAGENTA, 0.9), (0.05, 0.3, 0.5, VIOLET, 0.85),
                                            (0.15, 1.0, 0.6, SUN, 0.8), (0.98, 0.92, 0.5, CORAL, 0.7),
                                            (0.55, 0.6, 0.4, (88, 28, 160), 0.6)]), 0, 0)
    tile(c, "IMG_8711", 48, 196, 500, 556, 38, label=False)
    tile(c, "IMG_8598", 562, 196, 470, 270, 38, star=MAGENTA)
    tile(c, "IMG_7690", 562, 480, 470, 272, 38, label=False)
    c.alpha_composite(logo(124), (u(44), u(34)))
    trail(c, (178, 150), (400, 214), (600, 112), 12, 30, 8, [WHITE, (255, 214, 120)])
    liquid_pill(c, W - 48 - 205, 98, "Christmas offer  ·  until Dec 24", face(B, 24, 600), h=62, alpha=0.12)
    liquid(c, 36, 690, W - 72, 524, 54, blur=20, bend=36, tint=(34, 10, 70), alpha=0.34)
    d = ImageDraw.Draw(c)
    x = 80
    t(d, x, 780, Q, face(B, 44, 500), (240, 230, 252), -0.4)
    f = fit(B, A2, W - 2 * x, 116, 800, -3)
    accent(c, x - 4, 888, A2[0], "refund", f, WHITE, (255, 204, 100), -3)
    t(d, x - 4, 990, A2[1], f, WHITE, -3)
    t(d, x, 1058, EXTRA, face(B, 33, 600), (236, 220, 252), -0.3)
    button(c, x, 1092, W - 2 * x, 92, f"Book a tour  ·  {PHONE}", WHITE, INDIGO, face(B, 33, 700))
    xs = [W / 2 - 300, W / 2, W / 2 + 290]
    for cx, s in zip(xs, ["Ages 1 to 12", "Grande Prairie", WEB]):
        liquid_pill(c, cx, 1276, s, face(B, 22, 600), h=54, alpha=0.1)


def s20(c):
    """Puffy 3D: the promise blown up into glossy balloon letters, photo stickers on a pastel check, a holo star.
    Unbounded and Bricolage Grotesque."""
    W, H = BASE
    U, B = "Unbounded", "BricolageGrotesque"
    put(c, checker(u(W), u(H), u(54), (244, 237, 254), (252, 249, 255)), 0, 0)
    glow(c, W / 2, H + 80, 760, (255, 210, 234), 0.75)
    glow(c, 80, 120, 420, (230, 214, 255), 0.6)
    c.alpha_composite(logo(128), (u(46), u(34)))
    S.pill_sticker(c, 812, 92, "Christmas offer  ·  until Dec 24", face(B, 24, 650), MAGENTA, WHITE, 3)
    card(c, "IMG_8598", 232, 412, 360, 300, -6, border=12, r=28)
    card(c, "IMG_8711", 560, 372, 300, 340, 3, border=12, r=28)
    card(c, "IMG_7690", 860, 420, 348, 280, 7, border=12, r=28)
    holo_star(c, 968, 612, 176, 14)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 742, Q, face(B, 46, 600), INDIGO, -0.4, "ms")
    candy = [(0, (255, 150, 210)), (0.55, (242, 70, 160)), (1, (150, 60, 232))]
    puffy(c, W / 2, 878, A2, fit(U, A2, 980, 86, 900), 106, candy)
    t(d, W / 2, 1058, EXTRA, face(B, 36, 750), INDIGO, -0.3, "ms")
    puffy_button(c, W / 2 - 350, 1100, 700, 96, f"Book a tour  ·  {PHONE}", [(0, MAGENTA), (1, (110, 40, 190))],
                 face(B, 34, 700))
    t(d, W / 2, 1304, f"{WEB}  ·  {AGES}", face(B, 21, 500), SOFT, 0.2, "ms")


def s21(c):
    """Cover: the stained-glass classroom as a magazine cover, cover lines with round photos, a star badge, a barcode.
    Bricolage Grotesque."""
    W, H = BASE
    B = "BricolageGrotesque"
    c.alpha_composite(picture("g02", W, H, 0.6, 0.5, 1.0, lift=0.12), (0, 0))
    shade(c, 0, 420, (20, 6, 44), 0.62, 0.0)
    side_shade(c, 330, 980, 620, (20, 6, 44), 0.55)
    shade(c, 700, H, (20, 6, 44), 0.0, 0.93)
    d = ImageDraw.Draw(c)
    mast = fit(B, ["TINY STARS"], W - 80, 240, 800, -5, wdth=75)
    t(d, W / 2, 228, "TINY STARS", mast, WHITE, -5, "ms")
    t(d, W / 2, 274, "THE CHRISTMAS ISSUE   ·   UNTIL DECEMBER 24   ·   GRANDE PRAIRIE", face(B, 18, 700), WHITE, 2.4,
      "ms")
    lg = logo(112)
    c.alpha_composite(lg, (u(W - 44) - lg.width, u(300)))
    for i, (n, label) in enumerate([("IMG_8711", "Block city"), ("IMG_8598", "Hands-on art"),
                                    ("IMG_8707", "Rocket playroom"), ("IMG_7690", "Turf play yard")]):
        y = 372 + i * 100
        round_photo(c, n, 92, y, 76)
        glow_text(c, 148, y + 12, label, face(B, 34, 750), WHITE, -0.3)
    sticker(c, 880, 600, 300, [("$100 OFF", -8, face(B, 50, 800, wdth=75)), ("your first", 32, face(B, 24, 600)),
                               ("2 months", 60, face(B, 24, 600))], -10)
    glow_text(c, 52, 960, Q, face(B, 46, 500), (240, 232, 250), -0.4)
    f = fit(B, A2, W - 96, 122, 800, -3)
    accent(c, 46, 1074, A2[0], "refund", f, WHITE, (255, 204, 100), -3)
    t(d, 46, 1178, A2[1], f, WHITE, -3)
    button(c, 52, 1222, 640, 88, f"Book a tour  ·  {PHONE}", WHITE, INDIGO, face(B, 31, 700))
    bx, by, bw, bh = 742, 1222, 290, 88
    panel(c, bx, by, bw, bh, 10, WHITE, lift=0)
    rng = np.random.default_rng(24)
    xx = bx + 16
    while xx < bx + bw - 18:
        wbar = float(rng.choice([2, 2, 3, 4, 6]))
        d.rectangle((u(xx), u(by + 12), u(xx + wbar), u(by + bh - 30)), fill=INK)
        xx += wbar + float(rng.choice([2, 3, 4]))
    t(d, bx + bw / 2, by + bh - 9, WEB, face(B, 18, 700), INK, 1.2, "ms")


def s22(c):
    """Scrapbook: taped polaroids with handwritten captions on dot-grid paper, 'refund' circled in pen and the $100 off
    on a sticky note. Bricolage Grotesque and Caveat."""
    W, H = BASE
    B, C = "BricolageGrotesque", "Caveat"
    c.paste((252, 248, 242, 255), (0, 0, u(W), u(H)))
    glow(c, 900, 140, 520, (255, 226, 238), 0.55)
    glow(c, 120, 1250, 520, (234, 224, 255), 0.55)
    dot_grid(c, 34, (222, 212, 232, 255))
    c.alpha_composite(logo(118), (u(42), u(30)))
    d = ImageDraw.Draw(c)
    t(d, W - 56, 92, "Christmas offer!  until Dec 24", face(C, 44, 700), MAGENTA, 0, "rs")
    pen(c, [(W - 380 + i * 8, 108 + 4 * np.sin(i * 0.9)) for i in range(41)], MAGENTA, 3.5)
    polaroid(c, "IMG_8711", 220, 400, 290, -7, "block city!", (255, 196, 214))
    polaroid(c, "IMG_8598", 540, 372, 290, 3, "art time", (206, 226, 255))
    polaroid(c, "IMG_7690", 860, 410, 290, 8, "our rainbow yard", (255, 230, 150))
    doodle_star(c, 72, 640, 46, SUN, seed=1)
    doodle_star(c, 1020, 660, 38, MAGENTA, seed=2)
    heart(c, 400, 640, 26, MAGENTA)
    t(d, 56, 744, Q, face(C, 64, 700), PEN, 0)
    f = fit(B, A2, 900, 118, 800, -3)
    accent(c, 50, 862, A2[0], "refund", f, INDIGO, INDIGO, -3)
    # circle the word by hand
    pre = O.width(d, "We'll ", f, -3) / O.S
    wr = O.width(d, "refund", f, -3) / O.S
    sz = f.size / O.S
    loop_around(c, 50 + pre - 6, 862 - sz * 0.74, 50 + pre + wr, 862 + sz * 0.06, MAGENTA, 5.5)
    t(d, 50, 966, A2[1], f, INDIGO, -3)
    S.ramp_button(c, 56, 1030, 560, 90, f"Book a tour  ·  {PHONE}", PINK_RAMP, WHITE, face(B, 30, 650))
    note = Image.new("RGBA", (u(300), u(260)), (255, 234, 128, 255))
    nd = ImageDraw.Draw(note)
    for k, s in enumerate(["Plus $100 off", "your first", "2 months"]):
        nd.text((note.width / 2, u(80 + k * 62)), s, font=face(C, 54, 700), fill=PEN, anchor="ms")
    curl = Image.new("RGBA", note.size, (0, 0, 0, 0))
    ImageDraw.Draw(curl).polygon([(note.width, note.height - u(40)), (note.width, note.height),
                                  (note.width - u(40), note.height)], fill=(236, 206, 96, 255))
    note.alpha_composite(curl)
    stick(c, note, 852, 1120, 5)
    heart(c, 980, 1006, 22, MAGENTA)
    arrow(c, (690, 1210), (640, 1250), (560, 1150), PEN)
    t(d, 58, 1186, "ages 1 to 12  ·  tinystars.ca", face(C, 40, 650), PEN)
    f2 = face("DMSans", 21, 600)
    items = [("mail", INDIGO, "info@tinystars.ca"), ("pin", S.ORANGE, "10629 West Side Drive, Grande Prairie")]
    x = 56
    for kind, col, s in items:
        icon(c, x + 16, 1300, 32, col, kind)
        t(d, x + 42, 1307, s, f2, INK)
        x += 42 + O.width(d, s, f2) / O.S + 34


SAMPLES = {19: s19, 20: s20, 21: s21, 22: s22}


def render(i):
    O.S = SIZE[0] / BASE[0] * SS
    c = Image.new("RGBA", (u(BASE[0]), u(BASE[1])), WHITE + (255,))
    SAMPLES[i](c)
    out = c.convert("RGB").resize(SIZE, Image.LANCZOS)
    out.save(OUT / f"offer_sample_{i}.jpg", quality=95, subsampling=0, optimize=True)
    print("wrote", OUT / f"offer_sample_{i}.jpg", flush=True)
    return out


def main():
    picks = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(SAMPLES)
    outs = {i: render(i) for i in picks}
    if all(i in outs for i in SAMPLES):
        tw, th = 720, 900
        sheet = Image.new("RGB", (4 * tw + 5 * 30, th + 2 * 30 + 50), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 30, 700)
        for k, i in enumerate(SAMPLES):
            x = 30 + k * (tw + 30)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, 30))
            d.text((x, 30 + th + 10), f"Sample {i}", font=f, fill=INK)
        sheet.save(OUT / "offer_samples_modern.jpg", quality=90)
        print("wrote", OUT / "offer_samples_modern.jpg", flush=True)


if __name__ == "__main__":
    main()
