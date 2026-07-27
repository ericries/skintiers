# Design Spec — Skeptical, Science-First Skincare Directory

**Date:** 2026-07-26
**Status:** Draft for user review
**Working identity:** **SkinTiers.** Repo name `skintiers`, CLI `sk`. **v1 deploys to the
default GitHub Pages URL — no custom domain** (the build workflow omits the CNAME step).
The custom domain is deferred (user is deciding); leading candidates held: `skintiers.com`,
`skintiers.org`, `tiers.skin`. "SkinAtlas" and "actives.skin" were considered and rejected
(see Identity). All name references are centralized in the **Identity** section.

---

## Context — why we're building this

Consumers cannot tell, from packaging and marketing, what a skincare product actually does.
Claims ("clinically proven," "dermatologist-tested," "clean," "reduces wrinkles in 4 weeks")
routinely outrun the evidence, and the honest signal — effect size and evidence quality — is
buried or absent. This project builds a **skeptical, science-first directory** whose entire
job is to help people **sort truth from marketing**: for every product and ingredient, state
what we actually know, graded on a consistent, transparent rubric, every claim cited to
independent primary sources.

It is modeled on `~/Projects/seedlist` (a live, LLM-researched, statically-generated
directory of startup investors) and follows the roadmap in this repo's `meta/` docs. The
infrastructure pattern ports verbatim; the topic, entities, and feeds change. The
anti-hallucination discipline is the product, not a constraint — every past Seedlist failure
traced to an agent inventing data to fill a gap.

## Mission & voice

A skeptical, evidence-first reference that tells people **what we actually know** about
skincare — separating evidence from marketing and grading everything on one consistent
rubric. Trustworthy, plain-spoken, never hype, never fearmongering (explicitly rejects
unscientific "clean beauty" panic).

## Identity

- **Name:** **SkinTiers** — describes the mechanic (we sort products/ingredients into tiers)
  without an obscure word; taps the shareable "tier list" format; accessible and collision-free.
- **Repo:** `skintiers`. **CLI:** `sk`.
- **Hosting (v1):** default GitHub Pages URL, **no custom domain** — build workflow omits CNAME.
- **Domain (deferred):** user deciding; candidates held: `skintiers.com` (consumer canonical),
  `skintiers.org` (OSS), `tiers.skin` (alias). All confirmed available as of 2026-07-26.
