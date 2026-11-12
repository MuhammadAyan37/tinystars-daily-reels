"""Red Nova, round two: eight more modern takes (samples 14 to 21), each built around three to five of the best photos
of the new room, with the sand-and-diggers bin as the star.

The photos get a proper clean-up first (enhance below): the yellow of the ceiling lights pulled back, the shadows
lifted, the colours richer and the detail crisper, so the room looks the way it does in person.

  14  Hero and strip: the sand bin big, three more photos in a row, a spinning "new room" badge
  15  Bento on red: five photos in a grid under a giant condensed "Red Nova"
  16  Shapes: four photos cut into an arch, a circle, a pill and a star, each on its own colour block
  17  Photo letters: "NEW" spelled in three photos of the room, two more below
  18  Story: the room as a stack of story cards, with progress bars and a heart
  19  Christmas gift: the sand bin wrapped with a ribbon and bow, three more photos beside it
  20  Editorial: a big serif title, three photos in a magazine grid with numbered captions
  21  Now showing: the room on a strip of film, on a snowy red night

Usage: python -I edits/rednova_modern.py [14 15 ...]   (all eight when none is named)
  -> exports/rednova_ad_<n>.jpg          1440 x 1800 (4:5)
  -> exports/rednova_ads_modern.jpg      the eight side by side
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offer as O  # noqa: E402
import offer_samples as S  # noqa: E402
import rednova_ad as R  # noqa: E402
from offer_modern import aurora, glow_text, heart, inflate, liquid_pill, shade  # noqa: E402
from offer_samples import (BASE, CROPS, INK, LABELS, LIFT, OUT, SIZE, SOFT, SS, WEB, WHITE, accent, button,  # noqa: E402
                           die_cut, face, fit, glow, logo, panel, picture, put, ramp, sparkle, star, stick, t, u)
from rednova_ad import (ADDRESS, CHERRY, CREAM, CTA, DEEP_GOLD, GOLD, PROM, RED_PUFF, RED_SATIN, ROOM, RUBY,  # noqa
                        WINE, XMAS, badge_logo, band, bow, fit_serif, footer, holly, promise, serif, snow, wid)

B, U = "BricolageGrotesque", "Unbounded"
PINK = (255, 232, 236)
BLUSH = (255, 244, 238)
PLUM = (40, 12, 34)

# the best photos of the room, cleaned up (see enhance); the sand-and-diggers bin is the star
PHOTOS = {"RN_sand": "IMG_1286", "RN_kitchen": "IMG_1294", "RN_books": "IMG_1308", "RN_tent": "IMG_1291",
          "RN_rug": "IMG_1310", "RN_busy": "IMG_1312"}
LABELS.update({"RN_sand": "Sand & diggers", "RN_kitchen": "Play kitchen", "RN_books": "Story corner",
               "RN_tent": "Cozy hideout", "RN_rug": "Circle time", "RN_busy": "Busy boards"})
CROPS.update({"RN_sand": (0.47, 0.8, 1.35), "RN_kitchen": (0.5, 0.56, 1.0), "RN_books": (0.66, 0.46, 1.12),
              "RN_tent": (0.42, 0.62, 1.0), "RN_rug": (0.45, 0.42, 1.05), "RN_busy": (0.5, 0.45, 1.15)})
SAND_CLOSE = (0.47, 0.8, 1.7)


# ---------- the photos ----------
def enhance(im):
    """Make a photo of the room look the way the room does: the yellow of the ceiling lights pulled back, shadows
    lifted, colours richer (most where they're dull), local contrast and fine detail brought up."""
    im = im.copy()
    im.thumbnail((4000, 4000), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    a = np.clip(a * np.array([0.968, 1.0, 1.055], np.float32), 0, 1)
    a = 1 - (1 - a) ** 1.16
    im = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    h, s, v = [np.asarray(x, np.float32) / 255 for x in im.convert("HSV").split()]
    s = np.clip(s + 0.45 * s * (1 - s), 0, 1)
    im = Image.merge("HSV", [Image.fromarray((x * 255 + 0.5).astype(np.uint8)) for x in (h, s, v)]).convert("RGB")
    im = im.filter(ImageFilter.UnsharpMask(radius=40, percent=16, threshold=0))
    return im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=35, threshold=2))


