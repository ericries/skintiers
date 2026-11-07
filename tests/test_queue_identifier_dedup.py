"""A queue row that names a regulatory identifier must not duplicate the page
that already IS that identifier.

Observed twice in two days, both on the product fill cron:

  2026-11-06  "reVive Light Therapy LED Ultrasonic Wrinkle System (LED
              Technologies)" was queued although K180445 was already covered.
  2026-11-07  "Tanda Mini (K124042, blue-light acne handheld)" reached the
              queue head although tanda-mini-skincare-system.md had been
              built from K124042 in full six days earlier.

Both sailed past page_exists_for because it only resolves the WHOLE name, and
"Tanda Mini (K124042, blue-light acne handheld)" scores 69 against
"Tanda Mini Skincare System" -- well under PAGE_IDENTITY_MATCH_SCORE.

The guard must be conservative in the other direction too: a K number that is
merely CITED by some page (a predicate in a footnote, an entry in a survey
table) is NOT covered, and queueing it is real work that must not be blocked.
41 of 135 pending product rows name a K number cited somewhere on the site,
and most of them are legitimate. So the test for "already covered" is that the
identifier resolves through the repo's identity index at an exact grade, i.e.
the page claims it as an alias, not that the string appears in a page body.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import sklib


def _page(tmp_path, plural, slug, name, typ, aliases=(), body=""):
    d = tmp_path / plural
    d.mkdir(parents=True, exist_ok=True)
    alias_block = "".join(f"\n- {a}" for a in aliases)
    (d / f"{slug}.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"slug: {slug}\n"
        f"aliases:{alias_block or ' []'}\n"
        "status: published\n"
        f"type: {typ}\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )


def test_identifier_claimed_as_alias_blocks_the_duplicate(tmp_path):
    _page(
        tmp_path,
        "products",
        "tanda-mini-skincare-system",
        "Tanda Mini Skincare System",
        "product",
        aliases=["Tanda Clear", "K124042"],
        body="Cleared as K124042 under product code OLP.",
    )
    assert sklib.page_exists_for(
        str(tmp_path), "Tanda Mini (K124042, blue-light acne handheld)", "product"
    ) is True


def test_identifier_only_cited_in_a_body_does_not_block(tmp_path):
    # dpl-therapy-system cites K051681 as its predicate. The Dermillume device
    # itself has no page, and queueing it is legitimate work.
    _page(
        tmp_path,
        "products",
        "dpl-therapy-system",
        "DPL Therapy System",
        "product",
        aliases=["K081570"],
        body='Substantially equivalent to the Dermillume Red HR 1000, 510(k) K051681.',
    )
    assert sklib.page_exists_for(
        str(tmp_path), "Dermillume Red HR 1000 (K051681)", "product"
    ) is False


def test_pmid_duplicate_closes_only_when_the_words_agree_too(tmp_path):
    _page(
        tmp_path,
        "studies",
        "gold-2019-stratacel-vs-aquaphor",
        "Gold 2019 Stratacel versus Aquaphor after microneedling",
        "study",
        aliases=["PMID 30756451"],
    )
    # Same study, same words: closes.
    assert sklib.page_exists_for(
        str(tmp_path),
        "Gold 2019 Stratacel versus Aquaphor after microneedling (PMID 30756451)",
        "study",
    ) is True
    # Same PMID cited by a row about something else: must not close.
    assert sklib.page_exists_for(
        str(tmp_path), "A later replication of PMID 30756451", "study"
    ) is False


def test_two_identifiers_means_predicate_or_sibling_not_duplicate(tmp_path):
    """Observed on the live queue 2026-11-07.

    "TheraFace Mask (K230293, Therabody, ...)" also cites K212155, which
    theraface-led-light-ring.md owns. K230293 itself is owned by nobody, so the
    row is real work and closing it would have destroyed it."""
    _page(
        tmp_path,
        "products",
        "theraface-led-light-ring",
        "TheraFace LED Light Ring (K212155)",
        "product",
        aliases=["K212155"],
    )
    assert sklib.page_exists_for(
        str(tmp_path),
        "TheraFace Mask (K230293, Therabody, predicate K212155)",
        "product",
    ) is False


def test_sibling_device_sharing_a_filing_is_not_a_duplicate(tmp_path):
    """Also observed live: "illuMask Anti-Aging Light Therapy Mask (K123999
    sibling)" against illumask-acne-light-therapy-mask.md, which owns K123999.
    One identifier, but the words disagree: Anti-Aging is not Acne."""
    _page(
        tmp_path,
        "products",
        "illumask-acne-light-therapy-mask",
        "illuMask Acne Light Therapy Mask (La Lumiere)",
        "product",
        aliases=["K123999"],
    )
    assert sklib.page_exists_for(
        str(tmp_path),
        "illuMask Anti-Aging Light Therapy Mask (K123999 sibling)",
        "product",
    ) is False


def test_a_maintenance_task_naming_a_filing_is_not_a_page_request(tmp_path):
    """And again: a row whose name is an instruction, not a thing."""
    _page(
        tmp_path,
        "products",
        "revive-light-therapy-led-cleansing-system",
        "reVive Light Therapy LED Cleansing System",
        "product",
        aliases=["K180445"],
    )
    assert sklib.page_exists_for(
        str(tmp_path),
        "Sweep the four remaining footnotes that repeat openFDA's phantom device name for K180445",
        "product",
    ) is False


def test_name_with_no_identifier_is_unaffected(tmp_path):
    _page(tmp_path, "products", "some-cream", "Some Cream", "product", aliases=[])
    assert sklib.page_exists_for(str(tmp_path), "A Totally Different Cream", "product") is False


def test_reconcile_closes_an_identifier_duplicate(tmp_path):
    """queue_reconcile must agree with page_exists_for.

    Its own docstring promises that a sweep using the identity index "agrees
    with the single-row guard", but it only tested the whole name and the name
    with parentheticals stripped. So the guard could learn to block a row at
    insert time while the sweep left the identical row pending forever.
    """
    _page(
        tmp_path,
        "products",
        "tanda-mini-skincare-system",
        "Tanda Mini Skincare System",
        "product",
        aliases=["K124042"],
    )
    (tmp_path / "queues").mkdir(parents=True, exist_ok=True)
    (tmp_path / "queues" / "products.yaml").write_text(
        "- name: Tanda Mini (K124042, blue-light acne handheld)\n"
        "  type: product\n"
        "  status: pending\n"
        "- name: Dermillume Red HR 1000 (K051681)\n"
        "  type: product\n"
        "  status: pending\n",
        encoding="utf-8",
    )
    assert sklib.queue_reconcile(str(tmp_path), dry_run=True) == 1

    sklib.queue_reconcile(str(tmp_path))
    rows = sklib.load_queue(str(tmp_path), "product")
    by_name = {r["name"]: r for r in rows}
    assert by_name["Tanda Mini (K124042, blue-light acne handheld)"]["status"] == "done"
    assert by_name["Dermillume Red HR 1000 (K051681)"]["status"] == "pending"
