"""`sk publish` may only stamp `assurance: opus` on page types whose fill
workflow runs an independent Opus critic (product/ingredient/study). Person,
brand, condition, goal, and list pages have no critic, so a passing review-log
entry is a self-check and must NOT be upgraded to opus.
"""
import importlib.machinery
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_sk():
    loader = importlib.machinery.SourceFileLoader("sk_cli", str(ROOT / "scripts" / "sk"))
    spec = importlib.util.spec_from_loader("sk_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_only_critic_types_earn_opus():
    sk = _load_sk()
    for t in ("product", "ingredient", "study"):
        assert sk._publish_assurance(t, "publish") == "opus", t
    for t in ("person", "brand", "condition", "goal", "list"):
        assert sk._publish_assurance(t, "publish") is None, t


def test_no_passing_verdict_never_bumps():
    sk = _load_sk()
    assert sk._publish_assurance("product", "revise") is None
    assert sk._publish_assurance("study", None) is None
