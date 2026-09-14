"""The channel-health partition must route each roster entry correctly:
YouTube and TikTok channels get network-checked (TikTok with browser cookies),
`channel_broken` entries are muted (not re-flagged every run), and
Instagram/other channels are skipped.
"""
import importlib.machinery
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    loader = importlib.machinery.SourceFileLoader(
        "channel_health", str(ROOT / "scripts" / "channel_health.py"))
    spec = importlib.util.spec_from_loader("channel_health", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_partition_routes_each_kind():
    ch = _load()
    roster = [
        {"creator_slug": "yt-a", "channel": "https://www.youtube.com/@a/videos"},
        {"creator_slug": "tiktok-b", "channel": "https://www.tiktok.com/@b"},
        {"creator_slug": "broken-c", "channel": "", "channel_broken": "404s"},
        # a channel_broken marker mutes even a youtube.com URL:
        {"creator_slug": "broken-d", "channel": "https://www.youtube.com/@d",
         "channel_broken": "renamed"},
        {"creator_slug": "nochan-e"},
    ]
    youtube, tiktok, muted, other = ch.partition(roster)
    assert [c["creator_slug"] for c in youtube] == ["yt-a"]
    assert [c["creator_slug"] for c in tiktok] == ["tiktok-b"]
    assert sorted(c["creator_slug"] for c in muted) == ["broken-c", "broken-d"]
    assert [c["creator_slug"] for c in other] == ["nochan-e"]
