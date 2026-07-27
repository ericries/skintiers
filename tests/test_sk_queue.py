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


def test_queue_add_and_list(tmp_path):
    assert _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient", "--priority", "9").returncode == 0
    assert _sk(tmp_path, "queue-add", "CeraVe Cream", "--type", "product", "--priority", "6").returncode == 0
    out = _sk(tmp_path, "queue")
    assert out.returncode == 0
    # priority-sorted: higher first
    assert out.stdout.index("Retinol") < out.stdout.index("CeraVe Cream")


def test_queue_resolve_hides_item(tmp_path):
    _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient")
    _sk(tmp_path, "queue-resolve", "Retinol")
    assert "Retinol" not in _sk(tmp_path, "queue").stdout
