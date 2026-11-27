"""A page may not cite a source cache entry that is not in the cache.

Why it exists. "cached verbatim at research-cache/web/<hash>.md" is the most
verifiable-looking sentence a page can carry, and nothing checked it.

Found 2026-11-27, on two published product pages:
  products/la-roche-posay-toleriane-double-repair-uv-spf-30 -> cc15428ac4f066b2
  products/cyspera-intensive-cysteamine-cream              -> 7dac1ec99fad6085
Neither file exists. Worse, the cache key is sha1(url)[:16], and neither hash is
the key of ANY url on its own page, so neither was ever a real capture of the
source it was offered as evidence for. 160 of the other 162 cache citations on
the site were sound, so this is rare rather than systemic, which is exactly why
a human reading the page would never think to check it.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sklib  # noqa: E402


def test_missing_cache_ref_is_found(tmp_path):
    (tmp_path / "research-cache" / "web").mkdir(parents=True)
    content = "## Sources\n\nCached at research-cache/web/deadbeefdeadbeef.md.\n"
    assert sklib.missing_cache_refs(content, root=tmp_path) == [
        "research-cache/web/deadbeefdeadbeef.md"
    ]


def test_present_cache_ref_is_accepted(tmp_path):
    d = tmp_path / "research-cache" / "web"
    d.mkdir(parents=True)
    (d / "abc123abc123abc1.md").write_text("<!-- cached-source -->\nbody")
    content = "## Sources\n\nCached at research-cache/web/abc123abc123abc1.md.\n"
    assert sklib.missing_cache_refs(content, root=tmp_path) == []


def test_page_citing_no_cache_is_fine(tmp_path):
    assert sklib.missing_cache_refs("## Sources\n\nNo cache here.\n", root=tmp_path) == []


def test_verify_reports_it(tmp_path, monkeypatch):
    (tmp_path / "research-cache" / "web").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    content = (
        "## Summary\n\nx\n\n## The Rubric\n\nx\n\n## What's In It\n\nx\n\n"
        "## The Evidence\n\nx\n\n## Common Marketing Claims\n\nx\n\n"
        "## Where to Buy\n\nx\n\n## See Also\n\nx\n\n"
        "## Sources\n\n[^a]: Brand. https://pubmed.ncbi.nlm.nih.gov/1/ "
        "Cached at research-cache/web/deadbeefdeadbeef.md.\n"
    )
    errors, warnings = sklib.verify_profile(
        {"type": "product", "status": "published"}, content
    )
    assert any("deadbeefdeadbeef" in w for w in warnings), warnings


def test_the_whole_site_cites_no_missing_cache_entry():
    """Regression guard: the two real cases must stay fixed."""
    import frontmatter

    bad = []
    for p in sorted((ROOT / "data").rglob("*.md")):
        post = frontmatter.load(p)
        for ref in sklib.missing_cache_refs(post.content, root=ROOT):
            bad.append(f"{p.relative_to(ROOT)} -> {ref}")
    assert not bad, "pages citing a cache entry that does not exist:\n" + "\n".join(bad)