- **Rejected:** "SkinAtlas" (collides with SKIN ATLAS NYC, skin.science "The Skin Atlas," and
  the scientific "Human Skin Cell Atlas" term); "actives.skin" (adjacent to "Skin Actives
  Scientific" brand; "actives" is itself jargon).
- **Caveat:** mild sound-alike to the "Skintific" brand; distinct in spelling/sound, low risk.

## The core analytical model — a two-axis, *relative* rubric

Every **product** and every **active ingredient** is graded on two independent ordinal axes:

- **Effect size:** None · Minimal · Modest · Notable · Strong
- **Evidence quality:** Anecdotal · Preliminary · Mixed · Solid · Gold-standard

**Relative, not absolute.** Grades are ranked *within* a Goal or Condition, and always name
the comparators in prose (e.g. "modest effect — larger than niacinamide, smaller than
tretinoin"). We do **not** assign 0–100 numeric scores (avoids fake precision the evidence
can't support; consistent with "never invent numbers / show your reasoning"). A derived
numeric/sortable score may be added later *only* once we have enough consistently-graded
data to compute it defensibly.

This captures the honest truths absolute grading hides: "gold-standard evidence but small
effect" (many peptides) or "only preliminary evidence, but still the best-supported option
for this goal."

## Entity model — seven first-class types

All entity types are simply **folders of markdown files**. "First-class" means it has its own
profile pages and its own research queue; it does not imply top-level navigation.

- **Top-level navigation (4):** Products *(primary entity — richest treatment, landing page)*
  · Ingredients · Conditions (acne, rosacea, …) · Goals (anti-aging, barrier health, …)
- **First-class but link-reached (3, no top-nav):** Brands (portfolio roll-up) · Studies/Papers
  (skeptically-annotated citation targets) · People (dermatologists, aestheticians, credible
  influencers — with a credibility assessment)

**Fine-grained rule:** category labels ("peptides") are *hub pages* that link out to the
specific ingredient profiles (each individual peptide) where the real evidence lives. Always
drill to the finest grain that has its own evidence.

## Data architecture — flat markdown first, schema later

- **Database = git.** Each entity type is a folder (`data/<type>/`); each profile is one
  markdown file of **cited prose**. Every change is a commit with full history.
- **Flat-first, schema-later (explicit user decision):** we do NOT design elaborate per-type
  YAML schemas up front. The main data is flat markdown. The structured/machine-readable
  layer (frontmatter fields, grades-as-data, INCI fields, cross-reference graph, comparators)
  is built *on top of* the flat files later, once real content exists and its shape is obvious.
- **Minimal day-one frontmatter:** `name`, `slug`, `type`, `status`, `updated`, `analyzed`
  (see status ladder below). Everything else stays prose until the structured layer (Phase 3).

## Profile status ladder & freshness display

Every profile carries an **explicit status** so the reader always knows *how "done" the page
is*, and the status is shown as a **prominent badge** on the page:

- **stub** — a placeholder / link target with little or no content. Created **prolifically**:
  whenever research needs to link to something that doesn't exist yet, we spawn a stub so the
  cross-link resolves immediately (and the entity is added to its research queue).
- **draft** — an unsynthesized collection of links / notes / sources; raw material, not yet
  written up.
- **published** — fully synthesized and two-pass reviewed (10/10).

(Additional rungs — e.g. **synthesized** (LLM-written, unverified) or **flagged** (known
problem) — can be added later. v1 uses just stub/draft/published.)
**The site renders every status** (stubs and drafts included) — transparency about maturity is
the point — each clearly badged. Only a truly missing entity (no file at all) degrades to plain
text.

**Freshness — always shown prominently on each profile:**
- **`updated`** — date/time of the most recent change of any kind.
- **`analyzed`** — date/time of the most recent *full LLM summary/analysis* (a whole-page
  rewrite), tracked separately because a page may be regenerated wholesale. `null` for stubs.

## Profile anatomy

**Product profile (the model):**
1. **The Rubric** — the two-axis grade up top, with a one-line justification
2. **What We Actually Know** — the honest synthesis
3. **Evidence, tiered & labeled** — never blended; each tier its own contextualized section:
   Clinical/Scientific → Dermatologist → Aesthetician → Influencer/Anecdote
4. **Manufacturer Claims** — quarantined section, explicitly discounted
5. **Ingredient breakdown** — each active linked to its profile, with its own grade
6. **Comparators** — how it ranks for its Goal/Condition, comparators named
7. **Sources** — every claim footnoted; re-fetched; three-independent-primary rule

Ingredient / Study / Brand / Condition / Goal / Person each get a leaner treatment in the
same spirit (e.g. a Study profile records design, n, effect size, funding source, limitations).

## Sourcing & anti-hallucination (ported from Seedlist, applies from profile #1)

- **Sources-first:** build the verified source list before writing prose; delete any claim
  with no source.
- **Three independent primaries** (entity's own material + second first-party + tier-1
  press/journal) or mark `unresolvable`. Aggregators (Wikipedia, EWG scores, INCIDecoder
  scores, AI summaries) are pointers to follow, never citable themselves.
- Preserve units/concentrations (0.5% w/w stays; no invented conversions).
- Show percentage math inline (`12 of 28 products (43%)`).
- Verbatim quotes only; re-fetch every cited URL to confirm it loads and matches.
- **Two-pass review** (draft → verify) and publish only at 10/10; else `status: flagged`.
- `sk lint` is the automated CI gate (footnotes present, URLs resolve, no dup/dead URLs,
  xref slugs exist) — enforced on PRs.

## Editorial stance & ethics

- **Graded verdicts at the ingredient/claim level** ("no independent trials support this at
  the concentration used"), always cited — but **no singling out of named products/brands as
  "misleading"** beyond what the evidence carries.
- **Medical disclaimer** site-wide and on every Condition page: educational, not medical
  advice; see a dermatologist. (Acne/rosacea/eczema are medical conditions.)
- **"Credible" People criteria:** default = credentialed (derm/PhD) *or* a documented track
  record of citing primary sources; each Person page states *why* they're considered credible
  and how much to trust them.
- **Licensing (proposed):** MIT for code, CC-BY 4.0 for the data (open evidence maximizes
  public benefit and lets others cite us).

## Discovery — per-category research queues

- **One prioritized queue per entity type** (`data/queue-<type>.yaml` or similar).
- **Priority = 1–10 by LLM judgment** of how promising/interesting an item is.
- **Encounter-time enqueue:** the moment any research run hits a novel entity (product, brand,
  paper, ingredient, person), it is added to the right queue immediately. *Any* research can
  add to *any* queue.
- **Products-primary seeding:** the other queues fill mostly from what we meet during product
  research (products drive discovery).
- **One cron per queue,** each pacing slowly through its backlog daily to stay under API
  quotas. A daily watchdog recreates crons (session crons expire after 7 days).

## Freshness feed

- **Flagship intake = new studies/papers** (PubMed / journals / Cochrane), the primary thing
  we want to keep adding to the dataset.
- Also: new products, new credible-influencer/dermatologist posts, and recalls/regulatory
  actions (FDA/EMA).
- A **durable scraper** (GitHub Action, no LLM) drops candidates into the appropriate queues;
  an agent then verifies against the three-source rule and publishes.
- Renders as a reverse-chronological feed page; staleness is the #1 quality signal.

## Routine builder (later-phase interactive feature)

- **Client-side only, URL-addressable.** A user assembles products into AM / PM / weekly /
  custom-frequency slots; the site computes their **coverage** across ingredients, conditions,
  and goals from that routine.
- Purely static: the build emits JSON indices; JavaScript does the rest. State encoded in the
  URL so routines are shareable. Depends on the Phase-3 structured layer.

## Product badges & shareable routine signature (later phase)

A visual/social layer that turns profiles and routines into shareable artifacts — a growth loop.

- **Per-product canonical badge:** every product gets one badge image in a **consistent style
  and format** — a small **square badge** that (a) carries the product's own brand/logo/image,
  (b) uses **color/design to encode the product type** (cleanser vs. moisturizer vs. serum vs.
  sunscreen…), and (c) embeds a **QR code linking to the product's profile page**. Generated at
  build time as a static asset from a single template, so the whole catalog looks like one system.
- **Composite routine signature:** when a user builds their URL-addressable routine, the site
  generates **one composited image** — the concatenation of that routine's product badges in a
  clever, compact layout — as a downloadable PNG. Because routines are client-side/URL-encoded,
  the composite is assembled **client-side (canvas)** from the individual badges referenced by
  the routine state. Purpose: users post it on Reddit/forums as a **signature** to show off (and
  implicitly link back to) their routine — a self-propagating share mechanic.
- **Design considerations (to resolve when built):** badge template + type→color taxonomy;
  QR target (canonical profile URL); deterministic layout for N products; PNG export.
- **IP caveat (important):** badges embed third-party brand logos / product imagery, which
  carries **copyright/trademark** exposure. Nominative/informational use of a product's name and
  a factual product photo is generally defensible, but compositing and redistributing brand
  *logos* at scale is legally sensitive. Decide the imagery policy (own photography vs. official
  product shots vs. text/color-only badges with no logo) before shipping this. Aligns with the
  project's "ask before legal/ethical decisions" rule.

## Tech stack & tooling

- **Static generation:** one hand-written `build.py` + Jinja2 → static `_site/`; filters
  `status: published`; emits HTML pages + JSON indices (search, coverage, feed).
- **Deploy:** GitHub Pages via a push-triggered Action (adapted from
  `meta/reference/seedlist_github_action_build.yml`).
- **CLI:** a single-file `scripts/sk` wrapping the lifecycle (status / lint / build / publish /
  flag / ship / queue-add / post-batch). Built TDD, one subcommand at a time.
- **TDD for all tooling** (pytest): every `sk` subcommand, `build.py`, scrapers, and
  validators are written test-first (red → green → refactor). TDD does NOT apply to the
  markdown *content* (that's governed by the three-source rule + two-pass review).
- **Dependencies:** python-frontmatter, markdown, jinja2, pyyaml, scipy, numpy, + feedparser
  (scraper). Node only if/when the routine builder needs a bundler (prefer vanilla JS).

## Phased rollout — depth before breadth

| Phase | Build | Data shape |
|---|---|---|
| **1 — Flat content + live site** | `products/` + `ingredients/` markdown profiles; simple `build.py`; minimal `sk` (status/lint/build/publish); Pages deploy | flat markdown, ~no schema |
| **2 — Breadth + discovery** | add `studies/ conditions/ goals/ brands/ people/`; per-queue research + crons; studies/papers freshness feed | flat markdown |
| **3 — Structured layer** | layer frontmatter/derived indices onto existing files: grades-as-data, INCI fields, xref graph, comparators | schema on top |
| **4 — Interactivity & sharing** | effect×evidence visual, sorting/comparison, routine builder + coverage, product badges + composite routine-signature image | consumes structured layer |

Same schema throughout; sequenced so early profiles are deep and fully sourced (the meta docs
warn that thin, half-sourced profiles are the #1 quality failure).

## Verification

- **Tooling:** `.venv/bin/python -m pytest tests/ -v` green before every commit.
- **Build:** `python build.py` produces `_site/` with published profiles; broken xrefs render
  as plain text, not errors.
- **Deploy:** the GitHub Action succeeds and the Pages URL serves the profile.
- **Content quality:** `sk lint SLUG` exits 0 (footnotes present, URLs fetch, quotes verbatim,
  percentages show denominators, xref slugs exist, no dup/dead URLs) before any publish;
  two-pass review; publish only at 10/10.

## Open items (not blocking the plan)

1. **Name = SkinTiers** (settled for v1). **Custom domain deferred** — v1 runs on the default
   GitHub Pages URL; user will choose/register a domain later (candidates held).
2. **Repo visibility** — public (required for free Pages) assumed; confirm.
3. **Exact freshness-feed source list** — starter set proposed above; refine in Phase 2.
4. **People-credibility policy** — refine the "credible" bar as we add the first People.
5. **Badge imagery IP policy** — before the badge/signature feature ships, decide how product
   imagery is sourced (own photography vs. official product shots vs. logo-free text/color
   badges) given copyright/trademark exposure on brand logos.

## Non-goals (out of scope)

- No numeric 0–100 scores (until/unless a defensible derived score is possible).
- No user reviews / Reddit anecdote cited *as evidence* (may be described as "claimed").
- No naming specific products/brands as "misleading" beyond the evidence.
- No elaborate per-type schemas before flat content exists.
- No "coming soon" placeholder profiles; no broad-before-deep publishing.