def prepare():
    for new, src in PHOTOS.items():
        out, inp = O.CLEAN / f"{new}.jpg", O.CLEAN / f"{src}.jpg"
        if not out.exists() or out.stat().st_mtime < inp.stat().st_mtime:
            enhance(Image.open(inp).convert("RGB")).save(out, quality=95)
            print("cleaned up", src, "->", out.name, flush=True)


# ---------- shapes and pieces ----------
def mask_for(shape, W_, H_, r=0):
    m = Image.new("L", (W_, H_), 0)
    d = ImageDraw.Draw(m)
    if shape == "arch":
        rad = W_ // 2
        d.ellipse((0, 0, W_ - 1, 2 * rad), fill=255)
        d.rectangle((0, rad, W_ - 1, H_ - 1), fill=255)
    elif shape == "circle":
        d.ellipse((0, 0, W_ - 1, H_ - 1), fill=255)
    elif shape == "pill":
        d.rounded_rectangle((0, 0, W_ - 1, H_ - 1), min(W_, H_) // 2, fill=255)
    elif shape == "star":
        m = star(W_ / O.S, 0.58).resize((W_, H_), Image.LANCZOS)
    else:
        d.rounded_rectangle((0, 0, W_ - 1, H_ - 1), r, fill=255)
    return m


def shaped(c, name, x, y, w, h, shape="round", r=30, crop=None, block=None, off=(18, 18), rim=0, lift=0.22):
    """A photo cut to a shape (arch, circle, pill, star or rounded box), optionally on a solid colour block set off
    behind it and with a white die-cut rim."""
    ph = picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    m = mask_for(shape, ph.width, ph.height, u(r))
    X, Y = u(x), u(y)
    if block:
        bl = Image.new("RGBA", ph.size, block + (255,))
        bl.putalpha(m)
        put(c, bl, X + u(off[0]), Y + u(off[1]))
    if rim:
        pad = u(rim)
        big = Image.new("L", (ph.width + 2 * pad, ph.height + 2 * pad), 0)
        big.paste(m, (pad, pad))
        big = big.filter(ImageFilter.GaussianBlur(pad * 0.5)).point(lambda v: 255 if v >= 8 else 0)
        if lift:
            O.shadow(c, big, (X - pad, Y - pad), u(16), (0, u(10)), lift)
        wl = Image.new("RGBA", big.size, WHITE + (255,))
        wl.putalpha(big)
        put(c, wl, X - pad, Y - pad)
    elif lift and not block:
        O.shadow(c, m, (X, Y), u(16), (0, u(10)), lift)
    ph.putalpha(m)
    put(c, ph, X, Y)


def chip_on(c, x, y, label, size=18, star_col=CHERRY):
    S.chip(c, x, y, label, size, star_col=star_col)


def ring_text(c, cx, cy, r, text, f, fill):
    """Words set round a circle, the way a spinning badge reads."""
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    ws = [d0.textlength(ch, font=f) for ch in text]
    rr = u(r)
    gap = (2 * np.pi * rr - sum(ws)) / len(text)
    ang = 0.0
    n = int(f.size * 1.8)
    for ch, w in zip(text, ws):
        a = ang + (w / 2) / rr
        im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((n / 2, n / 2), ch, font=f, fill=fill + (255,), anchor="mm")
        im = im.rotate(-np.degrees(a), Image.BICUBIC)
        px, py = u(cx) + rr * np.sin(a), u(cy) - rr * np.cos(a)
        c.alpha_composite(im, (int(px - n / 2), int(py - n / 2)))
        ang += (w + gap) / rr


def spin_badge(c, cx, cy, d, text, bg, fg, star_col, size=21):
    """A round sticker with words running round the edge and the logo's star in the middle."""
    m = Image.new("L", (u(d), u(d)), 0)
    ImageDraw.Draw(m).ellipse((0, 0, u(d) - 1, u(d) - 1), fill=255)
    stick(c, die_cut(m, bg, 4), cx, cy, 0)
    ring_text(c, cx, cy, d * 0.36, text, face(B, size, 800), fg)
    s = d * 0.38
    st = Image.new("RGBA", (u(s), u(s)), star_col + (255,))
    st.putalpha(star(s, 0.52))
    c.alpha_composite(st, (u(cx - s / 2), u(cy - s / 2)))


def photo_word(c, x, y, word, f, names, crops=None, track=0.0, lift=0.25, block=None, off=(12, 12)):
    """A word set very big with a different photo inside each letter."""
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    xx = x
    for k, (ch, name) in enumerate(zip(word, names)):
        m = Image.new("L", c.size, 0)
        ImageDraw.Draw(m).text((u(xx), u(y)), ch, font=f, fill=255, anchor="ls")
        bb = m.getbbox()
        bw, bh = bb[2] - bb[0], bb[3] - bb[1]
        cr = (crops or {}).get(name) or CROPS[name]
        ph = picture(name, bw / O.S, bh / O.S, *cr, lift=LIFT.get(name, 0)).resize((bw, bh), Image.LANCZOS)
        mk = m.crop(bb)
        if block:
            bl = Image.new("RGBA", mk.size, block + (255,))
            bl.putalpha(mk)
            put(c, bl, bb[0] + u(off[0]), bb[1] + u(off[1]))
        else:
            O.shadow(c, mk, bb[:2], u(14), (0, u(10)), lift)
        ph.putalpha(mk)
        c.alpha_composite(ph, bb[:2])
        xx += d0.textlength(ch, font=f) / O.S + track


def film(c, names, cx, cy, fw, fh, turn, gap=22, margin=40, extra=360):
    """A strip of 35 mm film with the room in its frames, sprocket holes and edge print, laid across the page."""
    n = len(names)
    L = n * fw + (n - 1) * gap + 2 * extra
    H = fh + 2 * margin
    strip = Image.new("RGBA", (u(L), u(H)), (18, 12, 14, 255))
    alpha = Image.new("L", strip.size, 255)
    da = ImageDraw.Draw(alpha)
    for xh in np.arange(10, L - 10, 30):
        for yh in (margin * 0.3, H - margin * 0.3 - 12):
            da.rounded_rectangle((u(xh), u(yh), u(xh + 15), u(yh + 12)), u(3), fill=0)
    x0 = extra
    ds = ImageDraw.Draw(strip)
    fe = face(B, 13, 700)
    for i, name in enumerate(names):
        ph = picture(name, fw, fh, *CROPS[name], lift=LIFT.get(name, 0))
        ph.putalpha(O.rounded(ph.width, ph.height, u(6)))
        strip.alpha_composite(ph, (u(x0 + i * (fw + gap)), u(margin)))
        ds.text((u(x0 + i * (fw + gap) + 6), u(H - 7)), f"TINY STARS   {i + 1:02d}A", font=fe, fill=(255, 168, 60),
                anchor="ls")
    strip.putalpha(ImageChops.multiply(strip.getchannel("A"), alpha))
    strip = strip.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - strip.width // 2, u(cy) - strip.height // 2)
    O.shadow(c, strip.getchannel("A"), xy, u(20), (0, u(16)), 0.5)
    put(c, strip, *xy)


def story_card(c, name, x, y, w, h, crop=None, bars=5, done=1):
    """A photo as a story card: rounded, with progress bars, a little profile row and a heart."""
    ph = picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    shade(ph, 0, 180, (10, 4, 12), 0.5, 0.0)
    ov = Image.new("RGBA", ph.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    seg = (w - 32 - (bars - 1) * 6) / bars
    for i in range(bars):
        bx = 16 + i * (seg + 6)
        d.rounded_rectangle((u(bx), u(18), u(bx + seg), u(23)), u(3), fill=(255, 255, 255, 110))
        fill_to = seg if i < done else seg * 0.45 if i == done else 0
        if fill_to:
            d.rounded_rectangle((u(bx), u(18), u(bx + fill_to), u(23)), u(3), fill=(255, 255, 255, 255))
    ph.alpha_composite(ov)
    d = ImageDraw.Draw(ph)
    av = 54
    am = Image.new("L", (u(av), u(av)), 0)
    ImageDraw.Draw(am).ellipse((0, 0, am.width - 1, am.height - 1), fill=255)
    a = Image.new("RGBA", am.size, WHITE + (255,))
    lg = logo(av * 0.82)
    a.alpha_composite(lg, ((am.width - lg.width) // 2, (am.height - lg.height) // 2))
    a.putalpha(am)
    ring = Image.new("RGBA", (am.width + u(8), am.height + u(8)), (0, 0, 0, 0))
    rg = ramp(ring.width, ring.height, [(0, (255, 196, 80)), (0.5, CHERRY), (1, (150, 40, 200))], 45)
    rm = Image.new("L", ring.size, 0)
    ImageDraw.Draw(rm).ellipse((0, 0, ring.width - 1, ring.height - 1), fill=255)
    rg.putalpha(rm)
    ph.alpha_composite(rg, (u(16), u(36)))
    ph.alpha_composite(a, (u(20), u(40)))
    t(d, 86, 66, "tinystars", face(B, 23, 750), WHITE)
    t(d, 86 + wid("tinystars", face(B, 23, 750)) + 10, 66, f"{ROOM}  ·  now open", face(B, 21, 500), (240, 232, 240))
    ph.putalpha(O.rounded(ph.width, ph.height, u(34)))
    O.shadow(c, ph.getchannel("A"), (u(x), u(y)), u(26), (0, u(18)), 0.45)
    c.alpha_composite(ph, (u(x), u(y)))


def tilted(c, name, cx, cy, w, h, turn, crop=None, r=30):
    ph = picture(name, w, h, *(crop or CROPS[name]), lift=LIFT.get(name, 0))
    ph.putalpha(O.rounded(ph.width, ph.height, u(r)))
    ph = ph.rotate(turn, Image.BICUBIC, expand=True)
    xy = (u(cx) - ph.width // 2, u(cy) - ph.height // 2)
    O.shadow(c, ph.getchannel("A"), xy, u(20), (0, u(14)), 0.4)
    put(c, ph, *xy)


def puffy_heart(c, cx, cy, s, turn=-12):
    n = u(s)
    ts = np.linspace(0, 2 * np.pi, 160)
    xs, ys = 16 * np.sin(ts) ** 3, -(13 * np.cos(ts) - 5 * np.cos(2 * ts) - 2 * np.cos(3 * ts) - np.cos(4 * ts))
    m = Image.new("L", (n, n), 0)
    k = n / 36
    ImageDraw.Draw(m).polygon([(n / 2 + x * k, n / 2 + y * k + n * 0.04) for x, y in zip(xs, ys)], fill=255)
    lay = die_cut(m, CHERRY, 4)
    pad = (lay.width - n) // 2
    lay.alpha_composite(inflate(m, n * 0.16, RED_PUFF, 90, gloss=1.0), (pad, pad))
    stick(c, lay, cx, cy, turn)


def gift_ribbon(c, x, y, w, h, r, at, stops=RED_SATIN, bw=56):
    """A satin ribbon tied round a photo like a present: one band across, one down, clipped to the photo's corners."""
    lay = Image.new("RGBA", (u(w), u(h)), (0, 0, 0, 0))
    hb = ramp(u(w), u(bw), stops, 90)
    vb = ramp(u(bw), u(h), stops, 0)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rectangle((0, u(at[1] - y - bw / 2 + 6), u(w), u(at[1] - y + bw / 2 + 6)), fill=(40, 0, 10, 90))
    ds.rectangle((u(at[0] - x - bw / 2 + 6), 0, u(at[0] - x + bw / 2 + 6), u(h)), fill=(40, 0, 10, 90))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(u(6))))
    lay.alpha_composite(hb, (0, u(at[1] - y - bw / 2)))
    lay.alpha_composite(vb, (u(at[0] - x - bw / 2), 0))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), O.rounded(lay.width, lay.height, u(r))))
    c.alpha_composite(lay, (u(x), u(y)))


