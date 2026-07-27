# CLI Toolkit Pattern — `scripts/sl`

Every repeated operation should get a subcommand of a single CLI tool. Seedlist calls it `sl`. You can call yours whatever fits your topic (`sk` for skincare, `bg` for board games, etc.). The point is not the name — the point is **one entry point, many subcommands**.

## Why this exists

Without a CLI toolkit, agents write ad-hoc `git commit -m "..."` and hand-craft file edits. This:
1. Triggers permission prompts on every command
2. Introduces inconsistency (different commit message formats, missed lint checks)
3. Duplicates logic across dozens of prompts
4. Makes recovery from failures fragile

With a CLI toolkit:
1. Add each command to `.claude/settings.local.json` allowlist once — no more prompts
2. Every operation goes through the same lint/xref/format checks
3. Agent prompts stay short: "run `sk post-batch`" instead of 10 lines of git commands
4. Bug fixes in one place fix all agents

## Seedlist's `sl` subcommands (reference)

Look at `meta/reference/seedlist_sl.py` for the full source. Highlights:

| Subcommand | Purpose |
|-----------|---------|
| `sl status` | Show pipeline overview (profiles by status, queue depth, git state) |
| `sl queue [TYPE]` | Show pending queue items |
| `sl publish SLUG` | Set profile to published + rebuild + commit + push |
| `sl flag SLUG NOTES` | Set flagged with review notes |
| `sl draft SLUG` | Unpublish back to draft |
| `sl build` | Rebuild site from published profiles |
| `sl ship [MSG]` | git add + commit + push |
| `sl lint SLUG` | Automated citation + structure checker |
| `sl lint-drafts` | Lint all draft profiles |
| `sl publish-clean` | Publish all drafts that pass lint |
| `sl prune` | Remove low-value queue items |
| `sl fix-citations SLUG` | Auto-fix duplicate URLs, orphan defs, renumber footnotes |
| `sl auto-fix SLUG` | Fix citations + missing fields + mechanical issues |
| `sl queue-add NAME ...` | Dedup-safe queue append |
| `sl post-batch` | THE post-agent command: process queue files → auto-fix → xref → lint → publish → rebuild → commit → push |
| `sl batch-publish SLUG...` | Lint+fix+publish specific profiles in one commit |
| `sl xref-backfill-startup SLUG` | Backfill cross-references |
| `sl xref-reconcile-firm SLUG` | Bidirectional consistency check |
| `sl xref-compute-lvi SLUG` | Compute last_verified_investment |
| `sl xref-all` | All xref operations across the repo |
| `sl pending-rounds` | Show scraper output awaiting agent processing |

**The single most important one:** `sl post-batch`. It's the "everything happens automatically after the agent finishes" command. One invocation.

## Design principles

### P1. Single Python file
`scripts/sl` is one Python file (executable, `#!/usr/bin/env python3`). Adding a subcommand = adding a function. No install step, no packaging, no venv complications.

### P2. Same interpreter as build.py
Use the project's `.venv/bin/python3`. Agents should invoke via the full path to avoid picking up system Python.

### P3. Subcommands are functions
Standard `argparse` or a simple `sys.argv[1]` switch. Each subcommand is a top-level function. Testable in isolation.

### P4. Return exit codes correctly
- 0 = success
- 1 = errors (lint failures, missing data)
- 2 = warnings (lint pass but has warnings)
- Non-zero → agent should notice and adapt

### P5. Idempotent by default
`sl publish SLUG` should be safe to run twice. `sl queue-add NAME` should skip duplicates. `sl xref-all` should produce the same result on rerun. Idempotence removes fear.

### P6. Dry-run flags for destructive commands
Any command that removes/overwrites significant data must have `--dry-run` that shows what WOULD happen.

### P7. Every subcommand has a test
See `04_TDD_WORKFLOW.md`. `tests/test_sl_publish.py`, `tests/test_sl_lint.py`, etc.

## Starter subcommands to build first (in TDD order)

1. `sl status` — reads `data/`, prints counts. Zero risk, immediate value.
2. `sl lint SLUG` — parses one profile, checks basic structure. First failing test: "returns exit 1 on a profile missing frontmatter."
3. `sl build` — wraps `python build.py`. Later, add smart rebuild-if-changed.
4. `sl ship [MSG]` — `git add . && git commit -m MSG && git push`.
5. `sl publish SLUG` — flips `status: draft` to `status: published`, then `sl build && sl ship`.
6. `sl queue-add NAME [...]` — dedup-safe append to `data/queue.yaml`.

Add the rest as needed. Do NOT design the whole toolkit up front.

## The `post-batch` command

Once you have 6+ subcommands, wrap them into `sl post-batch`:

```python
def post_batch():
    """The one command every agent runs after a batch of work."""
    # 1. Process any queue additions written to data/.pending-queue-adds.yaml
    process_pending_queue_adds()
    # 2. Process any completions written to data/.pending-completions.yaml
    process_pending_completions()
    # 3. For every draft profile: auto-fix mechanical issues
    for slug in list_drafts():
        auto_fix(slug)
    # 4. Cross-reference reconciliation
    xref_all()
    # 5. Lint everything
    lint_results = lint_all_drafts()
    # 6. Publish anything that passes
    for slug in [r.slug for r in lint_results if r.exit_code == 0]:
        publish(slug, skip_ship=True)
    # 7. Rebuild site
    build()
    # 8. Single commit + push
    ship(msg=f"Post-batch: {len(published)} published, {len(flagged)} flagged")
```

Now the freshness-feed and fact-check cron prompts can end with "run `sk post-batch`" instead of 10 lines of commands. All the concurrency-safe stash/rebase/push logic goes inside `ship()`.

## Add to permissions allowlist

In `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 scripts/sl:*)",
      "Bash(.venv/bin/python3 scripts/sl:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git pull:*)"
    ]
  }
}
```

Every `sl` subcommand is now pre-approved. No permission prompts during autonomous batches.

## Anti-patterns to avoid

- **Do NOT** put `sl` in a subprocess that shells out to itself. Straight function calls.
- **Do NOT** make `sl` interactive (no `input()`). It's for agents.
- **Do NOT** silently succeed on errors. Print clearly, exit non-zero.
- **Do NOT** hide side effects. `sl publish` should print "Published: X. Rebuilt: Y files. Pushed: commit abc123." Not just silently exit 0.
