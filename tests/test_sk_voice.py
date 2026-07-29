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
