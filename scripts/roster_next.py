#!/usr/bin/env python3
"""Deterministic creator selection for the video crons.

Centralizes the oldest-last_pulled / smallest-backfill_cursor logic the video-pull
and video-backfill crons used to run inline as a throwaway heredoc every firing.
Crucially it FILTERS TO YOUTUBE-PULLABLE creators, so the ~24 TikTok/IG-only roster
entries (which cannot be processed by the YouTube-centric pull) no longer jam the
rotation by perpetually being the "oldest" pick.

Usage:
  python scripts/roster_next.py pull        # oldest last_pulled YouTube creator
  python scripts/roster_next.py backfill     # smallest backfill_cursor flagship YouTube creator
  python scripts/roster_next.py backfill --all-high   # smallest cursor among ALL HIGH-tier YouTube creators
  python scripts/roster_next.py noyt          # list the non-YouTube creators (the separate track)

Prints one TSV line: field=value pairs, or "none" if no creator qualifies.
"""
import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROSTER = ROOT / "data" / "video-sources.yaml"


def _rows():
    d = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d.get("creators", d.get("sources", []))


def _is_youtube(r):
    return "youtube.com" in (r.get("channel") or "")


def _fmt(r):
    keys = ("creator_slug", "name", "credential", "tier", "channel", "conflict",
            "product_recs", "last_pulled", "backfill_cursor", "flagship")
    return "\t".join(f"{k}={r.get(k)}" for k in keys)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["pull", "backfill", "noyt"])
    ap.add_argument("--all-high", action="store_true",
                    help="backfill mode: consider ALL HIGH-tier YouTube creators, not just flagship")
    args = ap.parse_args(argv)
    rows = _rows()
    yt = [r for r in rows if _is_youtube(r)]

    if args.mode == "noyt":
        for r in rows:
            if not _is_youtube(r):
                print(_fmt(r))
        return 0

    if args.mode == "pull":
        # oldest (or null) last_pulled; ties broken by file order (stable sort)
        pick = sorted(yt, key=lambda r: (r.get("last_pulled") or ""))
        if not pick:
            print("none")
            return 0
        print(_fmt(pick[0]))
        return 0

    # backfill: smallest backfill_cursor among flagship (or all HIGH with --all-high)
    pool = [r for r in yt if (r.get("tier") == "HIGH" if args.all_high else r.get("flagship"))]
    pool = [r for r in pool if r.get("backfill_cursor") is not None]
    if not pool:
        print("none")
        return 0
    pick = sorted(pool, key=lambda r: r.get("backfill_cursor"))
    print(_fmt(pick[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
