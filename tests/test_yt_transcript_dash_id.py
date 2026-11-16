"""A YouTube id beginning with a dash must not be read as a command-line option.

YouTube ids are base64url and legitimately start with "-". Passed through to
yt-dlp as a bare id, such an id is parsed as an option: on 2026-11-16 the id
-IT6N0tVEaA produced "Invalid playlist-items 'T6N0tVEaA'", which looks like the
video is unavailable rather than like an argument-quoting bug. A tick could
reasonably misread that as a missing video. Normalising a bare id to a full
watch URL removes the ambiguity entirely.
"""
import importlib.machinery
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
_loader = importlib.machinery.SourceFileLoader("yt_transcript", str(ROOT / "scripts" / "yt_transcript.py"))
_spec = importlib.util.spec_from_loader("yt_transcript", _loader)
yt = importlib.util.module_from_spec(_spec)
_loader.exec_module(yt)


def test_leading_dash_id_becomes_a_watch_url():
    assert yt.as_fetchable("-IT6N0tVEaA") == "https://www.youtube.com/watch?v=-IT6N0tVEaA"


def test_ordinary_id_also_becomes_a_watch_url():
    assert yt.as_fetchable("dZTTnH7BgyU") == "https://www.youtube.com/watch?v=dZTTnH7BgyU"


def test_a_url_is_left_alone():
    for u in ("https://www.youtube.com/watch?v=abc", "http://youtu.be/abc",
              "https://www.tiktok.com/@someone/video/123"):
        assert yt.as_fetchable(u) == u


def test_non_id_shaped_input_is_left_alone():
    """Anything that is not an 11-character id stays untouched, so a future
    input shape this function does not understand is passed through rather
    than mangled into a wrong URL."""
    assert yt.as_fetchable("not-an-id") == "not-an-id"
    assert yt.as_fetchable("") == ""
