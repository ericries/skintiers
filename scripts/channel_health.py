#!/usr/bin/env python3
"""Flag roster channels that no longer resolve.

Creators rename their YouTube channels, which silently 404s a roster URL and
makes video-pull/backfill return empty for an active creator (this bit us on
Scott Walter and Dustin Portela). This sweep asks yt-dlp for the single newest
upload from each YouTube channel; a channel that cannot produce one is flagged
so the URL can be re-pinned to the stable /channel/UC... form before it wastes
pulls. Non-YouTube channels (TikTok/IG) are skipped — they have a different
failure mode. Exit status is nonzero if any YouTube channel is broken, so a
cron can surface it.

Usage: .venv/bin/python scripts/channel_health.py [--timeout SECONDS]
"""
import argparse
import concurrent.futures
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROSTER = ROOT / "data" / "video-sources.yaml"


def partition(roster):
    """Split the roster into (to_check, muted, non_youtube).

    `muted` are entries with a truthy `channel_broken` marker — already known
    broken and awaiting a re-pin, so we don't re-flag them every run. Pure
    (no network) so it can be unit-tested.
    """
    to_check, muted, non_youtube = [], [], []
    for c in roster:
        if c.get("channel_broken"):
            muted.append(c)
        elif "youtube.com" in (c.get("channel") or ""):
            to_check.append(c)
        else:
            non_youtube.append(c)
    return to_check, muted, non_youtube


def check_channel(url, timeout):
    """Return (ok, detail). ok=True if yt-dlp lists >=1 entry from the channel."""
    try:
        proc = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--playlist-end", "1",
             "--print", "id", "--no-warnings", url],
            capture_output=True, text=True, timeout=timeout,
        )
    except FileNotFoundError:
        return False, "yt-dlp not installed"
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    if proc.returncode == 0 and proc.stdout.strip():
        return True, proc.stdout.strip().splitlines()[0]
    err = (proc.stderr or proc.stdout or "no output").strip().splitlines()
    return False, err[-1] if err else "empty"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=40)
    args = ap.parse_args(argv)

    roster = yaml.safe_load(ROSTER.read_text())
    yt, muted, non_youtube = partition(roster)

    broken = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(check_channel, c["channel"], args.timeout): c for c in yt}
        for fut in concurrent.futures.as_completed(futs):
            c = futs[fut]
            ok, detail = fut.result()
            if not ok:
                broken.append((c, detail))

    print(f"checked {len(yt)} YouTube channels "
          f"({len(non_youtube)} non-YouTube, {len(muted)} known-broken muted)")
    if muted:
        print("known-broken (muted; re-pin to clear): "
              + ", ".join(c["creator_slug"] for c in muted))
    if not broken:
        print("all checked channels resolve.")
        return 0
    print(f"\n{len(broken)} BROKEN — re-pin to a stable /channel/UC... URL:")
    for c, detail in sorted(broken, key=lambda x: x[0]["creator_slug"]):
        flag = " [FLAGSHIP]" if c.get("flagship") else ""
        print(f"  - {c['creator_slug']}{flag}: {c['channel']}\n      -> {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
