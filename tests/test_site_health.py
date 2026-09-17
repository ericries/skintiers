"""site_health.check_hub_behind must respect a `tier_list_reviewed:` marker:
slugs the maintainer has deliberately reviewed and excluded from a hub's
tier_list (e.g. products that link an actives-by-evidence hub but cannot join
an actives ranking) stop being re-flagged, while genuinely-new candidates that
link the hub still surface.
"""
import importlib.machinery
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    loader = importlib.machinery.SourceFileLoader(
        "site_health", str(ROOT / "scripts" / "site_health.py"))
    spec = importlib.util.spec_from_loader("site_health", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def _hub(reviewed):
    return {
        "slug": "neck-hub", "status": "published", "updated": "2026-01-01",
        "tier_list": {"items": ["retinoids"]},
        "tier_list_reviewed": reviewed,
    }


def _wire(sh, hub_fm, catalog):
    def fake_all_pages(*dirs):
        if "products" in dirs or "ingredients" in dirs:
            return catalog
        return [("hub.md", hub_fm, "", "")]
    sh.all_pages = fake_all_pages


def test_reviewed_slug_suppressed_new_candidate_still_flagged():
    sh = _load()
    catalog = [
        ("p1.md", {"slug": "prod-reviewed", "status": "published"}, "", "[[neck-hub]]"),
        ("p2.md", {"slug": "prod-new", "status": "published"}, "", "[[neck-hub]]"),
    ]
    _wire(sh, _hub(["prod-reviewed"]), catalog)
    task = sh.check_hub_behind("goal", "goals")
    assert task is not None
    assert "prod-new" in task
    assert "prod-reviewed" not in task


def test_all_reviewed_returns_none():
    sh = _load()
    catalog = [
        ("p1.md", {"slug": "prod-a", "status": "published"}, "", "[[neck-hub]]"),
        ("p2.md", {"slug": "prod-b", "status": "published"}, "", "[[neck-hub]]"),
    ]
    _wire(sh, _hub(["prod-a", "prod-b"]), catalog)
    assert sh.check_hub_behind("goal", "goals") is None


def test_no_marker_flags_normally():
    sh = _load()
    catalog = [
        ("p1.md", {"slug": "prod-a", "status": "published"}, "", "[[neck-hub]]"),
    ]
    hub = _hub([])
    del hub["tier_list_reviewed"]
    _wire(sh, hub, catalog)
    task = sh.check_hub_behind("goal", "goals")
    assert task is not None and "prod-a" in task
