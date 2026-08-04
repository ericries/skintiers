import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _node_or_skip():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    probe = subprocess.run([node, "-e", "process.exit(0)"], capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip(f"node present but not runnable: {probe.stderr.strip()[:120]}")
    return node


def test_js_codec_matches_shared_vectors():
    node = _node_or_skip()
    r = subprocess.run([node, str(ROOT / "tests" / "js" / "codec_parity.test.js")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_dashboard_fixture_matches_python_routine_summary():
    import json
    case = json.loads((ROOT / "tests" / "fixtures" / "routine_dashboard_case.json").read_text())
    exp = case["expected"]
    # Cross-check the fixture's expectations against the Python rules directly.
    segs = [case["catalog"]["p"][c]["g"] for c in ["0", "1", "2", "3"]]
    mean = sum(segs) / len(segs)
    label = next(w for cut, w in ((3.0, "Strong"), (2.25, "Solid"), (1.5, "Moderate"), (0, "Light")) if mean >= cut)
    assert label == exp["strength"]
    assert exp["ingredients"][0] == {"slug": "niacinamide", "name": "Niacinamide", "count": 2}
    assert exp["filters"]["coverage"] == "UVB + UVA"
    assert exp["absent"] == ["Retinoid", "Exfoliant"]
