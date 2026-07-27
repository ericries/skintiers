import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _run(tmp_path, slug):
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    return subprocess.run([sys.executable, str(SK), "style", slug], env=env,
                          capture_output=True, text=True)


def _write(tmp_path, slug, body, status="draft"):
    d = tmp_path / "products"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n"
        f"updated: 2026-07-27\n---\n\n{body}"
    )


CLEAN = (
    "CeraVe Moisturizing Cream contains three ceramides. A trial found it "
    "improved a barrier measure.\n\n## Sources\n[^1]: X. https://nature.com/a\n"
)

DIRTY = (
    "Let us delve into this cream, which boasts a seamless barrier — truly.\n\n"
    "## Sources\n[^1]: X. https://nature.com/a\n"
)


def test_style_clean_exits_0(tmp_path):
    _write(tmp_path, "ok", CLEAN)
    r = _run(tmp_path, "ok")
    assert r.returncode == 0
    assert "clean style" in r.stdout


def test_style_dirty_exits_2(tmp_path):
    _write(tmp_path, "dirty", DIRTY)
    r = _run(tmp_path, "dirty")
    assert r.returncode == 2
    assert "WARN:" in r.stdout


def test_style_not_found_exits_1(tmp_path):
    r = _run(tmp_path, "nope")
    assert r.returncode == 1
    assert r.stderr
