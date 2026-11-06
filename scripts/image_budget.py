#!/usr/bin/env python3
"""Flag source images that are far larger than the site ever displays.

Product photos render in a 148px-wide rail (`.photo-rail{width:148px}`), so
even a 3x display needs about 444px. On 2026-11-06 static/images held PNGs up
to 5200x5200 and 3.4MB, and the whole _site was 155MB, enough that the Pages
deploy timed out mid `syncing_files`. Resizing to 444px WebP measured 95%
smaller across all 471 files.

This REPORTS; it does not convert. Converting is a one-way change to source
assets and belongs to a human decision, not a cron tick. Run it to see whether
the problem is growing:

    .venv/bin/python scripts/image_budget.py            # offenders only
    .venv/bin/python scripts/image_budget.py --all      # every file

Exit 1 if anything breaches the budget, so the image cron can notice.
"""
import argparse
import pathlib
import sys

# 148px CSS rail * 3 for the densest screens, plus headroom for the few images
# shown larger (brand/hero). Anything well beyond this is paying for pixels no
# visitor receives.
MAX_EDGE = 600
MAX_BYTES = 250_000
IMG_DIR = pathlib.Path("static/images")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="list every image, not just offenders")
    ap.add_argument("--dir", default=str(IMG_DIR))
    args = ap.parse_args()

    try:
        from PIL import Image
    except ImportError:
        print("Pillow not available; cannot measure images")
        return 2

    d = pathlib.Path(args.dir)
    if not d.is_dir():
        print(f"no such directory: {d}")
        return 2

    rows, total, over_bytes = [], 0, 0
    for p in sorted(d.iterdir()):
        if not p.is_file():
            continue
        size = p.stat().st_size
        total += size
        try:
            with Image.open(p) as im:
                w, h = im.size
                fmt = im.format
        except Exception:
            continue
        bad = max(w, h) > MAX_EDGE or size > MAX_BYTES
        if bad:
            over_bytes += size
        if bad or args.all:
            rows.append((size, w, h, fmt, p.name, bad))

    rows.sort(reverse=True)
    for size, w, h, fmt, name, bad in rows:
        mark = "OVER " if bad else "     "
        print(f"  {mark}{size/1024:7.0f}KB  {w}x{h:<6} {str(fmt):5} {name[:52]}")

    offenders = sum(1 for r in rows if r[5])
    print(f"\n{offenders} of {sum(1 for p in d.iterdir() if p.is_file())} images "
          f"exceed the budget ({MAX_EDGE}px edge / {MAX_BYTES//1000}KB).")
    print(f"directory total: {total/1e6:.1f}MB, of which offenders are {over_bytes/1e6:.1f}MB.")
    if offenders:
        print("These are shipped at full size to every visitor and counted "
              "against the Pages deploy, which has already timed out once.")
    return 1 if offenders else 0


if __name__ == "__main__":
    sys.exit(main())