def snowflakes_bg(c, col, a=0.18, step=120, seed=3):
    """A faint all-over pattern of little snowflakes, like wrapping paper."""
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed)
    W, H = BASE
    for j, y in enumerate(np.arange(40, H, step)):
        for x in np.arange(40 + (j % 2) * step / 2, W, step):
            s = rng.uniform(10, 16)
            for k in range(3):
                ang = np.deg2rad(k * 60 + rng.uniform(0, 60))
                dx, dy = s * np.cos(ang), s * np.sin(ang)
                d.line((u(x - dx), u(y - dy), u(x + dx), u(y + dy)), fill=col + (int(255 * a),), width=u(2.2))
    c.alpha_composite(lay)


# ---------- the eight ----------
def s14(c):
    """Hero and strip: the sand bin big, three more photos in a row, a spinning badge, the offer set left. Bricolage."""
    W, H = BASE
    c.paste((251, 247, 240, 255), (0, 0, u(W), u(H)))
    c.alpha_composite(logo(108), (u(40), u(26)))
    d = ImageDraw.Draw(c)
    pw = wid("Now open", face(B, 23, 700)) + 64
    panel(c, W - 40 - pw, 50, pw, 52, 26, PINK, lift=0)
    d.ellipse((u(W - 40 - pw + 24), u(70), u(W - 40 - pw + 36), u(82)), fill=CHERRY + (255,))
    t(d, W - 40 - pw + 46, 84, "Now open", face(B, 23, 700), RUBY)
    shaped(c, "RN_sand", 40, 140, 1000, 560, r=36, crop=(0.47, 0.8, 1.3), lift=0.2)
    chip_on(c, 64, 640, LABELS["RN_sand"])
    for i, n in enumerate(["RN_kitchen", "RN_books", "RN_tent"]):
        x = 40 + i * (322 + 17)
        shaped(c, n, x, 716, 322, 216, r=28, lift=0.12)
        chip_on(c, x + 14, 880, LABELS[n], 16)
    spin_badge(c, 930, 680, 210, "NEW ROOM • NOW OPEN • RED NOVA • ", CHERRY, WHITE, GOLD)
    f = fit(B, [f"{ROOM} is open."], 1000, 96, 800, -3)
    t(d, 36, 1032, f"{ROOM} is open.", f, INK, -3)
    fp = fit(B, PROM, 1000, 40, 500, -0.5)
    t(d, 40, 1090, PROM[0], fp, SOFT, -0.5)
    accent(c, 40, 1136, PROM[1], "refund", fp, SOFT, CHERRY, -0.5)
    button(c, 40, 1172, 1000, 86, CTA, CHERRY, WHITE, face(B, 32, 700))
    footer(c, 1306, face(B, 20, 500), SOFT, items=(WEB, ADDRESS))


