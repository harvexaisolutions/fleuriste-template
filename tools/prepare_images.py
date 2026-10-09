#!/usr/bin/env python3
"""Crop and resize the photos in images/originals/ into the slot files rebrand.py uses.

Each entry: slot -> (source file, output width, output height, centre x, centre y, zoom)
centre x/y are fractions of the source image (0.5, 0.5 = middle); zoom 1 takes the
largest crop of the target aspect ratio, 2 takes half of that, and so on.

Requires cwebp (brew install webp). Run, then run rebrand.py:
  python3 tools/prepare_images.py && python3 tools/rebrand.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "originals"
OUT = ROOT / "images"

CROPS = {
    # Product photos (square)
    "product-blush-rose": ("jessie-daniella-QLuleNy8LMM-unsplash.jpg", 1600, 1600, 0.5, 0.52, 1),
    "product-peach-garden-roses": ("angelina-jollivet-mNEpmNiFdXs-unsplash.jpg", 1000, 1000, 0.5, 0.5, 1),
    "product-white-hydrangea": ("jessie-daniella-aiNU4cA4UzQ-unsplash.jpg", 1000, 1000, 0.5, 0.48, 1),
    "product-lilac-tulips": ("pexels-olenkabohovyk-11116390.jpg", 1000, 1000, 0.5, 0.5, 1),
    "product-wild-garden": ("pexels-leah-newhouse-50725-37423023.jpg", 1000, 1000, 0.5, 0.5, 1),
    "product-red-aster": ("pexels-inga-sv-9360504.jpg", 1000, 1000, 0.5, 0.52, 1),
    "product-dried-posy": ("insung-yoon-Vxm213warDA-unsplash.jpg", 1000, 1000, 0.5, 0.55, 1),
    "product-purple-carnation": ("pexels-saharisphotos-29892601.jpg", 1000, 1000, 0.5, 0.62, 1),
    "product-white-rose-tribute": ("viacheslav-volodin-vXicvRewPk0-unsplash.jpg", 1000, 1000, 0.5, 0.45, 1),
    "product-eucalyptus-jug": ("pexels-teona-swift-6913739.jpg", 1000, 1000, 0.5, 0.55, 1),
    "product-babys-breath-noir": ("pexels-tuan-vy-903011268-19843318.jpg", 1000, 1000, 0.5, 0.5, 1),
    "product-white-blossom-dome": ("evie-s-SxEhEk9O2H0-unsplash.jpg", 1000, 1000, 0.5, 0.5, 1),
    "product-build-your-own": ("pexels-leah-newhouse-50725-37423023.jpg", 1000, 1000, 0.55, 0.6, 1.6),
    # Home page scenes
    "hero-main": ("salah-darwish-0tSdTCEadTE-unsplash.jpg", 900, 1600, 0.5, 0.5, 1),
    "hero-secondary": ("pexels-olly-3933012.jpg", 900, 900, 0.48, 0.45, 1.3),
    "about-florist": ("pexels-amina-filkins-5410074.jpg", 1380, 1050, 0.5, 0.5, 1),
    "occasion-birthday": ("pexels-muinuddin-31204553.jpg", 1200, 940, 0.5, 0.45, 1),
    "occasion-anniversary": ("salah-darwish-0tSdTCEadTE-unsplash.jpg", 1200, 590, 0.5, 0.85, 1),
    "occasion-sympathy": ("viacheslav-volodin-vXicvRewPk0-unsplash.jpg", 800, 800, 0.4, 0.4, 1.8),
    "occasion-get-well": ("pexels-leah-newhouse-50725-37423023.jpg", 800, 800, 0.4, 0.22, 2),
    "offer-mothers-day": ("pexels-olenkabohovyk-11116390.jpg", 800, 1200, 0.5, 0.5, 1),
    "offer-subscription": ("pexels-teona-swift-6913739.jpg", 800, 1200, 0.5, 0.5, 1),
    "offer-birthday-bundle": ("pexels-muinuddin-31204553.jpg", 800, 1200, 0.5, 0.5, 1),
    "subscribe-cutout": ("pixnio-5000x7308.png", 340, 497, 0.5, 0.5, 1),
}


def size(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                         capture_output=True, text=True, check=True).stdout
    vals = [int(line.split()[-1]) for line in out.splitlines() if "pixel" in line]
    return vals[0], vals[1]


def crop(slot, src, w, h, cx, cy, zoom):
    sw, sh = size(SRC / src)
    aspect = w / h
    bw = min(sw, sh * aspect) / zoom
    bh = bw / aspect
    x = int(min(max(cx * sw - bw / 2, 0), sw - bw))
    y = int(min(max(cy * sh - bh / 2, 0), sh - bh))
    for old in OUT.glob(f"{slot}.*"):
        old.unlink()
    subprocess.run(["cwebp", "-quiet", "-q", "80", "-crop", str(x), str(y), str(int(bw)), str(int(bh)),
                    "-resize", str(w), str(h), str(SRC / src), "-o", str(OUT / f"{slot}.webp")], check=True)
    print(f"{slot}.webp  <- {src}")


if __name__ == "__main__":
    for slot, spec in CROPS.items():
        crop(slot, *spec)
