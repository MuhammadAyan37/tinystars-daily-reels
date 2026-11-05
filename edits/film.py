"""Render the film: 1080x1920, 30 fps, cut on the beat, 25 seconds.

Every parent asks "What did you do at daycare today?" and gets "Nothing." The film opens on that exchange, and a paint
bleed opens a paper title card ("Here's what nothing looks like"). The band comes in on the marshmallows and spaghetti,
then the challenge is shown step by step in close-up, until a boy lets go of his tower and it stays up. Only then is
"Nothing." struck through with a brush stroke: Engineering. The song stops dead while paint spreads across a frozen frame,
comes back bigger for the second one, Fine art, and settles on the whole room: "Nothing. Just growing up." A last paint
bleed opens a bright paper closing card, with the contact details landing on the song's final notes.

Only the blurred working copies from blur.py and photos.py are ever read here, so no effect can touch an unblurred face.

Usage: python -I edits/film.py [--stills t t t ...]
  -> exports/nothing_reel.mp4, exports/nothing_reel_nomusic.mp4, exports/nothing_cover.jpg
     (--stills only writes check frames to work/stills/)
"""
import gc
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import soundfile as sf
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import BREATH, CHAPTERS, END, HOOK, MUSIC, PILLS, ROOM, SHOTS, STEPS  # noqa: E402
from lib import (CREAM, FPS, GOLD, H, INK, ITALIC, MAGENTA, ORANGE, PAPER, PURPLE, ROOT, SANS, SERIF, TEAL, VIOLET,  # noqa: E402
                 W, WHITE, Pill, blit, brush_stroke, clamp01, decode, ease_in_out, ease_out_back, ease_out_cubic,
                 ease_out_expo, encode, font, hash01, icon_image, lettering, logo_image, loudness_normalise,
                 periodic_noise, phone_copy, remux, render_frames, reveal_lr, rise, rounded_mask, star_image, to_sprite)

CLEAN = ROOT / "work" / "clean"
FACES = ROOT / "work" / "faces"
EXPORTS = ROOT / "exports"
BEAT = 60 / MUSIC["bpm"]


def bt(k):
    return k * BEAT


# ---------- footage ----------
class Source:
    """A baked clip, read one frame at a time, keeping just a few frames in memory."""

    def __init__(self, name, turn=0, want_w=None):
        data = json.loads((FACES / f"{name}.json").read_text())
        self.name, self.n, self.turn = name, data["n"], turn % 4
        w, h = data["w"], data["h"]
        k = min(1.0, want_w / w) if want_w else 1.0
        self.rw, self.rh = int(w * k) // 2 * 2, int(h * k) // 2 * 2  # the size frames are read at, before turning
        self.k = self.rw / w
        self.w, self.h = (self.rh, self.rw) if self.turn % 2 else (self.rw, self.rh)
        self.cap, self.pos, self.cache = None, 0, {}
        m = np.array(data["motion"])
        self.path = np.c_[np.cumsum(m[:, 0, 2]), np.cumsum(m[:, 1, 2]), np.cumsum(np.arctan2(m[:, 1, 0], m[:, 0, 0]))]

    def frame(self, i):
        i = int(max(0, min(self.n - 1, i)))
        if i in self.cache:
            return self.cache[i]
        if self.cap is None or i < self.pos:
            if self.cap is not None:
                self.cap.release()
            self.cap, self.pos = cv2.VideoCapture(str(CLEAN / f"{self.name}.mp4")), 0
        while self.pos < i:
            self.cap.grab()
            self.pos += 1
        ok, fr = self.cap.read()
        self.pos += 1
        if not ok:
            raise SystemExit(f"could not read frame {i} of {self.name}")
        if self.k < 1:
            fr = cv2.resize(fr, (self.rw, self.rh), interpolation=cv2.INTER_AREA)
        if self.turn:
            fr = np.rot90(fr, -self.turn)
        fr = cv2.cvtColor(np.ascontiguousarray(fr), cv2.COLOR_BGR2RGB)
        self.cache[i] = fr
        for k in sorted(self.cache)[:-4]:
            del self.cache[k]
        return fr

    def correction(self, sigma):
        """How far each frame sits from a smooth version of the camera's path, in the turned frame's pixels."""
        r = int(sigma * 3)
        g = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
        g /= g.sum()
        pad = np.pad(self.path, ((r, r), (0, 0)), mode="edge")
        c = np.stack([np.convolve(pad[:, i], g, "valid") for i in range(3)], 1) - self.path
        c[:, :2] *= self.k
        for _ in range(self.turn):
            c[:, :2] = np.c_[-c[:, 1], c[:, 0]]
        return c

    def close(self):
        if self.cap is not None:
            self.cap.release()
        self.cap, self.cache = None, {}


