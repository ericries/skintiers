# Lessons from Phase 1 — build, first content, and the review loop

**Date:** 2026-07-27

## What went well
- TDD tooling (`sklib`/`sk`/`build.py`) shipped clean: 48 tests; `lint` + `verify` gates.
- Data-as-git + flat-markdown-first worked; "schema later" avoided premature abstraction.
- Anti-hallucination discipline held under autonomy: subagents tempered grades, flagged
  same-cohort evidence, omitted 404'd/paywalled sources rather than guessing, and refused to
  overclaim — one even overrode an instruction ("retinol underperforms") as unsupported.
- The critic + rubric + `sk verify` caught a real load-bearing defect (a misquote) on live content.
- Autonomous crons made steady, safe progress; the review→feedback→research loop closes gaps.

## What went wrong
1. **A misquote reached the PUBLISHED, live flagship** — the word "similar" was interpolated into
   a Griffiths quote. Caught only by the critic (which re-fetches sources), not by lint/verify.
2. **"Independently replicated" overstated independence** — two cited RCTs shared authors/cohort;
   the "3 *independent* primaries" rule wasn't verified at draft time.
3. **A 0.05%-strength finding was transferred to the 0.025% product** — internal inconsistency.
4. **5 ingredient profiles were published on a quick read, not a critic pass** — they remain
   critic-unverified on the live site and likely carry similar subtle issues.
5. **Fetch fragility** — many primary URLs (FDA/JAMA/Lancet) 403/paywall automated fetch, forcing
   source substitutions; a persistent constraint on automated quote-checking.

## Five whys — root cause of #1 (misquote reached live)
1. Published before any critic re-fetched sources to verify quotes.
2. The publish path was "draft → lint clean → publish"; the critic didn't gate it.
3. Lint/verify are offline/structural; quote fidelity needs fetching the cited source.
4. We conflated structural correctness (lint) with factual fidelity.
5. We built the easy-to-automate gate first and never wired the judgment gate (critic) into publish.

**ROOT CAUSE:** the definition of "publishable" was set by what was easy to automate (structure),
not by what "10/10 correct" requires (source-verified fidelity).

## Rules going forward
- **R1 — Review-before-publish gate.** A profile may be `published` only after a critic review
  with `verdict: publish` (sources re-fetched). Enforced in `sk publish` (blocks without a passing
  `review-log.yaml` entry; `--force` for an explicit, logged human override).
- **R2 — Independence is part of the 3-source rule.** Three primaries must be different
  authors/cohorts; never call same-cohort trials "independent replication."
- **R3 — Strength/dose provenance.** A cross-strength claim must state the strength its evidence
  came from.
- **R4 — Backfill review.** The review cron must vet the 5 batch-published profiles (queued via
  review-log staleness); expect auto-fixes to push over the next cycles.
- **R5 — Fetchable primaries.** When a primary 403s/paywalls, cite a fetchable equivalent
  (DailyMed, PMC) and flag; prefer sources the critic can actually re-verify.
- **R6 — Scope the uncited-stat check.** `sk verify` flags uncited statistics only in
  evidence-bearing sections (Rubric / Evidence / What We Actually Know), not in recap sections
  (Uses / Comparators), to cut false positives.

## Tool changes this iteration
- `sk publish` review-gate (R1). `sk verify` uncited-stat scope fix (R6).
- Next: real `CLAUDE.md` encoding the schema + the review-before-publish workflow (after Phase 2
  schema is set); evaluate moving the autonomous loop to durable GitHub Actions now the repo is public.
