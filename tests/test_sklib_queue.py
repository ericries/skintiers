import sklib


def test_queue_add_and_dedup(tmp_path):
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is True
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is False
    items = sklib.load_queue(tmp_path)
    assert len(items) == 1
    assert items[0]["status"] == "pending"
    assert items[0]["priority"] == 8


def test_queue_resolve(tmp_path):
    sklib.queue_add(tmp_path, "X", "product", 5)
    assert sklib.queue_resolve(tmp_path, "X") is True
    assert sklib.load_queue(tmp_path)[0]["status"] == "done"
    assert sklib.queue_resolve(tmp_path, "missing") is False
