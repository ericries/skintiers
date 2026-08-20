"""`sklib.CRITIC_TYPES` (which page types earn assurance: opus) must stay in sync
with the cron roster, which is the authoritative statement of which fill types run
an Opus profile-reviewer critic. I hand-maintained CRITIC_TYPES and got it wrong
TWICE -- first too broad, then too narrow (omitting condition + goal, whose cron
prompts explicitly mandate an Opus critic). This test derives the set from the
roster so the two can no longer drift: a type is critic-backed iff its `critic`
field mandates "Opus profile-reviewer critic MUST".
"""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402

_MANDATE = "Opus profile-reviewer critic MUST"


def test_critic_types_match_the_cron_roster():
    roster = yaml.safe_load((ROOT / "data" / "cron-roster.yaml").read_text())
    derived = {c["type"] for c in roster["crons"]
               if c.get("type") and _MANDATE in (c.get("critic") or "")}
    assert derived == set(sklib.CRITIC_TYPES), (
        f"sklib.CRITIC_TYPES {sorted(sklib.CRITIC_TYPES)} disagrees with the cron "
        f"roster's critic-mandating types {sorted(derived)}. Keep them in sync: a "
        f"type earns assurance:opus iff its cron prompt requires an Opus critic."
    )


def test_derivation_is_not_vacuous():
    # guard against the check silently passing because both sides are empty
    assert len(sklib.CRITIC_TYPES) >= 3
