import sklib


def test_em_dash_flagged():
    warnings = sklib.check_style("This is a sentence — with an em dash.")
    assert any("em dash" in w for w in warnings)


def test_en_dash_flagged():
    warnings = sklib.check_style("This is a sentence – with an en dash.")
    assert any("en dash" in w for w in warnings)


def test_ascii_hyphen_not_flagged():
    warnings = sklib.check_style("A well-known anti-aging ingredient at 0.025-0.1%.")
    assert warnings == []


def test_curly_quote_flagged():
    for q in ("‘", "’", "“", "”"):
        warnings = sklib.check_style(f"A {q}curly{q} quote here.")
        assert any("curly quote" in w for w in warnings)


def test_ai_ese_phrase_flagged():
    warnings = sklib.check_style("Let us delve into this topic.")
    assert any("AI-ese phrase" in w and "delve" in w for w in warnings)


def test_ai_ese_phrase_case_insensitive():
    warnings = sklib.check_style("This is a Testament To great work.")
    assert any("testament to" in w.lower() for w in warnings)


def test_multiword_phrase_flagged():
    warnings = sklib.check_style("It plays a crucial role in barrier repair.")
    assert any("plays a crucial role" in w for w in warnings)


def test_word_boundary_no_false_positive():
    # "harness" is AI-ese but "harnessing"? boasts vs boastsxyz; ensure substrings inside
    # unrelated words don't trigger. "delve" should not match "twelve".
    warnings = sklib.check_style("There are twelve steps and no underscore markup here except this.")
    # "twelve" must not trigger "delve"
    assert not any("'delve'" in w for w in warnings)
    # but "underscore" should
    assert any("underscore" in w for w in warnings)


def test_clean_ascii_sentence_no_warnings():
    content = (
        "CeraVe Moisturizing Cream contains three ceramides. A randomized trial "
        "found it improved a barrier measure but did not reduce eczema severity "
        "more than a vehicle.\n\nThe cream costs about 15 dollars for 16 ounces."
    )
    assert sklib.check_style(content) == []


def test_frontmatter_excluded():
    # Frontmatter is not part of content passed in; but ensure a leading --- block,
    # were it present, is excluded. check_style operates on body content already.
    content = "Plain body with no tells."
    assert sklib.check_style(content) == []


def test_sources_section_excluded():
    content = (
        "This body is clean ASCII with no tells.\n\n"
        "## Sources\n"
        "[^1]: Smith J — a study title with an em dash. https://pubmed.ncbi.nlm.nih.gov/1/\n"
    )
    warnings = sklib.check_style(content)
    assert warnings == []


def test_em_dash_before_sources_still_flagged():
    content = (
        "Body has an em dash — right here.\n\n"
        "## Sources\n[^1]: X. https://nature.com/a\n"
    )
    warnings = sklib.check_style(content)
    assert any("em dash" in w for w in warnings)


def test_dedupe_repeated_term_into_one_line():
    content = "delve delve delve into the details."
    warnings = sklib.check_style(content)
    delve_lines = [w for w in warnings if "'delve'" in w]
    assert len(delve_lines) == 1
