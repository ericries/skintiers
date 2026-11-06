#!/usr/bin/env python3
"""Report whether the deploy pipeline is actually shipping.

Why this exists: between 2026-10-18 and 2026-11-06 the site did not deploy
once. `build.yml` gates deploy on the test suite, two tests went red, and 96
consecutive runs failed. Nothing noticed, because every tick's definition of
done ended at `git push` and no part of the loop ever read CI back. Content
lint passed the whole time; the content was fine and simply never shipped.

This is the missing feedback edge. It is deliberately CHEAP (one `gh run list`
call, no waiting on the current run) so a tick can afford to call it every
time. It reports on the last COMPLETED run, so it catches a breakage within
one tick-cycle rather than blocking for four minutes on the current one.

Exit codes: 0 green, 1 the last completed run FAILED, 2 cannot tell.
"""
import json
import subprocess
import sys

LIMIT = 15


def _runs():
    try:
        out = subprocess.run(
            ["gh", "run", "list", "--limit", str(LIMIT),
             "--json", "status,conclusion,displayTitle,databaseId,createdAt"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"could not run gh ({exc})"
    if out.returncode != 0:
        return None, (out.stderr or "gh failed").strip().splitlines()[0]
    try:
        return json.loads(out.stdout), None
    except json.JSONDecodeError:
        return None, "gh returned unparseable json"


def main():
    runs, err = _runs()
    if runs is None:
        # Never fail a tick just because CI is unreachable; say so and move on.
        print(f"CI STATUS UNKNOWN: {err}")
        return 2
    # `cancelled` is not breakage. build.yml sets concurrency
    # cancel-in-progress, so pushing twice in quick succession cancels the
    # first run; treating that as RED would cry wolf and train the operator to
    # ignore the check. Only success and failure are verdicts.
    done = [r for r in runs
            if r.get("status") == "completed"
            and r.get("conclusion") in ("success", "failure")]
    if not done:
        print("CI STATUS UNKNOWN: no conclusive run in the last "
              f"{LIMIT} (only in-flight, cancelled or skipped).")
        return 2

    latest = done[0]
    streak = 0
    for r in done:
        if r.get("conclusion") == "failure":
            streak += 1
        else:
            break

    if latest.get("conclusion") == "success":
        print(f"CI GREEN: last completed run succeeded "
              f"({latest['createdAt'][:16]}, {latest['databaseId']})")
        return 0

    print(f"CI RED: the last completed run FAILED "
          f"({latest['createdAt'][:16]}, run {latest['databaseId']})")
    print(f"  title: {latest.get('displayTitle', '')[:70]}")
    if streak > 1:
        print(f"  consecutive failures: {streak}")
        print("  NOTHING HAS DEPLOYED since before that streak began. Content "
              "pushed meanwhile is in the repo but not on the site.")
    print("  diagnose: gh run view <id> --log-failed")
    print("  note: `gh run rerun --failed` does NOT work on this single-job "
          "workflow (it uploads a second pages artifact). Re-trigger with "
          "`gh workflow run build.yml` instead.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
