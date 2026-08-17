#!/usr/bin/env python3
"""Fetch a TikTok video's caption transcript via yt-dlp (eng auto/manual subs).

Usage:
    python scripts/tiktok_transcript.py <tiktok_video_url>
    python scripts/tiktok_transcript.py @user <video_id>

Prints a header line then the cleaned transcript text (captions joined).
Exit 0 with transcript on success; exit 0 with "NO TRANSCRIPT" line if none.

Mirrors yt_transcript.py but for TikTok. TikTok exposes VTT subs (often the
creator's on-screen/spoken captions) under language codes like eng-US / eng.
We try a small set of English variants and parse the first that downloads.
"""
import os
import re
import subprocess
import sys
import tempfile
import glob


def build_url(args):
    if len(args) == 1 and args[0].startswith("http"):
        return args[0]
    if len(args) == 2:
        user = args[0].lstrip("@")
        vid = args[1]
        return f"https://www.tiktok.com/@{user}/video/{vid}"
    raise SystemExit("usage: tiktok_transcript.py <url> | @user <video_id>")


def clean_vtt(path):
    lines = []
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("WEBVTT") or "-->" in ln:
            continue
        if re.match(r"^\d+$", ln):  # cue number
            continue
        if re.match(r"^(Kind|Language):", ln):
            continue
        ln = re.sub(r"<[^>]+>", "", ln)  # strip inline tags
        lines.append(ln.strip())
    # dedup consecutive repeats (TikTok cues often repeat)
    out = []
    for ln in lines:
        if not out or out[-1] != ln:
            out.append(ln)
    return " ".join(out).strip()


def main():
    url = build_url(sys.argv[1:])
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "tt")
        for langs in ("eng-US", "eng", "en-US,en", "en.*,eng.*"):
            subprocess.run(
                ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
                 "--sub-langs", langs, "--sub-format", "vtt", "--no-warnings",
                 "-o", base, url],
                capture_output=True, text=True, timeout=120,
            )
            vtts = glob.glob(base + "*.vtt")
            if vtts:
                text = clean_vtt(sorted(vtts)[0])
                if text:
                    print(f"TikTok transcript: {url}")
                    print(text)
                    return
            for f in glob.glob(base + "*"):
                try:
                    os.remove(f)
                except OSError:
                    pass
    print(f"NO TRANSCRIPT: {url}")


if __name__ == "__main__":
    main()
