"""Two published pages must not claim the same `name:` for the same type.

Found 2026-11-23 while linking the Paula's Choice brand page: its detector listed
`paulas-choice-skin-perfecting-8-aha-gel-exfoliant` as unlinked while the page
already linked `paulas-choice-skin-perfecting-8-aha-gel`. Both files exist, both are
published, and both carry the identical name "Paula's Choice Skin Perfecting 8% AHA
Gel Exfoliant". A site-wide sweep found three such pairs, all created in late
September against originals from July and August.

This is NOT the same failure as a duplicate SLUG across directories, which
test_data_dirs_and_slug_collisions already guards: there, one page silently
overwrites the other at build. Here both render, at different URLs, each with its own
grade and sources, and a reader can land on either. Nothing in the pipeline noticed
because every gate works from a single slug.

The three known pairs are grandfathered rather than fixed, because merging or
deleting a published page changes a live URL and is the user's decision. The ratchet
is the same as the wikilink test: this set never grows.
"""
import collections
import glob

import frontmatter

# slug pairs that already share a name on 2026-11-23, pending a user decision on
# which to keep. Measured: in every pair the OLDER page is longer and far better
# linked (20 inbound vs 1, 6 vs 1, 4 vs 2).
GRANDFATHERED = {
    ("product", "la roche-posay toleriane double repair face moisturizer"),
    ("product", "paula's choice skin perfecting 2% bha liquid exfoliant"),
    ("product", "paula's choice skin perfecting 8% aha gel exfoliant"),
}


def _duplicate_names():
    seen = collections.defaultdict(list)
    for path in sorted(glob.glob("data/*/*.md")):
        meta = frontmatter.load(path).metadata
        name = str(meta.get("name") or "").strip().lower()
        if name:
            seen[(meta.get("type"), name)].append(path)
    return {k: v for k, v in seen.items() if len(v) > 1}


def test_no_new_pages_share_a_name():
    dupes = _duplicate_names()
    new = {k: v for k, v in dupes.items() if k not in GRANDFATHERED}
    assert not new, (
        "two pages of the same type claim the same name:, so both render at "
        "different URLs and a reader can land on either: "
        + "; ".join(f"{k[1]!r} -> {', '.join(v)}" for k, v in sorted(new.items()))
    )


def test_grandfathered_duplicates_are_still_real():
    """The ratchet only works if the exception list cannot go stale."""
    dupes = set(_duplicate_names())
    stale = GRANDFATHERED - dupes
    assert not stale, (
        "these name collisions are listed as known but no longer exist; remove them "
        f"from GRANDFATHERED so the guard keeps tightening: {sorted(stale)}"
    )