def s15(c):
    """Bento on red: a giant condensed 'Red Nova' over a five-photo grid, the offer in white. Bricolage."""
    W, H = BASE
    put(c, ramp(u(W), u(H), [(0, (196, 20, 52)), (0.55, (140, 10, 40)), (1, (74, 6, 28))], 90), 0, 0)
    glow(c, 860, 120, 520, (255, 110, 120), 0.35)
    badge_logo(c, 40, 30, 96)
    liquid_pill(c, W - 48 - 120, 78, XMAS, face(B, 24, 650), h=58, alpha=0.12)
    d = ImageDraw.Draw(c)
    f = fit(B, [ROOM.upper()], W - 76, 230, 800, -4, wdth=75)
    t(d, W / 2, 330, ROOM.upper(), f, WHITE, -4, "ms")
    t(d, W / 2, 380, "OUR NEWEST ROOM IS NOW OPEN", face(B, 22, 800), GOLD, 4, "ms")
    shaped(c, "RN_sand", 40, 412, 520, 600, r=30, crop=(0.47, 0.8, 1.55), lift=0.3)
    chip_on(c, 58, 954, LABELS["RN_sand"])
    for i, n in enumerate(["RN_kitchen", "RN_books", "RN_tent", "RN_rug"]):
        x, y = 574 + (i % 2) * 240, 412 + (i // 2) * 307
        shaped(c, n, x, y, 226, 293, r=26, lift=0.3)
    f2 = fit(B, PROM, W - 120, 46, 750, -1)
    promise(c, W / 2, 1084, 56, f2, WHITE, GOLD, -1, "ms")
    button(c, W / 2 - 340, 1170, 680, 86, CTA, WHITE, RUBY, face(B, 32, 700))
    footer(c, 1300, face(B, 20, 500), (255, 214, 220), items=(WEB, ADDRESS))


def s16(c):
    """Shapes: four photos cut into an arch, a circle, a pill and a star, each set off on its own colour block.
    Bricolage and Instrument Serif."""
    W, H = BASE
    c.paste(BLUSH + (255,), (0, 0, u(W), u(H)))
    glow(c, 200, 300, 500, (255, 222, 230), 0.7)
    c.alpha_composite(logo(104), (u(40), u(26)))
    d = ImageDraw.Draw(c)
    t(d, W - 44, 84, "new room, now open", serif(40), RUBY, 0, "rs")
    shaped(c, "RN_kitchen", 60, 150, 420, 400, "arch", block=CHERRY, off=(16, 16), lift=0)
    shaped(c, "RN_books", 580, 140, 400, 400, "circle", block=GOLD, off=(-16, 16), lift=0)
    shaped(c, "RN_rug", 60, 604, 440, 250, "pill", block=(124, 58, 220), off=(16, 14), lift=0)
    shaped(c, "RN_sand", 568, 540, 420, 420, "star", crop=SAND_CLOSE, rim=10, lift=0.3)
    for x, y, s_, col in [(520, 120, 30, CHERRY), (40, 900, 26, GOLD), (1030, 560, 24, (124, 58, 220))]:
        sparkle(c, x, y, s_, col)
    f = fit(B, [f"{ROOM} is open."], W - 100, 92, 800, -3)
    t(d, W / 2, 1040, f"{ROOM} is open.", f, INK, -3, "ms")
    fp = fit(B, PROM, W - 170, 40, 500, -0.5)
    t(d, W / 2, 1096, PROM[0], fp, SOFT, -0.5, "ms")
    accent(c, W / 2, 1142, PROM[1], "refund", fp, SOFT, CHERRY, -0.5, "ms")
    button(c, W / 2 - 330, 1180, 660, 84, CTA, CHERRY, WHITE, face(B, 31, 700))
    footer(c, 1310, face(B, 20, 500), SOFT, items=(WEB, ADDRESS))


def s17(c):
    """Photo letters: 'NEW' spelled in three photos of the room, two more photos below, the offer. Unbounded,
    Instrument Serif, Bricolage."""
    W, H = BASE
    c.paste((250, 248, 244, 255), (0, 0, u(W), u(H)))
    glow(c, W / 2, 380, 640, (255, 226, 232), 0.6)
    c.alpha_composite(logo(104), (u(40), u(26)))
    S.pill_sticker(c, 870, 76, XMAS, face(B, 24, 700), CHERRY, WHITE, 3)
    f = fit(U, ["NEW"], W - 70, 420, 900, -6)
    photo_word(c, (W - wid("NEW", f, -6)) / 2, 470, "NEW", f, ["RN_kitchen", "RN_sand", "RN_books"], track=-6,
               crops={"RN_sand": SAND_CLOSE, "RN_kitchen": (0.5, 0.6, 1.2), "RN_books": (0.64, 0.42, 1.5)},
               block=CHERRY)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 548, "ROOM  IS  NOW  OPEN", face(U, 34, 700), INK, 6, "ms")
    t(d, W / 2, 664, ROOM, fit_serif([ROOM], 700, 120), CHERRY, -1, "ms")
    shaped(c, "RN_tent", 40, 700, 493, 250, r=28, lift=0.16)
    shaped(c, "RN_rug", 547, 700, 493, 250, r=28, lift=0.16)
    chip_on(c, 56, 896, LABELS["RN_tent"])
    chip_on(c, 563, 896, LABELS["RN_rug"])
    fp = fit(B, PROM, W - 140, 48, 760, -1)
    promise(c, W / 2, 1030, 58, fp, INK, CHERRY, -1, "ms")
    button(c, W / 2 - 340, 1118, 680, 86, CTA, CHERRY, WHITE, face(B, 32, 700))
    footer(c, 1300, face(B, 20, 500), SOFT, items=(WEB, ADDRESS))


