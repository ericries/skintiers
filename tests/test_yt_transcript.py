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
    assert yt_transcript.video_id("https://labmuffin.com/article/").startswith("url-")  # URL -> hash key
    assert yt_transcript.video_id("not a url or id") is None


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


def test_parse_vtt_strips_timing_and_tags():
    vtt = (
        "WEBVTT\n\n"
        "00:00:00.080 --> 00:00:03.439\n"
        "ascorbic acid in water has to be\n\n"
        "00:00:03.440 --> 00:00:06.359\n"
        "<c>formulated at a lower pH.</c>\n"
    )
    assert yt_transcript.parse_vtt(vtt) == "ascorbic acid in water has to be formulated at a lower pH."


def test_parse_vtt_collapses_rolling_duplicates():
    vtt = ("WEBVTT\n\n1\n00:00.000 --> 00:01.000\na low pH\n\n"
           "2\n00:01.000 --> 00:02.000\na low pH\n")   # duplicate cue text
    assert yt_transcript.parse_vtt(vtt) == "a low pH"


def test_video_id_tiktok_and_generic():
    assert yt_transcript.video_id(
        "https://www.tiktok.com/@labmuffinbeautyscience/video/7178297870498483457") == "7178297870498483457"
    # a non-YouTube, non-TikTok URL still caches deterministically via a hash
    h = yt_transcript.video_id("https://example.com/some/video")
    assert h and h.startswith("url-")
    assert yt_transcript.video_id("https://example.com/some/video") == h  # stable
