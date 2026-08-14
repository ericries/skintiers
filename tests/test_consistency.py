"""Cross-page consistency gate (Phase C). Two jobs:

1. `test_no_cross_page_consistency_errors` scans the REAL data tree and fails the
   build on any consistency ERROR - a key_active/tier-list slug that points at no
   published page, an images: file that isn't self-hosted, a product mis-tagged vs
   its own name (the-ordinary-lactic-acid class), or a sunscreen naming an uncharted
   UV filter as its own active. CI runs pytest before deploy, so an inconsistency
   blocks the broken version from going live. Learning #5: cross-page consistency
   needs automation, not luck. Grade-consistency divergences (product grade vs. an
   ingredient page's own rubric grade) are ADVISORY - printed as warnings, never
   failing this test - because a product's use-specific grade legitimately diverging
   from the ingredient page's general one is normal (see check_grade_consistency).
2. Unit tests protect the check functions themselves (fire on bad input, silent on
   good), so a future refactor can't quietly neuter the gate.
"""
import sklib


# --- The build-blocking gate over real data ------------------------------

def test_no_cross_page_consistency_errors(capsys):
    errors, warnings = sklib.consistency_issues()
    # Warnings (name mentions an active that may be secondary) are advisory - print
    # them so they show in CI logs, but do not fail the build on them.
    if warnings:
        with capsys.disabled():
            print("\nconsistency warnings (advisory):")
            for slug, w in warnings:
                print(f"  [{slug}] {w}")
    assert errors == [], "cross-page consistency errors (these block deploy):\n" + \
        "\n".join(f"  [{slug}] {e}" for slug, e in errors)


# --- Unit tests: each check fires on bad input and stays silent on good ---

ING = {"lactic-acid", "glycolic-acid", "hyaluronic-acid", "niacinamide", "avobenzone"}
PUB = ING | {"exfoliating-acids-by-strength", "melasma"}


def test_key_actives_must_be_published_ingredient_pages():
    assert sklib.check_key_actives({"key_actives": ["lactic-acid"]}, ING) == []
    bad = sklib.check_key_actives({"key_actives": ["ketoconazole", "niacinamide"]}, ING)
    assert len(bad) == 1 and "ketoconazole" in bad[0]


def test_name_active_substitution_is_an_error():
    # named 'Lactic Acid' but key_actives lists glycolic instead -> ERROR
    errs, warns = sklib.check_name_actives(
        {"type": "product", "name": "The Ordinary Lactic Acid 10% + HA",
         "key_actives": ["glycolic-acid", "hyaluronic-acid"]}, ING)
    assert warns == [] and len(errs) == 1 and "lactic-acid" in errs[0]


def test_name_active_plain_absence_is_a_warning_not_error():
    # a sunscreen 'with niacinamide' whose actives are UV filters -> WARN only
    errs, warns = sklib.check_name_actives(
        {"type": "product", "name": "Brand SPF50 with Niacinamide",
         "key_actives": ["avobenzone"]}, ING)
    assert errs == [] and len(warns) == 1 and "niacinamide" in warns[0]


def test_name_active_correct_tag_is_silent():
    errs, warns = sklib.check_name_actives(
        {"type": "product", "name": "The Ordinary Lactic Acid 10% + HA",
         "key_actives": ["lactic-acid", "hyaluronic-acid"]}, ING)
    assert errs == [] and warns == []


def test_non_product_name_check_is_skipped():
    errs, warns = sklib.check_name_actives(
        {"type": "ingredient", "name": "Lactic acid", "key_actives": []}, ING)
    assert errs == [] and warns == []


def test_missing_image_file_is_an_error(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "real.jpg").write_bytes(b"x")
    assert sklib.check_images_exist({"images": [{"file": "real.jpg"}]}, tmp_path) == []
    bad = sklib.check_images_exist({"images": [{"file": "ghost.jpg"}]}, tmp_path)
    assert len(bad) == 1 and "ghost.jpg" in bad[0]
    # a full-URL image is used as-is, nothing to self-host, so no error
    assert sklib.check_images_exist(
        {"images": [{"file": "https://cdn.example/x.jpg"}]}, tmp_path) == []


def test_tier_list_slug_must_be_published():
    ok = sklib.check_tier_list_slugs(
        {"tier_list": {"items": [{"slug": "lactic-acid"}]}}, PUB)
    assert ok == []
    bad = sklib.check_tier_list_slugs(
        {"tier_list": {"items": [{"slug": "ghost-acid"}, {"slug": "lactic-acid"}]}}, PUB)
    assert len(bad) == 1 and "ghost-acid" in bad[0]


# --- check_grade_consistency: WARNING only, directional flips only --------

# A synthetic ingredient page body shaped like a real one: a '## The Rubric' section
# with bolded use-case headings, each followed by a bolded 'Effect size: ...' bullet.
AZELAIC_BODY = """Intro paragraph about azelaic acid, not part of any rubric section.

## The Rubric

**Rosacea (papulopustular)**
- **Effect size: notable.** Head-to-head trials put it on par with metronidazole.
- **Evidence quality: solid.** Multiple RCTs and a Cochrane review.

**Acne (mild to moderate)**
- **Effect size: modest.** Comparable to some topical antibiotics.
- **Evidence quality: mixed.** Smaller trials, heterogeneous designs.

**Some mechanism note (in vitro)**
- **Effect size: unclear and hard to size from the available data.** Preclinical only.
"""


