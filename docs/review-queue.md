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

0. DONE 2026-08-03: **EMBED videos, don't just link them.** The `.vid` card auto-embeds from `videos[].url`
   via build.py `video_embed()` - a responsive YouTube iframe or a TikTok blockquote (+ `embed.js` once per
   page, gated by `needs_tiktok_js`); the attributed text stays and the plain link is the no-JS fallback.
   Live on all existing cards (Wong x2 incl. the TikTok, Ellis, Chemist Confessions). DONE too: the
   person-page "Verified videos from ..." aggregation now embeds as well (YouTube iframes are lazy-loaded;
   the tiktok embed.js is included once per page, gated by needs_tiktok_js over both the videos: and the
   aggregated list).
0. **[2026-08-03] People directory credential tiers.** Grouped by `expertise:` (`PEOPLE_EXPERTISE_ORDER` in
   build.py): Dermatologists / Cosmetic chemists / **Influencers & educators** (the non-credentialed tier -
   claims treated skeptically, credential labeled honestly, product recs suspect). DONE 2026-08-04: split a
   **Licensed estheticians** tier into PEOPLE_EXPERTISE_ORDER and moved Cassandra Bankson + Renee Rouleau there
   (both established licensed estheticians; their stubs' credential will be re-verified when the person cron fills them).
1. **Tier-list format (applies to every tier list):** (a) a click-down summary of the tiers at the top;
   (b) stronger visual separation between items within a tier. Build as a shared convention + CSS.
   **(c) [requested 2026-07-28] Replace bare "See Also" lists of similar items with a consistent
   tier-list.** Wherever a page links a set of comparable things, show them ranked in a tier list, not
   an unordered list — e.g. a retinoids potency tier list at the bottom of every retinoid page, products
   ranked within a category on product pages where applicable. Needs a reusable tier-list component driven
   by data (so the same ranking renders identically across every page that references the set), plus a
   source of truth for each ranking (potency, evidence, etc.).
   STATUS 2026-08-04: the reusable component is buildable but blocked on the ranking DATA (research). Those
   rankings are now QUEUED for the content crons: "Retinoids by potency" + "Best moisturizing ingredients" +
   "Best products for glass skin" (--type list), "Sunscreen UV filters, categorized" (--type ingredient). Build
   the shared tier-list macro + CSS once the first ranked list lands so it has a real consumer to render.
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

### A. Routine visualization (RUDIMENTARY VERSION SHIPPED 2026-08-03)
A `list` of `kind: routine` now gets an at-a-glance dashboard, baked as static HTML by build.py
(`routine_summary()` + the `.routine-dash` block in profile.html), first live on
[[minimal-evidence-led-acne-routine]]. It shows: product count, top-tier count, a tier-distribution bar,
the active ingredients as a whole (chips), what it's good for (chips), and the AM/PM steps with per-step
effect dots. `_site/routines.json` carries the same rollup for a future client-side renderer.

**SCHEMA (LOCKED 2026-08-03).** Two frontmatter fields drive it:
- On the routine list page: `for: [<condition/goal slug>, ...]` (what it targets) and an ordered
  `steps:` list, each `{when: AM|PM, product: <product slug>, role: <short label>, note: <optional>}`.
- On each product: `key_actives: [<ingredient slug>, ...]` — the genuine treatment actives (NOT base
  emollients or comparators). The ingredient union is author-declared via this field, not scraped from
  body links (scraping pulled in petrolatum, comparators, etc.). A product with no leave-on active (e.g.
  a rinse-off cleanser) simply omits it. **Maintenance:** when a product is added/reworked, set its
  `key_actives`; only the 5 products in the acne routine carry it so far, so backfill as routines grow.
Tier distribution and per-step effect come from each product's existing `grades:` (top HEALTH effect),
so those stay auto-synced with no extra fields.

**Updated 2026-08-03:**
- DONE: all 3 routine stubs now live (minimal-acne, rosacea-friendly, oily-skin-korean), each with a
  populated dashboard. key_actives backfilled on every product they use.
- DONE: composite "how well it works" score — `strength` (Strong/Solid/Moderate/Light, mean of products'
  best health effect), rendered prominently and in routines.json. Labeled as a summary of the graded
  products, not a routine trial.
- DONE (user request 2026-08-03): **layered-ingredient counts + "Does not contain" list.** An active in
  more than one of the routine's products shows an "x2 / x3 / x4" badge (e.g. niacinamide x4 in the oily
  routine). A plain "Does not contain" row lists only really-common, household-name actives the routine
  omits (`_NOTABLE_ACTIVES`: Retinoid, Vitamin C, Niacinamide, Exfoliant) — stated neutrally, no
  disclaimer (the user found "Not included" + a disclaimer read as a drawback callout). Azelaic acid and
  SPF were dropped from the list as specialist / not-an-ingredient. In build.py routine_summary + routines.json.