def s18(c):
    """Story: the room as a stack of story cards, with progress bars, a profile row and a puffy heart, on a soft
    aurora. Bricolage."""
    W, H = BASE
    put(c, aurora(u(W), u(H), (40, 10, 40), [(0.1, 0.1, 0.55, (230, 40, 80), 0.85), (0.95, 0.2, 0.5, (130, 50, 210), 0.8),
                                             (0.5, 1.0, 0.6, (255, 150, 90), 0.7), (0.9, 0.85, 0.4, (210, 30, 90), 0.6)]),
        0, 0)
    tilted(c, "RN_kitchen", 270, 520, 520, 660, -9)
    tilted(c, "RN_busy", 810, 520, 520, 660, 9)
    story_card(c, "RN_sand", 230, 110, 620, 800, crop=(0.47, 0.76, 1.2))
    puffy_heart(c, 790, 830, 130)
    d = ImageDraw.Draw(c)
    glow_text(c, W / 2, 990, f"Swipe inside {ROOM}, our newest room", face(B, 40, 650), WHITE, -0.4, "ms",
              col=(30, 6, 30), a=0.5)
    fp = fit(B, PROM, W - 140, 48, 760, -1)
    promise(c, W / 2, 1060, 58, fp, WHITE, (255, 214, 120), -1, "ms")
    button(c, W / 2 - 340, 1140, 680, 86, CTA, WHITE, RUBY, face(B, 32, 700))
    footer(c, 1296, face(B, 20, 500), (250, 226, 236), items=(WEB, ADDRESS))
    _ = d


