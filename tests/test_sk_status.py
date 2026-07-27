import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _write(dirpath, slug, status):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n---\n\nBody.\n"
    )


def test_status_counts(tmp_path):
    _write(tmp_path / "products", "a", "published")
    _write(tmp_path / "products", "b", "published")
    _write(tmp_path / "products", "c", "draft")
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    out = subprocess.run([sys.executable, str(SK), "status"], env=env,
                         capture_output=True, text=True)
    assert out.returncode == 0
    assert "published: 2" in out.stdout
    assert "draft: 1" in out.stdout