def test_grade_consistency_warns_on_directional_disagreement():
    # product grades its rosacea use 'minimal'; the ingredient page's own rosacea
    # rubric grades it 'notable' -> a clear HIGH/LOW flip, worth a human check
    warns = sklib.check_grade_consistency(
        {"type": "product", "key_actives": ["azelaic-acid"],
         "grades": [{"effect": "minimal", "evidence": "preliminary",
                     "use": "Facial redness / papulopustular rosacea (health)"}]},
        {"azelaic-acid": AZELAIC_BODY})
    assert len(warns) == 1
    assert "minimal" in warns[0] and "notable" in warns[0] and "Rosacea" in warns[0]


def test_grade_consistency_silent_on_modest_middle_ground():
    # 'modest' is deliberately excluded from both the HIGH and LOW buckets - a
    # product grading its own use 'modest' against a 'notable' ingredient rubric is
    # NOT a clear directional flip, so this must stay silent
    warns = sklib.check_grade_consistency(
        {"type": "product", "key_actives": ["azelaic-acid"],
         "grades": [{"effect": "modest", "evidence": "mixed",
                     "use": "Facial redness / papulopustular rosacea (health)"}]},
        {"azelaic-acid": AZELAIC_BODY})
    assert warns == []


def test_grade_consistency_silent_when_same_bucket():
    # product 'strong' vs ingredient 'notable' - both HIGH, not a flip
    warns = sklib.check_grade_consistency(
        {"type": "product", "key_actives": ["azelaic-acid"],
         "grades": [{"effect": "strong", "evidence": "solid",
                     "use": "Facial redness / papulopustular rosacea (health)"}]},
        {"azelaic-acid": AZELAIC_BODY})
    assert warns == []


def test_grade_consistency_silent_without_topic_keyword_overlap():
    # the product's use ('acne', matched to the Acne heading which is 'modest') has
    # no bearing on a mismatched, unrelated grade entry with no shared keywords
    warns = sklib.check_grade_consistency(
        {"type": "product", "key_actives": ["azelaic-acid"],
         "grades": [{"effect": "strong", "evidence": "solid",
                     "use": "Daily moisturizing"}]},
        {"azelaic-acid": AZELAIC_BODY})
    assert warns == []


def test_grade_consistency_silent_on_unparseable_ingredient_prose():
    # the ingredient page's own effect-size wording ('unclear and hard to size...')
    # is outside the five-word vocabulary, so it is left unparsed rather than guessed
    warns = sklib.check_grade_consistency(
        {"type": "product", "key_actives": ["azelaic-acid"],
         "grades": [{"effect": "minimal", "evidence": "preliminary",
                     "use": "Some mechanism note for dermal cells"}]},
        {"azelaic-acid": AZELAIC_BODY})
    assert warns == []


def test_grade_consistency_skipped_for_multi_active_products():
    # a grade entry doesn't say which active it's for, so multi-active products are
    # skipped entirely rather than risk comparing a grade to the wrong active's page
    warns = sklib.check_grade_consistency(
        {"type": "product", "key_actives": ["azelaic-acid", "niacinamide"],
         "grades": [{"effect": "minimal", "evidence": "preliminary",
                     "use": "Facial redness / papulopustular rosacea (health)"}]},
        {"azelaic-acid": AZELAIC_BODY})
    assert warns == []


def test_grade_consistency_skipped_for_non_products():
    warns = sklib.check_grade_consistency(
        {"type": "ingredient", "key_actives": ["azelaic-acid"]},
        {"azelaic-acid": AZELAIC_BODY})
    assert warns == []


# --- check_uv_filter_coverage: ERROR, referenced-but-uncharted filters ----

def test_uv_filter_named_but_uncharted_is_an_error():
    errs = sklib.check_uv_filter_coverage(
        {"type": "product", "category": "Sunscreens", "grades": []},
        "Built around oxybenzone 3% as the primary UVA filter.",
        PUB)
    assert len(errs) == 1 and "oxybenzone" in errs[0]


def test_uv_filter_named_and_already_charted_is_silent():
    errs = sklib.check_uv_filter_coverage(
        {"type": "product", "category": "Sunscreens", "grades": []},
        "Built around avobenzone 3% as the UVA filter.",
        PUB)  # PUB includes avobenzone
    assert errs == []


def test_uv_filter_negation_claim_is_silent():
    # "free of X" / "X-free" is a marketing exclusion claim, not a reference to this
    # product's own active - the real false-positive trap found in production data
    # (every 'oxybenzone' mention in the current dataset is one of these)
    errs = sklib.check_uv_filter_coverage(
        {"type": "product", "category": "Sunscreens", "grades": []},
        "Marketed as free of oxybenzone and octinoxate, and PABA-free.",
        PUB)
    assert errs == []


def test_uv_filter_check_skipped_outside_sunscreen_category():
    errs = sklib.check_uv_filter_coverage(
        {"type": "product", "category": "Moisturizers", "grades": []},
        "Contains oxybenzone.",
        PUB)
    assert errs == []


def test_uv_filter_check_skipped_for_non_products():
    errs = sklib.check_uv_filter_coverage(
        {"type": "ingredient", "category": "Sunscreens"},
        "Contains oxybenzone.",
        PUB)
    assert errs == []
