#!/usr/bin/env python3
"""Resize oversized source images down to what the site actually displays.

Product photos render in a 148px rail (`.photo-rail{width:148px}`), but
static/images held PNGs up to 5200x5200 and 3.4MB. _site reached 155MB and the
Pages deploy timed out mid `syncing_files` on 2026-11-06.

Design choices, and why:

* FORMAT IS DRIVEN BY THE FILE EXTENSION, not by the detected format. One file
  (chemist-confessions-aquafix) was PNG data behind a .jpg name; keying on the
  extension fixes that mismatch instead of preserving it, and it keeps every
  filename identical, so no page frontmatter has to change. That is the whole
  reason this is resize-in-place rather than a WebP conversion: WebP would save
  a further ~6MB but would rename 471 files referenced across data/.
* ALPHA IS PRESERVED for PNG output. 73 of 471 images are genuinely
  transparent (product cutouts). Flattening them with a plain RGB convert
  composites onto BLACK, which would have quietly ruined them.
* JPEG output flattens onto WHITE, which matches the rail's own
  `background:#fff`.
* A file is only replaced if the result is genuinely smaller AND re-opens
  cleanly. Anything already within budget is left untouched, so re-running is
  safe and does not stack generation loss.

Originals are recoverable from git history; this intentionally does not keep a
second copy in the tree.

    .venv/bin/python scripts/shrink_images.py --dry-run
    .venv/bin/python scripts/shrink_images.py
"""
import argparse
import io
import pathlib
import sys

MAX_EDGE = 444          # 148px rail * 3 for the densest displays
MAX_BYTES = 250_000
JPEG_Q = 85
WEBP_Q = 82


def _has_alpha(im):
    return im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)


def _encode(im, ext, alpha):
    buf = io.BytesIO()
    if ext in (".jpg", ".jpeg"):
        flat = Image.new("RGB", im.size, (255, 255, 255))
        if alpha:
            rgba = im.convert("RGBA")
            flat.paste(rgba, mask=rgba.getchannel("A"))
        else:
            flat.paste(im.convert("RGB"))
        flat.save(buf, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    elif ext == ".webp":
        im.save(buf, "WEBP", quality=WEBP_Q, method=6)
    else:
        (im.convert("RGBA") if alpha else im.convert("RGB")).save(
            buf, "PNG", optimize=True)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dir", default="static/images")
    ap.add_argument("--max-edge", type=int, default=MAX_EDGE)
    args = ap.parse_args()

    d = pathlib.Path(args.dir)
    if not d.is_dir():
        print(f"no such directory: {d}")
        return 2

    before = after = 0
    changed = skipped = failed = 0
    for p in sorted(d.iterdir()):
        if not p.is_file():
            continue
        size = p.stat().st_size
        before += size
        try:
            with Image.open(p) as im:
                im.load()
                alpha = _has_alpha(im)
                work = im.copy()
        except Exception as exc:
            print(f"  SKIP (unreadable) {p.name}: {exc}")
            after += size
            failed += 1
            continue

        oversized = max(work.size) > args.max_edge
        if not oversized and size <= MAX_BYTES:
            after += size
            skipped += 1
            continue

        dims_before = work.size
        if oversized:
            work.thumbnail((args.max_edge, args.max_edge), Image.LANCZOS)

        try:
            data = _encode(work, p.suffix.lower(), alpha)
        except Exception as exc:
            print(f"  SKIP (encode failed) {p.name}: {exc}")
            after += size
            failed += 1
            continue

        if len(data) >= size:
            # Already efficient; rewriting would only add generation loss.
            after += size
            skipped += 1
            continue

        try:
            with Image.open(io.BytesIO(data)) as check:
                check.load()
        except Exception as exc:
            print(f"  SKIP (result did not re-open) {p.name}: {exc}")
            after += size
            failed += 1
            continue

        after += len(data)
        changed += 1
        if not args.dry_run:
            p.write_bytes(data)
        print(f"  {size/1024:7.0f}KB -> {len(data)/1024:6.1f}KB  "
              f"{dims_before[0]}x{dims_before[1]} -> {work.size[0]}x{work.size[1]}  {p.name[:46]}")

    verb = "would change" if args.dry_run else "changed"
    print(f"\n{verb} {changed}, left alone {skipped}, failed {failed}")
    print(f"{before/1e6:.1f}MB -> {after/1e6:.2f}MB "
          f"({100*(1-after/before):.1f}% smaller)" if before else "")
    return 0


if __name__ == "__main__":
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not available")
        sys.exit(2)
    sys.exit(main())
