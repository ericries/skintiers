import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _run(tmp_path, slug):
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    return subprocess.run([sys.executable, str(SK), "lint", slug], env=env,
                          capture_output=True, text=True)


def _write(tmp_path, slug, body, status="draft", grades=True):
    d = tmp_path / "products"
    d.mkdir(parents=True, exist_ok=True)
    grades_block = (
        "grades:\n  - use: As a moisturizer\n    effect: notable\n    evidence: solid\n"
        if grades else ""
    )
    (d / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n"
        f"updated: 2026-07-26\n{grades_block}---\n\n{body}"
    )


def test_lint_clean_exits_0(tmp_path):
    _write(tmp_path, "ok",
           "## Summary\n\nClaim.[^1]\n\n## Sources\n[^1]: T. https://e.com (2026-07-26)\n")
    assert _run(tmp_path, "ok").returncode == 0


def test_lint_product_without_grades_or_rubric_errors(tmp_path):
    # No grades frontmatter and no "## The Rubric" heading -> lint error.
    _write(tmp_path, "norub",
           "Claim.[^1]\n\n## Sources\n[^1]: T. https://e.com\n", grades=False)
    assert _run(tmp_path, "norub").returncode == 1


def test_lint_error_exits_1(tmp_path):
    _write(tmp_path, "bad", "Claim.[^1]\n")
    assert _run(tmp_path, "bad").returncode == 1


def test_lint_warning_exits_2(tmp_path):
    _write(tmp_path, "warn", "No refs.\n\n## Sources\n[^1]: T. https://e.com\n")
    assert _run(tmp_path, "warn").returncode == 2
