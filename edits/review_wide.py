"""Check what a wide TV shot will reveal: each shot's whole clip frame, before framing, from the first, middle and last moments.

The phone film's crop is drawn in yellow, and every candidate face track on top (green = will be blurred, red = will not; the
number is the track id). Anything real outside the yellow box needs blurring before the TV version can show it: faces, cheeks,
staff badges, children's names on plates and walls. The decisions go in edits/faces.json as usual.

Usage: python -I edits/review_wide.py [shot_key ...]
  -> work/review_tv/shot_key.jpg
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import MUSIC, ROOT, SHOTS  # noqa: E402

BEAT = 60 / MUSIC["bpm"]
OUT = ROOT / "work" / "review_tv"


def phone_rect(sh, w, h, q):
    z0, z1 = sh.get("zoom", (1.04, 1.0))
    z = z0 + (z1 - z0) * q
    if sh.get("pan"):
        (x0, y0), (x1, y1) = sh["pan"]
        cx, cy = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
    else:
        cx, cy = sh.get("center", (0.5, 0.5))
    s = max(1080 / w, 1920 / h) * z
    hw, hh = 540 / s, 960 / s
    px, py = min(max(cx * w, hw), w - hw), min(max(cy * h, hh), h - hh)
    return px - hw, py - hh, px + hw, py + hh


def sheet(sh):
    name = sh["clip"]
    every = json.loads((ROOT / "work" / "tracks" / f"{name}.all.json").read_text())
    speed = sh.get("speed", 1.0)
    avg = speed if not isinstance(speed, (list, tuple)) else float(np.mean([p[1] for p in speed]))
    first, last = sh["start"], int(sh["start"] + sh["beats"] * BEAT * 30 * avg)
    want = {int(round(v)): q for v, q in zip(np.linspace(first, last, 3), (0, 0.5, 1))}
    cap = cv2.VideoCapture(str(ROOT / "work" / "clean" / f"{name}.mp4"))
    tiles, i = [], 0
    while i <= max(want):
        ok, fr = cap.read()
        if not ok:
            break
        if i in want:
            h, w = fr.shape[:2]
            k = 900 / w if w > h else 500 / w
            x0, y0, x1, y1 = phone_rect(sh, w, h, want[i])
            vis = cv2.resize(fr, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            cv2.rectangle(vis, (int(x0 * k), int(y0 * k)), (int(x1 * k), int(y1 * k)), (0, 230, 255), 2)
            for t in every:
                j = i - t["start"]
                if 0 <= j < len(t["boxes"]):
                    x, y, bw, bh = (v * k for v in t["boxes"][j])
                    col = (0, 230, 0) if t["kept"] else (60, 60, 255)
                    cv2.rectangle(vis, (int(x), int(y)), (int(x + bw), int(y + bh)), col, 1)
                    cv2.putText(vis, str(t["id"]), (int(x), int(max(12, y - 2))), cv2.FONT_HERSHEY_SIMPLEX, 0.4, col, 1, cv2.LINE_AA)
            cv2.putText(vis, f"{sh['key']} {name} f{i}", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            tiles.append(vis)
        i += 1
    cap.release()
    return np.vstack(tiles) if tiles[0].shape[1] > tiles[0].shape[0] else np.hstack(tiles)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for sh in SHOTS:
        if "clip" in sh and (len(sys.argv) < 2 or sh["key"] in sys.argv[1:]):
            cv2.imwrite(str(OUT / f"{sh['key']}.jpg"), sheet(sh), [cv2.IMWRITE_JPEG_QUALITY, 85])
            print("wrote", sh["key"], flush=True)


if __name__ == "__main__":
    main()
