"""`queue_reconcile` closes a queue row once the page it asked for exists.

Why it exists. The dedup guard runs only at INSERT time, so a row added before
its page was written stays pending forever, even after somebody builds that page
by another route or under a differently-worded row. Nothing ever re-checks. On
2026-11-06 a single index pass found 13 such rows across the queues, including
"Dupilumab (Dupixent)" and "Witch Hazel (Hamamelis virginiana extract)", both
long since written. Each one costs a whole tick: the staleness is only
discovered at the END, after the research is done.

The contract is deliberately narrow and auditable. It marks a row done and
records WHY on the row, so the decision is reviewable in git rather than being a
silent deletion. It never touches rows that are already done, never removes
anything, and is idempotent.
"""
import pathlib
import sys

import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402


def _page(root, sub, slug, typ, name=None):
    d = pathlib.Path(root) / sub
    d.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post("body", name=name or slug, slug=slug, type=typ,
                            status="published", updated="2026-01-01")
    with open(d / f"{slug}.md", "wb") as f:
        frontmatter.dump(post, f)


def _names(tmp_path, typ, status):
    return [i["name"] for i in sklib.load_queue(tmp_path, typ)
            if i.get("status") == status]


def test_a_row_whose_page_now_exists_is_closed(tmp_path):
    sklib.queue_add(tmp_path, "Retinol", "ingredient", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    assert sklib.queue_reconcile(tmp_path) == 1
    assert _names(tmp_path, "ingredient", "pending") == []
    assert _names(tmp_path, "ingredient", "done") == ["Retinol"]


def test_it_records_why_so_the_close_is_auditable(tmp_path):
    sklib.queue_add(tmp_path, "Retinol", "ingredient", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    sklib.queue_reconcile(tmp_path)
    row = sklib.load_queue(tmp_path, "ingredient")[0]
    assert "retinol" in str(row.get("resolved_reason", "")).lower()


def test_a_row_with_no_page_is_left_pending(tmp_path):
    """The failure that matters: closing real work because the matcher guessed."""
    sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    assert sklib.queue_reconcile(tmp_path) == 0
    assert _names(tmp_path, "ingredient", "pending") == ["Niacinamide"]


def test_it_matches_on_frontmatter_name_not_just_slug(tmp_path):
    """The Sheila Farhang shape: queued with an honorific the slug omits."""
    sklib.queue_add(tmp_path, "Dr. Sheila Farhang", "person", 5)
    _page(tmp_path, "people", "sheila-farhang", "person", name="Dr. Sheila Farhang")
    assert sklib.queue_reconcile(tmp_path) == 1


def test_already_done_rows_are_not_touched_again(tmp_path):
    sklib.queue_add(tmp_path, "Retinol", "ingredient", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    assert sklib.queue_reconcile(tmp_path) == 1
    assert sklib.queue_reconcile(tmp_path) == 0   # idempotent


def test_nothing_is_ever_deleted(tmp_path):
    sklib.queue_add(tmp_path, "Retinol", "ingredient", 5)
    sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    sklib.queue_reconcile(tmp_path)
    assert len(sklib.load_queue(tmp_path, "ingredient")) == 2


def test_a_dry_run_reports_without_writing(tmp_path):
    sklib.queue_add(tmp_path, "Retinol", "ingredient", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    assert sklib.queue_reconcile(tmp_path, dry_run=True) == 1
    assert _names(tmp_path, "ingredient", "pending") == ["Retinol"]


def test_type_is_respected(tmp_path):
    """A person page must not close a product row of the same name."""
    sklib.queue_add(tmp_path, "La Roche-Posay", "product", 5)
    _page(tmp_path, "people", "la-roche-posay", "person", name="La Roche-Posay")
    assert sklib.queue_reconcile(tmp_path) == 0


def test_it_closes_a_row_whose_page_exists_under_a_DIFFERENT_type(tmp_path):
    """The periorbital-wrinkles shape, found the hard way 2026-11-19.

    The condition queue held a pending row for "Periorbital wrinkles" while
    data/goals/periorbital-wrinkles.md already existed. Reconcile read only the
    row's OWN type index, so it never saw the goal page and left the row
    pending. A later tick then took the row, researched it, and wrote a SECOND
    page at the same slug under conditions/. Both render to the same filename,
    so one silently overwrites the other at build.
    """
    sklib.queue_add(tmp_path, "Periorbital wrinkles", "condition", 5)
    _page(tmp_path, "goals", "periorbital-wrinkles", "goal",
          name="Periorbital wrinkles")
    assert sklib.queue_reconcile(tmp_path) == 1
    assert _names(tmp_path, "condition", "pending") == []


def test_a_cross_type_close_names_the_type_that_satisfied_it(tmp_path):
    """Closing against another type is the surprising case, so say so plainly.

    A reader seeing a condition row closed needs to know a GOAL page is what
    satisfied it, or the close looks like the matcher guessing.
    """
    sklib.queue_add(tmp_path, "Periorbital wrinkles", "condition", 5)
    _page(tmp_path, "goals", "periorbital-wrinkles", "goal",
          name="Periorbital wrinkles")
    sklib.queue_reconcile(tmp_path)
    reason = str(sklib.load_queue(tmp_path, "condition")[0].get("resolved_reason", ""))
    assert "goal" in reason.lower(), reason
    assert "periorbital-wrinkles" in reason.lower() or "periorbital wrinkles" in reason.lower()


def test_an_unrelated_page_of_another_type_does_not_close_a_row(tmp_path):
    """The guard on the above: cross-type must still require an exact identity."""
    sklib.queue_add(tmp_path, "Periorbital wrinkles", "condition", 5)
    _page(tmp_path, "goals", "firmer-skin", "goal", name="Firmer skin")
    assert sklib.queue_reconcile(tmp_path) == 0
    assert _names(tmp_path, "condition", "pending") == ["Periorbital wrinkles"]


def test_cross_type_matching_is_an_allowlist_not_a_sweep(tmp_path):
    """The regression guard for the fix above.

    The first version of cross-type matching swept EVERY type and promptly
    broke test_type_is_respected: a person page named "La Roche-Posay" closed a
    product row of that name. Only condition and goal alias each other. This
    pins a second pairing that must stay closed, so a later widening of
    _ALIAS_TYPES has to come with a deliberate decision.
    """
    sklib.queue_add(tmp_path, "Retinol", "product", 5)
    _page(tmp_path, "ingredients", "retinol", "ingredient", name="Retinol")
    assert sklib.queue_reconcile(tmp_path) == 0
    assert _names(tmp_path, "product", "pending") == ["Retinol"]


def test_an_ambiguous_row_is_left_pending_even_at_the_same_score(tmp_path):
    """The guard that makes the above safe, and the reason score alone is not enough.

    On the real tree 'Retinol' as a product row scores 80 against TEN pages, and
    'Niacinamide' likewise, so closing on score alone would discard real work.

    A stricter rule, top score >= 80 AND held by exactly one page, was built and
    measured on 2026-11-22 and then REJECTED. It closed 7 real rows, of which 2 were
    wrong: 'Dipotassium Glycyrrhizate' matched licorice-root-extract, a related but
    different ingredient, and 'Home LED devices by what their clearance actually
    covers' matched home-led-devices-for-body-acne, a different list. Both scored 80
    with why="all query terms present" although the target contains only some of the
    terms, so find_entities' 80 grade is not reliable enough to close a row on. No
    threshold separates them: a correct match (capryloyl salicylic acid) scores 80 too.
    """
    sklib.queue_add(tmp_path, "Retinol", "product", 5)
    for slug, name in [("cosrx-the-retinol-cream", "COSRX The Retinol 0.1 Cream"),
                       ("inkey-retinol-serum", "The Inkey List Retinol Serum"),
                       ("necessaire-body-retinol", "Necessaire The Body Retinol")]:
        _page(tmp_path, "products", slug, "product", name=name)
    assert sklib.queue_reconcile(tmp_path) == 0
    assert _names(tmp_path, "product", "pending") == ["Retinol"]


def test_a_row_naming_a_page_by_a_prefix_or_variant_is_closed(tmp_path):
    """Five rows in the week to 2026-11-22 named a page by a shorter or variant name.

    The exact-identity index cannot match those, so the sweep closed none of them and
    each cost a tick to rediscover. find_entities scores this shape at 80 with exactly
    ONE page at the top, which is what makes it safe to act on.
    """
    sklib.queue_add(tmp_path, "Prequel Lucent-C", "product", 5)
    _page(tmp_path, "products", "prequel-lucent-c-vitamin-c-serum", "product",
          name="Prequel Lucent-C Brightening Vitamin C Serum")
    assert sklib.queue_reconcile(tmp_path) == 1
    assert _names(tmp_path, "product", "pending") == []


def test_a_scored_close_names_the_page_that_satisfied_it(tmp_path):
    """In this branch the row name and page name differ by definition, so a reader
    checking the close must be able to see what matched."""
    sklib.queue_add(tmp_path, "Prequel Lucent-C", "product", 5)
    _page(tmp_path, "products", "prequel-lucent-c-vitamin-c-serum", "product",
          name="Prequel Lucent-C Brightening Vitamin C Serum")
    sklib.queue_reconcile(tmp_path)
    reason = str(sklib.load_queue(tmp_path, "product")[0].get("resolved_reason", ""))
    assert "prequel-lucent-c-vitamin-c-serum" in reason, reason
