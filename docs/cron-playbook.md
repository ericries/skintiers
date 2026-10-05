# Cron playbook (shared standing instructions)

Every `[SkinTiers daily fill: <TYPE>]` tick used to carry these instructions inline.
Measured, they were ~1,537 tokens of the ~1,750-token prompt, identical across all
eight fill crons, re-sent on roughly 25 firings a day and then resident in context
for the rest of the session. This file is the single copy. A cron prompt now names
its type and points here.

**Read this file once per session, then service ticks against it.** Nothing here is
optional: it is the quality backbone (scope discipline, fetching order, source
caching, cross-feed) that keeps pages accurate and short. The text below is verbatim
from the prompts it replaces, so no guardrail was reworded in the move.

---

## Purpose and scope (this decides how much to write)

PURPOSE & SCOPE (this decides how much to write — obey it):
- The site's CORE VALUE is product reviews + evidence tier lists, backed by ingredient evidence. Concentrate effort there.
- product / ingredient: CORE. Write the full standard page (product-page standard / prose "## The Rubric"). Worth the depth and the Opus critic. FOR INGREDIENT PAGES: also set a top-level evidence `tier:` frontmatter field (one of best/good/mid/weak) that reflects the page's OWN rubric verdict for a visible skin benefit (best=top-evidenced, good=strong, mid=moderate, weak=minimal/thin). This is the same grade the prose already argues, expressed structurally so the routine builder can group the ingredient by evidence (entity_tier reads it). Do NOT invent a tier; it must match the rubric you wrote/verified. If you only touch an already-published ingredient page that lacks `tier:`, add it from its existing rubric.
- list: CORE (best-of / tier lists / routines). Curatorial over pages that ALREADY exist; keep any tier_list block; be concise, no padding.
- condition / goal: hubs that drive DISCOVERY and host topic tier lists. Keep prose tight; PREFER adding/maintaining a tier_list of the graded items over a long essay.
- brand: DISCOVERY AID ONLY. LEAN, <=180 words: what it is, founder in one line, and a linked list of its products/ingredients ALREADY on the site. NO founding-history or positioning essay. Attribute any brand claim as the brand's own. Its job is to link to products.
- person: DISCOVERY AID ONLY. LEAN, <=150 words: who they are, an honest credential, and the products/videos they point to (linked). NO biography essay. Never state an unverified claim about a living person.
- study: AGENT-FACING INFRASTRUCTURE for routine analysis, NOT a reader essay. COMPACT + structured: one line on what it tested; design/population/n; intervention vs comparator; the PRIMARY result with the numbers; effect size; who it generalizes to; the one key limitation. Do NOT re-tell the ingredient's general story — link out.
NEVER re-explain what another page already owns — link out in ONE clause. Redundant prose is the enemy of this site.
TOKEN DISCIPLINE: bound research hard (stop at the few sources you actually need). For brand/person (lean, low-risk) do the draft INLINE in the main loop — do NOT spawn a subagent. For product/ingredient/study/list, ONE Sonnet subagent may draft; keep its prompt tight and its fetches few.

---

## STEP 1: pick the work (queue, else the maintenance lane)

Prefer an existing stub of your type, else the next queued item
(`.venv/bin/python scripts/sk queue-next --type <TYPE>`). If BOTH are absent, DO NOT
skip idly — an empty queue is the normal steady state of a mature site, not "nothing to do" (user 2026-09-03).
clearing MAINTENANCE task for an EXISTING page (a missing `tier:`, a stale price, a tier_list that omits pages
now linking to it, an unlinked brand product), or prints `NONE`. If it returns a task, DO exactly that one task
— follow its ACTION line literally, KEEP TOKEN USE LOW, operate only on the named page, add nothing gratuitous
(gate to the REAL gap; when in doubt leave it out) — then commit + push and STOP. Only if it prints `NONE` do
you skip this tick. (This supersedes the old CURATE-DON'T-SKIP behavior and applies it, deterministically, to
every type; person/study have no maintenance lane and will print NONE.)
Follow docs/writing-guide.md + docs/anti-ai-ese.md, SCALED to the scope above.

