import sklib


def test_extract_source_urls_from_sources_block():
    content = (
        "Body.[^1]\n\n"
        "## Sources\n"
        "[^1]: Griffiths CEM, et al. https://jamanetwork.com/x (accessed 2026-07-27)\n"
        "[^2]: Weiss JS, et al. https://pubmed.ncbi.nlm.nih.gov/3336176/ (2026)\n"
    )
    assert sklib.extract_source_urls(content) == [
        "https://jamanetwork.com/x",
        "https://pubmed.ncbi.nlm.nih.gov/3336176/",
    ]


def test_extract_source_urls_footnote_without_url_contributes_nothing():
    content = "## Sources\n[^1]: Personal communication, no link.\n[^2]: X. https://nature.com/a\n"
    assert sklib.extract_source_urls(content) == ["https://nature.com/a"]


def test_classify_domain_primary():
    for url in (
        "https://pubmed.ncbi.nlm.nih.gov/3336176/",
        "https://dailymed.nlm.nih.gov/dailymed/x",
        "https://www.accessdata.fda.gov/label",
        "https://dpcj.org/article/5172",
        "https://JAMANETWORK.com/UP",
    ):
        assert sklib.classify_domain(url) == "primary"


def test_classify_domain_aggregator():
    for url in (
        "https://www.ewg.org/skindeep",
        "https://incidecoder.com/ingredients/retinol",
        "https://en.wikipedia.org/wiki/Tretinoin",
        "https://www.reddit.com/r/x",
        "https://www.sephora.com/product",
    ):
        assert sklib.classify_domain(url) == "aggregator"


def test_classify_domain_unknown():
    assert sklib.classify_domain("https://some-brand.com/page") == "unknown"


# --- verify_profile ---

DRAFT_META = {"name": "X", "slug": "x", "type": "product", "status": "draft", "updated": "2026-07-27"}
STUB_META = {"name": "X", "slug": "x", "type": "ingredient", "status": "stub", "updated": "2026-07-27"}

CLEAN_BODY = (
    "## The Rubric\nNotable effect.[^1]\n\n"
    "## The Evidence\nIn one trial, 72.7% vs 55.8%, P<.001 improved.[^1]\n\n"
    "## Manufacturer Claims\nBrand says it reverses aging.\n\n"
    "## Sources\n[^1]: Griffiths CEM, et al. https://pubmed.ncbi.nlm.nih.gov/3336176/ (2026)\n"
)


def test_verify_clean_profile_no_errors_no_warnings():
    errors, warnings = sklib.verify_profile(DRAFT_META, CLEAN_BODY)
    assert errors == [] and warnings == []


def test_verify_aggregator_source_is_error():
    body = CLEAN_BODY.replace(
        "https://pubmed.ncbi.nlm.nih.gov/3336176/", "https://www.ewg.org/skindeep"
    )
    errors, _ = sklib.verify_profile(DRAFT_META, body)
    assert any("aggregator/marketing source cited as evidence" in e and "ewg.org" in e for e in errors)


