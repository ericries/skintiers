"""Guards against [[wikilinks]] that point at no page.

Found 2026-11-09 while writing an ingredient page: a [[cleansers]] link was shipped
to a slug that does not exist, and sk lint, sk style and sk verify ALL passed it.
The renderer degrades an unresolved wikilink to PLAIN TEXT, so the page rendered the
sentence "The cleansing-oil format itself is covered on cleansers." with the promise
of a cross-reference and no link, and nothing anywhere flagged it. A sweep then
found 33 such occurrences across 26 distinct targets.

Ten were purely mechanical, a wrong case or a space instead of a hyphen on a target
that does exist ([[Ceramides]], [[hyaluronic acid]]), and were repaired in place with
the original wording preserved as the link label. The rest name pages the site does
not have, which is an editorial question rather than a typo: whether [[eczema]] should
point at atopic-dermatitis, or whether [[sebum]] deserves its own page, is not a
decision a test or a tick should take, so they are grandfathered by target and queued.

This is the same source-versus-render gap recorded before: the existing gates read the
markdown and the defect only exists once the renderer has swallowed it.
"""
import glob
import os
import re

TARGET_RE = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]*)?\]\]")

# Targets that name no page and whose correct resolution is an editorial decision.
# Shrinks only as pages are written or links are deliberately repointed.
# Trimmed 2026-11-10: eczema, photoaging, sodium-hyaluronate, aloe, oat,
# oxymetazoline and selenium-disulfide were repointed to
# pages that already cover them (atopic-dermatitis, sun-damage-photoaging,
# hyaluronic-acid), with the original wording kept as the link label. The rest still
# name no page and each needs a content decision rather than a redirect.
# Emptied 2026-11-11: all nine remaining dangling targets were resolved, six by
# pointing at the page that already owned the topic and three by de-linking where
# no page should exist. A target belongs here only while it is a known, accepted
# gap; the ratchet is that this set never grows.
GRANDFATHERED = set()


def _slugs():
    return {os.path.basename(p)[:-3] for p in glob.glob("data/*/*.md")}


def unresolved():
    slugs = _slugs()
    out = []
    for path in sorted(glob.glob("data/*/*.md")):
        text = open(path, encoding="utf-8", errors="replace").read()
        for target in TARGET_RE.findall(text):
            target = target.strip()
            if target and target not in slugs:
                out.append((os.path.basename(path)[:-3], target))
    return out


def test_no_new_unresolved_wikilinks(capsys):
    hits = unresolved()
    new = sorted({t for _, t in hits} - GRANDFATHERED)
    if hits:
        with capsys.disabled():
            print("\nunresolved wikilinks (render as plain text, no link):")
            for slug, target in hits:
                mark = "NEW" if target not in GRANDFATHERED else "known"
                print(f"  [{mark}] {slug}: [[{target}]]")
    assert not new, (
        "a wikilink points at no page, so the renderer silently drops it to plain "
        "text and the sentence promises a cross-reference it never makes: "
        + ", ".join(new))


def test_mechanical_case_and_space_targets_are_all_repaired():
    # The ten found on 2026-11-09 were fixable with certainty; none should return.
    slugs = _slugs()
    sloppy = [(s, t) for s, t in unresolved()
              if t.strip().lower().replace(" ", "-") in slugs]
    assert not sloppy, (
        "wikilink differs from an existing slug only by case or spacing, which is a "
        "typo rather than a missing page:\n"
        + "\n".join(f"  [{s}] [[{t}]]" for s, t in sloppy))
