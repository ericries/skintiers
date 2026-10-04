import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402


def _hits(text):
    return " | ".join(sklib.check_voice(text))


def test_flags_site_self_reference():
    assert any("self-reference" in w for w in sklib.check_voice("SkinTiers grades this."))


def test_flags_defensive_meta():
    assert any("meta" in w for w in sklib.check_voice("This page grades the treatments."))
    assert any("meta" in w for w in sklib.check_voice("What follows is a survey."))
    assert any("meta" in w for w in sklib.check_voice("These are the source's opinions, not our verdict."))


def test_flags_process_language():
    assert any("process" in w for w in sklib.check_voice("This ingredient is queued for research."))
    assert any("process" in w for w in sklib.check_voice("Full coverage is a later phase."))


def test_does_not_flag_not_a_finding_of_harm():
    # substantive FDA-status content, NOT defensive meta (QC 2/5 false positive)
    assert sklib.check_voice("The request triggers more study, not a finding of harm.") == []


def test_clean_body_has_no_voice_warnings():
    assert sklib.check_voice("Azelaic acid reduces papules and pustules in rosacea.") == []


def test_check_style_includes_voice_warnings():
    # sk style must surface voice violations too
    assert any("self-reference" in w for w in sklib.check_style("SkinTiers is great."))


def test_flags_absolute_absence_of_evidence_claims():
    # Regression: clascoterone.md asserted "no head-to-head trial exists" while
    # Trifu 2011 (PMID 21428978) compared it with tretinoin 0.05%. A universal
    # existence claim about the literature is unverifiable; the hedged form
    # ("no trial cited here") is what the site can actually stand behind.
    assert any("absence" in w for w in sklib.check_voice("No head-to-head trial exists."))
    assert any("absence" in w for w in sklib.check_voice("no trial exists against tretinoin"))
    assert any("absence" in w for w in sklib.check_voice("No independent study exists."))
    assert any("absence" in w for w in sklib.check_voice("No randomized trials exist for this active."))


def test_does_not_flag_scoped_absence_claims():
    # These are the correct, defensible forms and must stay clean.
    assert sklib.check_voice("No trial cited here compares the two actives.") == []
    assert sklib.check_voice("There is no published trial of this specific cream.") == []
    assert sklib.check_voice("This profile has no head-to-head trial against tretinoin.") == []
    assert sklib.check_voice("No product-specific trial was found.") == []
