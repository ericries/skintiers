"""A cooldown must not hide a transcript that is already on disk.

The YouTube 429 cooldown exists to avoid extending a server-side throttle with
more requests. Serving a cached transcript makes no request at all, so the
cooldown has nothing to protect against. Before this was fixed, main() returned
at the cooldown gate before fetch_transcript() ever consulted the cache, which
made every already-verified transcript unreachable for the length of the
cooldown. That blocked a goal page on 2026-11-16 whose video had been fetched
and cached successfully earlier the same day.
"""
import json
import subprocess
import sys
import pathlib
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "yt_transcript.py"
VID = "zzTestCache"


def _run(cache_root, *args):
    import os
    env = dict(os.environ, SK_RESEARCH_CACHE=str(cache_root))
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, env=env)


def test_cached_transcript_is_served_during_a_cooldown(tmp_path):
    cache = tmp_path / "research-cache"
    (cache / "transcripts").mkdir(parents=True)
    (cache / "transcripts" / f"{VID}.json").write_text(json.dumps({
        "id": VID, "title": "Cached Title",
        "url": f"https://www.youtube.com/watch?v={VID}", "duration": 60,
        "uploader": "Someone", "channel": "Someone", "posted": "20260101",
        "source": "manual", "has_transcript": True, "text": "CACHED BODY TEXT",
    }), encoding="utf-8")

    # Arm the cooldown the same way a real 429 does.
    (REPO / "research-cache" / "yt-429-cooldown").write_text(str(time.time()), encoding="utf-8")
    try:
        r = _run(cache, VID)
        assert "CACHED BODY TEXT" in r.stdout, (
            "a cached transcript must be served during a cooldown; got:\n"
            + r.stdout + r.stderr)
        assert r.returncode == 0
    finally:
        (REPO / "research-cache" / "yt-429-cooldown").unlink(missing_ok=True)
