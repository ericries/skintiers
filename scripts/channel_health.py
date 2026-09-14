#!/usr/bin/env python3
"""Flag roster channels that no longer resolve.

Creators rename their YouTube channels, which silently 404s a roster URL and
makes video-pull/backfill return empty for an active creator (this bit us on
Scott Walter and Dustin Portela). This sweep asks yt-dlp for the single newest
upload from each channel; a channel that cannot produce one is flagged so the
URL can be re-pinned (YouTube: to the stable /channel/UC... form) or the handle
muted/replaced before it wastes pulls.

TikTok handles have their own silent failure mode: the account page returns
HTTP 200 but yt-dlp cannot list its videos ("Unable to extract secondary user
ID", or "does not have any videos posted"), so the TikTok rotation keeps
handing the dead handle back and every pull wastes a tick (this bit us on
@gohealio and @drsharimarchbein). We now probe TikTok handles too, using
browser cookies (TikTok blocks cookieless fetches), at low concurrency to stay
under TikTok's rate limit. Instagram/other non-pullable channels are still
skipped. Exit status is nonzero if any checked channel is broken, so a cron can
surface it.

Usage: .venv/bin/python scripts/channel_health.py [--timeout SECONDS]
                                                   [--tiktok-cookies BROWSER]
                                                   [--skip-tiktok]
"""
import argparse
import concurrent.futures
import os
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROSTER = ROOT / "data" / "video-sources.yaml"


def partition(roster):
    """Split the roster into (youtube, tiktok, muted, other).

    `muted` are entries with a truthy `channel_broken` marker — already known
    broken and awaiting a re-pin/replace, so we don't re-flag them every run.
    `youtube` and `tiktok` are the pullable channels we probe; `other` is
    Instagram and anything else we cannot pull here. Pure (no network) so it
    can be unit-tested.
    """
    youtube, tiktok, muted, other = [], [], [], []
    for c in roster:
        chan = c.get("channel") or ""
        if c.get("channel_broken"):
            muted.append(c)
        elif "youtube.com" in chan:
            youtube.append(c)
        elif "tiktok.com" in chan:
            tiktok.append(c)
        else:
            other.append(c)
    return youtube, tiktok, muted, other


def check_channel(url, timeout, cookies_browser=None):
    """Return (ok, detail). ok=True if yt-dlp lists >=1 entry from the channel.

    When cookies_browser is set (required for TikTok), yt-dlp reads that
    browser's cookies via the YTDLP_COOKIES_FROM_BROWSER env var, which the
    project's other scripts also honor.
    """
    env = os.environ.copy()
    if cookies_browser:
        env["YTDLP_COOKIES_FROM_BROWSER"] = cookies_browser
    cmd = ["yt-dlp", "--flat-playlist", "--playlist-end", "1",
           "--print", "id", "--no-warnings"]
    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]
    cmd.append(url)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env,
        )
    except FileNotFoundError:
        return False, "yt-dlp not installed"
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    if proc.returncode == 0 and proc.stdout.strip():
        return True, proc.stdout.strip().splitlines()[0]
    err = (proc.stderr or proc.stdout or "no output").strip().splitlines()
    return False, err[-1] if err else "empty"


def probe(entries, timeout, workers, cookies_browser=None):
    """Probe a set of channels concurrently; return list of (entry, detail) broken."""
    broken = []
    if not entries:
        return broken
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(check_channel, c["channel"], timeout, cookies_browser): c
                for c in entries}
        for fut in concurrent.futures.as_completed(futs):
            c = futs[fut]
            ok, detail = fut.result()
            if not ok:
                broken.append((c, detail))
    return broken


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=40)
    ap.add_argument("--tiktok-cookies", default="chrome",
                    help="browser to read cookies from for TikTok checks")
    ap.add_argument("--skip-tiktok", action="store_true",
                    help="do not probe TikTok handles (YouTube only)")
    args = ap.parse_args(argv)

    roster = yaml.safe_load(ROSTER.read_text())
    youtube, tiktok, muted, other = partition(roster)

    yt_broken = probe(youtube, args.timeout, 8)
    tk_broken = []
    if not args.skip_tiktok:
        # low concurrency to stay under TikTok's rate limit
        tk_broken = probe(tiktok, args.timeout, 2, cookies_browser=args.tiktok_cookies)

    tk_note = "skipped" if args.skip_tiktok else f"{len(tiktok)} checked"
    print(f"checked {len(youtube)} YouTube channels; TikTok {tk_note}; "
          f"{len(other)} other/IG skipped; {len(muted)} known-broken muted")
    if muted:
        print("known-broken (muted; re-pin or replace to clear): "
              + ", ".join(c["creator_slug"] for c in muted))

    if not yt_broken and not tk_broken:
        print("all checked channels resolve.")
        return 0

    if yt_broken:
        print(f"\n{len(yt_broken)} YouTube BROKEN — re-pin to a stable /channel/UC... URL:")
        for c, detail in sorted(yt_broken, key=lambda x: x[0]["creator_slug"]):
            flag = " [FLAGSHIP]" if c.get("flagship") else ""
            print(f"  - {c['creator_slug']}{flag}: {c['channel']}\n      -> {detail}")
    if tk_broken:
        print(f"\n{len(tk_broken)} TikTok UN-PULLABLE — mark channel_broken (mute) "
              f"and replace the creator, or fix the handle:")
        for c, detail in sorted(tk_broken, key=lambda x: x[0]["creator_slug"]):
            flag = " [FLAGSHIP]" if c.get("flagship") else ""
            print(f"  - {c['creator_slug']}{flag}: {c['channel']}\n      -> {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
