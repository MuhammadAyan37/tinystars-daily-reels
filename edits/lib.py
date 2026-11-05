"""Shared drawing, lettering and encoding helpers for the daily reels."""
import gc
import json
import math
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "brand" / "fonts"
W, H, FPS = 1080, 1920, 30

# fonts: an elegant italic serif for the big words, a tight modern sans for everything small
SERIF = "InstrumentSerif-Regular.ttf"
ITALIC = "InstrumentSerif-Italic.ttf"
SANS = "InterTight.ttf"

# palette (RGB), from the daycare's logo and the stained-glass window in the classroom
INK = (35, 20, 48)
PURPLE = (100, 42, 115)
GOLD = (246, 199, 37)
MAGENTA = (214, 44, 122)
ORANGE = (248, 124, 44)
TEAL = (24, 164, 170)
VIOLET = (118, 72, 196)
CREAM = (255, 247, 234)
PAPER = (250, 244, 232)
WHITE = (255, 255, 255)


# ---------- easing ----------
def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out_cubic(p):
    p = clamp01(p)
    return 1 - (1 - p) ** 3


def ease_out_expo(p):
    p = clamp01(p)
    return 1.0 if p >= 1 else 1 - 2 ** (-10 * p)


def ease_out_back(p, s=1.7):
    p = clamp01(p) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def ease_in_out(p):
    return 0.5 - 0.5 * math.cos(math.pi * clamp01(p))


def hash01(*k):
    """Deterministic pseudo-random number in [0, 1) from integers."""
    h = 2166136261
    for v in k:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 1274126177) & 0xFFFFFFFF
    return (h & 0xFFFFFF) / float(0x1000000)


# ---------- lettering and sprites ----------
def to_sprite(img):
    """PIL RGBA -> premultiplied float RGBA."""
    a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def text_width(text, f, track=0):
    return f.getlength(text) if not track else sum(f.getlength(c) for c in text) + track * (len(text) - 1)


def lettering(text, f, track=0, fill=CREAM, shadow=0.5):
    """Text with letter-spacing and a soft drop shadow, cropped to what is drawn."""
    pad = 40
    asc, desc = f.getmetrics()
    w, h = int(text_width(text, f, track)) + 2 * pad, asc + desc + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    if track:
        x = pad
        for c in text:
            d.text((x, pad), c, font=f, fill=255)
            x += f.getlength(c) + track
    else:
        d.text((pad, pad), text, font=f, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * shadow))
        layer = Image.new("RGBA", (w, h), (15, 8, 20, 0))
        layer.putalpha(sh)
        out = Image.alpha_composite(out, layer.transform(out.size, Image.AFFINE, (1, 0, 0, 0, 1, -5)))
    ink = Image.new("RGBA", (w, h), tuple(fill) + (0,))
    ink.putalpha(mask)
    out = Image.alpha_composite(out, ink)
    return out.crop(out.getbbox())


