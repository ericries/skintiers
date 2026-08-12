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

## Phase E - Agent-native access ("For Agents" page + installable skill) [PLANNED]
Requested 2026-08-11. Rationale: the whole site is already data-as-git markdown with
structured frontmatter + citations, plus machine-readable endpoints (`routines.json`,
`routine-catalog.json`, `feed.json`/`feed.xml`). That makes it uniquely consumable by an
AI agent - a skeptical, cited evidence library an agent can reason over. The decision layer
(Phase A) is a JS routine builder; this phase adds a *conversational* equivalent: talk
through your routine (or concern) with an agent and get the same evidence-graded analysis
inline, no clicking. Goal: a person who has NEVER installed a skill or plugin can be up and
running from one page.

Deliverables:
1. **A "For Agents" page** (`for-agents.html`, linked in nav + footer). Plain-language,
   novice-friendly. Sections:
   - *What this is* - one paragraph: SkinTiers as an agent-readable evidence source, and
     what an agent can do with it (routine analysis, concern -> actives, claim-checking,
     ingredient/product comparisons), all cited back to pages.
   - *Zero-install path* - the lowest bar: point any capable agent at the site. Sample
     lines to paste, e.g. tell the agent: "Read https://ericries.github.io/skintiers/
     for-agents.html and follow it," or hand it the raw data
     (`https://raw.githubusercontent.com/<repo>/main/data/...`) + the JSON endpoints.
   - *Install-the-skill path* - a downloadable skill bundle the site itself publishes
     (see #2). Step-by-step for the two named hosts:
       - **Claude Code**: download, unzip into `~/.claude/skills/skintiers/` (or the
         project's `.claude/skills/`), restart, invoke `/skintiers`. Show the exact
         `curl -O <url>` + `unzip` + `mkdir -p` command lines.
       - **Cowork** (and the general pattern for other agents): the equivalent drop-in
         location + how to point the agent at SKILL.md.
     Written for someone who does not know what a skill *is* - define it in one line
     ("a folder with a SKILL.md that teaches the agent a task"), no jargon assumed.
   - *Sample usage* - real transcripts, at least: (a) THE flagship example - "Here's my
     current routine: CeraVe foaming cleanser AM/PM, The Ordinary buffet, Anthelios SPF60
     AM. What's my evidence strength and what's missing?" -> agent replies with a
     routine-builder-equivalent dashboard (strength tier, actives covered, sunscreen
     present, gaps) computed inline from the same grade data, no JS builder needed;
     (b) "I have melasma, what actives are proven and which products have them?" ->
     concern hub logic; (c) "Is CeraVe's 'clinically proven' claim on X supported?" ->
     stated-vs-inferred; (d) "tretinoin vs adapalene for a beginner" -> ingredient pages.
2. **The installable skill bundle** (published as a build artifact, e.g. `skintiers-skill.zip`
   at the site root, and mirrored as a browsable `skill/` dir). Contents:
   - `SKILL.md` - teaches the agent: where the data lives (raw markdown + the JSON
     endpoints), the frontmatter schema, how grades/tiers/evidence levels encode strength,
     how to REPLICATE the routine-builder analysis inline (the same strength computation
     from `key_actives` + tier grades + sunscreen presence that `routine-builder.js` does -
     factor that logic into a documented, language-agnostic spec so the JS and the skill
     cannot drift), and the non-negotiable HOUSE RULES the agent must honor: separate
     health vs cosmetic claims, never overstate, cite the page, "when in doubt leave it
     out." The skill makes the agent behave like the site: skeptical and sourced.
   - Small helper pointers/scripts as needed (e.g. a documented list of endpoints).
   - Build-time generation + a test that the bundle stays in sync with the live schema.
3. **Keep the routine-builder strength logic single-sourced** so the inline (agent) and
   JS (browser) analyses give the same answer - extract the algorithm into one spec the
   skill references and, ideally, `routine-builder.js` also reads.

Open decisions to settle at execution time: exact skill name/slug; whether to also expose a
tiny read-only HTTP/JSON "MCP-ish" manifest; how much of the catalog to inline in SKILL.md
vs fetch on demand (token budget); the download-artifact hosting detail on GitHub Pages.

## Learnings that shape how we work
1. Gate at the layer where bugs manifest (render, not just source) -> render-smoke-test.
2. Prefer build-time derivation over manual backfill (five-whys -> auto-derived evidence box).
3. Opus critic where accuracy is non-negotiable (health-claim pages), Sonnet elsewhere.
4. Tier-list ladders are the core-value multiplier (one list lights up a whole category).
5. Cross-page consistency needs automation, not luck.
