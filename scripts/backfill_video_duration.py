#!/usr/bin/env python3
"""Backfill `duration:` (seconds) onto video cards from the local transcript cache.

`duration` is the only RECOMMENDED Google VideoObject property the site was missing
(see docs/web-best-practices.md). Every cached transcript already carries it, so this
needs no network and cannot be rate-limited, unlike re-probing 400+ videos with
yt-dlp.

Edits are deliberately surgical text insertions rather than a frontmatter round-trip:
re-dumping YAML would reformat hundreds of unrelated lines on pages whose frontmatter
runs to 300 lines. Every touched file is re-parsed with yaml.safe_load before it is
written, so a malformed edit fails loudly instead of corrupting data.

    python scripts/backfill_video_duration.py [--apply]
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sklib  # noqa: E402
import yaml   # noqa: E402

CACHE = sklib.ROOT / "research-cache" / "transcripts"
_URL_LINE = re.compile(r"^(\s+)url:\s*(\S+)\s*$")


def cached_durations():
    out = {}
    for f in CACHE.glob("*.json"):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        d, vid = j.get("duration"), (j.get("id") or f.stem)
        if d and vid:
            try:
                out[str(vid)] = int(float(d))
            except (TypeError, ValueError):
                pass
    return out


def video_id_of(url):
    emb = None
    for pat in (r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{6,})",
                r"tiktok\.com/[^/]+/video/(\d+)"):
        m = re.search(pat, url or "")
        if m:
            emb = m.group(1)
            break
    return emb


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args(argv)

    durations = cached_durations()
    touched = added = missing = 0
    for md in sorted(sklib.DATA_DIR.glob("*/*.md")):
        text = md.read_text(encoding="utf-8")
        if "\nvideos:" not in text and not text.startswith("videos:"):
            continue
        lines, out, changed = text.split("\n"), [], 0
        for i, line in enumerate(lines):
            out.append(line)
            m = _URL_LINE.match(line)
            if not m:
                continue
            indent, url = m.group(1), m.group(2)
            # only inside a videos: card, and only if this card has no duration yet
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if nxt.strip().startswith("duration:"):
                continue
            vid = video_id_of(url)
            if not vid:
                continue
            d = durations.get(vid)
            if d is None:
                missing += 1
                continue
            out.append(f"{indent}duration: {d}")
            changed += 1
        if not changed:
            continue
        new = "\n".join(out)
        try:                      # fail loudly rather than corrupt
            yaml.safe_load(new.split("---")[1])
        except Exception as e:
            print(f"SKIP {md.name}: edit would break YAML ({e})", file=sys.stderr)
            continue
        touched += 1
        added += changed
        if args.apply:
            md.write_text(new, encoding="utf-8")
    verb = "added" if args.apply else "would add"
    print(f"{verb} duration on {added} card(s) across {touched} page(s); "
          f"{missing} card(s) had no cached duration")
    return 0


if __name__ == "__main__":
    sys.exit(main())
