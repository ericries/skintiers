# Review queue — shipped pages & open work

Pages now ship **live** as soon as the critic gate clears (no draft-for-sign-off hold). This is the
running list to skim and give feedback on. Live site: https://ericries.github.io/skintiers/

## Shipped this session — please review

**Products reworked to the new standard** (results-first, quoted editorial opinions, health-vs-cosmetic
grades, side-rail photos, no imperatives):
- skinceuticals-c-e-ferulic · cerave-moisturizing-cream · the-ordinary-multi-peptide-ha-serum
- beauty-of-joseon-relief-sun-rice-probiotics-spf50 · differin-adapalene-0-1-gel
- prequel-lucent-c-vitamin-c-serum · eltamd-uv-clear-spf-46 · la-roche-posay-toleriane
- cosrx-6-peptide-skin-booster-serum (reworked + fixed category-vs-product conflation)
- cerave-hydrating-facial-cleanser (reworked from held draft; first Cleansers-category page)

**Ingredient hubs:** vitamin-c · probiotics (topical + ingested)

**Ingredients filled in the parallel drain (18, published):** ceramides · niacinamide · hyaluronic-acid ·
glycerin · zinc-oxide · colloidal-oatmeal · ferulic-acid · retinol · peptides · bakuchiol · centella-asiatica ·
ascorbic-acid-vitamin-c · salicylic-acid · hydroquinone · tranexamic-acid · avobenzone · snail-secretion-filtrate · copper-peptides

**Goal / condition / study drafts now clearing to publish:** anti-aging · glass-skin · acne ·
rosacea (+ rosacea-erythematotelangiectatic, rosacea-papulopustular) · skin-barrier-strengthening ·
skin-barrier-repair · van-zuuren-2017 study · cerave (brand) · samantha-ellis (person)

**Shipped 2026-07-28/29 (the cleanup + overnight):** rosacea overview + type 1 + type 2 (with "How to know"
openers) · atopic-dermatitis · la-roche-posay-effaclar-mat · some-by-mi-yuja-niacin-serum (all Apify-verified)
· skin-barrier-strengthening · skin-barrier-repair · cerave (brand) · glass-skin · samantha-ellis · a
**What's New** page (footer, `sk log`). **Held:** `acne` (draft — known correctness errors + spend limit;
punch-list in review-log). **Tooling shipped:** `sk audit` (drafted-but-unshipped detector) + build warning;
`sk style` voice deny-list; `sk lint` required-section WARN. **Overnight reports:** `docs/overnight/2026-07-29-*`
(UX audit, QC findings, five-whys, tooling, MORNING-BRIEF).

## Open backlog (in rough priority order)

1. **Tier-list format (applies to every tier list):** (a) a click-down summary of the tiers at the top;
   (b) stronger visual separation between items within a tier. Build as a shared convention + CSS.
   **(c) [requested 2026-07-28] Replace bare "See Also" lists of similar items with a consistent
   tier-list.** Wherever a page links a set of comparable things, show them ranked in a tier list, not
   an unordered list — e.g. a retinoids potency tier list at the bottom of every retinoid page, products
   ranked within a category on product pages where applicable. Needs a reusable tier-list component driven
   by data (so the same ranking renders identically across every page that references the set), plus a
   source of truth for each ranking (potency, evidence, etc.).
2. **anti-aging → hub + child:** make `anti-aging` a general, health-first anti-aging hub (boosting skin
   health / reversing damage, not just cosmetic look); move the perimenopause material to a child page
   `anti-aging-perimenopause`; leave room to add more anti-aging sub-goals to the hub.
3. **glass-skin:** add a best-in-class product tier list for its four elements (hydration, even tone,
   surface smoothness, sun protection).
4. **moisturizing:** add a tier list of moisturizing ingredients/approaches with an example high-rated
   product for each.
5. **Sunscreen filters hub** (categorized mineral vs chemical) + a simple per-sunscreen visual showing
   which filters are present and their coverage (which nm of UV each blocks).
6. **Condition pages:** ~~add the layperson "How to know you have this" opener to rosacea (×3) and acne~~
   DONE for rosacea ×3 (published). acne opener added but the page is HELD (correctness punch-list, see
   review-log/review-feedback).
7. **Barrier tier lists:** ~~critic + publish skin-barrier-strengthening and skin-barrier-repair~~ DONE
   (both published 2026-07-28). Still want the tier-format from #1 applied when it exists.
8. **Fill stub ingredient pages** that these pages lean on: ceramides, niacinamide, hyaluronic-acid,
   glycerin, colloidal-oatmeal, panthenol, ferulic-acid, retinol, peptides, ascorbic-acid.
9. **Rosacea drug pages (queued):** ivermectin, metronidazole, brimonidine, oxymetazoline, doxycycline,
   minocycline; plus the queued study pages.
10. **Batch 3 product rollout** (9 products left on the old structure): anua-azelaic, anua-nano-retinol,
    beauty-of-joseon-light-on, cos-de-baha-az20, cosrx-6-peptide, la-roche-posay-anthelios,
    the-ordinary-copper-peptides, tretinoin-0-025-cream (+ the held cerave-hydrating-facial-cleanser).

