"""Render-level smoke test: build the REAL site and assert the composed HTML has no
known-bad patterns. Our other gates (sk lint/verify/style) validate the markdown
SOURCE; this is the only gate that looks at what the reader actually sees. Every bug
in the 2026-08-10 session lived here (evidence-box subject-doubling, empty verdicts,
unresolved xrefs, an unreplaced chart marker). CI runs pytest before build+deploy, so
a failure here blocks the broken version from going live.
"""
import os
import re
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# An actual unrendered xref: [[slug]] or [[slug|alias]] that survived to HTML. The
# renderer always turns these into <a> or plain label text, so any survivor is a bug.
_UNRENDERED_XREF = re.compile(r"\[\[[a-z0-9][a-z0-9 |#-]*\]\]")
# The evidence box composes level 01 as "{Name} is {note}"; a note that restated the
# subject doubled it ("Adapalene is adapalene is ..."). Detect a word repeated as
# "Word is word is" inside a verdict.
_DOUBLED_SUBJECT = re.compile(r"\b(\w+) is \1 is\b", re.IGNORECASE)
_EVL_VERDICT = re.compile(r'<p class="evl-verdict">(.*?)</p>', re.DOTALL)


def _build_real_site(tmp_path):
    out = tmp_path / "_site"
    env = {**os.environ, "SK_OUTPUT": str(out)}  # SK_DATA defaults to the real data/
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


def test_rendered_site_has_no_render_defects(tmp_path):
    out = _build_real_site(tmp_path)
    pages = list(out.glob("*.html"))
    assert pages, "build produced no pages"

    unrendered_xrefs, doubled, empty_verdicts, stray_markers = [], [], [], []
    for p in pages:
        html = p.read_text()
        if _UNRENDERED_XREF.search(html):
            unrendered_xrefs.append(f"{p.name}: {_UNRENDERED_XREF.search(html).group(0)}")
        if "<!--uv-filter-spectrum-->" in html:
            stray_markers.append(p.name)
        for verdict in _EVL_VERDICT.findall(html):
            inner = verdict.strip()
            if inner in (".", ""):
                empty_verdicts.append(p.name)
            m = _DOUBLED_SUBJECT.search(re.sub(r"<[^>]+>", "", verdict))
            if m:
                doubled.append(f"{p.name}: {m.group(0)}")

    problems = []
    if unrendered_xrefs:
        problems.append(f"unrendered xref markup survived to HTML: {unrendered_xrefs[:5]}")
    if doubled:
        problems.append(f"evidence-box subject doubled ('Word is word is'): {doubled[:5]}")
    if empty_verdicts:
        problems.append(f"empty evidence-box verdict (bare '.'): {empty_verdicts[:5]}")
    if stray_markers:
        problems.append(f"unreplaced UV-filter chart marker: {stray_markers[:5]}")
    assert not problems, "render defects found:\n" + "\n".join(problems)
