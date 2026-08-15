"""Phase E: the 'For Agents' page and the installable skill bundle.

These tests run a real build into a tmp dir and assert the bundle is produced and stays
schema-consistent with the live build - every endpoint the skill advertises must exist as
a build output, the zip must be produced, and the strength algorithm must stay single-sourced.
"""
import json
import os
import subprocess
import sys
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _write(dirpath, slug, status, typ, front="", body="Body.\n"):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: {typ}\nstatus: {status}\n"
        f"updated: 2026-07-26\nanalyzed: 2026-07-26\n{front}---\n\n{body}"
    )


def _build(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    # A minimal but realistic universe so the JSON endpoints are non-trivially populated.
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    _write(data / "products", "serum", "published", "product",
           front="category: Serums\nkey_actives:\n- niacinamide\n"
                 "grades:\n- effect: modest\n  evidence: solid\n  use: Acne (health)\n",
           body="Contains [[niacinamide]].\n")
    _write(data / "conditions", "acne", "published", "condition")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


def test_for_agents_page_built_and_linked_in_nav(tmp_path):
    out = _build(tmp_path)
    page = out / "for-agents.html"
    assert page.exists()
    html = page.read_text()
    assert "Zero-install" in html and "install-the-skill" in html.lower()
    assert "skintiers-skill.zip" in html
    # Launched: the page is wired into the shared nav and footer (base.html), so it
    # appears on every rendered page including the homepage.
    index = (out / "index.html").read_text()
    assert "for-agents.html" in index


def test_skill_bundle_dir_and_zip_produced(tmp_path):
    out = _build(tmp_path)
    skill_dir = out / "skill"
    assert (skill_dir / "SKILL.md").exists()
    assert (skill_dir / "routine-strength-spec.md").exists()
    assert (skill_dir / "endpoints.json").exists()
    zip_path = out / "skintiers-skill.zip"
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    assert "skintiers/SKILL.md" in names
    assert "skintiers/routine-strength-spec.md" in names
    assert "skintiers/endpoints.json" in names


def test_advertised_endpoints_all_exist_as_build_outputs(tmp_path):
    out = _build(tmp_path)
    manifest = json.loads((out / "skill" / "endpoints.json").read_text())
    assert manifest["endpoints"], "endpoint manifest is empty"
    for e in manifest["endpoints"]:
        assert (out / e["path"]).exists(), f"advertised endpoint missing: {e['path']}"
    # Endpoints named in SKILL.md prose must also be real build outputs.
    skill_md = (out / "skill" / "SKILL.md").read_text()
    for name in ("routine-catalog.json", "routines.json", "feed.json", "feed.xml"):
        assert name in skill_md
        assert (out / name).exists()


def test_strength_algorithm_single_sourced(tmp_path):
    # The spec ships inside the bundle verbatim from docs/, and both implementations point
    # at it, so the browser/build/skill cannot silently drift.
    out = _build(tmp_path)
    canonical = (ROOT / "docs" / "routine-strength-spec.md").read_text()
    shipped = (out / "skill" / "routine-strength-spec.md").read_text()
    assert shipped == canonical
    # The three implementers reference the canonical spec.
    assert "routine-strength-spec.md" in (ROOT / "assets" / "routine-builder.js").read_text()
    assert "routine-strength-spec.md" in (ROOT / "skill" / "SKILL.md").read_text()
    # The strength cutoffs match across the spec and the JS builder.
    js = (ROOT / "assets" / "routine-builder.js").read_text()
    assert "2.25" in js and "2.25" in canonical
    assert "1.5" in js and "1.5" in canonical
