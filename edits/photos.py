"""Blur every face in the photos the film uses.

Finds faces at several sizes and four rotations. edits/faces.json can drop false hits and add missed ones by hand, in
pixels of the upright photo: {"IMG_xxxx": {"drop": [i], "add": [[x, y, w, h]]}}.

Usage: python -I edits/photos.py IMG_xxxx ...
  -> work/clean/IMG_xxxx.jpg  (full resolution, upright, blurred)
  -> work/photo_review/IMG_xxxx.jpg  numbered boxes, for checking by eye (green = blurred, red = dropped)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pillow_heif
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blur import blur_face, blur_patch  # noqa: E402
from detect import MODEL, TURNS, merge, raw_path, turned_back  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXES = ROOT / "edits" / "faces.json"
OUT = ROOT / "work" / "clean"
REVIEW = ROOT / "work" / "photo_review"
KEEP = 0.62


def find(img, det):
    h, w = img.shape[:2]
    found = []
    for s in (1.0, 0.6, 0.35):
        small = img if s == 1.0 else cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        for turn in TURNS:
            im = small if turn is None else cv2.rotate(small, turn)
            det.setInputSize((im.shape[1], im.shape[0]))
            _, faces = det.detect(im)
            if faces is not None:
                for f in faces:
                    box = turned_back(f[:4], turn, small.shape[1], small.shape[0])
                    found.append([float(v) / s for v in box] + [float(f[-1])])
    return merge(found)


def main():
    pillow_heif.register_heif_opener()
    OUT.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    fixes = json.loads(FIXES.read_text()) if FIXES.exists() else {}
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320), 0.4, 0.3, 500)
    for name in sys.argv[1:]:
        rgb = ImageOps.exif_transpose(Image.open(raw_path(name, (".heic",)))).convert("RGB")
        img = cv2.cvtColor(np.asarray(rgb), cv2.COLOR_RGB2BGR)
        fx = fixes.get(name, {})
        boxes = find(img, det)
        vis = img.copy()
        for i, b in enumerate(boxes):
            keep = (b[4] >= KEEP or i in fx.get("keep", [])) and i not in fx.get("drop", [])
            x, y, w, h = map(int, b[:4])
            col = (0, 200, 0) if keep else (0, 0, 255)
            cv2.rectangle(vis, (x, y), (x + w, y + h), col, 5)
            cv2.putText(vis, f"{i}:{b[4]:.2f}", (x, max(40, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.6, col, 4)
        for b in fx.get("add", []):
            x, y, w, h = map(int, b)
            cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 255), 5)
        small = 1500 / max(vis.shape[:2])
        cv2.imwrite(str(REVIEW / f"{name}.jpg"), cv2.resize(vis, None, fx=small, fy=small, interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        kept = [b[:4] for i, b in enumerate(boxes) if (b[4] >= KEEP or i in fx.get("keep", [])) and i not in fx.get("drop", [])]
        for b in kept + fx.get("add", []):
            blur_face(img, b)
        for p in fx.get("patches", []):
            blur_patch(img, p["poly"])
        cv2.imwrite(str(OUT / f"{name}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"{name}: {len(boxes)} found, {len(kept)} kept, {len(fx.get('add', []))} added", flush=True)


if __name__ == "__main__":
    main()
