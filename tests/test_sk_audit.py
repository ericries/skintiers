import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402


def _write(dirpath, slug, status):
    dirpath.mkdir(parents=True, exist_ok=True)
    p = dirpath / f"{slug}.md"
    p.write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n---\n\nBody.\n"
    )
    return p


def _abs(p):
    return str(p.resolve())


def test_untracked_draft_is_flagged(tmp_path):
    # a page that exists on disk but git is not tracking = never committed
    p = _write(tmp_path / "products", "ghost", "draft")
    report = sklib.audit_stuck(tmp_path, tracked_files=set(), review_log={})
    assert ("ghost", "draft") in report["untracked"]


def test_stuck_publish_is_flagged(tmp_path):
    # committed + critic said publish, but still draft = ship-live leak
    p = _write(tmp_path / "products", "leaker", "draft")
    report = sklib.audit_stuck(
        tmp_path,
        tracked_files={_abs(p)},
        review_log={"leaker": {"verdict": "publish"}},
    )
    assert ("leaker", "publish") in report["stuck_publish"]
    # a stuck_publish is NOT also double-counted as an unreviewed draft
    assert report["unreviewed_draft"] == []


def test_unreviewed_draft_listed_separately(tmp_path):
    p = _write(tmp_path / "products", "wip", "draft")
    report = sklib.audit_stuck(tmp_path, tracked_files={_abs(p)}, review_log={})
    assert ("wip", "unreviewed") in report["unreviewed_draft"]
    assert report["stuck_publish"] == []


def test_draft_with_revise_verdict_is_in_flight_not_stuck(tmp_path):
    # a draft the critic sent back is in-flight, not a ship-live leak
    p = _write(tmp_path / "goals", "midreview", "draft")
    report = sklib.audit_stuck(
        tmp_path,
        tracked_files={_abs(p)},
        review_log={"midreview": {"verdict": "revise"}},
    )
    assert ("midreview", "revise") in report["unreviewed_draft"]
    assert report["stuck_publish"] == []


def test_published_and_tracked_is_clean(tmp_path):
    p = _write(tmp_path / "products", "shipped", "published")
    report = sklib.audit_stuck(
        tmp_path,
        tracked_files={_abs(p)},
        review_log={"shipped": {"verdict": "publish"}},
    )
    assert report["untracked"] == []
    assert report["stuck_publish"] == []
    assert report["unreviewed_draft"] == []
