import pathlib
import sklib


def _write(dirpath, slug, status, typ="product"):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: {typ}\nstatus: {status}\n---\n\nBody.\n"
    )


def test_load_and_filter(tmp_path):
    _write(tmp_path / "products", "good", "published")
    _write(tmp_path / "products", "wip", "draft")
    posts = sklib.load_profiles(tmp_path)
    assert {p["slug"] for p in posts} == {"good", "wip"}
    published = sklib.filter_published(posts)
    assert [p["slug"] for p in published] == ["good"]


def test_find_profile(tmp_path):
    _write(tmp_path / "ingredients", "niacinamide", "published", "ingredient")
    found = sklib.find_profile(tmp_path, "niacinamide")
    assert found is not None and found.name == "niacinamide.md"
    assert sklib.find_profile(tmp_path, "nope") is None
