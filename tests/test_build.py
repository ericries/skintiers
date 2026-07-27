import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _write(dirpath, slug, status, typ, body="Body.\n"):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: {typ}\nstatus: {status}\n"
        f"updated: 2026-07-26\nanalyzed: 2026-07-26\n---\n\n{body}"
    )


def test_build_renders_all_statuses_with_badge_and_xref(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    _write(data / "products", "serum", "published", "product",
           "Contains [[niacinamide]] and [[unobtainium]].\n")
    _write(data / "products", "secret", "draft", "product")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (out / "serum.html").exists()
    assert (out / "niacinamide.html").exists()
    assert (out / "secret.html").exists()              # draft renders as a link target
    assert (out / "index.html").exists()
    assert "draft" in (out / "secret.html").read_text().lower()   # status badge shown
    serum_html = (out / "serum.html").read_text()
    assert 'href="niacinamide.html"' in serum_html   # resolvable xref linked
    assert "unobtainium.html" not in serum_html        # broken xref is plain text
