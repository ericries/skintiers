import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import yt_transcript  # noqa: E402


def test_video_id_extraction():
    assert yt_transcript.video_id("https://www.youtube.com/watch?v=U68MTXuOG9k") == "U68MTXuOG9k"
    assert yt_transcript.video_id("https://www.youtube.com/shorts/K5zwloQza9M") == "K5zwloQza9M"
    assert yt_transcript.video_id("https://youtu.be/K5zwloQza9M") == "K5zwloQza9M"
    assert yt_transcript.video_id("U68MTXuOG9k") == "U68MTXuOG9k"          # bare id
    assert yt_transcript.video_id("https://labmuffin.com/article/") is None


def test_fetch_transcript_serves_from_cache_without_network(tmp_path, monkeypatch):
    # A cached transcript is returned verbatim and never re-fetched (yt-dlp is not called).
    cache = tmp_path / "transcripts"
    cache.mkdir()
    monkeypatch.setattr(yt_transcript, "TRANSCRIPT_CACHE", cache)
    vid = "ABCDEFGHIJK"
    (cache / f"{vid}.json").write_text(json.dumps({
        "id": vid, "title": "T", "channel": "C", "uploader": "C", "url": "u",
        "duration": "1", "has_transcript": True, "source": "manual", "text": "cached text"}))

    def _boom(*a, **k):
        raise AssertionError("network fetch should not run on a cache hit")
    monkeypatch.setattr(yt_transcript, "video_meta", _boom)

    res = yt_transcript.fetch_transcript(f"https://www.youtube.com/watch?v={vid}")
    assert res["cached"] is True
    assert res["text"] == "cached text"


def test_parse_json3_joins_segments_and_skips_windows():
    data = {"events": [
        {"tStartMs": 0, "segs": [{"utf8": "Vitamin C"}, {"utf8": " serums"}]},
        {"tStartMs": 900, "wWinId": 1},                      # window event, no segs
        {"tStartMs": 1000, "segs": [{"utf8": "oxidise over time."}]},
    ]}
    assert yt_transcript.parse_json3(data) == "Vitamin C serums oxidise over time."


def test_parse_json3_collapses_rolling_duplicates_and_whitespace():
    # Auto-captions repeat the same line across cues and pad with newlines.
    data = {"events": [
        {"segs": [{"utf8": "a low pH\n"}]},
        {"segs": [{"utf8": "a low pH"}]},                    # duplicate of previous line
        {"segs": [{"utf8": "  does not\nmean it works "}]},
    ]}
    assert yt_transcript.parse_json3(data) == "a low pH does not mean it works"


def test_parse_json3_empty():
    assert yt_transcript.parse_json3({}) == ""
    assert yt_transcript.parse_json3({"events": [{"wWinId": 1}]}) == ""
