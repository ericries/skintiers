#!/usr/bin/env python3
"""List published pages that have NO video card - the demand signal for backfill.

Supply-driven backfill walks a creator's catalog and cards whatever matches; this
flips it: it surfaces the product/ingredient/condition/goal pages that currently
have zero embedded videos, so a demand-driven pass can go find the single best
vetted-creator video for exactly those gaps instead of adding a 4th sunscreen clip.

Ranks core types (product/ingredient) first, then condition/goal hubs.

Usage:
  python scripts/video_gaps.py               # all gap pages, core types first
  python scripts/video_gaps.py --type ingredient --limit 20
  python scripts/video_gaps.py --count       # just per-type counts
"""
import argparse
import glob
import pathlib
import sys

import frontmatter

ROOT = pathlib.Path(__file__).resolve().parent.parent
TYPE_DIRS = {"product": "products", "ingredient": "ingredients",
             "condition": "conditions", "goal": "goals"}
ORDER = ["product", "ingredient", "condition", "goal"]


def gaps(only_type=None):
    out = []
    for t in ORDER:
        if only_type and t != only_type:
            continue
        for f in sorted(glob.glob(str(ROOT / "data" / TYPE_DIRS[t] / "*.md"))):
            try:
                post = frontmatter.load(f)
            except Exception:
                continue
            if post.get("status") != "published":
                continue
            if not (post.get("videos") or []):
                out.append((t, pathlib.Path(f).stem, post.get("name") or pathlib.Path(f).stem))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--type", choices=list(TYPE_DIRS))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args(argv)
    g = gaps(args.type)
    if args.count:
        from collections import Counter
        c = Counter(t for t, _, _ in g)
        for t in ORDER:
            print(f"{t}: {c.get(t, 0)} pages without video")
        print(f"total: {len(g)}")
        return 0
    rows = g[:args.limit] if args.limit else g
    for t, slug, name in rows:
        print(f"{t}\t{slug}\t{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
