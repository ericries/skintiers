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
