#!/usr/bin/env python3
"""Fetch a video's transcript (captions) via yt-dlp, for the social-media sourcing
pipeline. Works on any platform yt-dlp supports that exposes captions; tested on
YouTube (json3 captions) and TikTok (VTT subtitles). Prefers creator-provided
(manual) subtitles over auto-captions and reports which was used, so the caller
knows how trustworthy the text is. Transcripts are cached (see research-cache).

Usage:
    python scripts/yt_transcript.py <url-or-youtube-id>
    python scripts/yt_transcript.py --json <url>       # machine-readable
    python scripts/yt_transcript.py --refresh <url>    # ignore the cache

The parse steps are pure and unit-tested; the fetch step shells out to yt-dlp and
needs network.
"""
import argparse
import glob
import hashlib
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
_TT_ID = re.compile(r"tiktok\.com/.+?/video/(\d+)")


def video_id(url_or_id):
    """A stable cache key for a video URL (or bare YouTube id), or None.

    YouTube -> the 11-char id; TikTok -> the numeric video id; any other URL ->
    a short hash of the URL so it still caches deterministically."""
    s = url_or_id or ""
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = _YT_ID.search(s)
    if m:
        return m.group(1)
    m = _TT_ID.search(s)
    if m:
        return m.group(1)
    if "://" in s:
        return "url-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]
    return None


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


def parse_vtt(text):
    """Turn a WebVTT subtitle file (TikTok and others) into clean plain text.

    Drops the WEBVTT header, NOTE/STYLE blocks, cue-timing lines, numeric cue
    ids, and inline tags; collapses consecutive duplicate lines and whitespace."""
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if (not line or line == "WEBVTT" or "-->" in line or line.isdigit()
                or line.startswith(("NOTE", "STYLE", "Kind:", "Language:"))):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and (not lines or line != lines[-1]):
            lines.append(line)
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def _run(args):
    # Optionally pass browser cookies to yt-dlp to clear YouTube's rate-limit /
    # bot-detection (HTTP 429 "Sign in to confirm you're not a bot"). Set
    # YTDLP_COOKIES_FROM_BROWSER=chrome (or firefox/safari/...) to enable.
    cb = os.environ.get("YTDLP_COOKIES_FROM_BROWSER")
    if cb and args and args[0] == "yt-dlp":
        args = [args[0], "--cookies-from-browser", cb] + args[1:]
    return subprocess.run(args, capture_output=True, text=True, timeout=120)


def video_meta(url):
    """Return {id, title, uploader, channel, duration, url, posted} via yt-dlp, no
    download. `posted` is the video's original upload date as 'YYYY-MM-DD' (or ''
    if yt-dlp reports none) - used as the `posted:` field on video cards so the
    Feed page can order them by when the video was posted."""
    fields = ("%(id)s\t%(title)s\t%(uploader)s\t%(channel)s\t"
              "%(duration)s\t%(webpage_url)s\t%(upload_date)s")
    r = _run(["yt-dlp", "--skip-download", "--no-warnings", "--print", fields, url])
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp metadata failed: {r.stderr.strip()[:300]}")
    vid, title, uploader, channel, duration, wurl, uploaded = (
        r.stdout.strip().split("\t") + [""] * 7)[:7]
    posted = (f"{uploaded[0:4]}-{uploaded[4:6]}-{uploaded[6:8]}"
              if uploaded.isdigit() and len(uploaded) == 8 else "")
    return {"id": vid, "title": title, "uploader": uploader, "channel": channel,
            "duration": duration, "url": wurl, "posted": posted}


def _download_subs(url, langs, auto, workdir):
    """Ask yt-dlp for one caption file (json3 preferred, VTT fallback); return
    (path, ext) or (None, None). Covers YouTube (json3) and TikTok (vtt)."""
    flag = "--write-auto-subs" if auto else "--write-subs"
    _run(["yt-dlp", "--skip-download", "--no-warnings", flag,
          "--sub-langs", langs, "--sub-format", "json3/vtt/best",
          "-o", os.path.join(workdir, "%(id)s.%(ext)s"), url])
    for ext in ("json3", "vtt"):
        files = sorted(glob.glob(os.path.join(workdir, f"*.{ext}")))
        if files:
            return files[0], ext
    return None, None


def _parse_sub_file(path, ext):
    with open(path, encoding="utf-8") as f:
        data = f.read()
    return parse_json3(json.loads(data)) if ext == "json3" else parse_vtt(data)


# Language preference lists (YouTube uses en*, TikTok uses eng-US).
_MANUAL_LANGS = "en,en-US,en-GB,en-orig,eng-US"
_AUTO_LANGS = "en,en-orig,en-US,en.*,eng-US"


def fetch_transcript(url, refresh=False):
    """Fetch the best English transcript for a video, using the local verbatim
    cache so a given video is fetched from the network only once.

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
        path, ext = _download_subs(url, _MANUAL_LANGS, auto=False, workdir=d)
        source = "manual"
        if not path:
            path, ext = _download_subs(url, _AUTO_LANGS, auto=True, workdir=d)
            source = "auto"
        if not path:
            result = {**meta, "has_transcript": False, "source": None, "text": ""}
        else:
            text = _parse_sub_file(path, ext)
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
    ap = argparse.ArgumentParser(description="Fetch a video transcript via yt-dlp (YouTube, TikTok, ...).")
    ap.add_argument("url", help="video URL, or a bare YouTube id")
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