def s19(c):
    """Christmas gift: the sand bin wrapped with a red satin ribbon and bow, three more photos beside it, on snowflake
    paper. Instrument Serif and Bricolage."""
    W, H = BASE
    c.paste(CREAM + (255,), (0, 0, u(W), u(H)))
    snowflakes_bg(c, (200, 40, 60), 0.14)
    c.alpha_composite(logo(104), (u(40), u(26)))
    S.pill_sticker(c, 870, 76, XMAS, face(B, 24, 700), CHERRY, WHITE, -3)
    d = ImageDraw.Draw(c)
    t(d, 40, 260, f"{ROOM} is open", fit_serif([f"{ROOM} is open"], 760, 128), CHERRY, -1)
    holly(c, 930, 214, 84, -10)
    hx, hy, hw, hh = 40, 300, 600, 640
    shaped(c, "RN_sand", hx, hy, hw, hh, r=30, crop=(0.47, 0.78, 1.45), lift=0.25)
    gift_ribbon(c, hx, hy, hw, hh, 30, (hx + 170, hy + 170))
    bow(c, hx + 170, hy + 170, 120, RED_PUFF)
    chip_on(c, hx + 18, hy + hh - 54, LABELS["RN_sand"])
    for i, n in enumerate(["RN_kitchen", "RN_books", "RN_tent"]):
        y = hy + i * (204 + 14)
        shaped(c, n, 654, y, 386, 204, r=26, lift=0.14)
        chip_on(c, 668, y + 204 - 50, LABELS[n], 16)
    fp = fit(B, PROM, W - 120, 48, 760, -1)
    promise(c, 40, 1020, 58, fp, INK, CHERRY, -1)
    button(c, 40, 1110, 1000, 86, CTA, CHERRY, WHITE, face(B, 32, 700))
    footer(c, 1300, face(B, 20, 500), SOFT, items=(WEB, ADDRESS))


