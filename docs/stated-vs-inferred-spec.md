# Spec: "Stated Claims vs Inferred Reality" — structured per-product audit

Status: DRAFT SPEC (Wave 3, 2026-08-16). Not built. This scopes the original Phase-0
differentiator (per ROADMAP Phase B) into a concrete, buildable feature. Do brainstorm ->
plan before implementing.

## The idea (unchanged since Phase 0)

Every product page should make one comparison scannable at a glance: **what the product/brand
CLAIMS** vs **what its formulation + the clinical evidence actually SUPPORT**. The delta is the
site's whole value proposition. Today this is only *partially* realized, split across three
places that a reader has to assemble themselves:

- `grades:` frontmatter (per-use `effect`/`evidence` + a prose note) — the "inferred reality"
- the `## Common Marketing Claims` section — the "stated claims", quarantined and rebutted
- `## The Evidence` prose — the reasoning

The feature makes the **stated-vs-inferred delta itself** a first-class, structured, rendered
object, instead of prose the reader has to reconcile.

## Current state (what to build ON, not duplicate)

- Products already carry `grades: [{use, effect, evidence, note}]` (the graded verdict).
- `## Common Marketing Claims` already lists each label/marketing claim with a rebuttal and a
  `[^n]` source (see cosrx-niacinamide-15-serum.md, tower-28-sos-*.md,
  medik8-crystal-retinal-6.md for the mature pattern).
- `build.py` already renders grades as filled segments (see `_ROUTINE_TIERS`, the product
  template's grade rendering) and `render_filter`/`routine_summary` compute strength.
- `sk lint` enforces `check_price_backing`, `check_key_actives`, `check_name_actives`.

DO NOT re-derive grades or re-fetch claims — this feature *structures* what's already there.

## Proposed schema (frontmatter, additive)

Add an optional `claims_audit:` list to product frontmatter. Each entry pairs one STATED claim
with the INFERRED verdict, both already sourced elsewhere on the page:

```yaml
claims_audit:
  - claim: "Clinically proven to reduce sebum by up to 50% in 4 weeks"   # verbatim, from the label/page
    claim_source: "^1"                                                    # footnote the claim is quoted from
    verdict: unsupported        # supported | partly-supported | unsupported | misleading
    inferred: "Manufacturer-run, unpublished, no control arm or methodology disclosed; niacinamide's
      better-evidenced topical uses are barrier/pigment/acne, not a quantified sebum percentage."
    evidence_ref: "^2"          # footnote(s) backing the inferred verdict (optional)
```

Rules (enforced by a new `check_claims_audit` in sklib, wired into `sk lint` + a test):
- Every `claim` string MUST appear verbatim somewhere on the page (reuse the
  `check_price_backing` verbatim-on-page pattern) — no inventing a claim to knock down.
- `verdict` in the fixed enum above.
- `claim_source` and any `evidence_ref` must resolve to a real `[^n]` footnote on the page.
- The audit does not REPLACE `## Common Marketing Claims`; it is the structured index of it.
  (Optionally, later: generate the section prose FROM the audit to keep them in sync.)

## Rendering (build.py + template)

- A compact **"Claims, audited"** table/card near the top of the product page (after the
  blockquote), one row per `claims_audit` entry: the claim (quoted), a colored verdict pill
  (supported=green, partly=amber, unsupported/misleading=red — reuse the semantic colors, NOT
  the accent), and the one-line inferred reality. Rows link to their footnotes.
- A single headline stat the page can show and the Feed/filter can consume: e.g.
  `"2 of 4 label claims unsupported"` — derived, not authored.
- Emit the audit into `products-filter.json` (the filter catalog) so "show me products whose
  key claims are supported" becomes filterable later. This is the payoff: the audit becomes
  queryable, not just readable.

## Guardrails (the usual spine)

- Verbatim claims only; `verdict` must be defensible from the page's own cited evidence — the
  Opus critic re-verifies the audit like any health claim.
- Separate health vs cosmetic (carry the tag from the matching grade).
- Never harsher than the evidence: default to `partly-supported`/`unsupported` over
  `misleading`; reserve `misleading` for a claim that contradicts cited evidence, and only
  with a source.
- Backfill is a CRON job, not a one-shot: a new `claims-audit` fill pass (Sonnet draft from the
  existing `## Common Marketing Claims` + grades, Opus-critic-verified) over published products,
  bounded batches. Most pages already have the raw material.

## Open decisions (settle at plan time)

- Table vs inline-per-claim rendering; where it sits relative to the grades block.
- Whether to auto-generate `## Common Marketing Claims` prose from `claims_audit` (single-source)
  or keep both and lint that they agree.
- The Feed/filter exposure (a "claims audited" badge) — Phase A filter integration.
- Whether ingredient pages get an analogous `claims_audit` (probably not; grades cover it).

## Why now / why this shape

It reuses everything the site already enforces (verbatim-on-page, footnote resolution, grades,
semantic colors, the filter catalog) and turns the site's core editorial act — separating hype
from evidence — into structured data an agent or a filter can consume. That directly serves the
For-Agents skill and the price/evidence filter already shipped.
