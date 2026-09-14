#!/usr/bin/env python3
"""Cheap DAILY sweep: detect NEW uploads from EVERY roster creator.

The video-pull cron ingests one creator per firing (transcript read + card), so
with 60+ creators any given channel is only revisited every couple of weeks -
the freshest uploads sit undiscovered for that long. This sweep is the cheap
complement: it lists each pullable creator's most recent uploads (yt-dlp
`--flat-playlist` metadata only, NO transcript download, NO LLM), diffs them
against the videos already carded on the site AND against the pending candidate
queue, and appends the genuinely-new ones to data/queues/video-candidates.yaml.
The (expensive) ingestion cron then drains that queue newest-first, so the
freshest content is always the next thing ingested.

It is also self-healing: each run first prunes queue entries whose video has
since been carded (so the ingestion cron never has to explicitly resolve a
successful ingest; only rejects are marked `status: skipped`).

Runs daily over the WHOLE roster; keep it cheap. YouTube and TikTok (the latter
needs browser cookies) are pullable; Instagram/other are skipped, as are
`channel_broken` entries.

Usage:
  # daily sweep (network) - the video-scan cron:
  .venv/bin/python scripts/video_scan.py --scan [--per N] [--workers W]
       [--tiktok-cookies BROWSER] [--skip-tiktok] [--timeout S] [--dry-run]
  # cheap local queue reads/writes - the pull crons:
  .venv/bin/python scripts/video_scan.py --list-pending N [--platform youtube|tiktok]
  .venv/bin/python scripts/video_scan.py --resolve VIDEO_ID [--reason TEXT]
"""
import argparse
import concurrent.futures
import os
import pathlib
import re
import subprocess
import sys

import frontmatter
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROSTER = ROOT / "data" / "video-sources.yaml"
QUEUE = ROOT / "data" / "queues" / "video-candidates.yaml"
DATA_DIR = ROOT / "data"

_PLATFORM_LABEL = {"youtube": "YouTube", "tiktok": "TikTok", "instagram": "Instagram"}


def id_from_url(url):
    """Extract the platform video id from a card's `url`. Handles YouTube
    watch?v=, youtu.be/, /shorts/, and TikTok /video/<id>; falls back to the
    last path segment. Returns None if there is nothing to parse."""
    if not url:
        return None
    u = str(url).strip()
    for pat in (r"[?&]v=([A-Za-z0-9_-]+)",
                r"youtu\.be/([A-Za-z0-9_-]+)",
                r"/shorts/([A-Za-z0-9_-]+)",
                r"/video/(\d+)"):
        m = re.search(pat, u)
        if m:
            return m.group(1)
    seg = u.split("?")[0].rstrip("/").split("/")[-1]
    return seg or None


def ingested_ids(data_dir=DATA_DIR):
    """Set of every video id already carded anywhere on the site, read from each
    page's `videos:` frontmatter url (dedup is per-page on the site, so this
    unions across all pages)."""
    ids = set()
    for md in pathlib.Path(data_dir).glob("*/*.md"):
        try:
            meta = frontmatter.load(md).metadata
        except Exception:
            continue
        for v in (meta.get("videos") or []):
            if not isinstance(v, dict):
                continue
            vid = id_from_url(v.get("url"))
            if not vid and v.get("id"):
                vid = str(v.get("id"))
            if vid:
                ids.add(vid)
    return ids


def load_queue(path=QUEUE):
    p = pathlib.Path(path)
    if not p.exists():
        return []
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else []


def queued_ids(queue):
    return {str(item.get("id")) for item in queue if item.get("id")}


def prune_ingested(queue, ingested):
    """Drop PENDING queue entries whose video is now carded (ingested). Entries
    with any other status (e.g. `skipped`) are kept as a record."""
    out = []
    for item in queue:
        if item.get("status", "pending") == "pending" and str(item.get("id")) in ingested:
            continue
        out.append(item)
    return out


