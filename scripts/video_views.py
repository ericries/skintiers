#!/usr/bin/env python3
"""Fetch view_count + upload_date for a handful of YouTube video ids, newest data.

The backfill cron uses this to make its deep-catalog sweep POPULARITY-AWARE: after
title-filtering a window down to a few candidates, it ranks them by views and skips
low-signal old uploads below a view floor, so we card the evergreen hits rather than
whatever happens to be next chronologically. Bounded by design - pass only the few
candidate ids (each id costs ~2s of non-flat extraction), never a whole catalog.

Usage:
  python scripts/video_views.py <id1> <id2> ...            # TSV, sorted by views desc
  python scripts/video_views.py --min-views 30000 <id...>  # also print PASS/LOW verdict

Output columns: views  upload_date(YYYY-MM-DD)  verdict  id  title
"""
import argparse
import subprocess
import sys


def fetch(vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    try:
        out = subprocess.run(
            ["yt-dlp", "--skip-download", "--no-warnings",
             "--print", "%(view_count)s\t%(upload_date)s\t%(title)s", url],
            capture_output=True, text=True, timeout=60)
        line = (out.stdout or "").strip().splitlines()
        if not line:
            return None
        views, date, title = (line[0].split("\t", 2) + ["", "", ""])[:3]
        v = int(views) if views.isdigit() else 0
        d = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if len(date) == 8 and date.isdigit() else ""
        return {"id": vid, "views": v, "date": d, "title": title}
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--min-views", type=int, default=0,
                    help="mark videos below this as LOW (low-signal, skip)")
    args = ap.parse_args(argv)
    rows = [r for r in (fetch(v) for v in args.ids) if r]
    rows.sort(key=lambda r: r["views"], reverse=True)
    for r in rows:
        verdict = ("PASS" if r["views"] >= args.min_views else "LOW") if args.min_views else "-"
        print(f'{r["views"]}\t{r["date"]}\t{verdict}\t{r["id"]}\t{r["title"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
