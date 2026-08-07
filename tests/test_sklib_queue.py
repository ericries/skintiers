import yaml

import sklib


def test_type_to_list_mapping_covers_all_types():
    assert sklib.TYPE_TO_LIST == {
        "product": "products",
        "ingredient": "ingredients",
        "condition": "conditions",
        "goal": "goals",
        "brand": "brands",
        "person": "people",
        "study": "studies",
        "list": "lists",
    }
    # Inverse is consistent.
    for t, plural in sklib.TYPE_TO_LIST.items():
        assert sklib.LIST_TO_TYPE[plural] == t


def test_queue_path_is_per_type(tmp_path):
    p = sklib.queue_path(tmp_path, "product")
    assert p == tmp_path / "queues" / "products.yaml"
    assert sklib.queue_path(tmp_path, "person") == tmp_path / "queues" / "people.yaml"


def test_load_queue_missing_is_empty(tmp_path):
    assert sklib.load_queue(tmp_path, "product") == []


def test_queue_add_writes_per_type_file(tmp_path):
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is True
    # Written to the plural per-type file.
    f = tmp_path / "queues" / "ingredients.yaml"
    assert f.exists()
    items = yaml.safe_load(f.read_text())
    assert len(items) == 1
    assert items[0]["status"] == "pending"
    assert items[0]["priority"] == 8


def test_queue_add_dedup_within_type(tmp_path):
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is True
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is False
    assert len(sklib.load_queue(tmp_path, "ingredient")) == 1


def test_queue_add_same_name_different_type_is_separate(tmp_path):
    assert sklib.queue_add(tmp_path, "Vitamin C", "ingredient", 7) is True
    assert sklib.queue_add(tmp_path, "Vitamin C", "product", 7) is True
    assert len(sklib.load_queue(tmp_path, "ingredient")) == 1
    assert len(sklib.load_queue(tmp_path, "product")) == 1


def test_load_all_queues_covers_seven_types(tmp_path):
    all_q = sklib.load_all_queues(tmp_path)
    assert set(all_q) == set(sklib.TYPE_TO_LIST)
    assert all(v == [] for v in all_q.values())
    sklib.queue_add(tmp_path, "Retinol", "ingredient", 9)
    assert len(sklib.load_all_queues(tmp_path)["ingredient"]) == 1


def test_queue_next_priority_then_fifo(tmp_path):
    sklib.queue_add(tmp_path, "Low", "ingredient", 3)
    sklib.queue_add(tmp_path, "HighA", "ingredient", 9)
    sklib.queue_add(tmp_path, "HighB", "ingredient", 9)  # tie, added after HighA
    nxt = sklib.queue_next(tmp_path, "ingredient")
    assert nxt["name"] == "HighA"  # highest priority, FIFO tie-break


def test_queue_next_none_when_empty_or_all_done(tmp_path):
    assert sklib.queue_next(tmp_path, "product") is None
    sklib.queue_add(tmp_path, "X", "product", 5)
    sklib.queue_resolve(tmp_path, "X", "product")
    assert sklib.queue_next(tmp_path, "product") is None


def test_queue_next_skips_done_items(tmp_path):
    sklib.queue_add(tmp_path, "Done", "ingredient", 10)
    sklib.queue_add(tmp_path, "Pending", "ingredient", 4)
    sklib.queue_resolve(tmp_path, "Done", "ingredient")
    assert sklib.queue_next(tmp_path, "ingredient")["name"] == "Pending"


def test_queue_resolve_with_type(tmp_path):
    sklib.queue_add(tmp_path, "X", "product", 5)
    assert sklib.queue_resolve(tmp_path, "X", "product") is True
    assert sklib.load_queue(tmp_path, "product")[0]["status"] == "done"
    assert sklib.queue_resolve(tmp_path, "missing", "product") is False


def test_queue_resolve_without_type_searches_all(tmp_path):
    sklib.queue_add(tmp_path, "Shared", "product", 5)
    sklib.queue_add(tmp_path, "Shared", "brand", 5)
    assert sklib.queue_resolve(tmp_path, "Shared") is True
    assert sklib.load_queue(tmp_path, "product")[0]["status"] == "done"
    assert sklib.load_queue(tmp_path, "brand")[0]["status"] == "done"
    assert sklib.queue_resolve(tmp_path, "Shared") is False  # nothing left to change


def test_type_autopublishes():
    # All types now ship live once the critic gate clears (no draft-for-sign-off hold).
    assert sklib.type_autopublishes("product") is True
    assert sklib.type_autopublishes("ingredient") is True
    assert sklib.type_autopublishes("brand") is True
    assert sklib.type_autopublishes("goal") is True
    assert sklib.type_autopublishes("condition") is True
    assert sklib.AUTOPUBLISH_TYPES == {"product", "ingredient", "goal",
                                       "condition", "brand", "person", "study", "list"}


