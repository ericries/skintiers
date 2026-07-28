import sklib

GRADES = [{"use": "As a moisturizer", "effect": "notable", "evidence": "solid"}]
GOOD_META = {"name": "X", "slug": "x", "type": "product", "status": "draft",
             "updated": "2026-07-26", "grades": GRADES}


def test_clean_profile_passes():
    content = "Claim.[^1]\n\n## Sources\n[^1]: Title. https://example.com (2026-07-26)\n"
    errors, warnings = sklib.check_profile(GOOD_META, content)
    assert errors == [] and warnings == []


def test_product_with_grades_and_no_rubric_is_clean():
    # grades in frontmatter, no "## The Rubric" body heading -> clean.
    content = "Intro.[^1]\n\n## The Evidence\nText.[^1]\n\n## Sources\n[^1]: T. https://example.com\n"
    errors, warnings = sklib.check_profile(GOOD_META, content)
    assert errors == [] and warnings == []


def test_product_with_rubric_heading_and_no_grades_is_clean():
    meta = {k: v for k, v in GOOD_META.items() if k != "grades"}
    content = "Intro.[^1]\n\n## The Rubric\nGrades here.\n\n## Sources\n[^1]: T. https://example.com\n"
    errors, warnings = sklib.check_profile(meta, content)
    assert errors == [] and warnings == []


def test_product_without_grades_or_rubric_is_error():
    meta = {k: v for k, v in GOOD_META.items() if k != "grades"}
    content = "Intro.[^1]\n\n## Sources\n[^1]: T. https://example.com\n"
    errors, _ = sklib.check_profile(meta, content)
    assert any("grades" in e.lower() or "rubric" in e.lower() for e in errors)


def test_non_stub_missing_sources_is_error():
    content = "Claim.[^1]\n\n## The Rubric\nGrades.\n"
    meta = {k: v for k, v in GOOD_META.items() if k != "grades"}
    errors, _ = sklib.check_profile(meta, content)
    assert any("sources" in e.lower() for e in errors)


def test_stub_with_no_footnotes_is_clean():
    meta = {"name": "X", "slug": "x", "type": "ingredient", "status": "stub", "updated": "2026-07-26"}
    errors, warnings = sklib.check_profile(meta, "One link placeholder.\n")
    assert errors == [] and warnings == []


def test_missing_updated_is_error():
    meta = {"name": "X", "slug": "x", "type": "product", "status": "draft"}
    errors, _ = sklib.check_profile(meta, "Body.\n")
    assert any("updated" in e for e in errors)


def test_missing_frontmatter_field_is_error():
    errors, _ = sklib.check_profile({"name": "X", "slug": "x", "type": "product"}, "Body.\n")
    assert any("status" in e for e in errors)


def test_bad_type_is_error():
    meta = {**GOOD_META, "type": "banana"}
    errors, _ = sklib.check_profile(meta, "Body.\n")
    assert any("type" in e for e in errors)


def test_condition_type_passes_frontmatter_check():
    meta = {**GOOD_META, "type": "condition"}
    content = "Body.[^1]\n\n## Sources\n[^1]: Title. https://example.com (2026-07-26)\n"
    errors, warnings = sklib.check_profile(meta, content)
    assert errors == [] and warnings == []


def test_brand_type_passes_frontmatter_check():
    meta = {"name": "CeraVe", "slug": "cerave", "type": "brand",
            "status": "draft", "updated": "2026-07-28"}
    content = "CeraVe is a brand.[^1]\n\n## Sources\n[^1]: T. https://example.com\n"
    errors, warnings = sklib.check_profile(meta, content)
    assert errors == [] and warnings == []


def test_footnote_reference_without_definition_is_error():
    errors, _ = sklib.check_profile(GOOD_META, "Claim.[^1]\n")
    assert any("[^1]" in e for e in errors)


def test_orphan_definition_is_warning():
    content = "No refs.\n\n## Sources\n[^1]: Title. https://example.com\n"
    errors, warnings = sklib.check_profile(GOOD_META, content)
    assert errors == []
    assert any("[^1]" in w for w in warnings)


def test_duplicate_definition_is_error():
    content = "A.[^1]\n\n## Sources\n[^1]: One. https://a.com\n[^1]: Two. https://b.com\n"
    errors, _ = sklib.check_profile(GOOD_META, content)
    assert any("duplicate" in e.lower() for e in errors)
