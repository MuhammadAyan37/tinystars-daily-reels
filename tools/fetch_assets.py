"""Download the fonts, the face-detection model and the Tiny Stars logo the pipeline needs.

Usage: python -I tools/fetch_assets.py
  -> brand/fonts/*.ttf (Google Fonts, OFL), models/face_detection_yunet_2023mar.onnx (OpenCV Zoo), brand/logo.png,
     source/music/*.mp3 (Pixabay)
"""
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = "https://github.com/google/fonts/raw/main/ofl"
FILES = {
    "brand/fonts/InstrumentSerif-Regular.ttf": f"{FONTS}/instrumentserif/InstrumentSerif-Regular.ttf",
    "brand/fonts/InstrumentSerif-Italic.ttf": f"{FONTS}/instrumentserif/InstrumentSerif-Italic.ttf",
    "brand/fonts/InterTight.ttf": f"{FONTS}/intertight/InterTight%5Bwght%5D.ttf",
    "models/face_detection_yunet_2023mar.onnx":
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "brand/logo.png": "https://tinystars.ca/assets/images/logo/logo.png",
    "source/music/cinematic_corporate_alexmorgan_556231.mp3":
        "https://cdn.pixabay.com/download/audio/2026/06/23/audio_506b25c5cd.mp3",
}


def main():
    for rel, url in FILES.items():
        dest = ROOT / rel
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            dest.write_bytes(r.read())
        print("fetched", rel)


if __name__ == "__main__":
    main()
