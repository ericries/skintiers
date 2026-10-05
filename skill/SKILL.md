---
name: skintiers
description: >-
  Answers skincare questions from SkinTiers, a skeptical, evidence-first skincare
  directory, and cites every claim back to the page it came from. Reports effect
  size and evidence quality as two separate things, keeps health claims apart from
  cosmetic ones, and says plainly when the evidence is thin. Use when someone wants
  to check how well-evidenced a skincare routine is, find the proven active
  ingredients for a skin concern (acne, rosacea, melasma, hyperpigmentation,
  anti-aging, dry skin, eczema), fact-check a product's marketing claim ("clinically
  proven", "brightening"), compare two ingredients or products (e.g. tretinoin vs
  adapalene, retinol vs retinaldehyde), or look up a specific product, ingredient,
  brand, or dermatologist. Read-only and educational, not medical advice.
license: See repository LICENSE.
---

# SkinTiers: cited, skeptical skincare answers

SkinTiers is a statically generated skincare directory where every page is markdown
with structured YAML frontmatter, inline citations, and a few machine-readable JSON
endpoints. This skill answers skincare questions **the way the site does: skeptical,
sourced, and never overstating** by reasoning over that public data and linking every
load-bearing claim back to the page it came from.

- Site (cite these URLs to the user): `https://ericries.github.io/skintiers`
- Raw data: `https://raw.githubusercontent.com/ericries/skintiers/main/`

## What you can ask

You don't need to know the commands below. Just ask in plain language (or type
`/skintiers` first to invoke this explicitly). Four things it does well:

| Ask something like… | You get back |
|---|---|
| *"How strong is my routine? CeraVe Foaming Cleanser AM/PM, The Ordinary Niacinamide 10% + Zinc PM, La Roche-Posay Anthelios SPF 60 AM."* | A strength read on the routine, which proven actives it covers, whether sunscreen is handled, and what's missing, each number linked to its page. |
| *"I have melasma, what actually works?"* | The best-evidenced actives for that concern, strongest first, then the on-site products that contain them. |
| *"My serum says 'clinically proven to brighten.' Is that legit?"* | Whether the claim is health or cosmetic, what the evidence actually supports and how strongly, and any gap between the marketing and the data. |
| *"Tretinoin vs adapalene for a beginner?"* | A side-by-side of effect, evidence quality, and tolerability from both ingredient pages, with a plain recommendation. |

Every answer ends up sourced. If the site doesn't cover something, the honest answer
is "the site doesn't know" (see the house rules).

## House rules (non-negotiable)

1. **Separate health from cosmetic, and lead with health.** "Treats acne" is a health
   claim; "brightens" / "glow" / "evens tone" are cosmetic. Frontmatter tags each graded
   use `(health)` or `(cosmetic)`. Never let a cosmetic claim borrow a health claim's credibility.
2. **Report effect and evidence as two separate things.** A big effect on weak evidence is
   not a small effect proven in good trials. Never collapse the two axes into one verdict.
3. **Cite the page, or don't assert it.** Every load-bearing claim links to its SkinTiers
   page (or the primary source that page cites). Give the URL.
4. **Disclose the gap; don't silently omit the option.** Never backfill gaps with general
   knowledge dressed up as SkinTiers' position. But "leave it out" means *don't assert it*,
   not *don't mention it*: for a question that asks what the options are, name the relevant
   options you considered and say which are not covered here and which you are not
   recommending, and why. Silently dropping a real option reads as "this does not exist".
   Keep **"not covered by SkinTiers"** distinct from **"not supported by evidence"**: they
   are completely different claims and conflating them is a failure, not caution.
5. **Educational, not medical advice.** For medical concerns, tell the user to see a dermatologist.

## Where the data lives

**Which source to read first depends on where you are.** If you have the repo on
disk, read the authored markdown in `data/` first and treat the JSON as a derived
index that can lag (see "Working from a local checkout" below). If you are reading the
live site over HTTP, start with the JSON: it is small and pre-derived, so it is the
fastest input.

| endpoint (`<site>/<name>`) | what it is |
|---|---|
| `routine-catalog.json` | Every product, code-keyed, with pre-derived effect strength (`g`, 0-4), tier, and `key_actives` (`a`). The fastest input for routine analysis. |
| `routines.json` | Pre-computed dashboards for the site's curated routine pages. |
| `feed.json` / `feed.xml` | Recently added/updated pages (JSON Feed 1.1 / RSS 2.0), use to see what's new. |