def new_candidates(recent, seen_ids):
    """`recent`: list of {id,...} in the channel's newest-first feed order.
    Returns those whose id is not in `seen_ids`, deduped within the batch (first
    occurrence wins), each tagged with `_feed_rank` (0 = newest on that channel)
    so the queue can be drained freshest-first even though flat-playlist carries
    no upload date."""
    out, batch = [], set()
    for rank, r in enumerate(recent):
        vid = str(r.get("id") or "")
        if not vid or vid in seen_ids or vid in batch:
            continue
        batch.add(vid)
        item = dict(r)
        item["_feed_rank"] = rank
        out.append(item)
    return out


def fmt_date(yyyymmdd):
    """yt-dlp upload_date (YYYYMMDD) -> YYYY-MM-DD; '' for unknown/NA."""
    s = str(yyyymmdd or "").strip()
    if len(s) == 8 and s.isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return ""


def _platform(r):
    ch = r.get("channel") or ""
    if "youtube.com" in ch:
        return "youtube"
    if "tiktok.com" in ch:
        return "tiktok"
    if "instagram.com" in ch:
        return "instagram"
    return None


def recent_uploads(channel, n, timeout, cookies_browser=None):
    """Return (rows, err). rows: list of {id, upload_date, title} for the newest
    `n` uploads (flat-playlist metadata only). err set (rows None) on failure."""
    env = os.environ.copy()
    cookie_args = []
    if cookies_browser:
        env["YTDLP_COOKIES_FROM_BROWSER"] = cookies_browser
        cookie_args = ["--cookies-from-browser", cookies_browser]
    cmd = ["yt-dlp", *cookie_args, "--flat-playlist", "--playlist-end", str(n),
           "--no-warnings", "--print", "%(id)s\t%(upload_date)s\t%(title)s", channel]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except FileNotFoundError:
        return None, "yt-dlp not installed"
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout}s"
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        return None, (err[-1] if err else "yt-dlp failed")
    rows = []
    for line in proc.stdout.strip().splitlines():
        parts = line.split("\t")
        vid = parts[0] if parts else ""
        if not vid or vid == "NA":
            continue
        rows.append({"id": vid,
                     "upload_date": parts[1] if len(parts) > 1 else "",
                     "title": parts[2] if len(parts) > 2 else ""})
    return rows, None


def build_candidate(row, creator):
    """Assemble a queue entry carrying every field the ingestion step needs, so
    it never has to re-read the roster."""
    plat = _platform(creator)
    return {
        "id": row["id"],
        "title": row.get("title") or "",
        "creator": creator.get("name"),
        "creator_slug": creator.get("creator_slug"),
        "credential": creator.get("credential"),
        "channel": creator.get("channel"),
        "platform": _PLATFORM_LABEL.get(plat, plat or ""),
        "tier": creator.get("tier"),
        "product_recs": creator.get("product_recs"),
        "conflict": creator.get("conflict"),
        "posted": fmt_date(row.get("upload_date")),
        "feed_rank": row.get("_feed_rank", 99),
        "status": "pending",
    }


def _pullable(roster, skip_tiktok):
    """Return (youtube, tiktok) lists of pullable, non-muted creators."""
    youtube, tiktok = [], []
    for r in roster:
        if r.get("channel_broken"):
            continue
        p = _platform(r)
        if p == "youtube":
            youtube.append(r)
        elif p == "tiktok" and not skip_tiktok:
            tiktok.append(r)
    return youtube, tiktok


def _probe_group(creators, per, timeout, workers, cookies_browser=None):
    """Probe a set of channels concurrently; return {slug: (creator, rows, err)}."""
    out = {}
    if not creators:
        return out
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(recent_uploads, r["channel"], per, timeout, cookies_browser): r
                for r in creators}
        for fut in concurrent.futures.as_completed(futs):
            r = futs[fut]
            rows, err = fut.result()
            out[r["creator_slug"]] = (r, rows, err)
    return out


def collect_new(results, seen):
    """From {slug: (creator, rows, err)} produce (new_items, errors), mutating
    `seen` so a video added for one creator is not re-added for another."""
    new_items, errors = [], []
    for slug in sorted(results):
        r, rows, err = results[slug]
        if rows is None:
            errors.append((slug, err))
            continue
        for f in new_candidates(rows, seen):
            seen.add(f["id"])
            new_items.append(build_candidate(f, r))
    return new_items, errors


