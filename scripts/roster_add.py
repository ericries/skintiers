#!/usr/bin/env python3
"""Append ONE vetted creator to data/video-sources.yaml safely.

The roster carries a comment header that a yaml.dump round-trip would destroy, so
new entries are appended as text (properly indented) and the whole file is then
re-parsed to prove it is still valid YAML and that exactly one creator was added.
Used by the weekly creator-vetting cron to promote a candidate that passed the
rubric. Refuses to add a duplicate creator_slug.

Usage:
  python scripts/roster_add.py --name "Doctorly" --creator-slug doctorly \
    --credential "Board-certified dermatologists (Muneeb Shah + Luke Maxfield)" \
    --tier HIGH --channel https://www.youtube.com/channel/UCHCZnC9akNA9pBP7aJGNKdg \
    --conflict "" --product-recs "" [--flagship] [--last-pulled 2026-08-25]
"""
import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROSTER = ROOT / "data" / "video-sources.yaml"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", required=True)
    ap.add_argument("--creator-slug", dest="slug", required=True)
    ap.add_argument("--credential", required=True)
    ap.add_argument("--tier", required=True, choices=["HIGH", "MED"])
    ap.add_argument("--channel", required=True)
    ap.add_argument("--conflict", default="")
    ap.add_argument("--product-recs", dest="product_recs", default="")
    ap.add_argument("--flagship", action="store_true")
    ap.add_argument("--backfill-cursor", dest="cursor", type=int, default=None)
    ap.add_argument("--last-pulled", dest="last_pulled", default=None)
    args = ap.parse_args(argv)

    text = ROSTER.read_text(encoding="utf-8")
    rows = yaml.safe_load(text) or []
    if any((r.get("creator_slug") or "") == args.slug for r in rows):
        print(f"ERROR: creator_slug '{args.slug}' already in roster; not added")
        return 1
    if "youtube.com" not in args.channel and "tiktok.com" not in args.channel \
            and "instagram.com" not in args.channel:
        print("ERROR: channel must be a youtube/tiktok/instagram URL")
        return 1

    # Build the entry as a dict and let PyYAML serialize it as a one-item list;
    # lists don't get a '...' document-end marker and all quoting is library-handled.
    entry = {
        "name": args.name,
        "creator_slug": args.slug,
        "credential": args.credential,
        "tier": args.tier,
        "channel": args.channel,
        "conflict": args.conflict or None,
        "product_recs": args.product_recs or None,
    }
    if args.flagship:
        entry["flagship"] = True
    if args.cursor is not None:
        entry["backfill_cursor"] = args.cursor
    if args.last_pulled:
        entry["last_pulled"] = args.last_pulled
    block = yaml.safe_dump([entry], default_flow_style=False, sort_keys=False,
                           allow_unicode=True, width=1000).rstrip("\n")

    new_text = text.rstrip("\n") + "\n" + block + "\n"
    reparsed = yaml.safe_load(new_text)
    if not isinstance(reparsed, list) or len(reparsed) != len(rows) + 1:
        print("ERROR: append would not add exactly one valid entry; aborting")
        return 1
    if not new_text.lstrip().startswith("#") and text.lstrip().startswith("#"):
        print("ERROR: comment header would be lost; aborting")
        return 1
    ROSTER.write_text(new_text, encoding="utf-8")
    print(f"roster-add: {args.slug} ({args.tier}) added; roster now {len(reparsed)} creators")
    return 0


if __name__ == "__main__":
    sys.exit(main())