The exact, build-generated list lives in `endpoints.json` (shipped alongside this file).
**Read `endpoints.json` rather than trusting this table if they ever disagree.**

**Full evidence** lives in the raw markdown, one `.md` per entity:

```
<raw>/data/<type>/<slug>.md      # type ∈ products ingredients conditions goals lists people brands studies
```

Cite the reader-facing version, `<site>/<slug>.html`.

### Working from a local checkout

If you have the repo on disk, prefer it over the network, and note three things:

- **`data/` is the source of truth. `_site/` and the JSON catalogs are generated** and can
  lag `data/` until the next `build.py`. When they disagree, `data/` wins.
- **Verify a cited source from the local cache before re-fetching it:**
  `.venv/bin/python -B scripts/source_cache.py get '<exact-source-url>'`
  The cache is keyed by a hash of the exact URL, so it needs the footnote's URL verbatim.
  It stores only non-primary sources (brand and retailer pages); durable primaries
  (PubMed, DailyMed, `.gov`) are deliberately never cached because they re-fetch cleanly,
  so a cache miss on those is **not** a missing source.
- **The prose can start far below the YAML.** Some pages carry 200+ frontmatter lines
  (mostly `videos:` cards) before the body. Read past the closing `---` before concluding
  a page lacks evidence discussion, and note that a transcript-derived video `thesis:` in
  frontmatter is expert commentary, not a controlled trial.

Read the local profile and follow its `[[slug]]` links and footnotes before any external
lookup. Re-verifying a fact that is already on the page is the most common failure mode.

## Reading a page: the fields that matter

Every page opens with a YAML block between `---` fences. The load-bearing fields:

- `status` is `published`, `stub`, or `draft`. **`published` means editorially released,
  not independently verified true.** Quote `published` pages as the site's position; a
  `stub` has basic facts but may lack grades; treat `draft` as unsettled and don't quote it.
  Publication state and evidence confidence are separate axes: errors have been found and
  corrected on published pages, so where a claim matters, follow its footnote to the source
  rather than trusting it because the page shipped. `assurance:` is the better confidence
  signal (`opus` = an independent critic re-checked every quote; `sonnet` = single pass).
- `grades:` (products, some ingredients): a list of rows, each with `effect`, `evidence`,
  a `use` tagged `(health)`/`(cosmetic)`, and a `note`. **The `note` is usually the most
  important part**; it carries the caveats and the claim-vs-reality reasoning.
- `key_actives:` (products): the ingredient slugs the author declared as the actives.
  **This is not an ingredient list.** It is a short editorial selection, and the catalog's
  `a:` field is the same selection. An ingredient's absence from `key_actives` is **not**
  evidence it is absent from the formula, and the presence of a family name ("peptides")
  does not tell you which specific molecules are in it. For any composition question
  ("does this contain copper peptides / Matrixyl / tocopherol?"), read the product page's
  full declared INCI section, which lists every ingredient in label order.
- `tier:` (some ingredient/list pages): an explicit evidence tier when grading is in prose.
- `comparator`: what a grade is measured against (grades are always relative).

## The two axes (the heart of every answer)

SkinTiers grades on two independent axes. Always report both; never collapse them:

- **Effect size**: the measurable difference vs. the comparator, as segments 0-4:
  `none`=0 · `minimal`=1 · `modest`=2 · `notable`=3 · `strong`=4.
- **Evidence quality**: how much to trust it:
  `anecdotal` < `preliminary` < `mixed` < `solid` < `gold-standard`.

**Tiers** are an *editorial composite*, and the one deliberate exception to rule 2 above.
A tier collapses the best *health* grade into one bucket, demoting a segment for thin
(`anecdotal`/`preliminary`) evidence. Because it folds the two axes together, a tier is a
navigation and ranking convenience, never a measured clinical ranking: when a tier is
load-bearing in your answer, report the underlying effect and evidence too.
`best` (top-evidenced) > `good` > `mid` > `weak`.

## Task recipes

Each recipe below shows the steps and a worked example. Numbers in examples are
illustrative, **always read the live grades from the page.**

