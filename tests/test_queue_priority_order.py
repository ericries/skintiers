"""`queue_next` is the SCHEDULER for all eight fill crons: whatever it returns
is what gets built that tick. These tests pin the ordering contract to the
convention the DATA uses, which is the ordinary one: priority 1 is the most
important, priority 10 the least.

Why they exist. On 2026-11-06 `sk queue-next --type goal` offered "Combination
skin, if it ever needs its own page" -- a deliberate placeholder queued at
priority 8 whose own note says the default answer is NO -- as the top goal on
the site, while priority-4 items waited. The selector sorted by DESCENDING
priority number. Across all queues the corpus promotes 78 rows to priority 3-4
and demotes only 12 to 6-8 around a default of 5, which is a normal triage
pattern only if lower means more important.

The second half of the contract matters just as much: 647 of roughly 1,193
pending rows carry NO priority key at all. They must fall back to the schema
default (5), not to 0, or every unprioritised row in the backlog jumps the
queue ahead of work someone deliberately marked urgent.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402

DEFAULT = 5


def test_lower_priority_number_wins(tmp_path):
    sklib.queue_add(tmp_path, "Urgent", "ingredient", 1)
    sklib.queue_add(tmp_path, "Routine", "ingredient", 5)
    sklib.queue_add(tmp_path, "Parked", "ingredient", 9)
    assert sklib.queue_next(tmp_path, "ingredient")["name"] == "Urgent"


def test_a_parked_item_never_outranks_an_urgent_one(tmp_path):
    """The exact 2026-11-06 goal-queue shape: one deliberately deprioritised
    placeholder among ordinary work. It must not be offered first."""
    sklib.queue_add(tmp_path, "Real work", "goal", 4)
    sklib.queue_add(tmp_path, "Do not build yet", "goal", 8)
    assert sklib.queue_next(tmp_path, "goal")["name"] == "Real work"


def test_fifo_breaks_ties(tmp_path):
    sklib.queue_add(tmp_path, "First", "ingredient", 3)
    sklib.queue_add(tmp_path, "Second", "ingredient", 3)
    assert sklib.queue_next(tmp_path, "ingredient")["name"] == "First"


def test_missing_priority_is_treated_as_the_default_not_as_zero(tmp_path):
    """647 pending rows have no priority key. Defaulting them to 0 would make
    the entire unprioritised backlog outrank deliberately urgent work."""
    sklib.queue_add(tmp_path, "Explicitly urgent", "product", 2)
    sklib.queue_add(tmp_path, "No priority field", "product", DEFAULT)
    items = sklib.load_queue(tmp_path, "product")
    for it in items:
        if it["name"] == "No priority field":
            del it["priority"]
    sklib.save_queue(tmp_path, "product", items)
    assert sklib.queue_next(tmp_path, "product")["name"] == "Explicitly urgent"


def test_missing_priority_still_outranks_an_explicitly_deprioritised_row(tmp_path):
    """The other half: an unprioritised row is ordinary work, so it should beat
    something a human deliberately pushed down to 7."""
    sklib.queue_add(tmp_path, "Pushed down", "product", 7)
    sklib.queue_add(tmp_path, "No priority field", "product", DEFAULT)
    items = sklib.load_queue(tmp_path, "product")
    for it in items:
        if it["name"] == "No priority field":
            del it["priority"]
    sklib.save_queue(tmp_path, "product", items)
    assert sklib.queue_next(tmp_path, "product")["name"] == "No priority field"


def test_explicit_null_priority_is_also_the_default(tmp_path):
    """A row written with `priority:` and no value parses to None. `-None`
    raises TypeError, so this must be handled rather than assumed absent."""
    sklib.queue_add(tmp_path, "Null priority", "list", DEFAULT)
    sklib.queue_add(tmp_path, "Urgent", "list", 2)
    items = sklib.load_queue(tmp_path, "list")
    for it in items:
        if it["name"] == "Null priority":
            it["priority"] = None
    sklib.save_queue(tmp_path, "list", items)
    assert sklib.queue_next(tmp_path, "list")["name"] == "Urgent"


def test_done_items_are_still_skipped(tmp_path):
    sklib.queue_add(tmp_path, "Done but urgent", "ingredient", 1)
    sklib.queue_add(tmp_path, "Pending", "ingredient", 9)
    sklib.queue_resolve(tmp_path, "Done but urgent", "ingredient")
    assert sklib.queue_next(tmp_path, "ingredient")["name"] == "Pending"


def test_none_when_nothing_pending(tmp_path):
    assert sklib.queue_next(tmp_path, "study") is None
