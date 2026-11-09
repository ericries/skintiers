"""Guards the roster's `conflict:` notes against silent truncation.

A creator's `conflict:` note is POLICY TEXT, not commentary: every video-pull tick
reads it to decide what is eligible from that creator. On 2026-11-09 a TikTok pull
found 7 of 56 notes cut off mid-word with a platform suffix appended after the cut,
e.g. karan-lal's "...that monetizes his pick" - severed at the exact word carrying
the rule. The cut sat at 130 characters in six of them: a fixed-width DISPLAY
truncation that leaked into stored data during the overnight roster-expansion push.
Nothing in the repo produces that suffix, so the generator is gone and cannot be
fixed; this gate instead makes a truncated note impossible to persist unnoticed.

Detection needs precision, not zeal: 45 of 56 notes simply end without a full stop,
so "no terminal punctuation" alone is useless. The signal is an unterminated clause
with a suffix appended AFTER it - nobody deliberately appends to an unfinished
sentence. That isolates exactly the real defect set.

The real-data test is a RATCHET: the 7 known-bad rows are grandfathered by slug so
the gate cannot block deploy, and any NEW truncated note fails the build. The
allowlist is the to-do list - repairing a row means re-deriving its policy from
sources, which cannot be guessed, so it is deliberately not done here.
"""
import sklib


COMPLETE = "Runs #ad sponsored posts (e.g. TruSkin); treat product picks as promotional."
CUT = ("Self-describes as a \"Key Opinion Leader for industry beauty companies\" "
       "(per her own practice bio) and most sampled TikTok videos e; no YouTube; "
       "TikTok/IG intake")


def test_note_cut_midsentence_before_an_appended_suffix_is_flagged():
    assert sklib.truncated_policy_note(CUT)


def test_note_ending_in_a_full_stop_is_silent():
    assert not sklib.truncated_policy_note(COMPLETE)


def test_note_without_a_final_full_stop_is_not_enough_to_flag():
    # 45 of 56 real notes look like this. Flagging them would make the gate noise.
    assert not sklib.truncated_policy_note(
        "No own-brand product line and no affiliate storefront")


def test_suffix_after_a_properly_closed_clause_is_silent():
    assert not sklib.truncated_policy_note(
        "Co-developed a serum (formulation partnership).; no YouTube; TikTok/IG intake")


def test_empty_and_missing_notes_are_silent():
    assert not sklib.truncated_policy_note(None)
    assert not sklib.truncated_policy_note("")
    assert not sklib.truncated_policy_note("   ")


def test_short_fragment_is_not_flagged():
    # A terse note is a style choice, not a truncation; require real length.
    assert not sklib.truncated_policy_note("none known; no YouTube")


# --- The ratchet over the real roster -------------------------------------

GRANDFATHERED = {
    "emma-wedgeworth", "michelle-henry-md-faad", "geeta-yadav", "hannah-english",
    "justine-kluk", "karan-lal", "sheila-farhang", "thivi-maruthappu",
}


def test_no_new_truncated_policy_notes_in_the_roster(capsys):
    hits = sklib.truncated_roster_notes()
    new = {s for s, _ in hits} - GRANDFATHERED
    if hits:
        with capsys.disabled():
            print("\ntruncated conflict notes (policy text lost at the cut):")
            for slug, note in hits:
                mark = "NEW" if slug not in GRANDFATHERED else "known"
                print(f"  [{mark}] {slug}: ...{note[-70:]!r}")
    assert not new, (
        "a creator's conflict note is cut mid-sentence, so the rule it carries is "
        "lost to every future pull tick: " + ", ".join(sorted(new)))
