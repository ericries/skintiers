"""The tier_list maintenance task must tell the cron to RECORD what it excluded.

Why it exists. site_health already honours a `tier_list_reviewed` list on a hub,
so a candidate the maintainer has considered and rejected stops being offered.
The field existed and was empty everywhere, because the ACTION line the cron
actually reads said only "Skip any that do not truly fit" and never said where
to write the skip down.

The consequence is a false-gap generator. The lane clears on the hub's `updated`
date, so the hub comes back round later with the same rejected candidates, and
whoever picks it up re-litigates them from scratch. Found 2026-11-27 on
conditions/hyperpigmentation: of the 8 candidates offered, 7 could never belong
in a ranking of actives by evidence (five were finished products, one a soothing
botanical with no pigment claim, one an unproven hair-reduction extract), and
nothing in the workflow would have remembered that.
"""
import pathlib
import sys

import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import site_health  # noqa: E402


def _tier_list_task():
    for hub_type, hub_dir in (("condition", "conditions"), ("goal", "goals")):
        out = site_health.check_hub_behind(hub_type, hub_dir)
        if out:
            return out
    raise AssertionError(
        "no hub reported a stale tier_list, so this test cannot check the "
        "ACTION text; if every hub is current, give one a stale `updated`"
    )


def test_action_text_names_the_field_to_record_exclusions():
    task = _tier_list_task()
    assert "tier_list_reviewed" in task, (
        "the ACTION line must tell the cron where to record a deliberate "
        "exclusion, or the same rejected candidates resurface every cycle:\n" + task
    )


def test_reviewed_slugs_are_not_offered_as_candidates():
    """The honouring half, which already worked: guard it."""
    fm = frontmatter.load(ROOT / "data/conditions/hyperpigmentation.md").metadata
    reviewed = set(fm.get("tier_list_reviewed") or [])
    assert reviewed, "hyperpigmentation should carry the 2026-11-27 exclusions"
    assert not (reviewed & site_health.tier_list_slugs(fm)), (
        "a slug cannot be both ranked and reviewed-excluded"
    )
