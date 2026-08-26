#!/usr/bin/env python3
"""Mine creator REFERRALS out of videos we already process.

Vetted creators constantly point at each other - collab @handles and channel
links in the description, and positive spoken shout-outs in the transcript
("check out Dr X", "as Lab Muffin showed"). A creator another vetted creator
vouches for is a high-signal candidate. This extracts those POSITIVE references,
drops self-references and the ones already rostered, and appends the rest to the
same creator-candidates vetting queue discover_creators writes to.

Only positive/neutral references are kept: a transcript name mention is taken
only when it sits next to endorsing language, never next to "wrong / disagree /
misinformation". Description @handle links are treated as positive by default
(they are credits, collabs, or shout-outs). Nothing is auto-added to the roster.

Usage:
  python scripts/mine_referrals.py <video-id-or-url> [more ...]
  python scripts/mine_referrals.py --dry-run <url>
"""
import argparse
import pathlib
import re
import subprocess
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import discover_creators as dc          # noqa: E402  (shared roster dedup + candidate file)
import yt_transcript as yt              # noqa: E402

HANDLE_LINK = re.compile(r"youtube\.com/(@[\w.-]+|channel/UC[\w-]+)", re.I)
BARE_HANDLE = re.compile(r"(?<![\w@])@([A-Za-z][\w.-]{2,})")
# spoken shout-out: endorsing verb/phrase near a "Dr Name" / "Name" mention
POS = re.compile(
    r"(?:check out|shout ?out|go follow|i (?:love|recommend|really like)|"
    r"as (?:dr\.?\s+)?[a-z]+ (?:explained|showed|said|put it)|"
    r"(?:dr\.?\s+)?[a-z]+(?:'s)? (?:great|excellent|amazing) (?:video|channel|content))",
    re.I)
NEG = re.compile(r"(wrong|misinformation|disagree|myth|debunk|bad advice|dangerous)", re.I)
DR_NAME = re.compile(r"\b(?:dr\.?\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)")


def _desc(url):
    # yt-dlp is occasionally throttled and returns empty; one retry covers it.
    for _ in range(2):
        try:
            r = subprocess.run(
                ["yt-dlp", "--skip-download", "--no-warnings", "--print",
                 "%(description)s\t%(uploader_id)s\t%(channel)s\t%(uploader_url)s\t%(channel_url)s",
                 url],
                capture_output=True, text=True, timeout=90)
            if (r.stdout or "").strip():
                parts = r.stdout.split("\t")
                return (parts + [""] * 5)[:5]
        except Exception:
            pass
    return ["", "", "", "", ""]


def referrals_from_video(url, roster_ucids, roster_names, roster_handles, self_norms):
    desc, up_id, channel, up_url, ch_url = _desc(url)
    found = {}   # channel_url -> name

    # 1) explicit @handle / channel links in the description (positive by default)
    for m in HANDLE_LINK.finditer(desc or ""):
        ref = m.group(1)
        curl = f"https://www.youtube.com/{ref}"
        name = ref.lstrip("@") if ref.startswith("@") else ref
        found[curl] = name
    for m in BARE_HANDLE.finditer(desc or ""):
        h = m.group(1)
        found.setdefault(f"https://www.youtube.com/@{h}", h)

    # 2) positive spoken mentions of "Dr Name" in the transcript
    try:
        tr = yt.fetch_transcript(url).get("text", "") or ""
    except Exception:
        tr = ""
    for m in DR_NAME.finditer(tr):
        name = m.group(1)
        window = tr[max(0, m.start() - 60): m.end() + 60]
        if POS.search(window) and not NEG.search(window):
            # resolve the spoken name to a channel via search (best-effort)
            found.setdefault(f"name:{name}", name)

    # drop self-references + already-known
    out = []
    for curl, name in found.items():
        nm = dc._norm_name(name)
        if not nm or nm in self_norms:
            continue
        # a name: pseudo-url means "resolve later"; keep the display name
        display, real_url = (name, "" ) if curl.startswith("name:") else (name, curl)
        if dc._is_rostered(display, real_url or "https://youtube.com/@" + nm, roster_ucids, roster_names):
            continue
        out.append((display, real_url))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("videos", nargs="+", help="video ids or URLs just processed")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    ucids, handles, names = dc._roster_keys()
    existing = dc._existing_candidates()
    seen_urls = {c.get("channel_url") for c in existing}
    seen_names = {dc._norm_name(c.get("name")) for c in existing}

    fresh = {}
    for v in args.videos:
        url = v if "://" in v else f"https://www.youtube.com/watch?v={v}"
        # self = the uploader of THIS video (never refer them to themselves)
        d = _desc(url)
        self_norms = {dc._norm_name(x) for x in (d[1], d[2]) if x}
        for display, curl in referrals_from_video(url, ucids, names, handles, self_norms):
            key = curl or f"name:{dc._norm_name(display)}"
            if key in seen_urls or dc._norm_name(display) in seen_names:
                continue
            rec = fresh.setdefault(key, {"name": display, "channel_url": curl,
                                         "hits": 0, "topics": ["referral"],
                                         "discovered_via": f"referral: {v}", "status": "pending"})
            rec["hits"] += 1

    rows = sorted(fresh.values(), key=lambda r: -r["hits"])
    for r in rows:
        print(f'REFERRAL x{r["hits"]}  {r["name"]}  {r["channel_url"] or "(resolve by name)"}')
    print(f"\n{len(rows)} new referral candidate(s).")
    if args.dry_run or not rows:
        return 0
    dc.CANDIDATES.write_text(
        yaml.safe_dump(existing + rows, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"appended {len(rows)} to {dc.CANDIDATES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
