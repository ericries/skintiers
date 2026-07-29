# Content QC sweep — findings

**Date:** 2026-07-29 · **Scope:** one bounded adversarial pass over all published pages (95 scanned). Standing rules from docs/writing-guide.md + docs/anti-ai-ese.md.

> Ran during an account spend-limit pause (subagents unavailable). Detection is a deterministic Python sweep; no unsafe auto-fixes were applied, per the 'do not guess' rule. Real findings are escalated to data/review-feedback.yaml.

## Clean (no findings)

- **(a) site self-reference by name:** none.
- **(c) process/roadmap language (queued / later phase / coming soon):** none.
- **(b) defensive meta-commentary:** none genuine. The regex flagged 7 instances of "not a finding of harm" (octocrylene, homosalate, octisalate, octinoxate, avobenzone) — these are substantive statements about FDA data-request status, not editorial meta-commentary about the page. No action.
- **(j) condition pages missing 'How to know you have this':** none.

## Should-fix (escalated — need judgment or careful multi-edit)

### 1. `tretinoin-0-025-cream` fails `sk style` (severity: should-fix)
`sk style` reports en-dash AI-ese throughout and the AI-ese word 'pivotal'. This is an early page that predates style enforcement. Fix needs care: numeric ranges (e.g. `10.28–26.14`, CI values) should become `to`, connector em/en-dashes become periods/commas, and quoted source text must be left verbatim. Not a safe bulk sed. Full de-dash + 'pivotal' rephrase required.

### 2. Product pages missing `## Summary` (severity: should-fix) — 8 pages
The summary-first standard postdates these; each needs a written, source-linked summary (research/judgment, not mechanical). Aligns with review-queue.md #10 (batch-3 rollout):
- anua-azelaic-acid-serum
- anua-nano-retinol-0-3-niacin-renewing-serum
- beauty-of-joseon-light-on-serum-centella-vita-c
- cos-de-baha-az20-azelaic-acid-20-serum
- la-roche-posay-anthelios-melt-in-milk-spf-60
- la-roche-posay-toleriane
- the-ordinary-multi-peptide-copper-peptides-serum
- tretinoin-0-025-cream

### 3. Cross-refs to uncreated pages (severity: nit→should-fix) — 9 targets
These `[[slug]]` references render as plain text today (not broken links / not visible bugs), but they point to pages that do not exist yet. Decision needed per target: create a stub, or unlink. Targets:
- `[[cerave-hydrating-mineral-sunscreen-spf-30-face]]` — referenced by: la-roche-posay-anthelios-melt-in-milk-spf-60
- `[[diethylamino-hydroxybenzoyl-hexyl-benzoate]]` — referenced by: beauty-of-joseon-relief-sun-rice-probiotics-spf50
- `[[diethylhexyl-butamido-triazone]]` — referenced by: beauty-of-joseon-relief-sun-rice-probiotics-spf50
- `[[isotretinoin]]` — referenced by: isotretinoin-sebum-suppression
- `[[neutrogena-ultra-sheer-dry-touch-spf-70]]` — referenced by: la-roche-posay-anthelios-melt-in-milk-spf-60
- `[[perlite]]` — referenced by: la-roche-posay-effaclar-mat
- `[[prequel]]` — referenced by: samantha-ellis
- `[[sebaceous-glands]]` — referenced by: isotretinoin-sebum-suppression
- `[[sebum]]` — referenced by: isotretinoin-sebum-suppression

## Correction: en/em-dash scope

The dash finding spans **16 published pages**, not one. Split by kind:

**Connector dashes (real AI-ese, fix):**
- adapalene (2 connector of 2 total)
- ascorbic-acid-vitamin-c (1 connector of 1 total)
- azelaic-acid (13 connector of 13 total)
- colloidal-oatmeal (2 connector of 2 total)
- cos-de-baha-az20-azelaic-acid-20-serum (2 connector of 2 total)
- hydroquinone (1 connector of 1 total)
- retinoids (1 connector of 1 total)
- salicylic-acid (2 connector of 2 total)
- sunscreen-uv-filters (2 connector of 3 total)
- tazarotene (3 connector of 3 total)
- the-ordinary-azelaic-acid-suspension-10 (2 connector of 2 total)
- tranexamic-acid (1 connector of 1 total)
- tretinoin (2 connector of 2 total)
- tretinoin-0-025-cream (25 connector of 31 total)
- trifarotene (1 connector of 1 total)
- zinc-oxide (1 connector of 1 total)

**Numeric-range en-dashes only (CI values etc.; house style prefers 'to', low severity):**
