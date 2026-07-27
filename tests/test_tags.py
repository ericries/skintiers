import frontmatter

import sklib


def _post(slug, name, typ, tags=None):
    meta = {"name": name, "slug": slug, "type": typ, "status": "published",
            "updated": "2026-07-27"}
    if tags is not None:
        meta["tags"] = tags
    return frontmatter.Post("Body.\n", **meta)


def test_tags_frontmatter_still_lints_and_verifies():
    # A profile carrying an extra `tags` field must not break existing checks.
    meta = {"name": "Tretinoin", "slug": "tretinoin", "type": "ingredient",
            "status": "stub", "updated": "2026-07-27", "tags": ["acne", "photoaging"]}
    content = "Placeholder.\n\n## Sources\n[^1]: X. https://nature.com/a\n"
    lint_errors, _ = sklib.check_profile(meta, content)
    verify_errors, _ = sklib.verify_profile(meta, content)
    assert lint_errors == []
    assert verify_errors == []


def test_build_tag_index_maps_tag_to_tagged_posts():
    posts = [
        _post("tretinoin", "Tretinoin", "ingredient", ["acne", "photoaging"]),
        _post("benzoyl-peroxide", "Benzoyl peroxide", "ingredient", ["acne"]),
        _post("moisturizer", "Moisturizer", "product", []),
        _post("niacinamide", "Niacinamide", "ingredient"),  # no tags key
    ]
    index = sklib.build_tag_index(posts)
    assert set(index.keys()) == {"acne", "photoaging"}
    assert [p["slug"] for p in index["acne"]] == ["benzoyl-peroxide", "tretinoin"]
    assert [p["slug"] for p in index["photoaging"]] == ["tretinoin"]


def test_build_tag_index_orders_by_type_then_name():
    posts = [
        _post("zinc", "Zinc", "ingredient", ["acne"]),
        _post("cleanser", "Cleanser", "product", ["acne"]),
        _post("adapalene", "Adapalene", "ingredient", ["acne"]),
    ]
    index = sklib.build_tag_index(posts)
    # product sorts before ingredient (ENTITY_TYPES order), then by name.
    assert [p["slug"] for p in index["acne"]] == ["cleanser", "adapalene", "zinc"]


def test_build_tag_index_empty_for_no_tags():
    posts = [_post("niacinamide", "Niacinamide", "ingredient")]
    assert sklib.build_tag_index(posts) == {}
