import os
import subprocess
import sys
import pathlib
import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _setup(tmp_path, review=None):
    """Create a draft profile; optionally seed data/review-log.yaml with `review` mapping."""
    data = tmp_path / "data"
    (data / "products").mkdir(parents=True)
    path = data / "products" / "serum.md"
    path.write_text("---\nname: Serum\nslug: serum\ntype: product\nstatus: draft\n---\n\nBody.\n")
    if review is not None:
        (data / "review-log.yaml").write_text(review)
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(tmp_path / "_site")}
    return data, path, env


def test_publish_flips_status(tmp_path):
    data, path, env = _setup(tmp_path, review="serum:\n  verdict: publish\n")
    r = subprocess.run([sys.executable, str(SK), "publish", "serum"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    post = frontmatter.load(path)
    assert post["status"] == "published"
    assert post["updated"] is not None            # updated is bumped
    assert post["analyzed"] is not None           # publishing stamps the analysis date


def test_publish_blocked_without_review(tmp_path):
    data, path, env = _setup(tmp_path, review=None)   # no review-log.yaml at all
    r = subprocess.run([sys.executable, str(SK), "publish", "serum"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert "no passing critic review" in r.stderr
    # Status is untouched.
    assert frontmatter.load(path)["status"] == "draft"


def test_publish_succeeds_with_passing_review(tmp_path):
    data, path, env = _setup(tmp_path, review="serum:\n  verdict: publish\n")
    r = subprocess.run([sys.executable, str(SK), "publish", "serum"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert frontmatter.load(path)["status"] == "published"


def test_publish_blocked_when_verdict_not_publish(tmp_path):
    data, path, env = _setup(tmp_path, review="serum:\n  verdict: revise\n")
    r = subprocess.run([sys.executable, str(SK), "publish", "serum"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert frontmatter.load(path)["status"] == "draft"


def test_publish_force_without_review(tmp_path):
    data, path, env = _setup(tmp_path, review=None)
    r = subprocess.run([sys.executable, str(SK), "publish", "serum", "--force"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert frontmatter.load(path)["status"] == "published"
    assert "force-published" in r.stdout