11. **Visual design pass (next phase):** evaluate every page type for the "wall of text" feeling. Use
    visual devices and typography/hierarchy (sub-headings, pull-quotes, the tier cards/summary, spacing,
    tables, and where useful simple diagrams or icons) to break pages up and make them easier and more
    fun to read, without sacrificing the evidence-first substance.

## Standing rules locked in this session
Never name the site on a content page. No defensive meta-commentary ("not our verdict", "a matching
INCI is not proof…", "What follows is…"). No process/roadmap language ("queued", "a later phase").
Results-first, jargon in The Evidence. Attribute editorial opinions to quoted credible sources.
Separate health vs cosmetic (lead with health). Never instruct the reader; attribute usage guidance.
Condition pages open with a layperson "How to know you have this". Photos = a side rail, no labels.
Separate the category verdict from the product verdict, and state both. On encountering a new study,
create a stub study landing page (grouping similar studies is fine), then write a very detailed
lay-audience summary. Conditions and Studies are top-level categories with their own queues.

## Research library seeded 2026-07-29 (stubs to fill)
Discovery workflow (Sonnet, grounded) + orchestrator verification seeded cross-referenceable stubs:
- **39 study stubs** (`data/studies/`) — every PMID resolved + title/year cross-checked against NCBI (0 fabrications).
  Clusters: acne systemic/hormonal (spironolactone SAFA, isotretinoin efficacy+psychiatric, COC, minocycline,
  antibiotic resistance), retinoid/photoaging mechanism (Fisher 1996, Griffiths 1993, Weiss 1988, Kafi 2007),
  sunscreen endpoints, pigmentation (cysteamine, kojic acid), barrier/eczema (filaggrin, ceramide, emollient-prevention).
- **15 person stubs** (`data/people/`) — dermatologists (Draelos, Bowe, Lio, Shah, Friedman, Mahto), cosmetic chemists
  (Wong/LabMuffin, Fu+Lu/Chemist Confessions, Romanowski, Dobos, Robinson, Ford), educators (Bankson, Rouleau).
- **10 list stubs** (`data/lists/`) — 7 best-of (azelaic, vitamin C, gentle cleansers, ceramide moisturizers,
  daily sunscreens, niacinamide, peptides) + 3 routines (minimal acne, rosacea-friendly, oily-skin Korean).
Fill each with the detailed-lay-summary (studies) / full profile (people) / ranked tier-list (lists) convention.

## Standing rule added 2026-07-31: ingredient -> product back-links
Ingredient pages should link to the products on the site that contain that ingredient (fine to list
only the high-tier / well-graded ones). Bidirectional maintenance rule (now in docs/writing-guide.md):
when a product is added/reworked, update the ingredient pages it uses; when an ingredient page is
written/updated, add its product back-links. Not done now, applied going forward.
DONE 2026-07-31: auto-generated at build time for ALL cross-reference types (not just ingredient->product).
build.py reverse-indexes every [[xref]] and renders a "Referenced by" section (published referrers only,
grouped by type) on every page. No manual back-link maintenance needed; the one-time backfill is moot.

## Next phase (2026-07-31): routine visualization + simple infographics
User-approved direction. Be judicious on tokens; cheaper models (Sonnet) for drafting, Opus only to verify claims.

### A. Routine visualization (the big one)
A `list` of `kind: routine` gets an at-a-glance dashboard computed from its products:
- **How well it works** (aggregate of the products' two-axis effect x evidence grades)
- **Ingredients as a whole** (deduped union of the products' key actives, each linked)
- **Conditions/goals it serves** (union of what its products/actives are graded for)
- **Tier distribution** (how many products are top-tier vs low-tier)
Technical approach (static site, no backend):
1. **Schema (the key gap):** routine pages need a machine-readable ordered `steps:` list, e.g.
   `steps: [{when: AM|PM, product: <slug>, note: ...}]` (PROPOSE + confirm the exact shape before locking it).
2. **build.py bakes the metadata:** aggregate each routine's steps -> {grade rollup, ingredient union, conditions,
   tier counts} and emit `_site/routines.json` (or per-page data- attributes). build.py already loads grades +
   [[ingredient]] links + the reverse-xref index, so the plumbing exists.
3. **Client JS** renders the dashboard dynamically from the pre-baked JSON (grade bar, ingredient chips, condition
   tags, filtering). No runtime computation.
4. **Generated icons** (SVG, standardized size) for conditions/ingredient classes; **product badges** = each product
   photo cropped/framed to a consistent size/layout with a tier badge overlay.
Start small: schema -> build.py aggregation JSON -> a rudimentary renderer, then icons/badges.

### B. Simple infographics
- **Sunscreen filter UV-coverage chart** (STARTED 2026-07-31): a static SVG spectrum (280-400 nm, UVB / UVA-II / UVA-I
  bands + the 370 nm broad-spectrum threshold) showing which wavelengths each filter covers, rendered from a small
  build.py data map onto [[sunscreen-uv-filters]]. First rudimentary version shipped; refine with per-filter
  absorption maxima once sourced from the filter ingredient pages / CIR, and add a per-sunscreen "which filters are
  present" view on each SPF product page.
- Other infographic candidates: tier-distribution bars (feeds the routine dashboard), health-vs-cosmetic split, an
  ingredient's product-count. Reuse the same static-SVG + build.py-data pattern.
