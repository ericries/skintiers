import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"

CLEAN = (
    "## The Rubric\nNotable.[^1]\n\n"
    "## The Evidence\nIn one trial, 72.7% vs 55.8%, P<.001.[^1]\n\n"
    "## Manufacturer Claims\nBrand hype.\n\n"
    "## Sources\n[^1]: X. https://pubmed.ncbi.nlm.nih.gov/1/ (2026)\n"
)


def _run(tmp_path, slug):
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    return subprocess.run([sys.executable, str(SK), "verify", slug], env=env,
                          capture_output=True, text=True)


def _write(tmp_path, slug, body, status="draft"):
    d = tmp_path / "products"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n"
        f"updated: 2026-07-27\n---\n\n{body}"
    )


def test_verify_clean_exits_0(tmp_path):
    _write(tmp_path, "ok", CLEAN)
    r = _run(tmp_path, "ok")
    assert r.returncode == 0
    assert "verified clean" in r.stdout


def test_verify_aggregator_exits_1(tmp_path):
    body = CLEAN.replace("https://pubmed.ncbi.nlm.nih.gov/1/", "https://www.ewg.org/x")
    _write(tmp_path, "agg", body)
    r = _run(tmp_path, "agg")
    assert r.returncode == 1
    assert "ERROR:" in r.stdout


def test_verify_uncited_stat_only_exits_2(tmp_path):
    body = (
        "## The Rubric\nNotable.[^1]\n\n"
        "## The Evidence\nAn uncited 42% reduction was seen.\n\n"
        "## Manufacturer Claims\nBrand hype.\n\n"
        "## Sources\n[^1]: X. https://pubmed.ncbi.nlm.nih.gov/1/ (2026)\n"
    )
    _write(tmp_path, "warn", body)
    r = _run(tmp_path, "warn")
    assert r.returncode == 2
    assert "WARN:" in r.stdout


def test_verify_stub_exits_0(tmp_path):
    _write(tmp_path, "stubby", "Placeholder.\n\n## Sources\n[^1]: X. https://nature.com/a\n",
           status="stub")
    r = _run(tmp_path, "stubby")
    assert r.returncode == 0


def test_verify_not_found_exits_1(tmp_path):
    r = _run(tmp_path, "nope")
    assert r.returncode == 1
    assert r.stderr