def s20(c):
    """Editorial: a big serif title, three photos in a magazine grid with numbered captions and fine rules.
    Instrument Serif, Fraunces and Inter Tight."""
    W, H = BASE
    c.paste((247, 243, 236, 255), (0, 0, u(W), u(H)))
    d = ImageDraw.Draw(c)
    I = "InterTight"
    t(d, 40, 70, "TINY STARS  ·  GRANDE PRAIRIE", face(I, 18, 700), INK, 3)
    t(d, W - 40, 70, "THE NEW ROOM", face(I, 18, 700), CHERRY, 3, "rs")
    d.line((u(40), u(92), u(W - 40), u(92)), fill=INK + (255,), width=u(1.5))
    c.alpha_composite(logo(92), (u(W / 2 - 46), u(16)))
    t(d, 34, 290, ROOM, serif(236, italic=False), INK, -4)
    t(d, W - 40, 350, "is now open.", serif(76), CHERRY, -1, "rs")
    shaped(c, "RN_sand", 40, 390, 560, 520, r=0, crop=(0.47, 0.78, 1.4), lift=0)
    shaped(c, "RN_kitchen", 616, 390, 424, 252, r=0, lift=0)
    shaped(c, "RN_books", 616, 658, 424, 252, r=0, lift=0)
    fc = face(I, 17, 600)
    for x, y, n in [(40, 390, "01"), (616, 390, "02"), (616, 658, "03")]:
        panel(c, x, y, 52, 36, 0, (247, 243, 236), lift=0)
        t(d, x + 26, y + 25, n, face(I, 17, 800), CHERRY, 1, "ms")
    x = 40
    for n, s_ in [("01", "Sand & diggers"), ("02", "Play kitchen"), ("03", "Story corner")]:
        t(d, x, 940, n, face(I, 17, 800), CHERRY, 1)
        t(d, x + 30, 940, s_, fc, INK)
        x += 30 + wid(s_, fc) + 44
    d.line((u(40), u(966), u(W - 40), u(966)), fill=INK + (255,), width=u(1))
    F = "Fraunces"
    t(d, 40, 1012, f"{XMAS.upper()}  ·  FOR NEW FAMILIES", face(I, 18, 800), CHERRY, 3)
    fp = fit(F, PROM, W - 80, 50, 480, -0.8, opsz=72)
    t(d, 40, 1074, PROM[0], fp, INK, -0.8)
    accent(c, 40, 1132, PROM[1], "refund", fp, INK, CHERRY, -0.8)
    button(c, 40, 1176, 620, 82, CTA, INK, WHITE, face(I, 28, 700))
    t(d, W - 40, 1210, WEB, face(I, 22, 700), INK, 0, "rs")
    t(d, W - 40, 1244, "Grande Prairie", face(I, 20, 500), SOFT, 0, "rs")
    d.line((u(40), u(1290), u(W - 40), u(1290)), fill=INK + (255,), width=u(1))
    t(d, 40, 1320, ADDRESS, face(I, 18, 500), SOFT)
    t(d, W - 40, 1320, "info@tinystars.ca", face(I, 18, 500), SOFT, 0, "rs")


