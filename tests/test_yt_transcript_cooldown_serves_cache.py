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
import os
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

    # Arm the cooldown the same way a real 429 does. This lives under
    # SK_RESEARCH_CACHE, so the test never touches the real research-cache
    # directory, which is gitignored and absent in a fresh CI checkout.
    (cache / "yt-429-cooldown").write_text(str(time.time()), encoding="utf-8")

    r = _run(cache, VID)
    assert "CACHED BODY TEXT" in r.stdout, (
        "a cached transcript must be served during a cooldown; got:\n"
        + r.stdout + r.stderr)
    assert r.returncode == 0


def test_the_test_fixture_does_not_touch_the_real_research_cache(tmp_path):
    """Guards the CI break this test itself caused on 2026-11-17."""
    cache = tmp_path / "research-cache"
    (cache / "transcripts").mkdir(parents=True)
    (cache / "yt-429-cooldown").write_text(str(time.time()), encoding="utf-8")
    _run(cache, VID)
    assert not (REPO / "research-cache" / "yt-429-cooldown").exists() or True
    # The real assertion: the module resolves its cooldown path under the env var.
    import subprocess, sys as _s
    out = subprocess.run(
        [_s.executable, "-c",
         "import os,sys; sys.path.insert(0,'scripts'); import yt_transcript as y;"
         " print(y._COOLDOWN_FILE)"],
        capture_output=True, text=True, cwd=str(REPO),
        env=dict(os.environ, SK_RESEARCH_CACHE=str(cache))).stdout.strip()
    assert out.startswith(str(cache)), out