def blit(frame, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    """Draw a premultiplied sprite centred at (cx, cy), in place."""
    if scale <= 0.01 or alpha <= 0.004:
        return
    h, w = spr.shape[:2]
    if abs(scale - 1) < 1e-3 and abs(rot) < 1e-3:
        warped, ox, oy = spr, w / 2, h / 2
    else:
        rad = math.radians(rot)
        bw = int(abs(w * scale * math.cos(rad)) + abs(h * scale * math.sin(rad))) + 4
        bh = int(abs(w * scale * math.sin(rad)) + abs(h * scale * math.cos(rad))) + 4
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
        M[0, 2] += bw / 2 - w / 2
        M[1, 2] += bh / 2 - h / 2
        warped = cv2.warpAffine(spr, M, (bw, bh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        ox, oy = bw / 2, bh / 2
    hh, ww = warped.shape[:2]
    x0, y0 = int(round(cx - ox)), int(round(cy - oy))
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(frame.shape[1], x0 + ww), min(frame.shape[0], y0 + hh)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    s = warped[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    region = frame[fy0:fy1, fx0:fx1]
    region *= 1 - s[..., 3:4] * alpha
    region += s[..., :3] * alpha


def rise(frame, spr, cx, cy, q, travel=None):
    """A line of type rising out of a mask, the way film titles do (q 0..1). In place."""
    if q <= 0:
        return
    h, w = spr.shape[:2]
    e = ease_out_expo(q)
    travel = h * 0.9 if travel is None else travel
    dy = (1 - e) * travel
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    rows = int(round(h - dy))
    if rows <= 0:
        return
    part = spr[:rows]
    fy0, fx0 = max(0, y0 + int(dy)), max(0, x0)
    fx1, fy1 = min(frame.shape[1], x0 + w), min(frame.shape[0], y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    s = part[fy0 - y0 - int(dy):fy1 - y0 - int(dy), fx0 - x0:fx1 - x0]
    region = frame[fy0:fy0 + s.shape[0], fx0:fx0 + s.shape[1]]
    a = clamp01(q * 3)
    region *= 1 - s[..., 3:4] * a
    region += s[..., :3] * a


def rounded_mask(w, h, r):
    """Anti-aliased rounded rectangle, float 0..1 (drawn at 4x, then scaled down)."""
    big = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), r * 4, fill=255)
    return np.asarray(big.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255.0


def icon_image(kind, d=52, col=PURPLE):
    """Small line icons for the contact details (phone, pin, globe), drawn at 4x for smooth edges."""
    s = d * 4
    m = Image.new("L", (s, s), 0)
    dr = ImageDraw.Draw(m)
    k = s / 208
    lw = int(14 * k)
    c = s / 2
    if kind == "phone":
        dr.rounded_rectangle((c - 56 * k, c - 98 * k, c + 56 * k, c + 98 * k), 24 * k, outline=255, width=lw)
        dr.rounded_rectangle((c - 18 * k, c + 62 * k, c + 18 * k, c + 74 * k), 6 * k, fill=255)
    elif kind == "pin":
        dr.ellipse((c - 74 * k, c - 104 * k, c + 74 * k, c + 44 * k), outline=255, width=lw)
        dr.line([(c - 60 * k, c - 2 * k), (c, c + 102 * k), (c + 60 * k, c - 2 * k)], fill=255, width=lw, joint="curve")
        dr.ellipse((c - 22 * k, c - 52 * k, c + 22 * k, c - 8 * k), fill=255)
    else:
        r = 94 * k
        dr.ellipse((c - r, c - r, c + r, c + r), outline=255, width=lw)
        dr.ellipse((c - r * 0.45, c - r, c + r * 0.45, c + r), outline=255, width=int(lw * 0.8))
        dr.line([(c - r, c), (c + r, c)], fill=255, width=int(lw * 0.8))
    out = Image.new("RGBA", (d, d), tuple(col) + (0,))
    out.putalpha(m.resize((d, d), Image.LANCZOS))
    return out


def logo_image(width):
    """The high-resolution Tiny Stars logo, falling back to the small one from the website."""
    path = ROOT / "brand" / "logo_hd.png"
    im = Image.open(path if path.exists() else ROOT / "brand" / "logo.png").convert("RGBA")
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def star_image(size, col):
    """A soft five-pointed star, like the one in the logo."""
    k = 4
    s = size * k
    pts = []
    for i in range(10):
        r = (0.5 if i % 2 == 0 else 0.23) * s
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(k * 0.6)).resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), tuple(col) + (0,))
    out.putalpha(m)
    return out


def periodic_noise(h, w, seed, octaves=((6, 1.0), (14, 0.5), (32, 0.25))):
    """Tileable cloudy noise in [0, 1] (FFT-filtered, so it wraps seamlessly)."""
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    out = np.zeros((h, w), np.float64)
    for cycles, amp in octaves:
        spec = np.fft.fft2(rng.standard_normal((h, w)))
        filt = np.exp(-(f * max(h, w) / cycles) ** 2)
        layer = np.real(np.fft.ifft2(spec * filt))
        out += amp * layer / (layer.std() + 1e-9)
    out = (out - out.min()) / (out.max() - out.min())
    return out.astype(np.float32)


def brush_stroke(w, h, col, seed=3):
    """A single dry brush stroke, as RGBA: uneven edges, bristle streaks running along its length, a slight curve."""
    rng = np.random.default_rng(seed)
    streaks = cv2.GaussianBlur(rng.normal(0, 1, (h, w // 4)).astype(np.float32), (0, 0), sigmaX=40, sigmaY=max(1.1, h / 30))
    streaks = cv2.resize(streaks / (streaks.std() + 1e-6), (w, h), interpolation=cv2.INTER_LINEAR)
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    edge = cv2.GaussianBlur(rng.normal(0, 1, (2, w // 8)).astype(np.float32), (0, 0), sigmaX=22, sigmaY=0.5)
    edge = cv2.resize(edge / (edge.std() + 1e-6), (w, 2), interpolation=cv2.INTER_LINEAR)
    top, bot = -0.74 + edge[0] * 0.07, 0.74 + edge[1] * 0.07
    body = np.clip((y - top[None, :]) / 0.06, 0, 1) * np.clip((bot[None, :] - y) / 0.06, 0, 1)
    # thin bristles show at the tail of the stroke, where the brush runs out of paint
    dry = np.clip((x - 0.45) / 0.55, 0, 1) ** 1.5
    bristle = np.clip(1.2 + 0.35 * streaks - dry * 0.85 * np.clip(0.8 - streaks, 0, 2), 0, 1)
    ends = np.clip(x / 0.03, 0, 1) * np.clip((1 - x + streaks * 0.03) / 0.05, 0, 1)
    a = (body * bristle * ends).astype(np.float32)
    # the curve
    shift = (np.sin(x[0] * math.pi) * h * 0.09).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = cv2.remap(a, xx, yy + shift[None, :], cv2.INTER_LINEAR)
    rgb = np.array(col, np.float32) / 255
    shade = (0.93 + 0.07 * np.clip(streaks, -1, 1))[..., None]
    return np.dstack([rgb * shade * a[..., None], a])


def reveal_lr(spr, q, soft=30):
    """Reveal a sprite from left to right (q 0..1)."""
    if q >= 1:
        return spr
    w = spr.shape[1]
    x = np.arange(w, dtype=np.float32)
    return spr * np.clip((q * (w + soft) - x) / soft, 0, 1)[None, :, None]


class Pill:
    """A small frosted label with tracked capitals."""

    def __init__(self, text, size=33):
        self.txt = to_sprite(lettering(text, font(SANS, size, 700), 5, fill=WHITE, shadow=0))
        self.w, self.h = self.txt.shape[1] + 62, self.txt.shape[0] + 40
        self.mask = rounded_mask(self.w, self.h, self.h // 2)

    def draw(self, img, cx, cy, q):
        if q <= 0:
            return
        a = clamp01(q * 2.5)
        cy = cy + 26 * (1 - ease_out_cubic(q))
        x0, y0 = int(cx - self.w / 2), int(cy - self.h / 2)
        x1, y1 = x0 + self.w, y0 + self.h
        if x0 < 0 or y0 < 0 or x1 > img.shape[1] or y1 > img.shape[0]:
            return
        m = 30
        X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(img.shape[1], x1 + m), min(img.shape[0], y1 + m)
        soft = cv2.GaussianBlur(img[Y0:Y1, X0:X1], (0, 0), 12)[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0]
        glass = soft * 0.55 + np.array(INK, np.float32) / 255 * 0.32
        k = self.mask[..., None] * a
        img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - k) + glass * k
        blit(img, self.txt, cx, cy, 1.0, 0, a)


# ---------- sound ----------
def decode(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(path)]
    if dur:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", "48000", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def loudness_normalise(raw_wav, out_wav):
    """Two-pass EBU R128 loudness normalisation to -14 LUFS, the level Instagram and TikTok play at."""
    target = "I=-14:TP=-1.5:LRA=11"
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw_wav), "-af",
                            f"loudnorm={target}:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    mm = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw_wav), "-af",
                    f"loudnorm={target}:measured_I={mm['input_i']}:measured_TP={mm['input_tp']}:"
                    f"measured_LRA={mm['input_lra']}:measured_thresh={mm['input_thresh']}:"
                    f"offset={mm['target_offset']}:linear=true,aresample=48000",
                    "-ar", "48000", "-c:a", "pcm_s16le", str(out_wav)], check=True)


# ---------- rendering and encoding ----------
def out_of_memory(e):
    return isinstance(e, MemoryError) or (isinstance(e, cv2.error) and "Insufficient memory" in str(e))


def render_frames(r, raw_path):
    """Render every frame into a raw RGB file on disk, so a crash can resume where it stopped and the
    encoder never runs at the same time as the renderer. Waits out moments when the PC is short of memory."""
    n = int(math.ceil(r.total * FPS))
    fb = W * H * 3
    done = min(n, raw_path.stat().st_size // fb) if raw_path.exists() else 0
    with open(raw_path, "r+b" if raw_path.exists() else "wb") as fh:
        fh.seek(done * fb)
        fh.truncate()
        for i in range(done, n):
            for attempt in range(60):
                try:
                    fr = r.frame(i / FPS)
                    data = (np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
                    break
                except (MemoryError, cv2.error) as e:
                    if not out_of_memory(e):
                        raise
                    r.release()
                    gc.collect()
                    time.sleep(5)
            else:
                raise SystemExit("still out of memory after 5 minutes; close some programs and run again to resume")
            fh.write(data)
            if i % 150 == 0:
                print(f"  frame {i}/{n}", flush=True)
    return n


def encode(raw_path, out_path, audio, dur):
    """H.264 + AAC at a quality Instagram can work from, tagged BT.709 so the colours stay right."""
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", str(raw_path), "-i", str(audio),
           "-filter_complex", "[0:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[v]",
           "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high",
           "-maxrate", "24M", "-bufsize", "48M", "-x264-params", "rc-lookahead=20", "-threads", "4",
           "-g", str(FPS * 2), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{dur:.3f}", "-movflags", "+faststart",
           str(out_path)]
    for attempt in range(5):
        if subprocess.run(cmd).returncode == 0:
            print("wrote", out_path, f"({out_path.stat().st_size / 2 ** 20:.1f} MiB)", flush=True)
            return
        time.sleep(10)
    raise SystemExit("ffmpeg failed")


def phone_copy(src, out_path, mib=29.0):
    """The same full-HD reel as a two-pass encode sized to fit under phone and web file limits (30 MiB)."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(src)], capture_output=True, text=True, check=True).stdout)
    kbps = int(mib * 1024 * 1024 * 8 / dur / 1000) - 192 - 100  # leave room for the audio and the container
    log = str(ROOT / "work" / "x264pass")
    common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k", "-maxrate", f"{kbps * 2}k",
              "-bufsize", f"{kbps * 4}k", "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", str(FPS * 2),
              "-x264-params", "rc-lookahead=20", "-threads", "4", "-passlogfile", log]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), *common, "-pass", "1", "-an", "-f", "null",
                    "-"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), *common, "-pass", "2", "-c:a", "copy",
                    "-movflags", "+faststart", str(out_path)], check=True)
    print("wrote", out_path, f"({out_path.stat().st_size / 2 ** 20:.1f} MiB)", flush=True)


def remux(video, audio, out_path):
    """Same picture, different soundtrack (no re-encode of the video)."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", str(out_path)], check=True)
    print("wrote", out_path, flush=True)
