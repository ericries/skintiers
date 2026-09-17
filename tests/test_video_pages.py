"""Per-video pages and per-creator feed pages: the slug helper must produce
stable, namespaced, SEO-friendly URLs; the creator-feed builder must order each
creator's videos newest-first and wire up correct prev/next neighbours.
"""
import importlib.machinery
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    loader = importlib.machinery.SourceFileLoader("buildmod", str(ROOT / "build.py"))
    spec = importlib.util.spec_from_loader("buildmod", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_slugify_is_seo_readable():
    b = _load()
    assert b._slugify("How Dermatologists FIX Pigmentation? (PIH)") == \
        "how-dermatologists-fix-pigmentation-pih"
    assert b._slugify("") == "video"
    assert len(b._slugify("word " * 60)) <= 80


def test_video_key_identifies_embeds():
    b = _load()
    assert b.video_key("https://www.youtube.com/watch?v=gD1RbEPw03M") == "youtube:gD1RbEPw03M"
    assert b.video_key("https://www.tiktok.com/@x/video/12345") == "tiktok:12345"
    assert b.video_key("https://example.com/clip") == "https://example.com/clip"


def test_slugs_are_namespaced_unique_and_collision_safe():
    b = _load()
    cards = [
        {"_key": "youtube:a", "title": "Azelaic Acid", "creator_slug": "dr-a"},
        {"_key": "youtube:b", "title": "Azelaic Acid", "creator_slug": "dr-b"},  # dup title
        {"_key": "youtube:c", "title": "Sunscreen Mistakes", "creator_slug": "dr-a"},
    ]
    m = b.assign_video_page_slugs(cards, reserved={"azelaic-acid"})
    slugs = [c["page_slug"] for c in cards]
    # every video slug is namespaced under `video-` (never clobbers an entity slug)
    assert all(s.startswith("video-") for s in slugs)
    assert "azelaic-acid" not in slugs
    # unique despite the duplicate title
    assert len(set(slugs)) == 3
    assert slugs[0] == "video-azelaic-acid"
    assert slugs[1] != slugs[0]
    assert m["youtube:c"] == "video-sunscreen-mistakes"


def test_creator_feed_orders_newest_first_with_neighbours():
    b = _load()
    cards = [
        {"_key": "1", "title": "Old", "creator_slug": "dr-a", "creator": "Dr A", "posted": "2024-01-01"},
        {"_key": "2", "title": "New", "creator_slug": "dr-a", "creator": "Dr A", "posted": "2026-01-01"},
        {"_key": "3", "title": "Mid", "creator_slug": "dr-a", "creator": "Dr A", "posted": "2025-01-01"},
        {"_key": "4", "title": "Other", "creator_slug": "dr-b", "creator": "Dr B", "posted": "2025-06-01"},
    ]
    b.assign_video_page_slugs(cards)
    feeds = b.build_creator_feeds(cards)
    assert set(feeds) == {"dr-a", "dr-b"}
    a = feeds["dr-a"]["videos"]
    assert [c["title"] for c in a] == ["New", "Mid", "Old"]  # newest first
    mid = a[1]
    assert mid["feed_newer"]["title"] == "New"   # the next more-recent video
    assert mid["feed_older"]["title"] == "Old"   # the next older video
    assert a[0]["feed_newer"] is None            # newest has no newer neighbour
    assert a[-1]["feed_older"] is None           # oldest has no older neighbour
    assert mid["creator_feed_slug"] == "dr-a-videos"
