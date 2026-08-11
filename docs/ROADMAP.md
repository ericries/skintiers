# SkinTiers Roadmap

Living roadmap for the phases after the catalog + evidence engine matured (2026-08-10).
The daily cron fleet handles ongoing content (products/ingredients/studies/conditions/
goals fills, video pull, image population) on autopilot. Human/agent attention goes to
what the crons CAN'T build: the decision layer, high-leverage tier lists, and gates.

## Strategic thesis
We have a superb evidence *library* but a thin decision *layer*. A real person still
can't search, filter by concern, or get a routine. Shift emphasis from "produce more
verified pages" (crons do that) to "make the accumulated evidence usable for decisions."

## Phase A - Ship the decision layer (FLAGSHIP, in progress)
- **Routine Builder.** CORRECTION (2026-08-10): it was already fully built and deployed,
  not unfinished - `assets/routine-builder.js` (search, add, live shareable-URL encoding,
  computed strength/actives/sunscreen dashboard), `render_builder` writes routine.html +
  404.html, catalog carries all 147 products. Verified working live in Chrome. The only
  gap was discoverability. DONE: added a prominent 'Routine builder' CTA to the top nav
  on every page (commit 4750598). REMAINING: (a) a homepage hero that invites building a
  routine; (b) minor UX polish - the sticky header overlaps the search/dashboard on
  scroll; (c) more product images so thumbnails fill in (image cron churning, ~49/147).
- **Concern-based navigation + site search.** Evidence tags (tier, concern, ingredient,
  price) exist; expose them as browse/filter. "Tier-1 vitamin C serums under $30" should
  be answerable. NOT started - the next Phase-A piece after the builder polish.

## Phase B - Deepen core value (ongoing, cron + targeted)
- 4-6 more tier-list ladder families: exfoliating acids (queued), peptides, sunscreen
  filters, ceramides/barrier, humectants-vs-occlusives. Each auto-wires the evidence box
  across its category.
- The "Stated Claims vs Inferred Reality" audit - the original Phase-0 differentiator,
  only partially realized via grades. Make it a structured, scannable per-product feature.

## Phase C - Trust & consistency hardening
- Extend the render-smoke-test: missing-image check, ladder-on-non-forms guard,
  referenced-but-uncharted UV filters, and a cross-page grade-consistency check
  (auto-detect a product page disagreeing with its ingredient page - the Mela B3/Melasyl
  and Cyspera formula_tested classes of bug).
- Freshness crons: price/availability drift re-check; auto-reconciliation sweeps when
  ingredient evidence updates.

## Phase D - Expansion (later, by prior decision)
- Anti-aging non-topical vertical (HRT/procedures/supplements/devices) - own evidence
  discipline.
- Expert pipeline toward 100+ video cards + auto-routine pages from vetted recommendations.

## Learnings that shape how we work
1. Gate at the layer where bugs manifest (render, not just source) -> render-smoke-test.
2. Prefer build-time derivation over manual backfill (five-whys -> auto-derived evidence box).
3. Opus critic where accuracy is non-negotiable (health-claim pages), Sonnet elsewhere.
4. Tier-list ladders are the core-value multiplier (one list lights up a whole category).
5. Cross-page consistency needs automation, not luck.