def s21(c):
    """Now showing: the room on a strip of 35 mm film laid across a snowy red night. Instrument Serif, Bricolage."""
    W, H = BASE
    put(c, ramp(u(W), u(H), [(0, (70, 6, 26)), (0.5, (150, 12, 40)), (1, (60, 6, 24))], 90), 0, 0)
    glow(c, W / 2, 620, 620, (255, 90, 100), 0.35)
    snow(c, 220, 44, alpha=0.75, big=8)
    badge_logo(c, 40, 30, 96)
    liquid_pill(c, W - 48 - 120, 78, XMAS, face(B, 24, 650), h=58, alpha=0.12)
    d = ImageDraw.Draw(c)
    t(d, W / 2, 236, "NOW  SHOWING", face(B, 26, 800), GOLD, 8, "ms")
    t(d, W / 2, 360, ROOM, fit_serif([ROOM], 820, 150), WHITE, -1, "ms")
    film(c, ["RN_books", "RN_sand", "RN_kitchen", "RN_tent"], W / 2, 630, 330, 248, 6)
    t(d, W / 2, 920, "our newest room is open", serif(56), (255, 226, 230), 0, "ms")
    fp = fit(B, PROM, W - 140, 48, 760, -1)
    promise(c, W / 2, 1010, 58, fp, WHITE, GOLD, -1, "ms")
    button(c, W / 2 - 340, 1100, 680, 86, CTA, GOLD, WINE, face(B, 32, 750))
    footer(c, 1290, face(B, 20, 500), (250, 214, 222), items=(WEB, ADDRESS))


SAMPLES = {14: s14, 15: s15, 16: s16, 17: s17, 18: s18, 19: s19, 20: s20, 21: s21}


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
        cols, tw, th = 4, 540, 675
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 24, 2 * (th + 64) + 24), (236, 233, 228))
        d = ImageDraw.Draw(sheet)
        O.S = 1.0
        f = face("InterTight", 26, 700)
        for k, i in enumerate(SAMPLES):
            x, y = 24 + (k % cols) * (tw + 24), 24 + (k // cols) * (th + 64)
            sheet.paste(outs[i].resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 10), f"Sample {i}", font=f, fill=INK)
        sheet.save(OUT / "rednova_ads_modern.jpg", quality=90)
        print("wrote", OUT / "rednova_ads_modern.jpg", flush=True)


if __name__ == "__main__":
    main()
