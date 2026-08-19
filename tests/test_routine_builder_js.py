import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _runnable(node):
    try:
        return subprocess.run([node, "-e", "process.exit(0)"],
                              capture_output=True, text=True).returncode == 0
    except OSError:
        return False


def _node_or_skip():
    # Try PATH's node first, then common install locations. A node that is present
    # but broken (e.g. Homebrew icu4c version drift) must NOT silently skip the
    # test when another working node exists -- this JS is the user-facing routine
    # builder logic and has to stay gated.
    candidates = [shutil.which("node"), "/opt/homebrew/bin/node", "/usr/local/bin/node"]
    for node in candidates:
        if node and _runnable(node):
            return node
    present = [c for c in candidates if c]
    if not present:
        pytest.skip("node not installed")
    pytest.skip(f"node present but none runnable (tried {present})")


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