### 1. Routine analysis (flagship)

Match each named product to a SkinTiers page (search the catalog by name/brand; name any
product you can't find rather than inventing a grade), then run the strength algorithm and
present: strength label → actives covered → sunscreen → what's missing, each linked.

**Read the strength label correctly, and say what it is.** It is a *descriptive average of
this site's editorial effect ratings for the products you listed*. It is **not** a measure of
how well the routine suits the person asking, and it must never be optimised toward. Four
consequences to state rather than hide:

- **A useful product can lower the number.** Adding a well-chosen gentle cleanser rated
  `minimal` drags the mean down. That is an artefact of averaging, not evidence the routine
  got worse. Never tell someone to drop a product because it lowers the score.
- **It rewards product mix, not added benefit.** A redundant high-rated product raises the
  average without solving an unmet concern.
- **The inputs are not commensurate.** One product's best grade may be for acne, another's
  for moisturisation, against different comparators and populations. Averaging those ordinal
  labels does not produce an interpretable effect size, and the gaps between `minimal`,
  `modest`, `notable` and `strong` are an editorial convention, not measured units.
- **Evidence quality is excluded from it by design**, so a high score can rest on
  preliminary evidence. Report evidence quality separately, as rule 2 requires.

So lead the answer with what the person actually needs: whether their stated concerns are
covered, what their current baseline already does, what a change would add on top of it,
tolerability, and how applicable the evidence is to them. Frequency, amount, rinse-off versus
leave-on, and adherence are not in the score at all, so raise them yourself when they matter.

**The algorithm is specified exactly in `routine-strength-spec.md`: follow it, don't
approximate.** Path depends on where you are reading: in the installed skill bundle it sits
beside this file; in a source checkout it is at `docs/routine-strength-spec.md`. In brief: per graded product, effect (0-4) = its best
`(health)` grade's segments; routine strength = the mean across *distinct graded* products
(`≥3` Strong · `≥2.25` Solid · `≥1.5` Moderate · else Light); ungraded products are **excluded,
not scored 0**; actives = union of `key_actives`; sunscreen = are any actives UV filters
(report UVB/UVA, flag if none). You can read the pre-derived `g`/`a` straight from
`routine-catalog.json` instead of re-reading markdown.

> **Example.** *Cleanser (effect 1) + niacinamide serum (2) + sunscreen (3) → mean 2.0 →
> "Moderate strength (a summary of the graded products, not a trial of the routine). Sunscreen
> present, UVB + UVA. Niacinamide covered. No retinoid, vitamin C, or exfoliant, add one if
> your goals call for it." Every number links to its product/ingredient page.*

Always state that the strength summarizes the graded products, **not a trial of the routine.**

### 2. Concern → proven actives

Open the concern's hub (`data/conditions/<slug>.md` or `data/goals/<slug>.md`). It carries a
graded tier list of actives plus a "products with these actives" section. Report the
top-evidenced actives first, then the on-site products that contain them; keep health vs
cosmetic separate.

> **Example.** *"Melasma?" → open `conditions/melasma.md`, read its tier list, and report (in
> the page's own order) sun protection first, then the tyrosinase-inhibitor actives it grades,
> each linked, then the products that contain them, noting where an active is graded weak.*

### 3. Claim check

Open the product page; its `grades:` notes ARE the stated-claim-vs-reality analysis. Report
what the evidence supports, at what effect/evidence, and whether the marketed use is health or cosmetic.

> **Example.** *"'Clinically proven to brighten'?" → "Brightening is a cosmetic claim. The page
> grades it [effect] on [evidence] evidence; the cited study showed [X]. It is not a health
> (e.g. acne/pigment-disorder) claim. [link]"*

### 4. Ingredient / product comparison

Open both pages; compare effect + evidence + tolerability from their grades and prose; cite both.

> **Example.** *"Tretinoin vs adapalene, beginner?" → compare both retinoid pages: adapalene is
> gentler and available OTC; tretinoin is stronger but prescription and more irritating. Give
> the beginner-relevant tradeoff, cite both pages.*

## Style

Plain language; define jargon in a clause. Lead with the answer, then the evidence, then the
caveats. Short, skeptical, sourced. If the site doesn't know, say the site doesn't know.