def test_verify_unknown_source_is_warning():
    body = CLEAN_BODY.replace(
        "https://pubmed.ncbi.nlm.nih.gov/3336176/", "https://some-brand.com/x"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors == []
    assert any("not on primary allowlist" in w and "some-brand.com" in w for w in warnings)


def test_verify_footnote_without_url_is_error():
    body = (
        "## The Rubric\nA.[^1]\n\n## The Evidence\nB.[^1]\n\n"
        "## Manufacturer Claims\nc\n\n## Sources\n[^1]: No link here.\n"
    )
    errors, _ = sklib.verify_profile(DRAFT_META, body)
    assert any("source [^1] has no URL" in e for e in errors)


def test_verify_missing_required_section_is_error():
    body = (
        "## The Rubric\nA.[^1]\n\n## Manufacturer Claims\nc\n\n"
        "## Sources\n[^1]: X. https://nature.com/a\n"
    )
    errors, _ = sklib.verify_profile(DRAFT_META, body)
    assert any("missing required section: The Evidence" in e for e in errors)


def test_verify_missing_quarantine_section_is_warning():
    body = (
        "## The Rubric\nA.[^1]\n\n## The Evidence\nB.[^1]\n\n"
        "## Sources\n[^1]: X. https://nature.com/a\n"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors == []
    assert any("no quarantined marketing-claims section" in w for w in warnings)


def test_verify_accepts_common_marketing_claims_heading():
    body = (
        "## The Rubric\nA.[^1]\n\n## The Evidence\nB.[^1]\n\n"
        "## Common Marketing Claims\nc\n\n## Sources\n[^1]: X. https://nature.com/a\n"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors == [] and warnings == []


def test_verify_uncited_statistic_is_warning():
    body = (
        "## The Rubric\nA.[^1]\n\n"
        "## The Evidence\nAn uncited 42% reduction was seen in patients.\n\n"
        "## Manufacturer Claims\nc\n\n## Sources\n[^1]: X. https://nature.com/a\n"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors == []
    assert any("uncited statistic in paragraph" in w for w in warnings)


def test_verify_uncited_statistic_outside_evidence_section_not_flagged():
    # An uncited stat under ## Uses (not an evidence-bearing section) is EXEMPT.
    body = (
        "## The Rubric\nA.[^1]\n\n## The Evidence\nB.[^1]\n\n"
        "## Uses\nComparable to metronidazole 0.75% for rosacea.\n\n"
        "## Manufacturer Claims\nc\n\n## Sources\n[^1]: X. https://nature.com/a\n"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors == [] and warnings == []


def test_verify_uncited_statistic_in_evidence_sections_flagged():
    # Each evidence-bearing heading (Rubric / Evidence / What We Actually Know) still warns.
    for heading in ("## The Rubric", "## The Evidence", "## What We Actually Know"):
        body = (
            "## The Rubric\nA.[^1]\n\n## The Evidence\nB.[^1]\n\n"
            f"{heading}\nAn uncited 42% reduction was seen.\n\n"
            "## Manufacturer Claims\nc\n\n## Sources\n[^1]: X. https://nature.com/a\n"
        )
        errors, warnings = sklib.verify_profile(DRAFT_META, body)
        assert errors == [], heading
        assert any("uncited statistic in paragraph" in w for w in warnings), heading


def test_verify_statistic_in_sources_not_flagged():
    body = (
        "## The Rubric\nA.[^1]\n\n## The Evidence\nB.[^1]\n\n"
        "## Manufacturer Claims\nc\n\n"
        "## Sources\n[^1]: Trial with 72.7% vs 55.8%. https://nature.com/a\n"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors == [] and warnings == []


def test_verify_stub_only_checks_sources_and_returns():
    # Stub missing all sections + missing quarantine, but has a good URL: clean.
    body = "Just a placeholder line.\n\n## Sources\n[^1]: X. https://nature.com/a\n"
    errors, warnings = sklib.verify_profile(STUB_META, body)
    assert errors == [] and warnings == []


def test_verify_stub_still_flags_aggregator_source():
    body = "Placeholder.\n\n## Sources\n[^1]: X. https://www.ewg.org/x\n"
    errors, _ = sklib.verify_profile(STUB_META, body)
    assert any("aggregator/marketing source cited as evidence" in e for e in errors)


# --- verify_profile: condition / goal (lenient structure) ---

CONDITION_META = {"name": "Acne", "slug": "acne", "type": "condition", "status": "draft", "updated": "2026-07-27"}


def test_verify_condition_missing_sources_is_error():
    body = "## The Evidence\nSome evidence.[^1]\n"
    errors, _ = sklib.verify_profile(CONDITION_META, body)
    assert any("missing required section: Sources" in e for e in errors)


def test_verify_condition_with_sources_but_no_evidence_is_warning():
    body = "Overview.[^1]\n\n## Sources\n[^1]: X. https://nature.com/a\n"
    errors, warnings = sklib.verify_profile(CONDITION_META, body)
    assert errors == []
    assert any("The Evidence" in w for w in warnings)


def test_verify_condition_clean_profile_no_errors_no_warnings():
    body = (
        "## The Evidence\nEvidence line.[^1]\n\n"
        "## Sources\n[^1]: X. https://nature.com/a\n"
    )
    errors, warnings = sklib.verify_profile(CONDITION_META, body)
    assert errors == [] and warnings == []


# --- verify_profile: brand (gated portfolio roll-up, Sources-only structure) ---

BRAND_META = {"name": "CeraVe", "slug": "cerave", "type": "brand",
              "status": "draft", "updated": "2026-07-28"}


def test_verify_brand_requires_only_sources():
    # A brand page is a cited portfolio roll-up: no Rubric/Evidence, and no
    # quarantine warning (marketing claims are handled in prose, not required).
    body = (
        "CeraVe is a US ceramide-focused skincare brand.[^1]\n\n"
        "## Sources\n[^1]: Valeant 8-K. "
        "https://www.sec.gov/Archives/edgar/data/885590/x.htm\n"
    )
    errors, warnings = sklib.verify_profile(BRAND_META, body)
    assert errors == []
    assert not any("required section" in w for w in warnings)
    assert not any("quarantined marketing-claims" in w for w in warnings)


def test_verify_brand_missing_sources_is_error():
    body = "CeraVe is a brand.[^1]\n"
    errors, _ = sklib.verify_profile(BRAND_META, body)
    assert any("missing required section: Sources" in e for e in errors)


def test_verify_sec_gov_is_primary_not_warned():
    body = (
        "Claim.[^1]\n\n## Sources\n[^1]: X. "
        "https://www.sec.gov/Archives/edgar/data/885590/x.htm\n"
    )
    errors, warnings = sklib.verify_profile(BRAND_META, body)
    assert errors == []
    assert not any("not on primary allowlist" in w for w in warnings)


def test_verify_errors_ordered_before_warnings():
    body = (
        "## The Rubric\nA.[^1]\n\n"
        "## The Evidence\nUncited 42% here.\n\n"
        "## Sources\n[^1]: X. https://www.ewg.org/x\n"
    )
    errors, warnings = sklib.verify_profile(DRAFT_META, body)
    assert errors and warnings  # both present, returned separately
