# Postmortem: drafted pages that never shipped

**Date:** 2026-07-28
**Impact:** 11 pages drafted (and mostly critic-cleared) sat unshipped — 8 uncommitted in
the working tree (would have vanished on a clean checkout), 3 committed but stuck at
`status: draft` after the critic had already cleared them to publish. None were visible on
the live site despite the work being done.

## What happened

The site moved to a **ship-live** model mid-session: pages go live the moment the critic
gate clears, no draft-for-sign-off hold. But the drain workflows deliberately do *not*
publish — they only draft + critic. Publishing (flip `status`, commit, push) is a separate
serial step the orchestrator runs afterward. Across a long session of back-to-back requests,
that publish tail was repeatedly deferred to "after the next thing," and the next thing kept
arriving. The drafted pages accumulated invisibly.

## Five whys

1. **Why did rosacea/barrier/held pages never ship?**
   The draft+critic step finished, but the publish tail (status→published, commit, push) is a
   separate manual step, and a new user request arrived before it ran.

2. **Why did the publish tail get dropped instead of queued?**
   It lived only in my working memory of "things to circle back to." A context switch to the
   next request overwrote that intent with nothing durable tracking it.

3. **Why was there nothing durable tracking it?**
   The pipeline has two states that look identical from the outside — "drafted in the working
   tree" and "published" — and *nothing surfaced the set of pages stuck between them*. The
   review-queue.md backlog *listed* some as "to publish," but that's a prose note, not a check.

4. **Why did the tooling never surface it?**
   There was no command that answered "what did we draft but not ship?" `sk status` counts
   drafts but doesn't distinguish a healthy in-flight draft from a critic-cleared page that
   should already be live, and nothing at all flagged data files git wasn't tracking.

5. **Root cause — why is drafted-but-unshipped invisible by construction?**
   Under the *old* gated model, "draft and hold" was the correct terminal state, so nothing
   was built to detect it. When the model flipped to ship-live, "draft" silently changed
   meaning from "done, awaiting sign-off" to "a leak," but no detector was added to match.
   The gap between an intended workflow (draft → critic → **publish**) and an
   enforced one (draft → critic → *stop*) had no guardrail.

## Fixes (shipped with this postmortem)

1. **`sk audit`** (`scripts/sklib.py:audit_stuck` + `scripts/sk`): reports three leak classes —
   `untracked` (drafted, never committed), `stuck_publish` (critic said publish, still draft),
   and `unreviewed_draft` (drafts legitimately in flight). Exits non-zero on any hard leak
   (untracked or stuck_publish). Covered by `tests/test_sk_audit.py`.
2. **Build-time warning** (`build.py`): every build — including CI on each push — prints a
   WARNING naming any committed page cleared to publish but still draft. A leak can no longer
   hide in a green build.
3. **Definition of done** (`docs/writing-guide.md`): a batch is not done until `sk audit`
   shows **0 hard leaks**. Publishing is part of the batch, not a follow-up.

## Prevention principle

When a workflow's *intended* terminal state and its *enforced* terminal state differ, that gap
needs a detector, not a note. Prose in a backlog is not a guardrail; a command that exits
non-zero is.
