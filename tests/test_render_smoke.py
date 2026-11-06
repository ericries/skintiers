"""Render-level smoke test: build the whole site from the REAL data and assert the
composed HTML has none of the known-bad render patterns that source-level lint
(sk lint/verify/style) cannot see. Every render bug this project has shipped lived
in the gap between markdown source and rendered output (unresolved [[xref]] showing
as raw slug text, doubled-subject verdicts like "Adapalene is adapalene is"). Those
are invisible to the source gates; this test is the render gate.

The build is isolated in a copy of data/ so it cannot mutate the repo (build.py
writes routine-codes.yaml back into its data dir).
"""
import glob
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

# routine.html and 404.html inline the routine catalog JSON, whose `notable`
# array-of-arrays legitimately contains "[[" — they are app shells, not profile
# content, so they are exempt from the xref-survival scan.
_SHELLS = {"routine.html", "404.html"}


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("render")
    data = tmp / "data"
    shutil.copytree(ROOT / "data", data)
    out = tmp / "_site"
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


def _content_pages(out):
    for f in glob.glob(str(out / "*.html")):
        if os.path.basename(f) not in _SHELLS:
            yield f


# An intended xref is `[[slug]]`/`[[slug|alias]]`, and page slugs are kebab-case
# starting with a lowercase letter. linkify_xrefs turns even an UNRESOLVED such
# xref into plain text (never raw brackets), so a surviving `[[<letter>` in HTML
# means a field was not linkified at all - the real bug. `[[` followed by `(` or
# a digit is legitimate IUPAC chemical nomenclature (e.g. `2-[[(2S)-...`), not an
# xref, so it is not flagged.
_UNRESOLVED_XREF = re.compile(r"\[\[[a-z]")


def test_no_unresolved_xref_survives_into_html(rendered_site):
    offenders = []
    for f in _content_pages(rendered_site):
        html = pathlib.Path(f).read_text()
        m = _UNRESOLVED_XREF.search(html)
        if m:
            i = m.start()
            offenders.append(f"{os.path.basename(f)}: ...{html[max(0, i-40):i+40]}...")
    assert not offenders, (
        "unresolved [[xref]] rendered as raw text (should be a link or |alias):\n"
        + "\n".join(offenders[:10])
    )


_EMPTY_ANCHOR = re.compile(r"<a [^>]*href=\"[^\"]*\"[^>]*>\\s*</a>")


def test_no_empty_anchor_survives_into_html(rendered_site):
    """A link with no text is invisible, unreachable by keyboard and silent to a
    screen reader. 84 video cards carried a blank `creator` beside a valid
    `creator_slug`, so three templates rendered `<a href="...."></a>`: 226 of
    them across the site, while each card's thesis still named the creator so
    the pages looked fine. The byline now falls back to the person page or the
    roster, and omits the anchor when there is genuinely no name."""
    offenders = []
    for f in _content_pages(rendered_site):
        html = pathlib.Path(f).read_text()
        m = _EMPTY_ANCHOR.search(html)
        if m:
            i = m.start()
            offenders.append(f"{os.path.basename(f)}: ...{html[max(0, i-70):i+40]}...")
    assert not offenders, (
        "anchor rendered with no link text:\n" + "\n".join(offenders[:10])
    )


def test_no_doubled_subject_in_html(rendered_site):
    # The evidence-box template composes "{name} is {note}"; a note that restates
    # the subject produced "Adapalene is adapalene is ...". Catch that class.
    pat = re.compile(r"\b(\w+) is \1 is\b", re.I)
    offenders = []
    for f in _content_pages(rendered_site):
        for m in pat.finditer(pathlib.Path(f).read_text()):
            offenders.append(f"{os.path.basename(f)}: '{m.group(0)}'")
    assert not offenders, "doubled-subject verdict rendered:\n" + "\n".join(offenders[:10])
