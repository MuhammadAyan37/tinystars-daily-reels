"""Bake the privacy blur into the clips, so everything after this step only ever sees blurred faces and names.

Each clip is decoded one frame at a time. Every tracked face gets a padded, feather-edged ellipse that is pixelated and
then heavily blurred (pixelating first stops the blur from keeping a recognisable outline). Patches are areas of the
picture that follow the camera, for children's names on the classroom wall. The result is a high-quality 4K working copy.

Usage: python -I edits/track.py && python -I edits/blur.py [IMG_xxxx ...]
  -> work/clean/IMG_xxxx.mp4  (the clip's full size, 30 fps, no sound; finished clips are skipped unless named)
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import RAW  # noqa: E402
from detect import clip_path, clip_size, frames  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FACES = ROOT / "work" / "faces"
TRACKS = ROOT / "work" / "tracks"
FIXES = ROOT / "edits" / "faces.json"
OUT = ROOT / "work" / "clean"
PAD_W, PAD_H = 1.55, 1.75   # ellipse size relative to the face box
LIFT = 0.04                 # move the ellipse up a little to cover the forehead and hair


def blur_face(img, box):
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2 - LIFT * h
    ax, ay = w * PAD_W / 2, h * PAD_H / 2
    H, W = img.shape[:2]
    x0, x1 = int(max(0, cx - ax * 1.6)), int(min(W, cx + ax * 1.6))
    y0, y1 = int(max(0, cy - ay * 1.6)), int(min(H, cy + ay * 1.6))
    if x1 <= x0 or y1 <= y0:
        return
    roi = img[y0:y1, x0:x1].astype(np.float32)
    rh, rw = roi.shape[:2]
    cell = max(6, int(w / 7))
    small = cv2.resize(roi, (max(1, rw // cell), max(1, rh // cell)), interpolation=cv2.INTER_AREA)
    pix = cv2.resize(small, (rw, rh), interpolation=cv2.INTER_NEAREST)
    soft = cv2.GaussianBlur(pix, (0, 0), max(8.0, w * 0.16))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = ((xx - cx) / ax) ** 2 + ((yy - cy) / ay) ** 2
    mask = np.clip((1.25 - d) / 0.35, 0, 1)[..., None]
    img[y0:y1, x0:x1] = (soft * mask + roi * (1 - mask)).astype(np.uint8)


def blur_patch(img, poly):
    """Blur inside a polygon, heavily enough that writing cannot be read, with a soft edge."""
    H, W = img.shape[:2]
    pts = np.array(poly, np.float32)
    x0, y0 = np.floor(pts.min(0)).astype(int) - 40
    x1, y1 = np.ceil(pts.max(0)).astype(int) + 40
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    roi = img[y0:y1, x0:x1].astype(np.float32)
    rh, rw = roi.shape[:2]
    small = cv2.resize(roi, (max(1, rw // 18), max(1, rh // 18)), interpolation=cv2.INTER_AREA)
    soft = cv2.GaussianBlur(cv2.resize(small, (rw, rh), interpolation=cv2.INTER_NEAREST), (0, 0), 16)
    m = np.zeros((rh, rw), np.uint8)
    cv2.fillPoly(m, [np.round(pts - [x0, y0]).astype(np.int32)], 255)
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 7)[..., None]
    img[y0:y1, x0:x1] = (soft * m + roi * (1 - m)).astype(np.uint8)


def camera_paths(motion):
    """For each frame, the 3x3 matrix taking a point in frame 0 to the same point in that frame."""
    T = [np.eye(3)]
    for m in motion[1:]:
        T.append(np.vstack([m, [0, 0, 1]]) @ T[-1])
    return T


def writer(path, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                             "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "13",
                             "-pix_fmt", "yuv420p", "-threads", "4", "-x264-params", "rc-lookahead=10",
                             "-g", "15", str(path)], stdin=subprocess.PIPE)


def bake(name, fixes):
    tracks = json.loads((TRACKS / f"{name}.json").read_text())["tracks"]
    path = clip_path(name)
    w, h = clip_size(path)
    motion = json.loads((FACES / f"{name}.json").read_text())["motion"]
    T = camera_paths(motion)
    patches = fixes.get(name, {}).get("patches", [])
    out = writer(OUT / f"{name}.mp4", w, h)
    n = 0
    for i, fr in enumerate(frames(path, w, h)):
        img = fr.copy()
        for p in patches:
            if "frames" in p and not p["frames"][0] <= i <= p["frames"][1]:
                continue  # a patch can be limited to the frames where its subject is in the picture
            M = T[i] @ np.linalg.inv(T[p["frame"]])
            pts = np.c_[np.array(p["poly"], np.float64), np.ones(len(p["poly"]))] @ M.T
            blur_patch(img, pts[:, :2])
        for t in tracks:
            k = i - t["start"]
            if 0 <= k < len(t["boxes"]):
                blur_face(img, t["boxes"][k])
        out.stdin.write(img.tobytes())
        n = i + 1
    out.stdin.close()
    out.wait()
    print(f"{name}: {n} frames, {len(tracks)} tracks, {len(patches)} patches", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fixes = json.loads(FIXES.read_text()) if FIXES.exists() else {}
    named = sys.argv[1:]
    names = named or sorted(p.stem.upper() for p in RAW.iterdir() if p.suffix.lower() == ".mov")
    for name in names:
        if named or not (OUT / f"{name}.mp4").exists():
            bake(name, fixes)


if __name__ == "__main__":
    main()