def _write_legacy(data_dir, items):
    (data_dir).mkdir(parents=True, exist_ok=True)
    (data_dir / "queue.yaml").write_text(yaml.safe_dump(items, sort_keys=False))


def test_migrate_queue_splits_by_type(tmp_path):
    legacy = [
        {"name": "Retinol", "type": "ingredient", "priority": 9,
         "status": "done", "discovered_from": None, "source": None},
        {"name": "CeraVe Cream", "type": "product", "priority": 6,
         "status": "pending", "discovered_from": "Retinol", "source": "url"},
        {"name": "The Ordinary", "type": "brand", "priority": 5,
         "status": "pending", "discovered_from": None, "source": None},
    ]
    _write_legacy(tmp_path, legacy)
    n = sklib.migrate_queue(tmp_path)
    assert n == 3
    ing = sklib.load_queue(tmp_path, "ingredient")
    assert ing[0]["name"] == "Retinol"
    assert ing[0]["status"] == "done"  # done status preserved
    prod = sklib.load_queue(tmp_path, "product")
    assert prod[0]["discovered_from"] == "Retinol"  # all fields preserved
    assert prod[0]["source"] == "url"
    assert sklib.load_queue(tmp_path, "brand")[0]["name"] == "The Ordinary"
    # Legacy renamed.
    assert not (tmp_path / "queue.yaml").exists()
    assert (tmp_path / "queue.yaml.migrated").exists()


def test_migrate_queue_idempotent(tmp_path):
    _write_legacy(tmp_path, [
        {"name": "A", "type": "product", "priority": 5, "status": "pending",
         "discovered_from": None, "source": None},
    ])
    assert sklib.migrate_queue(tmp_path) == 1
    # Second call: legacy gone, no-op returning 0, no duplication.
    assert sklib.migrate_queue(tmp_path) == 0
    assert len(sklib.load_queue(tmp_path, "product")) == 1


def test_migrate_queue_noop_when_absent(tmp_path):
    assert sklib.migrate_queue(tmp_path) == 0


def test_migrate_queue_merges_and_dedups(tmp_path):
    # Pre-existing per-type file with one item.
    sklib.queue_add(tmp_path, "A", "product", 5)
    _write_legacy(tmp_path, [
        {"name": "A", "type": "product", "priority": 9, "status": "pending",
         "discovered_from": None, "source": None},  # dup by (name,type) -> skipped
        {"name": "B", "type": "product", "priority": 3, "status": "pending",
         "discovered_from": None, "source": None},
    ])
    assert sklib.migrate_queue(tmp_path) == 1  # only B new
    names = [it["name"] for it in sklib.load_queue(tmp_path, "product")]
    assert names == ["A", "B"]


def test_profile_counts(tmp_path):
    import frontmatter

    def _mk(sub, slug, typ, status):
        d = tmp_path / sub
        d.mkdir(parents=True, exist_ok=True)
        post = frontmatter.Post(
            "body", name=slug, slug=slug, type=typ, status=status, updated="2026-01-01")
        with open(d / f"{slug}.md", "wb") as f:
            frontmatter.dump(post, f)

    _mk("ingredients", "a", "ingredient", "published")
    _mk("ingredients", "b", "ingredient", "stub")
    _mk("ingredients", "c", "ingredient", "stub")
    _mk("products", "d", "product", "draft")
    counts = sklib.profile_counts(tmp_path, "ingredient")
    assert counts == {"stub": 2, "draft": 0, "published": 1}
    assert sklib.profile_counts(tmp_path, "product") == {"stub": 0, "draft": 1, "published": 0}


def test_page_exists_for_catches_descriptor_names(tmp_path):
    # The dedup guard must catch the "<Existing thing> (descriptor)" harvest pattern,
    # where the queue name is a phrase but the page slug is a clean noun.
    (tmp_path / "ingredients").mkdir(parents=True)
    (tmp_path / "ingredients" / "hydroquinone.md").write_text("---\nslug: hydroquinone\n---\n")
    assert sklib.page_exists_for(tmp_path, "Hydroquinone (topical depigmenting agent)", "ingredient") is True
    assert sklib.page_exists_for(tmp_path, "hydroquinone", "ingredient") is True
    # a genuinely new one is not flagged
    assert sklib.page_exists_for(tmp_path, "Kojic acid (skin brightening)", "ingredient") is False
    # wrong type does not false-match
    assert sklib.page_exists_for(tmp_path, "Hydroquinone", "product") is False