- DONE 2026-08-03: **tier-distribution bar no longer clips labels.** Narrow segments used flex-basis:0 +
  overflow:hidden, so "TOP-TIER x1" showed as "P-TIER". Now segments flex-grow by count but never shrink
  below their text (min-width:max-content, no overflow clip).
- DONE 2026-08-03 (user request): **sunscreen filters grouped by UVB/UVA in the ingredient row.** Filter
  actives (bisoctrizole, octinoxate, etc.) that readers do not recognize by name collapse into ONE compact
  two-line block: "Sunscreen &middot; UVB + UVA" (coverage computed from each filter's UV_FILTERS range,
  links the filter hub) with the actual filter names shown underneath, each linking its own ingredient page.
  build.py routine_summary `filters` = {coverage, entries:[{slug,name}]} + routines.json + .rd-filters css.
  NOTE: the frontmatter key is `entries` not `items` (Jinja resolves `dict.items` to the builtin method).

- DONE 2026-08-03: **product badges.** Each routine step now shows the product's photo at a standardized
  46px square (CSS object-fit crop, no server-side image processing) inside a tier-colored frame
  (top/mid/entry), with a serif monogram fallback when a product has no photo. build.py routine_summary
  passes thumb/monogram/tier_key per step; .rd-step-badge in the template + css.

**Still TODO (heavier, next design week):**
- **Interactive routine builder** (the big one): the URL grammar, codec, code registry, and code-keyed
  `routine-catalog.json` are DONE. Links are clean, compact, COMMA-FREE PATH URLs:
  `r1/aIOU6D/p4Y~56/wM` (19 chars) where `rW` = routine + the base62 code WIDTH for that link (auto-sized to
  the routine's largest code, so a small routine stays width 1 even after the catalog passes 62 products, and
  the width travels in the URL so old links decode forever), `a/p/w` = AM/PM/weekly phase segments, codes are
  FIXED-WIDTH base62 concatenated with NO delimiter (self-delimiting, which is what removes the commas),
  `~N` = weekly cadence. Compactness analysis: base62 codes are the floor; fixed-width auto-sized per link is
  <= the comma form always (shorter at width 1, ties at width 2) and stays unbounded. HOSTING (static, no server
  rewrites): the builder page doubles as `404.html`; GitHub Pages serves it for any `/r1/...` path, and JS
  reads `location.pathname` + the catalog to render (the response carries a 404 status — fine for humans;
  put OG tags in it so link previews still work). DONE 2026-08-04 (MVP): `routine.html` (+ `404.html` copy)
  is a self-contained page (inlined catalog/CSS/JS, `<base href>`) — search -> add to AM/PM -> live dashboard
  (strength, layered actives xN, does-not-contain, UVA/UVB) -> URL updated via replaceState + Copy link. JS
  codec + dashboard mirror routine_string.py / routine_summary, pinned to a shared vectors fixture and verified
  in-browser (search/add/remove, dashboard, and the 404-fallback shared-link pre-load all confirmed). Linked in
  footer nav + a "Build your own" CTA on the routines index. See docs/superpowers/plans/2026-08-04-routine-builder.md.
  DONE 2026-08-04 (feature-complete): weekly (`w`) phase, per-product `~N` cadence (per-step frequency select),
  and step reordering (up/down) added to the builder UI; "open in builder" links on curated routine pages and
  generated OG/share images also shipped. The builder now covers the full URL grammar. (routine_builder_path
  still emits AM/PM only for the curated "open in builder" links, since routine_summary groups steps into
  AM/PM; extending it to weekly is a minor follow-up.)
