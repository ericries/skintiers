# SkinTiers

An evidence-first skincare knowledge base: product reviews and evidence tier lists, backed by ingredient evidence. Authored as markdown in `data/`, built by `build.py` into a static site at <https://ericries.github.io/skintiers>.

**Status: live.** 931 profiles, maintained daily by a fleet of scheduled agent jobs.

| type | count | what it holds |
|---|---|---|
| `data/products/` | 359 | Product reviews, each with graded uses, full declared INCI, and price |
| `data/ingredients/` | 191 | The evidence base per active, with an explicit `tier:` on many |
| `data/studies/` | 130 | Compact structured study records (design, n, result, limitation) |
| `data/brands/` | 67 | Lean discovery pages that link to a brand's products |
| `data/people/` | 60 | Lean creator/expert pages |
| `data/lists/` | 57 | Best-of and tier lists |
| `data/conditions/` | 43 | Condition hubs with topic tier lists |
| `data/goals/` | 24 | Goal hubs (anti-aging, barrier repair, routines) |

## Agents: start here

**Read [`skill/SKILL.md`](skill/SKILL.md).** It is the reader guide: where the data lives, which YAML fields are load-bearing, the two grading axes, and task recipes (routine analysis, concern to actives, claim check, comparisons). This README only orients you; `SKILL.md` is the contract.

The short version of how to answer a question from this repo:

0. **Resolve the name to a file first. Do not grep the tree.** You will be given a
   marketed product name; the repo is organised by slug, and they often differ.
   ```
   .venv/bin/python scripts/sk find "COS de BAHA AZ15"
   .venv/bin/python scripts/sk find "cerave am lotion" --json
   ```
   Scores are explainable: 100 exact slug, 95 exact name, 92 alias, 90 normalised,
   80+ all terms present, under 80 a guess. Reading the published site instead?
   Fetch `lookup.json` once and resolve offline. **A miss means the name is not
   indexed, not that the site lacks the product.**
1. **Read the local profile first.** `data/products/<slug>.md` for composition and price, `data/ingredients/<slug>.md` or `data/studies/<slug>.md` for efficacy.
2. **Follow its `[[slug]]` links and footnote sources** before reaching for the web. Most questions are answerable locally; repeated external lookups for facts already on the page are the most common mistake.
3. **Verify a cited non-primary source from the local cache**, not a re-fetch:
   `.venv/bin/python -B scripts/source_cache.py get '<exact-source-url>'`

### Traps that have actually caused wrong answers

- **`key_actives:` is not an ingredient list.** It is the handful of actives the author declared. An ingredient missing from `key_actives` (or from the catalog's `a:` field) says **nothing** about whether it is in the formula. For composition, read the product page's full declared INCI section.
- **`data/` is the source of truth; `_site/` is generated** and can lag it until the next `build.py`. A rendered tier list also groups by each product's own `grades:`, so its visual order can differ from a list page's `items:` order.
- **The body can sit far below the YAML.** Some pages carry 200+ lines of frontmatter (mostly video cards) before the prose. Read to the closing `---`, then the body; don't judge a page from its first 100 lines.
- **Primary sources are deliberately not cached.** `source_cache.py` skips durable primaries (PubMed, DailyMed, `.gov`) because they can be re-fetched. A missing cache entry for those is not missing evidence.
- **Never conclude a product is absent because you could not find its file.** Slugs are often shorter than the marketed name (`anua-azelaic-acid-serum`). Use `sk find` (step 0) rather than guessing or grepping, and report an unresolved name as unresolved, not as uncovered.

## Humans

Everything is plain markdown and git, so the whole evidence base is reviewable in a diff. Three rules the content is held to: every factual claim traces to primary sources; anything unresolved is marked rather than guessed; the two grading axes (effect size, evidence quality) are always reported separately and never collapsed.

## Layout

```
data/           <- authored profiles (source of truth), one .md per entity
skill/SKILL.md  <- the reader guide for agents  <- READ THIS
docs/           <- working docs (research cache, writing guide, roadmap)
scripts/sk      <- the CLI (find, lint, verify, style, publish, queue-*, add-video)
scripts/        <- support tools (source_cache, inci_lookup, site_health, video_*)
build.py        <- data/ -> _site/
_site/          <- generated output; never edit by hand
research-cache/ <- gitignored verbatim source cache, keyed by URL hash
feedback/       <- review notes from agents consuming this repo
meta/           <- the original bootstrap manual (historical)
```

`CLAUDE.md` holds the operating instructions for the maintaining agent (content standards, cron fleet). It is not the reader guide.
