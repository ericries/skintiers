#!/usr/bin/env python3
"""Continuously surface NEW candidate creators for the video roster.

The roster had no producer: it only grew in manual batches, so it stalled at ~55.
This mines YouTube by the site's own core topics ("<topic> dermatologist" /
"<topic> cosmetic chemist"), collects the channels that keep coming up, dedups
against the existing roster + prior candidates, and appends the fresh ones to a
VETTING queue (data/queues/creator-candidates.yaml). Nothing is auto-added to the
roster - a separate weekly vetting step promotes the ones that pass the rubric.

A channel that surfaces across MANY topic searches is a strong quality signal
(the algorithm keeps returning them for skincare-science queries), so candidates
are ranked by `hits`.

Usage:
  python scripts/discover_creators.py                 # default core-topic sweep
  python scripts/discover_creators.py --per 6 --dry-run
  python scripts/discover_creators.py --topics "tretinoin,azelaic acid,rosacea"
"""
import argparse
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROSTER = ROOT / "data" / "video-sources.yaml"
CANDIDATES = ROOT / "data" / "queues" / "creator-candidates.yaml"

# Core topics the site is built on; a channel that ranks for these is on-topic.
DEFAULT_TOPICS = [
    "tretinoin", "retinoids", "azelaic acid", "niacinamide", "vitamin C serum",
    "salicylic acid", "benzoyl peroxide", "sunscreen", "rosacea", "melasma",
    "hyperpigmentation", "fungal acne", "skin barrier", "peptides skincare",
    "hyaluronic acid",
]
QUALIFIERS = ["dermatologist", "cosmetic chemist"]
UC_RE = re.compile(r"/channel/(UC[\w-]+)")
HANDLE_RE = re.compile(r"/@([\w.-]+)")


def _norm_name(s):
    s = (s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)           # drop parentheticals
    s = re.sub(r"\b(dr|md|faad|phd|the)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def _roster_keys():
    rows = yaml.safe_load(ROSTER.read_text(encoding="utf-8")) or []
    ucids, handles, names = set(), set(), set()
    for r in rows:
        ch = r.get("channel") or ""
        m = UC_RE.search(ch)
        if m:
            ucids.add(m.group(1))
        h = HANDLE_RE.search(ch)
        if h:
            handles.add(h.group(1).lower())
            names.add(_norm_name(h.group(1)))       # @LabMuffinBeautyScience -> labmuffinbeautyscience
        nm = r.get("name") or ""
        names.add(_norm_name(nm))
        names.add(_norm_name(r.get("creator_slug")))
        for paren in re.findall(r"\((.*?)\)", nm):   # "Andrea Suarez (Dr Dray)" -> also index "Dr Dray"
            names.add(_norm_name(paren))
    names.discard("")
    return ucids, handles, names


def _is_rostered(name, url, ucids, names):
    uc = UC_RE.search(url)
    if uc and uc.group(1) in ucids:
        return True
    nm = _norm_name(name)
    if not nm:
        return False
    if nm in names:
        return True
    # containment both ways for names >=5 chars (catches "dray" in "drdrayzday")
    return any(len(k) >= 5 and (nm in k or k in nm) for k in names)


def _existing_candidates():
    if not CANDIDATES.exists():
        return []
    return yaml.safe_load(CANDIDATES.read_text(encoding="utf-8")) or []


def _search(topic, qualifier, per):
    q = f"ytsearch{per}:{topic} {qualifier}"
    try:
        out = subprocess.run(
            ["yt-dlp", q, "--flat-playlist", "--no-warnings",
             "--print", "%(channel)s\t%(channel_url)s"],
            capture_output=True, text=True, timeout=120)
        rows = []
        for line in (out.stdout or "").splitlines():
            parts = line.split("\t")
            if len(parts) == 2 and parts[1].strip():
                rows.append((parts[0].strip(), parts[1].strip()))
        return rows
    except Exception:
        return []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topics", help="comma-separated override of the topic list")
    ap.add_argument("--per", type=int, default=5, help="results per topic-qualifier search")
    ap.add_argument("--dry-run", action="store_true", help="print candidates, do not write")
    args = ap.parse_args(argv)
    topics = ([t.strip() for t in args.topics.split(",") if t.strip()]
              if args.topics else DEFAULT_TOPICS)

    ucids, handles, roster_names = _roster_keys()
    existing = _existing_candidates()
    seen_urls = {c.get("channel_url") for c in existing}
    seen_names = {_norm_name(c.get("name")) for c in existing}

    found = {}   # channel_url -> {name, hits, topics}
    for topic in topics:
        for qual in QUALIFIERS:
            for name, url in _search(topic, qual, args.per):
                if _is_rostered(name, url, ucids, roster_names):
                    continue
                rec = found.setdefault(url, {"name": name, "hits": 0, "topics": set()})
                rec["hits"] += 1
                rec["topics"].add(topic)

    # New candidates only (not already in the queue), ranked by cross-topic hits
    fresh = []
    for url, rec in found.items():
        if url in seen_urls or _norm_name(rec["name"]) in seen_names:
            continue
        fresh.append({"name": rec["name"], "channel_url": url,
                      "hits": rec["hits"], "topics": sorted(rec["topics"]),
                      "status": "pending"})
    fresh.sort(key=lambda c: -c["hits"])

    for c in fresh:
        print(f'HIT x{c["hits"]:>2}  {c["name"]}  {c["channel_url"]}  [{", ".join(c["topics"][:4])}]')
    print(f"\n{len(fresh)} new candidate(s); roster has {len(ucids)+len(handles)} known channels, "
          f"queue had {len(existing)}.")

    if args.dry_run or not fresh:
        return 0
    out = existing + fresh
    CANDIDATES.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"wrote {len(fresh)} to {CANDIDATES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
