#!/usr/bin/env python3
"""Fetch a YouTube video's transcript (captions) via yt-dlp, for the social-media
sourcing pipeline. Prefers creator-provided (manual) subtitles over auto-captions,
and reports which was used so the caller knows how trustworthy the text is.

Usage:
    python scripts/yt_transcript.py <youtube-url-or-id>
    python scripts/yt_transcript.py --json <url>      # machine-readable

Only YouTube is supported here (it exposes transcripts cleanly). The parse step is
pure and unit-tested; the fetch step shells out to yt-dlp and needs network.
"""
import argparse
import glob
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

# Private local verbatim cache (gitignored, never built into the site). Transcripts
# are cached by video id so re-verifying a claim never re-fetches. Override the
# location with SK_RESEARCH_CACHE (used by tests).
CACHE_ROOT = pathlib.Path(os.environ.get(
    "SK_RESEARCH_CACHE", pathlib.Path(__file__).resolve().parents[1] / "research-cache"))
TRANSCRIPT_CACHE = CACHE_ROOT / "transcripts"

_YT_ID = re.compile(r"(?:v=|/shorts/|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})")


def video_id(url_or_id):
    """Extract the 11-char YouTube id from a URL or bare id, or None."""
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id or ""):
        return url_or_id
    m = _YT_ID.search(url_or_id or "")
    return m.group(1) if m else None


def parse_json3(data):
    """Turn YouTube's json3 caption payload into clean plain text.

    json3 is {"events": [{"segs": [{"utf8": "..."}]}]}; window/position events
    carry no segs and are skipped. Consecutive duplicate lines (common in rolling
    auto-captions) are collapsed."""
    lines = []
    for ev in data.get("events") or []:
        segs = ev.get("segs")
        if not segs:
            continue
        line = "".join(s.get("utf8", "") for s in segs).strip()
        if not line:
            continue
        if lines and line == lines[-1]:
            continue
        lines.append(line)
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def _run(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=120)


def video_meta(url):
    """Return {id, title, uploader, channel, duration, url} via yt-dlp, no download."""
    fields = ("%(id)s\t%(title)s\t%(uploader)s\t%(channel)s\t"
              "%(duration)s\t%(webpage_url)s")
    r = _run(["yt-dlp", "--skip-download", "--no-warnings", "--print", fields, url])
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp metadata failed: {r.stderr.strip()[:300]}")
    vid, title, uploader, channel, duration, wurl = (r.stdout.strip().split("\t") + [""] * 6)[:6]
    return {"id": vid, "title": title, "uploader": uploader, "channel": channel,
            "duration": duration, "url": wurl}


def _download_json3(url, langs, auto, workdir):
    """Ask yt-dlp for one json3 caption file; return its path or None."""
    flag = "--write-auto-subs" if auto else "--write-subs"
    r = _run(["yt-dlp", "--skip-download", "--no-warnings", flag,
              "--sub-langs", langs, "--sub-format", "json3",
              "-o", os.path.join(workdir, "%(id)s.%(ext)s"), url])
    files = sorted(glob.glob(os.path.join(workdir, "*.json3")))
    return files[0] if files else None


def fetch_transcript(url, refresh=False):
    """Fetch the best English transcript for a YouTube video, using the local
    verbatim cache so a given video is fetched from the network only once.

    Returns a dict with metadata plus `source` ('manual'|'auto'), `text`,
    `has_transcript`, and `cached` (True if served from the local cache)."""
    vid = video_id(url)
    cache_json = TRANSCRIPT_CACHE / f"{vid}.json" if vid else None
    if cache_json and cache_json.exists() and not refresh:
        with open(cache_json, encoding="utf-8") as f:
            return {**json.load(f), "cached": True}

    meta = video_meta(url)
    with tempfile.TemporaryDirectory() as d:
        # Prefer creator-provided subs; fall back to auto-captions.
        path, source = _download_json3(url, "en,en-US,en-GB", auto=False, workdir=d), "manual"
        if not path:
            path, source = _download_json3(url, "en,en-orig,en-US,en.*", auto=True, workdir=d), "auto"
        if not path:
            result = {**meta, "has_transcript": False, "source": None, "text": ""}
        else:
            with open(path, encoding="utf-8") as f:
                text = parse_json3(json.load(f))
            result = {**meta, "has_transcript": bool(text), "source": source, "text": text}

    if vid:  # write to the verbatim cache (json canonical + txt for reading)
        TRANSCRIPT_CACHE.mkdir(parents=True, exist_ok=True)
        cache_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if result["has_transcript"]:
            (TRANSCRIPT_CACHE / f"{vid}.txt").write_text(
                f"{result['title']}\n{result['url']}\nsource: {result['source']}\n\n{result['text']}\n",
                encoding="utf-8")
    return {**result, "cached": False}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fetch a YouTube transcript via yt-dlp.")
    ap.add_argument("url", help="YouTube URL or video id")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--refresh", action="store_true", help="ignore the cache and re-fetch")
    args = ap.parse_args(argv)
    result = fetch_transcript(args.url, refresh=args.refresh)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(f"{result['title']}  [{result['channel'] or result['uploader']}]")
    print(f"{result['url']}  ({result['duration']}s){'  [cached]' if result.get('cached') else ''}")
    if not result["has_transcript"]:
        print("\nNO ENGLISH TRANSCRIPT AVAILABLE — do not cite this video.")
        return 1
    print(f"transcript source: {result['source']}\n")
    print(result["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
