"""A photo-free picture of the reel's graphics for the README (no children's photos in the repo).

Usage: python -I edits/demo.py -> docs/demo.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from film import Renderer  # noqa: E402
from lib import H, W, blit  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    r = Renderer()
    card = r.card_picture(r.by_key["card"], r.by_key["card"]["t0"] + 1.1)
    wash = r.paint.wash("glass").copy()
    blit(wash, r.breath, W / 2, 900)
    end = r.end_picture(r.by_key["end"], r.by_key["end"]["t0"] + 5.0)
    out = Image.new("RGB", (3 * 533 + 2 * 12, 948), (255, 255, 255))
    for i, pic in enumerate((card, wash, end)):
        tile = Image.fromarray((np.clip(pic, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((533, 948), Image.LANCZOS)
        out.paste(tile, (i * 545, 0))
    (ROOT / "docs").mkdir(exist_ok=True)
    out.save(ROOT / "docs" / "demo.png", optimize=True)
    print("wrote docs/demo.png", W, H)


if __name__ == "__main__":
    main()