def blend_flow(a, b, q):
    """A frame between a and b by optical flow, for slow motion."""
    if q < 0.03:
        return a
    if q > 0.97:
        return b
    ga = cv2.cvtColor(cv2.resize(a, (W // 2, H // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, (W // 2, H // 2), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    f_ab = cv2.resize(dis.calc(ga, gb, None), (W, H), interpolation=cv2.INTER_LINEAR) * 2
    f_ba = cv2.resize(dis.calc(gb, ga, None), (W, H), interpolation=cv2.INTER_LINEAR) * 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wa = cv2.remap(a, xx + f_ba[..., 0] * q, yy + f_ba[..., 1] * q, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.remap(b, xx + f_ab[..., 0] * (1 - q), yy + f_ab[..., 1] * (1 - q), cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(wa, 1 - q, wb, q, 0)


# ---------- the look ----------
def make_curve():
    """A filmic tone curve: deeper shadows, a soft shoulder on the highlights."""
    x = np.arange(256, dtype=np.float32) / 255
    s = x + 0.10 * (x - 0.5) * (1 - np.abs(2 * x - 1)) * 2
    s = np.where(s > 0.8, 0.8 + (s - 0.8) * 0.82, s)
    return (np.clip(s / s[-1], 0, 1) * 255).astype(np.uint8)


CURVE = make_curve()
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (np.clip(np.sqrt(((_xx - W / 2) / (W * 0.74)) ** 2 + ((_yy - H * 0.5) / (H * 0.74)) ** 2) - 0.5, 0, 1) ** 1.7)[..., None]
del _yy, _xx
WARM = np.array([1.0, 0.62, 0.34], np.float32)


def grade(img, dim=0.0):
    """uint8 RGB -> float RGB: warm highlights, slightly cool shadows, richer colour, a soft glow around bright things."""
    x = cv2.LUT(img, CURVE).astype(np.float32) / 255
    lum = (x @ LUMA)[..., None]
    x = lum + (x - lum) * 1.2
    x = x + (1 - lum) ** 2 * np.array([-0.012, -0.002, 0.022], np.float32) + lum ** 2 * np.array([0.022, 0.006, -0.03], np.float32)
    hi = cv2.resize(np.clip(lum[..., 0] - 0.74, 0, 1), (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    hi = cv2.resize(cv2.GaussianBlur(hi, (0, 0), 7), (W, H), interpolation=cv2.INTER_LINEAR)
    x = x + hi[..., None] * WARM * 0.5
    if dim:
        x = np.power(np.clip(x, 0, 1), 1 + 0.5 * dim) * (1 - 0.3 * dim)
    return x * (1 - VIG * (0.42 + 0.3 * dim))


def flash(img, k, col=(1.0, 0.96, 0.88)):
    return img + (np.array(col, np.float32) - img) * k


def dir_blur(img, length, vertical=False):
    if length < 3:
        return img
    length = int(length) | 1
    return cv2.blur(img, (1, length) if vertical else (length, 1), borderType=cv2.BORDER_REFLECT)


def slide(img, dx):
    if abs(dx) < 0.5:
        return img
    M = np.array([[1, 0, dx], [0, 1, 0]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


def light_leak(img, q, strength=1.0):
    """A warm light leak sweeping across the frame (q 0..1)."""
    if not 0 < q < 1:
        return img
    x = np.linspace(0, 1, W // 8, dtype=np.float32)[None, :]
    y = np.linspace(0, 1, H // 8, dtype=np.float32)[:, None]
    c = -0.3 + 1.6 * q + 0.25 * (y - 0.5)
    band = np.exp(-((x - c) / 0.3) ** 2) * math.sin(math.pi * q) * strength
    band = cv2.resize(band, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    col = np.array([1.0, 0.58, 0.2], np.float32) * (1 - 0.4 * band) + np.array([0.95, 0.3, 0.55], np.float32) * 0.4 * band
    return 1 - (1 - img) * (1 - np.clip(band * col, 0, 1))


# each wash is a few pigments, the way a brush actually carries them, rather than a whole rainbow
WASHES = {
    "plum": (PURPLE, VIOLET, MAGENTA),
    "sun": (GOLD, ORANGE, (250, 150, 96)),
    "glass": (MAGENTA, VIOLET, TEAL),
}


class Paint:
    """The film's signature move: watercolour bleeding across the frame."""

    def __init__(self):
        self.h, self.w = H // 3, W // 3
        self.n1 = periodic_noise(self.h, self.w, 5, ((3, 1.0), (7, 0.7), (16, 0.45), (40, 0.22)))
        self.n2 = periodic_noise(self.h, self.w, 9, ((10, 1.0), (28, 0.7), (70, 0.4)))
        self.yy, self.xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.granule = cv2.resize(self.n2, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        self.washes = {}

    def wash(self, name):
        """One wash of paint: its pigments meet in soft patches, never in rings."""
        if name not in self.washes:
            pig = np.array(WASHES[name], np.float32) / 255
            seed = sum(map(ord, name))
            n = np.stack([periodic_noise(self.h, self.w, seed + 7 * i, ((3, 1.0), (8, 0.6), (20, 0.3)))
                          for i in range(len(pig))], -1)
            w = np.exp((n - n.mean((0, 1))) * 9)
            w /= w.sum(-1, keepdims=True)
            col = cv2.resize(w @ pig, (W, H), interpolation=cv2.INTER_LINEAR)
            # denser where pigment pools, thinner where the paper shows through
            self.washes[name] = np.clip(1 - (1 - col) * (0.72 + 0.6 * self.granule), 0, 1)
        return self.washes[name]

    def field(self, cx, cy, t):
        """Distance from the point the paint starts at, made uneven by the wet edge. It creeps as time passes."""
        d = np.sqrt((self.xx * 3 - cx) ** 2 + (self.yy * 3 - cy) ** 2) / 2200
        roll = np.roll(self.n1, int(t * 18), axis=1)
        return d + 0.3 * (roll - 0.5) + 0.07 * (self.n2 - 0.5)

    def bleed(self, under, over, q, cx, cy, t, wash):
        """Paint spreads from (cx, cy) as q goes 0 -> 1, and the next picture shows through behind it."""
        F = self.field(cx, cy, t)
        lead = 1.3 * q - 0.16
        a = np.clip((lead - F) / 0.018, 0, 1)
        b = np.clip((lead - 0.17 - F) / 0.05, 0, 1)
        ring = np.exp(-((lead - F) / 0.02) ** 2)   # pigment gathers at the edge of a wash
        a = cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        b = cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        ring = cv2.resize(ring, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        colour = self.wash(wash) * (1 - 0.25 * ring)
        out = under * (1 - a) + colour * a
        return out * (1 - b) + over * b

    def blooms(self, img, t, grow, spots):
        """Washes of colour sitting on paper, so the paper's texture shows through them. spots: (x, y, reach, wash)."""
        for x, y, reach, wash in spots:
            d = reach * grow - self.field(x, y, t * 0.3)
            k = np.clip(d / 0.1, 0, 1) * 0.62 + np.exp(-(d / 0.02) ** 2) * 0.16
            k = cv2.resize(k, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
            img = img * (1 - k * (1 - self.wash(wash)))
        return img


# ---------- timeline ----------
def build_timeline():
    segs, b = [], 0
    for i, sh in enumerate(SHOTS):
        segs.append(dict(i=i, shot=sh, key=sh["key"], kind=sh.get("kind", "clip"), b0=b, b1=b + sh["beats"]))
        b += sh["beats"]
    for s in segs:
        s["t0"], s["t1"] = bt(s["b0"]), bt(s["b1"])
    return segs


class Renderer:
    def __init__(self):
        self.segs = build_timeline()
        self.total = self.segs[-1]["t1"]
        self.by_key = {s["key"]: s for s in self.segs}
        self.clips = {}
        self.cache = {}
        self.paint = Paint()
        g = np.random.default_rng(2).normal(0, 1, (H, W)).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 0.8) * 0.012 + cv2.resize(periodic_noise(H // 8, W // 8, 3), (W, H)) * 0.018
        self.paper = np.array(PAPER, np.float32)[None, None] / 255 * np.ones((H, W, 1), np.float32) + g[..., None]
        self.shade_top = np.clip(1 - np.arange(H, dtype=np.float32) / 980, 0, 1)[:, None, None] ** 1.25
        self.logo_small = to_sprite(logo_image(150))
        self.build_type()

    def release(self):
        for c in self.clips.values():
            c.close()
        self.clips.clear()
        self.cache.clear()

    def build_type(self):
        f_ask = font(ITALIC, 94)
        self.ask = [to_sprite(lettering(t, f_ask, 0, fill=CREAM, shadow=0.75)) for t in HOOK["ask"]]
        self.answer = to_sprite(lettering(HOOK["answer"], font(ITALIC, 214), 0, fill=CREAM, shadow=0.8))
        self.card = [to_sprite(lettering(HOOK["card"][0], font(SERIF, 176), 0, fill=INK, shadow=0)),
                     to_sprite(lettering(HOOK["card"][1], font(ITALIC, 196), 0, fill=PURPLE, shadow=0)),
                     to_sprite(lettering(HOOK["card"][2], font(SERIF, 176), 0, fill=INK, shadow=0))]
        self.card_stroke = brush_stroke(self.card[1].shape[1] + 60, 62, GOLD, 5)
        f_kick = font(SANS, 33, 700)
        f_no = font(ITALIC, 172)
        self.chapters = {}
        for key, c in CHAPTERS.items():
            no = to_sprite(lettering("Nothing.", f_no, 0, fill=CREAM, shadow=0.8))
            self.chapters[key] = dict(kick=to_sprite(lettering(c["kicker"], f_kick, 9, fill=CREAM, shadow=0.8)), no=no,
                                      real=to_sprite(lettering(c["real"], font(SERIF, 186), 0, fill=WHITE, shadow=0.85)),
                                      stroke=brush_stroke(no.shape[1] + 56, 86, MAGENTA if key == "crane" else GOLD,
                                                          7 if key == "crane" else 11))
        self.pills = [(k, b, x, y, Pill(t)) for k, b, t, x, y in PILLS]
        f_step, f_step_kick = font(ITALIC, 96), font(SANS, 31, 700)
        self.steps = []
        for st in STEPS:
            kick = to_sprite(lettering(st["kick"], f_step_kick, 9, fill=WHITE, shadow=0.8)) if st["kick"] else None
            lines = [to_sprite(lettering(t, f_step, 0, fill=WHITE, shadow=0.85)) for t in st["lines"]]
            self.steps.append(dict(st, kick=kick, lines=lines))
        self.breath = to_sprite(lettering(BREATH, font(ITALIC, 128), 0, fill=WHITE, shadow=0.7))
        self.room = [to_sprite(lettering(ROOM[0], font(ITALIC, 120), 0, fill=CREAM, shadow=0.85)),
                     to_sprite(lettering(ROOM[1], font(SERIF, 150), 0, fill=WHITE, shadow=0.85))]
        # the closing card
        self.e_logo = to_sprite(logo_image(330))
        self.e_l1 = to_sprite(lettering(END["line1"], font(ITALIC, 92), 0, fill=INK, shadow=0))
        self.e_l2 = to_sprite(lettering(END["line2"], font(ITALIC, 92), 0, fill=INK, shadow=0))
        self.e_stroke = brush_stroke(self.e_l2.shape[1] + 30, 34, GOLD, 13)
        pt = to_sprite(lettering(END["pill"], font(SANS, 34, 700), 7, fill=WHITE, shadow=0))
        pw, ph = pt.shape[1] + 84, pt.shape[0] + 46
        m = rounded_mask(pw, ph, ph // 2)
        fill = np.dstack([np.array(PURPLE, np.float32)[None, None] / 255 * m[..., None], m])
        fill[(ph - pt.shape[0]) // 2:(ph - pt.shape[0]) // 2 + pt.shape[0], 42:42 + pt.shape[1]] *= 1 - pt[..., 3:4]
        fill[(ph - pt.shape[0]) // 2:(ph - pt.shape[0]) // 2 + pt.shape[0], 42:42 + pt.shape[1]] += pt
        self.e_pill = fill
        f_row = font(SANS, 43, 600)
        self.e_rows = [(to_sprite(icon_image(k, 46, PURPLE)), to_sprite(lettering(t, f_row, 0, fill=INK, shadow=0)))
                       for k, t in END["rows"]]
        self.stars = [to_sprite(star_image(s, c)) for s in (26, 40, 58) for c in (GOLD, MAGENTA, VIOLET, TEAL, ORANGE)]

    # ----- a shot's camera -----
    def source(self, sh):
        name = sh["clip"]
        if name not in self.clips:
            data = json.loads((FACES / f"{name}.json").read_text())
            portrait = data["h"] > data["w"]
            zmax = max(sh.get("zoom", (1.0, 1.0)))
            self.clips[name] = Source(name, sh.get("turn", 0), min(2160, 1080 * zmax * 1.2) if portrait else None)
        return self.clips[name]

    @staticmethod
    def src_frame(sh, tau):
        speed = sh.get("speed", 1.0)
        if not isinstance(speed, (list, tuple)):
            return sh.get("start", 0) + tau * FPS * speed
        ts = np.array([p[0] * BEAT for p in speed])
        vs = np.array([p[1] for p in speed], np.float64)
        fine = np.linspace(0, tau, max(2, int(tau * 120) + 2))
        return sh.get("start", 0) + float(np.trapezoid(np.interp(fine, ts, vs), fine)) * FPS

    def matrix(self, sh, src, f, tau, dur):
        """Clip pixels to screen for this moment: an eased push, a punch on the beat, steadied footage."""
        z0, z1 = sh.get("zoom", (1.04, 1.0))
        e = ease_in_out(tau / dur)
        z = z0 + (z1 - z0) * e
        if sh.get("punch"):
            z *= 1 + sh["punch"] * math.exp(-tau / 0.16)
        if sh.get("pan"):
            (x0, y0), (x1, y1) = sh["pan"]
            cx, cy = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
        else:
            cx, cy = sh.get("center", (0.5, 0.5))
        s = max(W / src.w, H / src.h) * z
        half_w, half_h = W / 2 / s, H / 2 / s
        px, py = min(max(cx * src.w, half_w), src.w - half_w), min(max(cy * src.h, half_h), src.h - half_h)
        ox, oy, ang = 0.0, 0.0, 0.0
        if sh.get("steady"):
            cor = src.correction(sh["steady"])
            c = cor[int(min(len(cor) - 1, max(0, f)))]
            ox, oy, ang = c
        # never reveal the edge of the frame
        ox = max(px + half_w - src.w, min(px - half_w, ox))
        oy = max(py + half_h - src.h, min(py - half_h, oy))
        ca, sa = math.cos(ang) * s, math.sin(ang) * s
        return np.array([[ca, -sa, W / 2 - ca * px + sa * py + ox * s],
                         [sa, ca, H / 2 - sa * px - ca * py + oy * s]], np.float32)

    def sample(self, sh, tau, dur):
        src = self.source(sh)
        f = min(self.src_frame(sh, tau), src.n - 1.001)
        M = self.matrix(sh, src, f, tau, dur)
        i0 = int(math.floor(f))
        interp = cv2.INTER_CUBIC if M[0, 0] > 0.6 else cv2.INTER_AREA
        a = cv2.warpAffine(src.frame(i0), M, (W, H), flags=interp, borderMode=cv2.BORDER_REPLICATE)
        q = f - i0
        if q < 0.03:
            return a
        b = cv2.warpAffine(src.frame(i0 + 1), M, (W, H), flags=interp, borderMode=cv2.BORDER_REPLICATE)
        return blend_flow(a, b, q)

    def clip_picture(self, sg, t):
        sh = sg["shot"]
        tau = max(0.0, t - sg["t0"])  # a transition can show a shot just before it starts: hold on its first frame
        dur = sg["t1"] - sg["t0"]
        img = grade(self.sample(sh, tau, dur), sh.get("dim", 0.0))
        return img

    def photo_picture(self, sg, t):
        sh = sg["shot"]
        if "room" not in self.cache:
            im = cv2.imread(str(CLEAN / f"{sh['photo']}.jpg"))
            k = 2700 / im.shape[1]
            im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            self.cache["room"] = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        pic = self.cache["room"]
        ph, pw = pic.shape[:2]
        e = ease_in_out((t - sg["t0"]) / (sg["t1"] - sg["t0"]))
        z0, z1 = sh["zoom"]
        s = max(W / pw, H / ph) * (z0 + (z1 - z0) * e)
        (x0, y0), (x1, y1) = sh["pan"]
        cx, cy = (x0 + (x1 - x0) * e) * pw, (y0 + (y1 - y0) * e) * ph
        half_w, half_h = W / 2 / s, H / 2 / s
        cx, cy = min(max(cx, half_w), pw - half_w), min(max(cy, half_h), ph - half_h)
        M = np.array([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]], np.float32)
        return grade(cv2.warpAffine(pic, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE))

    def card_picture(self, sg, t):
        since = t - sg["t0"]
        img = self.paint.blooms(self.paper.copy(), t, ease_out_cubic(since / 1.2) + 0.15 * since,
                                [(1080, 120, 0.2, "plum"), (0, 1820, 0.22, "sun")])
        ys = [700, 866, 1046]
        for i, spr in enumerate(self.card):
            rise(img, spr, W / 2, ys[i], (since - 0.12 - 0.11 * i) / 0.5)
        q = (since - 0.62) / 0.3
        if q > 0:
            blit(img, reveal_lr(self.card_stroke, ease_in_out(q)), W / 2, ys[1] + 92, 1.0, -1.0)
            # keep the word on top of its stroke
            blit(img, self.card[1], W / 2, ys[1])
        return img

    def hold_picture(self, sg, t):
        """The last frame of the shot before it, frozen, with a slow push."""
        if "hold" not in self.cache:
            of = self.by_key[sg["shot"]["of"]]
            sh = of["shot"]
            self.cache["hold"] = (self.sample(sh, of["t1"] - of["t0"] - 1e-3, of["t1"] - of["t0"]), sh.get("dim", 0.0))
        pic, dim = self.cache["hold"]
        s = 1 + 0.035 * (t - sg["t0"])
        M = np.array([[s, 0, W / 2 * (1 - s)], [0, s, H / 2 * (1 - s)]], np.float32)
        return grade(cv2.warpAffine(pic, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE), dim)

    def end_picture(self, sg, t):
        since = t - sg["t0"]
        hit = bt(END["hit"])
        after = since - hit
        grow = 0.8 + 0.03 * since + (0.14 * ease_out_expo(after / 0.5) if after > 0 else 0)
        img = self.paint.blooms(self.paper.copy(), t, grow, [(1080, 0, 0.3, "plum"), (0, 1920, 0.32, "sun")])
        y_logo = 492 - 3 * math.sin(since * 2.2)
        pl = (since - 0.1) / 0.45
        pop = 1 + 0.07 * math.exp(-after / 0.14) if after > 0 else 1.0
        if pl > 0:
            blit(img, self.e_logo, W / 2, y_logo, (0.86 + 0.14 * ease_out_back(pl)) * pop, 0, clamp01(pl * 2.2))
        rise(img, self.e_l1, W / 2, 728, (since - 0.45) / 0.5)
        rise(img, self.e_l2, W / 2, 828, (since - 0.56) / 0.5)
        qs = (since - bt(1.9)) / 0.4
        if qs > 0:
            blit(img, reveal_lr(self.e_stroke, ease_in_out(qs)), W / 2, 890)
            blit(img, self.e_l2, W / 2, 828)
        pp = (since - bt(3)) / 0.35
        if pp > 0:
            blit(img, self.e_pill, W / 2, 998, 0.8 + 0.2 * ease_out_back(pp), 0, clamp01(pp * 2.5))
        block = 52 + max(txt.shape[1] for _, txt in self.e_rows)  # the rows are left-aligned, the block is centred
        x_icon = (W - block) / 2 + 23
        y = 1134
        for i, (icon, txt) in enumerate(self.e_rows):
            q = (since - bt(4 + i)) / 0.4
            if q > 0:
                a = clamp01(q * 2.5)
                dx = 24 * (1 - ease_out_cubic(q))
                blit(img, icon, x_icon + dx, y, 1.0, 0, a)
                blit(img, txt, x_icon + 52 + txt.shape[1] / 2 + dx, y, 1.0, 0, a)
            y += 88
        if after > 0:
            for i, s in enumerate(self.stars * 3):
                q = (after - 0.008 * i) / 1.3
                if 0 < q < 1:
                    a0 = hash01(i, 1) * 2 * math.pi
                    d = (240 + 620 * hash01(i, 2)) * ease_out_expo(q * 1.4)
                    blit(img, s, W / 2 + math.cos(a0) * d, y_logo + math.sin(a0) * d * 1.2 + 260 * q * q, 0.7 + 0.6 * hash01(i, 3),
                         q * 200 * (hash01(i, 4) - 0.5), clamp01((1 - q) * 3))
        return img

    def picture(self, sg, t):
        kind = sg["kind"]
        if kind == "clip":
            return self.clip_picture(sg, t)
        if kind == "photo":
            return self.photo_picture(sg, t)
        if kind == "card":
            return self.card_picture(sg, t)
        if kind == "hold":
            return self.hold_picture(sg, t)
        return self.end_picture(sg, t)

    # ----- the words over the footage -----
    def shaded(self, img, a):
        return img * (1 - self.shade_top * a)

    def overlay(self, img, sg, t):
        key, since, dur = sg["key"], t - sg["t0"], sg["t1"] - sg["t0"]
        if key == "ask":
            img = self.shaded(img, 0.55)
            rise(img, self.ask[0], W / 2, 470, (since - 0.12) / 0.45)
            rise(img, self.ask[1], W / 2, 572, (since - 0.42) / 0.45)
        elif key == "answer":
            img = self.shaded(img, 0.5)
            rise(img, self.answer, W / 2, 560, (since - 0.04) / 0.34)
        elif key == "breath":
            pass
        elif key == "room":
            img = img * (1 - 0.32 * clamp01((since - 0.1) / 0.4))
            rise(img, self.room[0], W / 2, 800, (since - 0.15) / 0.45)
            rise(img, self.room[1], W / 2, 950, (since - 0.15 - bt(1)) / 0.5)
        for st in self.steps:
            if st["shot"] == key and bt(st["b0"]) <= since < bt(st["b1"]):
                img = self.step(img, st, since - bt(st["b0"]), bt(st["b1"] - st["b0"]))
        # chapter titles can run across several shots
        for ck, c in CHAPTERS.items():
            s0 = self.by_key[ck]
            t0 = s0["t0"] + bt(c["at"])
            t1 = t0 + bt(c["beats"])
            if t0 <= t < t1 and sg["kind"] == "clip":
                img = self.chapter(img, ck, t - t0, t1 - t0)
        for k, b, x, y, pill in self.pills:
            if sg is self.by_key[k]:
                pill.draw(img, x, y, (since - bt(b)) / 0.32)
        if sg["kind"] in ("clip", "photo", "hold"):
            a = 0.96
            if key == "ask":
                a *= clamp01((since - 0.2) / 0.3)
            blit(img, self.logo_small, 112, 208, 1.0, 0, a)
        return img

    def step(self, img, st, since, dur):
        """A plain caption saying what's happening, on a soft dark band so white type reads on the bright tables."""
        y, leading = st["y"], 104
        kick, lines = st["kick"], st["lines"]
        first = y + 62 if kick is not None else y
        mid = (y + first + leading * (len(lines) - 1)) / 2
        out = clamp01((dur - since) / 0.12)
        band = np.exp(-((np.arange(H, dtype=np.float32) - mid) / (190 + 40 * len(lines))) ** 2)[:, None, None]
        img = img * (1 - 0.55 * clamp01(since / 0.18) * out * band)
        if kick is not None:
            rise(img, kick * out, W / 2, y, since / 0.32)
        for i, spr in enumerate(lines):
            rise(img, spr * out, W / 2, first + leading * i, (since - 0.05 - 0.16 * i) / 0.38)
        return img

    def chapter(self, img, key, since, dur):
        c = self.chapters[key]
        out = clamp01((dur - since) / 0.16)
        img = self.shaded(img, 0.72 * out * clamp01(since / 0.2))
        rise(img, c["kick"] * out, W / 2, 322, (since - 0.05) / 0.4)
        rise(img, c["no"] * out, W / 2, 452, (since - 0.1) / 0.4)
        q = (since - bt(1)) / 0.26
        if q > 0:
            blit(img, reveal_lr(c["stroke"], ease_in_out(q)), W / 2, 462, 1.0, -1.5, out)
        rise(img, c["real"] * out, W / 2, 628, (since - bt(1) - 0.2) / 0.42)
        return img

    # ----- one frame -----
    def composed(self, sg, t):
        return self.overlay(self.picture(sg, t), sg, t)

    def frame(self, t):
        t = min(t, self.total - 1e-4)
        i = next(k for k, s in enumerate(self.segs) if s["t0"] <= t < s["t1"])
        sg = self.segs[i]
        nxt = self.segs[i + 1] if i + 1 < len(self.segs) else None
        keep = {sg["shot"].get("clip"), nxt["shot"].get("clip") if nxt else None}
        for name in [n for n in self.clips if n not in keep]:
            self.clips.pop(name).close()
        img = self.composed(sg, t)
        since = t - sg["t0"]
        until = sg["t1"] - t
        # whip pans across the cut
        if nxt and nxt["shot"].get("whip") and until < 3.5 / FPS:
            q = 1 - until / (3.5 / FPS)
            d = nxt["shot"]["whip"]
            img = dir_blur(slide(img, -d * 0.34 * W * q * q), 1 + q * 240)
        if sg["shot"].get("whip") and since < 3.5 / FPS:
            q = 1 - since / (3.5 / FPS)
            d = sg["shot"]["whip"]
            img = dir_blur(slide(img, d * 0.34 * W * q * q), 1 + q * 240)
        # paint bleeds: from the answer into the card, the card into the band coming in,
        # across the frozen frame into the second half, and from the room into the closing card
        img = self.bleeds(img, sg, nxt, t)
        # the lifts in the music
        for b in MUSIC["lifts"]:
            d = t - bt(b)
            if 0 <= d < 0.3:
                img = flash(img, 0.5 * math.exp(-d / 0.07))
            if 0 <= d < 0.85:
                img = light_leak(img, d / 0.85, 0.8)
        return img

    def bleeds(self, img, sg, nxt, t):
        key = sg["key"]
        if key == "answer" and nxt and t > sg["t1"] - bt(0.45):
            q = (t - (sg["t1"] - bt(0.45))) / bt(0.7)
            return self.paint.bleed(img, self.composed(nxt, t), q, 540, 620, t, "plum")
        if key == "card" and t < sg["t0"] + bt(0.25):
            q = (t + bt(0.45) - sg["t0"]) / bt(0.7)
            return self.paint.bleed(self.composed(self.by_key["answer"], t), img, q, 540, 620, t, "plum")
        if key == "card" and t > sg["t1"] - bt(0.7):
            q = (t - (sg["t1"] - bt(0.7))) / bt(0.95)
            return self.paint.bleed(img, self.composed(nxt, t), q, 540, 880, t, "sun")
        if key == "mats" and t < sg["t0"] + bt(0.25):
            q = (t + bt(0.7) - sg["t0"]) / bt(0.95)
            return self.paint.bleed(self.composed(self.by_key["card"], t), img, q, 540, 880, t, "sun")
        if key == "breath":
            q = (t - sg["t0"]) / (sg["t1"] - sg["t0"])
            over = self.composed(nxt, t)
            out = self.paint.bleed(img, over, 0.04 + q * 0.92, 540, 1120, t, "glass")
            # the line sits on the paint, and goes as the band returns
            a = clamp01((t - sg["t0"] - 0.08) / 0.2) * clamp01((sg["t1"] - t) / 0.08)
            blit(out, self.breath, W / 2, 900, 1.0 + 0.03 * q, 0, a)
            return out
        if key == "room" and t > sg["t1"] - bt(0.5):
            q = (t - (sg["t1"] - bt(0.5))) / bt(0.8)
            return self.paint.bleed(img, self.composed(nxt, t), q, 540, 300, t, "plum")
        if key == "end" and t < sg["t0"] + bt(0.3):
            q = (t + bt(0.5) - sg["t0"]) / bt(0.8)
            return self.paint.bleed(self.composed(self.by_key["room"], t), img, q, 540, 300, t, "plum")
        return img


# ---------- sound ----------
def swish(sr, length=0.42, lo=500.0, hi=5200.0, seed=1):
    """A brush across paper: band-limited noise that rises and falls."""
    n = int(length * sr)
    x = np.random.default_rng(seed).normal(0, 1, n)
    env = np.sin(np.linspace(0, math.pi, n)) ** 1.6
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / sr)
    spec *= np.exp(-((np.log(f + 1) - np.log(np.sqrt(lo * hi))) / np.log(hi / lo) * 2.2) ** 2)
    y = np.fft.irfft(spec, n) * env
    y = (y / (np.abs(y).max() + 1e-9)).astype(np.float32)
    return np.stack([y, y], 1) * 0.6


def sub_boom(sr):
    """A soft low swell for the moment the band comes in."""
    n = int(1.1 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    y = np.sin(2 * np.pi * (46 * t + 14 * (1 - np.exp(-t * 7)) / 7)) * np.exp(-t * 3.6) * np.clip(t / 0.006, 0, 1)
    return np.stack([y, y], 1).astype(np.float32) * 0.8


def shimmer(sr, seed=4):
    """A few soft high chimes, for the stars at the end."""
    n = int(1.6 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    y = np.zeros(n, np.float32)
    rng = np.random.default_rng(seed)
    for f in (1760, 2093, 2349, 2794, 3136, 3520):
        at = rng.uniform(0, 0.28)
        k = np.clip(t - at, 0, None)
        y += np.sin(2 * np.pi * f * k).astype(np.float32) * np.exp(-k * 5.5).astype(np.float32) * (t > at)
    y /= np.abs(y).max() + 1e-9
    return np.stack([y, y], 1) * 0.5


def room_tone(sr, secs):
    """The real sound of the room, very low, under the opening (from a clip with no words in it)."""
    x = decode(next((ROOT / "source" / "2026-11-04_raw").glob("IMG_8694.*")), 0.2, min(4.4, secs + 0.1))
    x = x[:int(secs * sr)]
    f = int(0.25 * sr)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    rms = np.sqrt((x ** 2).mean()) + 1e-9
    return x / rms * 10 ** (-34 / 20)


def build_audio(r, music=True):
    sr = 48000
    n = int(math.ceil(r.total * sr))
    mix = np.zeros((n, 2), np.float32)
    if music:
        song = ROOT / "source" / "music" / MUSIC["file"]
        xf = int(0.024 * sr)
        for b_film, b_song, beats in MUSIC["parts"]:
            start = MUSIC["first_beat"] + b_song * BEAT
            m = decode(song, start, beats * BEAT + 0.03)[:int(beats * BEAT * sr) + xf]
            m[:xf] *= np.linspace(0, 1, xf)[:, None]
            m[-xf:] *= np.linspace(1, 0, xf)[:, None]
            i = int(bt(b_film) * sr)
            j = min(n, i + len(m))
            mix[i:j] += m[:j - i] * 0.95
        # the opening sits lower, so the band coming in feels like a lift
        k = int(bt(8) * sr)
        mix[:k] *= (np.linspace(0.5, 0.82, k) ** 1.4)[:, None]
    i = 0
    tone = room_tone(sr, bt(8))
    mix[i:len(tone)] += tone
    breath, end = r.by_key["breath"]["t0"], r.by_key["end"]["t0"]
    ev = [(swish(sr, 0.5, seed=2), bt(4.55), -9), (swish(sr, 0.7, 300, 3000, seed=3), bt(7.3), -9),
          (sub_boom(sr), bt(MUSIC["lifts"][0]), -3), (sub_boom(sr), bt(MUSIC["lifts"][1]), -2),
          (swish(sr, 1.05, 240, 2600, seed=5), breath + 0.03, -8), (swish(sr, 0.5, seed=8), end - bt(0.5), -9),
          (shimmer(sr), end + bt(END["hit"]), -9),
          (shimmer(sr, seed=7), r.by_key["stand"]["t0"] + bt(3.0), -15)]  # a small chime as the tower holds
    # the two strike-throughs, and every whip pan
    for ck, c in CHAPTERS.items():
        ev.append((swish(sr, 0.3, 900, 7000, seed=6), r.by_key[ck]["t0"] + bt(c["at"] + 1), -10))
    for sg in r.segs:
        if sg["shot"].get("whip"):
            ev.append((swish(sr, 0.26, 700, 6000, seed=10 + sg["i"]), sg["t0"] - 0.13, -15))
    for snd, t, g in ev:
        i = max(0, int(t * sr))
        j = min(n, i + len(snd))
        mix[i:j] += snd[:j - i] * 10 ** (g / 20)
    tail = int(0.2 * sr)
    mix[-tail:] *= np.linspace(1, 0, tail)[:, None]
    work = ROOT / "work"
    raw = work / ("mix_raw.wav" if music else "mix_raw_nomusic.wav")
    sf.write(str(raw), mix, sr, subtype="FLOAT")
    out = raw.with_name(raw.stem.replace("_raw", "") + ".wav")
    loudness_normalise(raw, out)
    return out


def main():
    r = Renderer()
    print(f"{len(r.segs)} segments, {r.total:.2f} s", flush=True)
    if "--stills" in sys.argv:
        out = ROOT / "work" / "stills"
        out.mkdir(parents=True, exist_ok=True)
        for arg in sys.argv[sys.argv.index("--stills") + 1:]:
            t = float(arg)
            fr = (np.clip(r.frame(t), 0, 1) * 255 + 0.5).astype(np.uint8)
            Image.fromarray(fr).save(out / f"t{t:06.2f}.jpg", quality=90)
            print("wrote", t, flush=True)
        return
    EXPORTS.mkdir(exist_ok=True)
    cover = (np.clip(r.frame(bt(6.6)), 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(cover).save(EXPORTS / "nothing_cover.jpg", quality=95)
    raw = ROOT / "work" / "frames.rgb"
    render_frames(r, raw)
    music, sfx_only = build_audio(r, music=True), build_audio(r, music=False)
    dur = r.total
    del r
    gc.collect()
    reel = EXPORTS / "nothing_reel.mp4"
    encode(raw, reel, music, dur)
    remux(reel, sfx_only, EXPORTS / "nothing_reel_nomusic.mp4")
    if reel.stat().st_size > 29 * 2 ** 20:  # when the master already fits, a second encode would only lose quality
        phone_copy(reel, EXPORTS / "nothing_reel_phone.mp4")
    raw.unlink()


if __name__ == "__main__":
    main()
