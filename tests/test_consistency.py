"""Cross-page consistency gate (Phase C). Two jobs:

1. `test_no_cross_page_consistency_errors` scans the REAL data tree and fails the
   build on any consistency ERROR - a key_active/tier-list slug that points at no
   published page, an images: file that isn't self-hosted, or a product mis-tagged
   vs its own name (the-ordinary-lactic-acid class). CI runs pytest before deploy,
   so an inconsistency blocks the broken version from going live. Learning #5:
   cross-page consistency needs automation, not luck.
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
