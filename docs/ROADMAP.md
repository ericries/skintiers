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
- **Concern-based navigation.** DONE (commit 0cc2044): every condition/goal page now has a
  'Products with these actives' section - the published products whose key_actives match
  the page's graded ingredient tier list, grouped by strongest active. Pure build-time
  derivation, no JS. "I have melasma -> here are products with the evidence-backed actives."
  Homepage builder hero + sticky-header scroll fix also done (d9b8b53).
- **Raw filter/search ("tier-1 vitamin C under $30").** DEFERRED: needs STRUCTURED PRICE
  (currently prose-only) and per-product concern tags. The concern hubs + category pages +
  the routine builder now cover most of the discovery need without it. Do the price-
  structuring data pass first (a Phase B/C data task) before a raw filter UI is worthwhile.
  Phase A decision layer is substantially shipped: assemble (builder) + discover-by-concern
  (hubs) + browse-by-category (existing).

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
