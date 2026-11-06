"""`ci_status.py` is the feedback edge that was missing when the site stopped
deploying for 19 days, so it has to behave predictably in the three cases that
matter: green, red, and cannot-tell. Cannot-tell must NOT be reported as green,
and must not be reported as red either -- a tick that cannot reach GitHub should
say so and carry on, not halt the fleet.
"""
import importlib.machinery
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "scripts" / "ci_status.py"
    loader = importlib.machinery.SourceFileLoader("ci_status", str(path))
    spec = importlib.util.spec_from_loader("ci_status", loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ci_status"] = mod
    loader.exec_module(mod)
    return mod


def _run(monkeypatch, runs, err=None):
    mod = _load()
    monkeypatch.setattr(mod, "_runs", lambda: (runs, err))
    return mod.main()


def _r(conclusion, status="completed", n=1):
    return {"status": status, "conclusion": conclusion, "displayTitle": "t",
            "databaseId": n, "createdAt": "2026-11-06T01:00:00Z"}


def test_green_when_last_completed_run_succeeded(monkeypatch, capsys):
    assert _run(monkeypatch, [_r("success")]) == 0
    assert "CI GREEN" in capsys.readouterr().out


def test_red_when_last_completed_run_failed(monkeypatch, capsys):
    assert _run(monkeypatch, [_r("failure")]) == 1
    assert "CI RED" in capsys.readouterr().out


def test_an_in_flight_run_does_not_mask_the_last_completed_one(monkeypatch, capsys):
    """The current run is usually still queued when a tick finishes pushing;
    the verdict must come from the last COMPLETED run, not from `None`."""
    runs = [_r(None, status="in_progress", n=9), _r("failure", n=8)]
    assert _run(monkeypatch, runs) == 1
    assert "CI RED" in capsys.readouterr().out


def test_consecutive_failures_are_counted_and_called_out(monkeypatch, capsys):
    """The 19-day outage was 96 straight failures. A streak means a BACKLOG:
    content is in the repo and not on the site, which the operator must be told."""
    assert _run(monkeypatch, [_r("failure", n=i) for i in range(5)]) == 1
    out = capsys.readouterr().out
    assert "consecutive failures: 5" in out
    assert "NOTHING HAS DEPLOYED" in out


def test_streak_stops_at_the_first_success(monkeypatch, capsys):
    runs = [_r("failure", n=3), _r("failure", n=2), _r("success", n=1)]
    assert _run(monkeypatch, runs) == 1
    assert "consecutive failures: 2" in capsys.readouterr().out


def test_unreachable_gh_is_unknown_not_green(monkeypatch, capsys):
    assert _run(monkeypatch, None, err="gh: not found") == 2
    out = capsys.readouterr().out
    assert "UNKNOWN" in out and "GREEN" not in out


def test_no_completed_runs_is_unknown_not_green(monkeypatch, capsys):
    assert _run(monkeypatch, [_r(None, status="in_progress")]) == 2
    out = capsys.readouterr().out
    assert "UNKNOWN" in out and "GREEN" not in out
