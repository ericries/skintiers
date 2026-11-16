"""review-log.yaml is a slug-keyed mapping; a repeated key silently discards a review.

yaml.safe_load accepts duplicate top-level keys and keeps only the last one, so an
entry appended for a slug that was already reviewed destroys the earlier record with
no error. That happened twice before this check existed (l-oreal and
best-affordable-drugstore-dupes), and was only noticed because the entry count failed
to rise after an append.
"""
import pathlib
import re

import yaml

LOG = pathlib.Path(__file__).resolve().parent.parent / "data" / "review-log.yaml"
KEY = re.compile(r"^([a-z0-9][a-z0-9\-]*):\s*$")


def top_level_keys(text):
    return [m.group(1) for m in (KEY.match(line) for line in text.split("\n")) if m]


def test_review_log_has_no_duplicate_slugs():
    keys = top_level_keys(LOG.read_text(encoding="utf-8"))
    seen, dupes = set(), []
    for k in keys:
        if k in seen:
            dupes.append(k)
        seen.add(k)
    assert not dupes, (
        "review-log.yaml repeats these slugs, so the earlier review of each is lost "
        "on load: %s. Merge the entries instead of appending a second one." % sorted(set(dupes))
    )


def test_every_parsed_entry_survives_the_round_trip():
    text = LOG.read_text(encoding="utf-8")
    assert len(yaml.safe_load(text)) == len(top_level_keys(text))