- DONE 2026-08-04: **Generated icons** (SVG, deterministic) — `gen_icon(seed, monogram)` in build.py renders a
  hue-from-slug gradient tile with the monogram, registered as a Jinja global; used on the routines index.
  Broader rollout (condition/ingredient listing cards without photos) is a cheap follow-up.
- DONE 2026-08-04: **routines index / landing** — `routines.html` (templates/routines_index.html) surfaces each
  published routine's dashboard (strength, product count, sun coverage, good-for, does-not-contain) + footer nav link.
- Consider weighting the composite toward treatment actives vs support products (today it's a flat mean).

### B. Simple infographics
- **Sunscreen filter UV-coverage chart** (STARTED 2026-07-31): a static SVG spectrum (280-400 nm, UVB / UVA-II / UVA-I
  bands + the 370 nm broad-spectrum threshold) showing which wavelengths each filter covers, rendered from a small
  build.py data map onto [[sunscreen-uv-filters]]. First rudimentary version shipped; refine with per-filter
  absorption maxima once sourced from the filter ingredient pages / CIR.
  DONE 2026-08-03: the **per-sunscreen "which filters are present" chart now auto-renders on every Sunscreen
  product page** (build.py `product_uv_filters()` derives the filters from the [[xref]]s the page names, then
  `render_uv_spectrum(subset)`, shown in a `.uv-product` section). Live on eltamd-uv-clear-spf-46,
  beauty-of-joseon-relief-sun-rice-probiotics-spf50, la-roche-posay-anthelios-melt-in-milk-spf-60.
- Other infographic candidates: tier-distribution bars (feeds the routine dashboard), health-vs-cosmetic split, an
  ingredient's product-count. Reuse the same static-SVG + build.py-data pattern.

## FUTURE PHASE (requested 2026-08-04): social sharing
User direction, NOT yet built. Make pages (and especially routines) shareable to social platforms:
- **Open Graph + Twitter Card meta** in base.html `<head>` per page: og:title/description/type/url + a
  per-page og:image (and twitter:card=summary_large_image). Drive title/description off each profile's name +
  standfirst; url off the canonical page URL.
- **Generated share images** (og:image, ~1200x630): reuse the deterministic-SVG approach (gen_icon / the tier
  and dashboard visuals) to bake a static share card per page at build time - for a ROUTINE, render its
  dashboard (strength, product badges, sun coverage) into the card so a shared routine link previews richly.
  SVG -> PNG needs a rasterizer (e.g. a tiny build-time step) since most platforms want PNG/JPG for og:image.
- **Share links/buttons** on each page (and on a built routine URL): prefilled share intents (X, Facebook,
  Reddit, copy-link) using the page's canonical/normal URL. For routines, the shareable URL is already the
  compact query-string builder link.
- Set a sensible `Referrer-Policy` / `<meta name="referrer">` so a shared routine query string does not leak
  via Referer to outbound product links.
Ties into the routine builder (share the routine URL) and the generated-icon work already done.

## FUTURE PHASE (requested 2026-08-03): freshness + news feed that seeds the queues
User direction, NOT yet built. Two linked feeds:

1. DONE 2026-08-03: **a syndication feed of recently added/updated pages.** build.py now emits `_site/feed.xml`
   (RSS 2.0) + `_site/feed.json` (JSON Feed 1.1) from `data/changelog.yaml`, with autodiscovery `<link>`s in
   every page head and a footer RSS link. `render_rss()` / `render_json_feed()` are pure + unit-tested;
   item ids are stable per (date, title) so readers do not re-notify. Slug'd entries deep-link the page,
   the rest point at What's New. (Improvement: pass `--slug` to `sk log` more often so more items deep-link.)

2. IN PROGRESS 2026-08-03: **a news ingester that seeds the queues.** Decision (user, 2026-08-03): *very
   high filter, quality sources only, auto-add* (no human-hold gate; the draft + Opus-critic stage is the
   safety net). First source shipped: **PubMed** via `scripts/ingest_pubmed.py` (NCBI E-utilities, stdlib,
   no key, ToS-friendly). The very-high filter = a small allowlist of top derm/cosmetic journals + Cochrane,
   restricted to RCTs / systematic reviews / meta-analyses, required to be about skin, on a topical-skincare
   topic, with procedures/devices/systemics excluded by title (laser, filler, toxin, oral supplements, etc.),
   English + human + last ~3y. Dedupes by PMID against study pages AND the queue, then auto `queue-add --type
   study` with the PubMed URL. Daily cron 9e24ec40 (8:47 AM, before the 9:09 study-fill cron) runs it and
   commits queue changes; nothing auto-publishes. First manual run auto-added 19 candidates. Pure logic
   unit-tested (tests/test_ingest_pubmed.py).
   REMAINING sources (same pattern, later): reputable product-launch / ingredient / FDA-regulatory news to
   seed `--type product`/`ingredient`/`brand`. Those are messier (ToS, non-structured feeds) - tackle after
   the PubMed study feed has proven itself. Anti-hallucination spine unchanged: news discovers, sources verify.

Open questions for the remaining commercial-news sources: which feeds (and their ToS), and whether the news
feed and the freshness feed share rendering. Scope as its own
project (brainstorm -> spec -> plan) when picked up.

## FUTURE PHASE (requested 2026-08-03): social-media expert pipeline
User direction, NOT yet built: pull practical skincare expertise from short-form video (TikTok, Reels,
YouTube Shorts), especially from dermatologists and cosmetic chemists, and fold it into the site. This is a
multi-component pipeline; scope it as its own project (brainstorm -> spec -> plan) when we pick it up. Sketch:

1. **Discovery.** Find candidate videos/creators (search by handle, hashtag, "routine for <condition>",
   ingredient names). Maintain a seed list of credentialed creators (board-certified derms, cosmetic
   chemists) rather than open-crawling. Feeds a queue like the freshness feed does.
2. **Transcript + extraction.** Pull the transcript (platform captions, or audio -> speech-to-text). An LLM
   pass extracts: named products, named ingredients, the claims made, and any "routine" structure (ordered
   AM/PM steps).
3. **Credibility gate (the hard part).** Two layers: (a) creator-level — credentials verified, cross-checked
   against a credibility rubric; (b) claim-level — EVERY factual claim is checked against the site's existing
   evidence, and anything that contradicts the science we have (e.g. debunked or unsafe advice) is filtered
   out. A video is a CANDIDATE, never evidence: each surviving claim still needs the normal 3-primary-source
   sourcing before it lands on a page. Creators who repeatedly push contradicted claims are excluded.
4. **Incorporation.** Vetted creators become `person` pages (with the credibility assessment + why they are
   trustworthy). Their videos are references/attribution, never primary evidence. Respect platform ToS and
   copyright: summarize and link, do not reproduce the video; observe the one-short-quote limit.
5. **"Routine for X" -> routine page (the killer feature).** A vetted expert's "my routine for <condition>"
   video maps directly onto the routine schema we just shipped: match the named products to site product
   pages (queue any missing), emit a `kind: routine` list with `for:`/`steps:`, and it gets the same
   at-a-glance dashboard (strength, tier split, layered/absent ingredients) — attributed to the creator, with
   each product's own graded evidence doing the load-bearing work. This is where short-form advice becomes
   a durable, checkable page.

Open questions for the brainstorm: which platforms/how to access transcripts within ToS; the exact
credibility rubric and who is on the seed list; how aggressively to auto-reject vs. queue-for-human-review;
how to attribute without over-reproducing copyrighted video. Anti-hallucination spine is unchanged: the
expert lends credibility and discovery, but claims are still verified against primary sources, not the video.
