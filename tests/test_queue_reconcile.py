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
