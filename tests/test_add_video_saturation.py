"""A page should not silently accumulate card after card from one creator.

Twice in one session a tick researched a clip in full, carded it, and only then
noticed the target page already carried three cards from the same creator making
the same argument. Both times the work was reverted. The cheap fix is to say so
at insert time, so the next tick sees it before spending the research.

This is a WARNING, not a refusal: a fourth card from one creator is sometimes
right, and only the person writing the thesis can tell.
"""
import importlib.machinery
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
_loader = importlib.machinery.SourceFileLoader("sk_cli", str(ROOT / "scripts" / "sk"))
_spec = importlib.util.spec_from_loader("sk_cli", _loader)
sk = importlib.util.module_from_spec(_spec)
_loader.exec_module(sk)


def _page(tmp_path, cards):
    import yaml
    body = "---\n" + yaml.safe_dump(
        {"name": "T", "slug": "t", "type": "goal", "status": "published",
         "videos": cards}, sort_keys=False) + "---\n\nbody\n"
    p = tmp_path / "t.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_no_warning_when_creator_is_new_to_the_page(tmp_path):
    p = _page(tmp_path, [{"id": "a", "creator_slug": "someone-else"}])
    assert sk.creator_card_count(p, "ella") == 0


def test_counts_only_the_named_creator(tmp_path):
    p = _page(tmp_path, [{"id": "a", "creator_slug": "ella"},
                         {"id": "b", "creator_slug": "ella"},
                         {"id": "c", "creator_slug": "other"}])
    assert sk.creator_card_count(p, "ella") == 2


def test_missing_videos_key_is_zero_not_an_error(tmp_path):
    import yaml
    p = tmp_path / "t.md"
    p.write_text("---\n" + yaml.safe_dump({"name": "T", "slug": "t"}) + "---\n\nb\n",
                 encoding="utf-8")
    assert sk.creator_card_count(p, "ella") == 0


def test_unparseable_page_is_zero_not_an_exception(tmp_path):
    """A warning must never be the thing that breaks a carding run."""
    p = tmp_path / "t.md"
    p.write_text("---\nthis: [is not: valid yaml\n---\n", encoding="utf-8")
    assert sk.creator_card_count(p, "ella") == 0