def rank_pending(queue, ingested, platform=None):
    """The pending, not-yet-ingested candidates a pull cron should ingest, freshest
    first (feed_rank asc; posted desc as a stable tie-break). Optional platform
    filter (YouTube/TikTok) so each pull cron drains only what it can process."""
    pending = [q for q in queue
               if q.get("status", "pending") == "pending"
               and str(q.get("id")) not in ingested
               and (not platform or (q.get("platform") or "").lower() == platform.lower())]
    ranked = sorted(pending, key=lambda q: (q.get("posted") or ""), reverse=True)
    return sorted(ranked, key=lambda q: q.get("feed_rank", 99))


def _write_queue(queue):
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(yaml.safe_dump(queue, sort_keys=False, allow_unicode=True, width=1000),
                     encoding="utf-8")


def do_scan(args):
    """Network sweep of every pullable creator; write new uploads to the queue.
    YouTube runs at full concurrency; TikTok at low concurrency (rate limits),
    with browser cookies. Self-heals by pruning already-carded pending entries."""
    roster = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    youtube, tiktok = _pullable(roster, args.skip_tiktok)

    ingested = ingested_ids()
    queue = prune_ingested(load_queue(), ingested)
    seen = ingested | queued_ids(queue)

    results = _probe_group(youtube, args.per, args.timeout, args.workers)
    results.update(_probe_group(tiktok, args.per, args.timeout,
                                min(2, args.workers), cookies_browser=args.tiktok_cookies))

    new_items, errors = collect_new(results, seen)
    queue.extend(new_items)
    if not args.dry_run:
        _write_queue(queue)

    n_chan = len(youtube) + len(tiktok)
    pending = [q for q in queue if q.get("status", "pending") == "pending"]
    print(f"scanned {n_chan} channels ({len(results) - len(errors)} ok, "
          f"{len(errors)} unreachable); {len(new_items)} new videos added; "
          f"{len(pending)} pending in queue"
          + (" [dry-run: not written]" if args.dry_run else ""))
    if errors:
        print("unreachable (weekly channel-health handles these): "
              + ", ".join(f"{s} ({e})" for s, e in errors[:12])
              + (" ..." if len(errors) > 12 else ""))
    return queue


def do_resolve(video_id, reason):
    queue = load_queue()
    hit = False
    for item in queue:
        if str(item.get("id")) == video_id:
            item["status"] = "skipped"
            if reason:
                item["skip_reason"] = reason
            hit = True
    if not hit:
        print(f"resolve: {video_id} not in queue")
        return 1
    _write_queue(queue)
    print(f"resolve: {video_id} marked skipped")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scan", action="store_true",
                    help="perform the network sweep over every creator and update "
                         "the queue (the daily video-scan cron uses this)")
    ap.add_argument("--per", type=int, default=6,
                    help="recent uploads to list per creator when scanning (default 6)")
    ap.add_argument("--timeout", type=int, default=40)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tiktok-cookies", default="chrome")
    ap.add_argument("--skip-tiktok", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --scan: sweep and report, but do not write the queue")
    ap.add_argument("--list-pending", type=int, metavar="N",
                    help="print the N freshest pending candidates (TSV) for a pull "
                         "cron to ingest; a cheap local read (no network unless "
                         "combined with --scan)")
    ap.add_argument("--platform", choices=["youtube", "tiktok"],
                    help="with --list-pending: only list candidates on this platform")
    ap.add_argument("--resolve", metavar="VIDEO_ID",
                    help="mark a candidate handled so it is not re-listed (use for "
                         "videos rejected at ingest); a cheap local write")
    ap.add_argument("--reason", default="", help="note stored with --resolve")
    args = ap.parse_args(argv)

    if args.resolve:
        return do_resolve(args.resolve, args.reason)

    queue = do_scan(args) if args.scan else load_queue()

    if args.list_pending is not None:
        ingested = ingested_ids()
        for q in rank_pending(queue, ingested, args.platform)[:args.list_pending]:
            print("\t".join(f"{k}={q.get(k)}" for k in
                            ("id", "creator_slug", "creator", "credential", "channel",
                             "platform", "tier", "product_recs", "posted", "title", "conflict")))
    elif not args.scan:
        ap.error("nothing to do: pass --scan, --list-pending N, or --resolve ID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
