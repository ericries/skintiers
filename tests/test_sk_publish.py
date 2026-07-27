import os
import subprocess
import sys
import pathlib
import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def test_publish_flips_status(tmp_path):
    data = tmp_path / "data"
    (data / "products").mkdir(parents=True)
    path = data / "products" / "serum.md"
    path.write_text("---\nname: Serum\nslug: serum\ntype: product\nstatus: draft\n---\n\nBody.\n")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(tmp_path / "_site")}
    r = subprocess.run([sys.executable, str(SK), "publish", "serum"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    post = frontmatter.load(path)
    assert post["status"] == "published"
    assert post["updated"] is not None            # updated is bumped
    assert post["analyzed"] is not None           # publishing stamps the analysis date
