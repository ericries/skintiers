# Lessons: set the standard before scaling (voice edition)

**Date:** 2026-07-27

## What happened
The house voice took ~6 rounds of user correction (judgmental -> neutral, verbose -> tight,
AI-ese removed, uncited claims removed). By then several pages were already published off-voice,
so we had to queue a voice-backfill of 6 pages.

## Five whys -> root cause
Editorial voice and each page's PURPOSE are first-class design decisions. They were left out of
the upfront design (which covered schema, sourcing, and scope), so they were discovered through
post-hoc correction instead of specified first.

## Rules going forward
1. Before generating a new PAGE TYPE (condition, goal, study, person, routine), settle its
   purpose and voice, and publish ONE exemplar for user sign-off, before scaling.
2. Lock a standard before mass generation. Generating first creates a backlog to backfill.
3. When a standard changes, add the affected pages to `data/review-feedback.yaml` so the loop
   backfills them; do not leave off-standard pages live.
4. The canonical standards are `docs/writing-guide.md` and `docs/anti-ai-ese.md`, enforced by
   `sk lint` + `sk verify` + `sk style` + the critic. Read them before authoring or reviewing.

## Self-note (for the agent talking to the user, too)
The anti-AI-ese rules apply to our own messages, not just profiles: plain prose, no em dashes,
no throat-clearing, lead with the point. Concision is respect for the reader's time.
