import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import yt_transcript  # noqa: E402


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
