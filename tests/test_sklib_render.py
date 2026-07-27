import sklib


def test_render_markdown_bold_and_table():
    html = sklib.render_markdown("**hi**\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    assert "<strong>hi</strong>" in html
    assert "<table>" in html


def test_linkify_resolvable():
    out = sklib.linkify_xrefs("See [[niacinamide]].", {"niacinamide"},
                              {"niacinamide": "Niacinamide"})
    assert "[Niacinamide](niacinamide.html)" in out


def test_linkify_with_label():
    out = sklib.linkify_xrefs("Try [[niacinamide|vitamin B3]].", {"niacinamide"},
                              {"niacinamide": "Niacinamide"})
    assert "[vitamin B3](niacinamide.html)" in out


def test_linkify_broken_is_plain_text():
    out = sklib.linkify_xrefs("See [[unobtainium]].", set(), {})
    assert "unobtainium" in out
    assert "unobtainium.html" not in out
    assert "[[" not in out
