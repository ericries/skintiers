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
import re
import subprocess
import sys
import tempfile


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


def fetch_transcript(url):
    """Fetch the best English transcript for a YouTube video.

    Returns a dict with metadata plus `source` ('manual'|'auto'), `text`, and
    `has_transcript` (False if the video has no English captions at all)."""
    meta = video_meta(url)
    with tempfile.TemporaryDirectory() as d:
        # Prefer creator-provided subs; fall back to auto-captions.
        path, source = _download_json3(url, "en,en-US,en-GB", auto=False, workdir=d), "manual"
        if not path:
            path, source = _download_json3(url, "en,en-orig,en-US,en.*", auto=True, workdir=d), "auto"
        if not path:
            return {**meta, "has_transcript": False, "source": None, "text": ""}
        with open(path, encoding="utf-8") as f:
            text = parse_json3(json.load(f))
    return {**meta, "has_transcript": bool(text), "source": source, "text": text}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fetch a YouTube transcript via yt-dlp.")
    ap.add_argument("url", help="YouTube URL or video id")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)
    result = fetch_transcript(args.url)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(f"{result['title']}  [{result['channel'] or result['uploader']}]")
    print(f"{result['url']}  ({result['duration']}s)")
    if not result["has_transcript"]:
        print("\nNO ENGLISH TRANSCRIPT AVAILABLE — do not cite this video.")
        return 1
    print(f"transcript source: {result['source']}\n")
    print(result["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
