"""Find every face in every frame of a day's clips, plus the camera's motion between frames.

A lot of daycare footage is shot from above, so faces can be sideways or upside down in the picture. YuNet only finds
roughly upright faces, so it runs on each frame turned four ways, at half and quarter size, and on nearly full size
upright every third frame (for far-away kids).

Usage: python -I edits/detect.py [IMG_xxxx ...]
  -> work/faces/IMG_xxxx.json  {"n", "w", "h", "dets": {frame: [[x, y, w, h, score], ...]}, "motion": [[2x3], ...]}
     (pixels in the frame as it plays with its rotation tag; motion[i] maps frame i-1 to frame i). Finished clips are skipped.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import RAW  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work" / "faces"
MODEL = ROOT / "models" / "face_detection_yunet_2023mar.onnx"
SCORE = 0.4
TURNS = (None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE)


def raw_path(name, exts=(".mov",)):
    """A day's original file by name: this film's own folder first, then every other day's (source/*_raw)."""
    for folder in [RAW, *sorted((ROOT / "source").glob("*_raw"), reverse=True)]:
        for p in folder.iterdir():
            if p.stem.upper() == name.upper() and p.suffix.lower() in exts:
                return p
    raise SystemExit(f"no original for {name}")


def clip_path(name):
    return raw_path(name)


def clip_size(path):
    """The frame size after ffmpeg has applied the clip's rotation tag."""
    r = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:stream_side_data=rotation", "-of", "json", str(path)],
                                  capture_output=True, text=True).stdout)["streams"][0]
    w, h = r["width"], r["height"]
    if any(abs(int(d.get("rotation", 0))) == 90 for d in r.get("side_data_list", [])):
        w, h = h, w
    return w, h


def frames(path, w, h):
    """Frames in BGR, one at a time, so a 4K clip never sits in memory."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE, bufsize=w * h * 3)
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.wait()


def turned_back(b, turn, w, h):
    """A box found on a turned picture of size-independent coords (w, h = the upright picture), in upright coords."""
    x, y, bw, bh = b
    if turn == cv2.ROTATE_90_CLOCKWISE:
        return y, h - x - bw, bh, bw
    if turn == cv2.ROTATE_180:
        return w - x - bw, h - y - bh, bw, bh
    if turn == cv2.ROTATE_90_COUNTERCLOCKWISE:
        return w - y - bh, x, bh, bw
    return x, y, bw, bh


def iou(a, b):
    iw = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    ih = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    inter = iw * ih
    return inter / (a[2] * a[3] + b[2] * b[3] - inter + 1e-9)


def merge(boxes):
    kept = []
    for b in sorted(boxes, key=lambda b: -b[4]):
        if all(iou(b, k) < 0.3 for k in kept):
            kept.append(b)
    return kept


def camera_motion(prev, gray, k):
    """How the whole picture moved from prev to gray (small grayscale pictures, k times smaller than the clip)."""
    pts = cv2.goodFeaturesToTrack(prev, 400, 0.01, 12)
    if pts is None or len(pts) < 8:
        return [[1, 0, 0], [0, 1, 0]]
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, gray, pts, None, winSize=(21, 21), maxLevel=3)
    good = st[:, 0] == 1
    M, _ = cv2.estimateAffinePartial2D(pts[good], nxt[good], method=cv2.RANSAC, ransacReprojThreshold=2.0)
    if M is None:
        return [[1, 0, 0], [0, 1, 0]]
    M[:, 2] *= k
    return M.tolist()


def find_faces(fr, det, i):
    h, w = fr.shape[:2]
    found = []
    for s, every, turns in ((0.75, 3, TURNS[:1]), (0.5, 1, TURNS), (0.25, 1, TURNS)):
        if i % every:
            continue
        small = cv2.resize(fr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        for turn in turns:
            im = small if turn is None else cv2.rotate(small, turn)
            det.setInputSize((im.shape[1], im.shape[0]))
            _, faces = det.detect(im)
            if faces is not None:
                for f in faces:
                    box = turned_back(f[:4], turn, small.shape[1], small.shape[0])
                    found.append([float(v) / s for v in box] + [float(f[-1])])
    return merge(found)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or sorted(p.stem.upper() for p in RAW.iterdir() if p.suffix.lower() == ".mov")
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320), SCORE, 0.3, 500)
    for name in names:
        out = OUT / f"{name}.json"
        if out.exists():
            continue
        t0 = time.time()
        path = clip_path(name)
        w, h = clip_size(path)
        result, motion, prev, i = {}, [], None, -1
        for i, fr in enumerate(frames(path, w, h)):
            result[str(i)] = [[round(v, 1) for v in b[:4]] + [round(b[4], 3)] for b in find_faces(fr, det, i)]
            gray = cv2.cvtColor(cv2.resize(fr, (w // 4, h // 4), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            motion.append([[1, 0, 0], [0, 1, 0]] if prev is None else camera_motion(prev, gray, 4))
            prev = gray
        out.write_text(json.dumps({"n": i + 1, "w": w, "h": h, "dets": result, "motion": motion}))
        hits = sum(len(v) for v in result.values())
        print(f"{name}: {i + 1} frames, {hits} detections, {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
