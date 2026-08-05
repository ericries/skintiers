# Postmortem: verbose supporting prose crowded out the core value

**Date:** 2026-08-05 · **Trigger:** user feedback that the site has "a LOT of verbiage not really needed for the core promise (brand summaries, redundant explanations of studies/ingredients) and relatively fewer product reviews, thorough tier lists."

## What the core value actually is
Product reviews + evidence tier lists, backed by an ingredient evidence library. Brand/person pages exist to aid **product/ingredient discovery**. Study pages exist so **future agents can analyze a full routine** and see what's true. None of the supporting types are ends in themselves.

## How the drift happened (root causes)
1. **Equal treatment by type.** One daily cron per type, all sharing a single `_fill_template` that asks for a full, writing-guide-grade essay + (for most) an Opus critic. A brand got a founding-history essay; a study got a lay-summary-plus-methods essay — same care as a product review.
2. **Egalitarian cadence + a bad pacing rule.** Daily slots for every type, and a memory that said "steady progress across ALL goals," optimized for *touching every type* over *maximizing core value*.
3. **Thoroughness inflates prose.** The critic/writing-guide loop rewards defensible completeness, so pages re-explain general evidence (hedges, recaps) instead of linking out. Drafter subagents burned 70k–286k tokens per page — a verbose brand/study essay cost what several product reviews or a tier list would.

## The fix (tools, not a mass site rewrite)
- **Per-type scope in `data/cron-roster.yaml` `_fill_template`:** brand ≤180 words / person ≤150 words, drafted **inline** (no subagent, no Opus critic); study = compact structured facts (population/design/n/intervention/result-with-numbers/effect-size/applicability/limitation), not an essay; product/ingredient/list/condition/goal stay core with tight, link-out prose.
- **Cadence:** brand + person crons moved to **weekly**; product stays every 6h; core types stay daily.
- **Harvest bias:** every cron's STEP-2 now biases queued candidates toward **products + ingredients** (grow the catalog).
- **Link out, don't re-explain:** the general case lives on one page; everything else references it in a clause.
- **Memory updated:** `pacing-steady-progress` reframed to the value hierarchy; new `token-efficient-core-value`.

## What we did NOT do
No mass rewrite of existing pages (per the user). Existing brand/study essays stay; the change is forward-looking. Live crons pick up the new roster as they expire (≤7 days) via the watchdog, or on demand.

## Guardrail going forward
Before spending a full drafter+critic pass, ask: does this page type earn it? Products/ingredients/tiers yes; brand/person/study get lean, purpose-scoped treatment.
