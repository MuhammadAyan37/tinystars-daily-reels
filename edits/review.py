"""Check the face tracks by eye, through the film's own framing: frames from each shot with every candidate track drawn on.

Usage: python -I edits/review.py shot_key [how many frames]
  -> work/review/shot_key.jpg  (green = will be blurred, red = will not; the number is the track id)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import MUSIC, SHOTS  # noqa: E402
from detect import clip_path, clip_size  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work" / "review"
BEAT = 60 / MUSIC["bpm"]
FPS = 30


def main():
    key = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    sh = next(s for s in SHOTS if s["key"] == key)
    name = sh["clip"]
    every = json.loads((ROOT / "work" / "tracks" / f"{name}.all.json").read_text())
    path = clip_path(name)
    w, h = clip_size(path)
    dur = sh["beats"] * BEAT
    speed = sh.get("speed", 1.0)
    avg = speed if not isinstance(speed, (list, tuple)) else float(np.mean([p[1] for p in speed]))
    first, last = sh["start"], int(sh["start"] + dur * FPS * avg)
    want = {int(round(v)): q for v, q in zip(np.linspace(first, last, count), np.linspace(0, 1, count))}
    turn = sh.get("turn", 0) % 4
    tw, th = (h, w) if turn % 2 else (w, h)
    tiles = []
    p = cv2.VideoCapture(str(path))
    i = 0
    while i <= last:
        ok, fr = p.read()
        if not ok:
            break
        if i in want:
            q = want[i]
            z0, z1 = sh.get("zoom", (1.04, 1.0))
            z = z0 + (z1 - z0) * q
            if sh.get("pan"):
                (x0, y0), (x1, y1) = sh["pan"]
                cx, cy = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
            else:
                cx, cy = sh.get("center", (0.5, 0.5))
            s = max(1080 / tw, 1920 / th) * z
            hw, hh = 540 / s, 960 / s
            px, py = min(max(cx * tw, hw), tw - hw), min(max(cy * th, hh), th - hh)
            k = 480 / (2 * hw)
            fr2 = np.rot90(fr, -turn) if turn else fr
            M = np.array([[k, 0, 240 - k * px], [0, k, 427 - k * py]], np.float32)
            vis = cv2.warpAffine(np.ascontiguousarray(fr2), M, (480, 854), flags=cv2.INTER_AREA)
            for t in every:
                j = i - t["start"]
                if 0 <= j < len(t["boxes"]):
                    x, y, bw, bh = t["boxes"][j]
                    for _ in range(turn):
                        x, y, bw, bh = (h if _ == 0 else w) - y - bh, x, bh, bw  # one quarter turn clockwise
                    a = M @ np.array([x, y, 1.0])
                    b = M @ np.array([x + bw, y + bh, 1.0])
                    if b[0] < 0 or b[1] < 0 or a[0] > 480 or a[1] > 854:
                        continue
                    col = (0, 230, 0) if t["kept"] else (60, 60, 255)
                    cv2.rectangle(vis, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), col, 1)
                    cv2.putText(vis, str(t["id"]), (int(max(0, a[0])), int(max(12, a[1] + 12))), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col, 1, cv2.LINE_AA)
            cv2.putText(vis, f"f{i}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            tiles.append(vis)
        i += 1
    p.release()
    OUT.mkdir(parents=True, exist_ok=True)
    gap = np.full((854, 6, 3), 255, np.uint8)
    row = []
    for t in tiles:
        row += [t, gap]
    cv2.imwrite(str(OUT / f"{key}.jpg"), np.hstack(row[:-1]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("wrote", key)


if __name__ == "__main__":
    main()