If the maintenance task's candidates genuinely do NOT belong, do not silently skip:
record them in the hub's `tier_list_reviewed:` frontmatter list so the flag
self-clears instead of re-firing forever. (Learned 2026-10-04 after the same
false positives re-fired for weeks.)

---

## Fetching composition, price, INCI and claims

FETCHING (product/ingredient composition, price, INCI, claims): FIRST try `.venv/bin/python scripts/inci_lookup.py "<product name>"` - incidecoder is server-side rendered, so this returns the full ordered INCI + real front-photo URL in one cheap HTTP call and caches it (no Apify needed). It also accepts `--slug <incidecoder-slug>` and `--photo` (photo URL only). Use it for the INCI + photo; you still need the BRAND page for price + marketing claims (incidecoder carries neither). If it prints MISS, then try `curl -sL -A "Mozilla/5.0" <url>`.
If it returns only a JS-SPA shell or a bot-block (Cloudflare/"Robot or human?", empty title, no INCI/price),
use the Apify browser instead: ToolSearch "select:mcp__apify__apify--rag-web-browser,mcp__apify__get-dataset-items",
then call apify--rag-web-browser with {query: <product URL> OR search keywords, maxResults:1-2, outputFormats:["markdown"], waitSecs:45}
and read the result via get-dataset-items {datasetId, fields:"metadata.title,metadata.url,markdown", clean:true}.
It renders JS AND does Google Search (so it also finds the right product URL when web-search is exhausted). Amazon still bot-blocks it; prefer brand sites + reputable reviews. If the item's identity is uncertain/garbled, resolve it via this search before drafting; do NOT draft from an unverified name.

---

## Source caching (required for load-bearing quotes)

SOURCE CACHING: for every source you CITE whose domain is NOT a durable primary (the ones sk verify flags
"verify manually", i.e. sklib classify_domain=='unknown'), pipe the fetched text (or the Apify markdown) to
`python scripts/source_cache.py put <url>` right after fetching it, so it can be verified later even if the
live site blocks a re-fetch. A load-bearing verbatim quote from such a source REQUIRES a cache entry.
(`python scripts/source_cache.py get <url>`), live-fetching only on a cache miss. Keep status:draft during

---

## STEP 2: cross-feed the other queues

STEP 2 (main loop, no subagent): add 2-5 REAL grounded candidates (name + source) to OTHER type queues via
`sk queue-add` — bias toward PRODUCTS and INGREDIENTS (the catalog), since brand/person/study exist mainly to
surface those. CROSS-FEED THE DISCOVERY QUEUES so they do not starve (user 2026-08-25): whenever the page you
just shipped genuinely surfaces a DISCOVERY entity that has NO page yet, queue it too (in addition to the
product/ingredient candidates) — a skin condition or goal the product treats but the site has no hub for
(`--type condition`/`--type goal`), a best-of / tier list the product clearly belongs on that does not exist
yet (`--type list`), or a credible expert/creator named on the page without a person page (`--type person`).
Only queue discovery entities that are genuinely grounded in the shipped page; do NOT invent hubs. Then commit
the shipped page, build, and push (git pull --rebase then push if rejected).

---

## Finish

One-line summary. (What's New is auto-derived from each page's `updated` date - do NOT run `sk log`.)

## Per-type critic requirement

- product / ingredient / condition / goal / study / list: an Opus profile-reviewer
  critic must re-verify every quote and statistic against the real source before
  publish. If no critic is available, self-verify in the main loop, publish with
  `--force`, and set `assurance: sonnet` (never leave `opus` unearned).
- brand / person: no critic. Lean draft inline, own lint/verify/style check, `--force`.

Record every publish in `data/review-log.yaml`, which is a slug-KEYED MAPPING
(not a list). Validate it with `yaml.safe_load` after editing.
