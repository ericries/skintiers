"""Corpus-level guards for the data/ tree.

Both bugs here were live on 2026-11-20. Three October commits wrote person pages
to `data/persons/` while the canonical directory for the `person` type is
`data/people/`. Nothing noticed, because sklib.load_profiles globs `data/*/*.md`
and so picks up ANY subdirectory, and the per-page lint/verify gates work from a
slug and never compare directories.

The consequence was silent and worse than a crash: `aleksandra-brown` existed in
both directories, load_profiles returned BOTH as separate posts, and the writer
emitted <slug>.html for each in sorted order. "persons" sorts after "people", so
the stale 2026-10-08 copy overwrote the 2026-11-09 rewrite on every build. The
site served the old page for 11 days while the good one sat on disk.
"""
import pathlib
import collections
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# The type -> directory map build.py actually uses.
KNOWN_DIRS = {"products", "ingredients", "studies", "conditions",
              "goals", "people", "brands", "lists"}


def _page_dirs():
    return {d.name for d in DATA.iterdir()
            if d.is_dir() and any(d.glob("*.md"))}


def test_no_unknown_page_directories():
    """A directory of .md pages that no type maps to still renders, silently."""
    unknown = _page_dirs() - KNOWN_DIRS
    assert not unknown, (
        f"data/ subdirectories holding .md pages that no type maps to: "
        f"{sorted(unknown)}. load_profiles globs data/*/*.md, so these DO render, "
        f"but nothing else knows they exist. Move them into the right type "
        f"directory (the slug, and so the URL, does not change)."
    )


def test_no_duplicate_slugs_across_directories():
    """Two files with one slug: the later directory silently wins the render."""
    seen = collections.defaultdict(list)
    for md in sorted(DATA.glob("*/*.md")):
        seen[md.stem].append(f"{md.parent.name}/{md.name}")
    dupes = {s: p for s, p in seen.items() if len(p) > 1}
    assert not dupes, (
        "slug collisions across data/ directories; the one whose directory sorts "
        "LAST overwrites the other in _site/<slug>.html, with no error: "
        + "; ".join(f"{s}: {' vs '.join(p)}" for s, p in sorted(dupes.items()))
    )
