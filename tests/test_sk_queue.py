import json
import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _sk(tmp_path, *args):
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    return subprocess.run([sys.executable, str(SK), *args], env=env,
                          capture_output=True, text=True)


def test_queue_add_and_list_by_type(tmp_path):
    assert _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient", "--priority", "9").returncode == 0
    assert _sk(tmp_path, "queue-add", "Niacinamide", "--type", "ingredient", "--priority", "3").returncode == 0
    out = _sk(tmp_path, "queue", "--type", "ingredient")
    assert out.returncode == 0
    # priority-sorted: higher first
    assert out.stdout.index("Retinol") < out.stdout.index("Niacinamide")


def test_queue_lists_all_types_grouped(tmp_path):
    _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient")
    _sk(tmp_path, "queue-add", "CeraVe", "--type", "product")
    out = _sk(tmp_path, "queue")
    assert out.returncode == 0
    # all seven type headers present
    for typ in ("product", "ingredient", "condition", "goal", "brand", "person", "study"):
        assert f"== {typ} ==" in out.stdout
    assert "(empty)" in out.stdout  # types with no items
    assert "total pending: 2" in out.stdout


def test_queue_routes_to_correct_type(tmp_path):
    _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient")
    # not shown when filtering a different type
    assert "Retinol" not in _sk(tmp_path, "queue", "--type", "product").stdout
    assert "Retinol" in _sk(tmp_path, "queue", "--type", "ingredient").stdout


def test_queue_resolve_with_type(tmp_path):
    _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient")
    assert _sk(tmp_path, "queue-resolve", "Retinol", "--type", "ingredient").stdout.startswith("resolved")
    assert "Retinol" not in _sk(tmp_path, "queue", "--type", "ingredient").stdout


def test_queue_resolve_without_type(tmp_path):
    _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient")
    assert _sk(tmp_path, "queue-resolve", "Retinol").stdout.startswith("resolved")
    assert "Retinol" not in _sk(tmp_path, "queue", "--type", "ingredient").stdout


def test_queue_next_text_and_empty(tmp_path):
    empty = _sk(tmp_path, "queue-next", "--type", "product")
    assert empty.returncode == 0
    assert "empty: products" in empty.stdout
    _sk(tmp_path, "queue-add", "Top", "--type", "product", "--priority", "9", "--from", "seed")
    _sk(tmp_path, "queue-add", "Low", "--type", "product", "--priority", "2")
    out = _sk(tmp_path, "queue-next", "--type", "product")
    assert out.returncode == 0
    assert "Top" in out.stdout
    assert "Low" not in out.stdout
    assert "seed" in out.stdout  # discovered_from shown


def test_queue_next_json(tmp_path):
    _sk(tmp_path, "queue-add", "Top", "--type", "product", "--priority", "9")
    out = _sk(tmp_path, "queue-next", "--type", "product", "--json")
    assert out.returncode == 0
    item = json.loads(out.stdout)
    assert item["name"] == "Top"
    assert item["priority"] == 9


def test_gate_check_autopublish_and_counts(tmp_path):
    import frontmatter
    d = tmp_path / "products"
    d.mkdir(parents=True, exist_ok=True)
    for slug, status in (("a", "published"), ("b", "draft"), ("c", "stub")):
        post = frontmatter.Post("body", name=slug, slug=slug, type="product",
                                status=status, updated="2026-01-01")
        with open(d / f"{slug}.md", "wb") as f:
            frontmatter.dump(post, f)
    out = _sk(tmp_path, "gate-check", "--type", "product")
    assert out.returncode == 0
    assert "type: product" in out.stdout
    assert "autopublish: true" in out.stdout
    assert "published: 1" in out.stdout
    assert "draft: 1" in out.stdout
    assert "stub: 1" in out.stdout


def test_gate_check_type(tmp_path):
    # Every type now autopublishes once the critic clears.
    out = _sk(tmp_path, "gate-check", "--type", "goal")
    assert "autopublish: true" in out.stdout


def test_queue_migrate_via_cli(tmp_path):
    import yaml
    legacy = [
        {"name": "Retinol", "type": "ingredient", "priority": 9, "status": "done",
         "discovered_from": None, "source": None},
        {"name": "CeraVe", "type": "product", "priority": 6, "status": "pending",
         "discovered_from": None, "source": None},
    ]
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "queue.yaml").write_text(yaml.safe_dump(legacy, sort_keys=False))
    out = _sk(tmp_path, "queue-migrate")
    assert "migrated 2 items" in out.stdout
    assert (tmp_path / "queues" / "products.yaml").exists()
    # second run is a no-op
    assert "nothing to migrate" in _sk(tmp_path, "queue-migrate").stdout


def test_queue_command_auto_migrates(tmp_path):
    import yaml
    legacy = [{"name": "CeraVe", "type": "product", "priority": 6, "status": "pending",
               "discovered_from": None, "source": None}]
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "queue.yaml").write_text(yaml.safe_dump(legacy, sort_keys=False))
    # calling `queue` should migrate legacy data automatically
    out = _sk(tmp_path, "queue", "--type", "product")
    assert "CeraVe" in out.stdout
    assert not (tmp_path / "queue.yaml").exists()
