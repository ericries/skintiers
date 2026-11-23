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

**OUT OF SCOPE FOR NOW: oral supplements and other non-topical anti-ageing.** By prior
user decision, recorded in `docs/ROADMAP.md` under "Phase D - Expansion (later)", the
non-topical anti-ageing vertical (HRT, procedures, supplements, devices) is full-coverage
but a LATER phase with "own evidence discipline", and the site is not in that phase. So:
do NOT open an ingredient, goal or product page for an oral supplement, and do NOT card a
video whose subject is one. A supplement STUDY may still be recorded as a study page when
it lands in the PubMed queue, with the oral route stated plainly so it is never read across
to a topical, as `amin-2025-oral-hyaluronic-acid-meta-analysis` does. Changing this is the
user's call, not a tick's. (Written down 2026-11-02 because three ticks had each
re-decided it separately.)
TOKEN DISCIPLINE: bound research hard (stop at the few sources you actually need). For brand/person (lean, low-risk) do the draft INLINE in the main loop — do NOT spawn a subagent. For product/ingredient/study/list, ONE Sonnet subagent may draft; keep its prompt tight and its fetches few.

---

## STEP 1: pick the work (queue, else the maintenance lane)

FIRST run `.venv/bin/python scripts/sk queue-reconcile` (about 2 seconds). It
closes pending rows whose page already exists, so the queue cannot hand you work
the site has already done. Without it, dedup only ever ran at INSERT time: a row
queued before its page was written stayed pending forever once somebody built
that page by another route, and the staleness was only discovered at the END of a
tick, after the research. A single sweep on 2026-11-06 closed 13 such rows.

Then prefer an existing stub of your type, else the next queued item
(`.venv/bin/python scripts/sk queue-next --type <TYPE>`). Priority runs 1 (most
important) to 10 (least), default 5. If BOTH are absent, DO NOT
skip idly — an empty queue is the normal steady state of a mature site, not "nothing to do" (user 2026-09-03).
Instead run `.venv/bin/python scripts/site_health.py --type <TYPE>`: it returns ONE grounded, bounded, self-
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
If it returns only a JS-SPA shell or a bot-block (Cloudflare/"Robot or human?", empty title, no INCI/price):
APIFY IS THE LAST RESORT AND IT IS METERED. It is the only paid service this project uses, and the account
reached 50% of its monthly limit mid-cycle in 2026-10 with no record of what the spend bought. Gate EVERY call:
1. `.venv/bin/python scripts/apify_gate.py check "<url-or-query>"`. Exit 1 means DO NOT CALL. Ship the page
   without that field and say so plainly, which is always an acceptable outcome ("when in doubt, LEAVE IT
   OUT"; 127 of 369 product pages already carry no price). NEVER work around a DENY by rephrasing to dodge
   the check.
2. On ALLOW: ToolSearch "select:mcp__apify__apify--web-fetch,mcp__apify__apify--rag-web-browser,mcp__apify__get-dataset-items".
   KNOWN URL -> use apify--web-fetch (cheap: no Google, no browser fan-out). Use apify--rag-web-browser ONLY
   for genuine discovery when the URL is unknown, with {query: ..., maxResults:1, outputFormats:["markdown"],
   waitSecs:45}. maxResults:1, never 2 or 3, since each extra result is another full browser page load.
   Read results via get-dataset-items {datasetId, fields:"metadata.title,metadata.url,markdown", clean:true};
   ALWAYS pass fields= and clean:true or the response envelope alone burns thousands of tokens.
3. ONE attempt per item, ever. If it misses, mark the field unresolvable and move on. The gate enforces this.
4. Immediately after the call, whatever the outcome:
   `.venv/bin/python scripts/apify_gate.py log "<url-or-query>" --cu <computeUnits from the run result> --used yes|no`
   Not optional. Without it nobody can tell a call that paid off from one that did not.
Amazon and other known bot-blockers are refused by the gate. Prefer brand sites, primary regulatory sources
(openFDA, DailyMed, accessdata.fda.gov) and reputable reviews. If the identity of the item is uncertain or
garbled, resolve it from a free source first; do NOT draft from an unverified name, and do NOT spend an
Apify call merely to confirm a name.

---

## Source caching (required for load-bearing quotes)

SOURCE CACHING: for every source you CITE whose domain is NOT a durable primary (the ones sk verify flags
"verify manually", i.e. sklib classify_domain=='unknown'), pipe the fetched text (or the Apify markdown) to
`python scripts/source_cache.py put <url>` right after fetching it, so it can be verified later even if the
live site blocks a re-fetch. A load-bearing verbatim quote from such a source REQUIRES a cache entry.
The critic MUST verify cited non-primary sources against the local cache first,
using `python scripts/source_cache.py get <url> --text` for QUOTES (it strips markup, so a
quote that spans an HTML tag still matches; without --text a correct quote reads as a
mismatch) and plain `get <url>` when checking a figure that lives inside a script block,
such as a schema.org price. Live-fetch only on a cache miss. Keep status:draft during
work; publish only once sk lint+verify+style are clean.

---

## STEP 2: cross-feed the other queues

STEP 2 (main loop, no subagent): add 2-5 REAL grounded candidates (name + source) to OTHER type queues via
`sk queue-add` — bias toward PRODUCTS and INGREDIENTS (the catalog), since brand/person/study exist mainly to
surface those. CROSS-FEED THE DISCOVERY QUEUES so they do not starve (user 2026-08-25): whenever the page you
just shipped genuinely surfaces a DISCOVERY entity that has NO page yet, queue it too (in addition to the
product/ingredient candidates) — a skin condition or goal the product treats but the site has no hub for
(`--type condition`/`--type goal`), a best-of / tier list the product clearly belongs on that does not exist
yet (`--type list`), or a credible expert/creator named on the page without a person page (`--type person`).
Only queue discovery entities that are genuinely grounded in the shipped page; do NOT invent hubs. To add a note to an item ALREADY queued, use `sk queue-note "<name>" --type <TYPE> --text "..."` (`--substring` to match loosely) and never hand-edit a queue YAML: a colon in appended prose has silently broken data/queues/products.yaml twice. Then commit
the shipped page, build, and push (git pull --rebase then push if rejected).

---

## Finish

After the push, run `.venv/bin/python scripts/ci_status.py`. It is one cheap
`gh` call and it reports on the LAST COMPLETED run, so it does not wait on your
own. **A push is not a ship.** `build.yml` refuses to deploy unless
`pytest tests/` is green, so a red suite means content lands in the repo and
never reaches the site, with every push still looking successful. That is not
hypothetical: between 2026-10-18 and 2026-11-06 nothing deployed for 19 days
across 96 consecutive failed runs, because two tests went red and no tick ever
looked. If it prints CI RED, STOP doing content work and fix the pipeline, or
report it; shipping more pages into a blocked pipeline just grows the backlog.

If you changed anything under `scripts/`, `templates/`, `tests/`, `build.py` or
`.github/`, run `pytest tests/` BEFORE pushing. A green local suite is necessary but NOT
sufficient: the working tree carries gitignored state (`research-cache/`, `.venv/`,
`_site/`) that a fresh CI checkout does not have. A test that touches any of those
paths passes locally and fails on the runner. On 2026-11-17 a new test armed a
throttle by writing `research-cache/yt-429-cooldown` into the repo and broke the
deploy with FileNotFoundError. Before pushing a test that touches cache or state
directories, move the real one aside (`mv research-cache /tmp/x`) and re-run, or
keep every path the test writes inside `tmp_path`. That is the exact gate CI uses,
and the Oct 18 breakage was a script edit pushed without it. (`githooks/pre-push`
automates this; it is inert unless someone has run `git config core.hooksPath
githooks`.)

One-line summary. (What's New is auto-derived from each page's `updated` date - do NOT run `sk log`.)

## Per-type critic requirement

- product / ingredient / condition / goal / study / list: an Opus profile-reviewer
  critic must re-verify every quote and statistic against the real source before
  publish. If no critic is available, self-verify in the main loop, publish with
  `--force`, and set `assurance: sonnet` (never leave `opus` unearned).
- brand / person: no critic. Lean draft inline, own lint/verify/style check, `--force`.

Record every publish in `data/review-log.yaml`, which is a slug-KEYED MAPPING
(not a list). Validate it with `yaml.safe_load` after editing.

## A CI RED that is not your fault: the Pages artifact metadata race

Seen 2026-11-20, run 44771306633. The job reported FAILURE with
`No artifacts named "github-pages" were found for this workflow run`, which reads
like a build failure and is not one. Before touching anything, read the log:

- `411 passed` — the suite was green
- `built 1277 profiles -> _site` — the build succeeded
- `Artifact github-pages has been successfully uploaded! Final size is 30360713 bytes`
  — the artifact uploaded and finalized, outcome=success

Then, **0.4 seconds later**, `deploy-pages@v4` queried the artifact metadata API and
printed `Found 0 artifact(s)`. Confirm with
`gh api repos/ericries/skintiers/actions/runs/<id>/artifacts`: the artifact is there,
correctly named, not expired. It is GitHub's artifact metadata being eventually
consistent, and `deploy-pages` does not retry a zero result; it fails on the first
fetch. The `error_count: 10` in its config is unrelated to this and buys nothing.

**ROOT CAUSE:** `.github/workflows` runs build and deploy as ONE job, so
`deploy-pages` fires immediately after `upload-pages-artifact` with no gap for the API
to propagate. Four of five runs that day were green, so it is intermittent, not
constant.

**WHAT TO DO:** nothing, usually. Check `gh run list` first — if a later commit has
already triggered a new run, that run deploys the same content and supersedes the
failure, so do NOT re-run and do NOT start editing the pipeline. Only when the failed
run is still the newest does the deploy need re-triggering, and then it must be
`workflow_dispatch` from the Actions tab, NOT `gh run rerun --failed`: the single-job
layout re-uploads the artifact and the deploy then aborts with "Multiple artifacts
named github-pages were unexpectedly found" (already noted in the workflow file).

**THE REAL FIX IS A JUDGMENT CALL, SO IT IS FLAGGED, NOT MADE.** Splitting build and
deploy into two jobs is GitHub's canonical layout and would close the race (job
scheduling latency gives the API time) AND remove the rerun limitation above. It is
not done here because it is the deploy pipeline, it cannot be tested locally, and a
mistake stops the site deploying entirely. That is the user's call.

**A wrinkle on "a newer run supersedes it", learned immediately after writing it.**
The workflow sets `concurrency: group: pages, cancel-in-progress: true`, so every push
CANCELS the run still in flight. Run 44785857007 was cancelled by the very commit that
documented the race above. That is harmless, because the newest run deploys the whole
tree rather than one commit, but it means a burst of commits keeps pushing the actual
deploy back until the last one lands, and the site stays stale for the whole burst.
A `cancelled` conclusion is therefore NOT a failure and needs no investigation: check
whether a newer run exists before reading any log. Confirmed green on 44786290235.

## Never infer absence from a shell glob

On 2026-11-21 I reported 57 broken creator links across 81 pages, filed it at
priority 2, and told the user. It was wrong: all 57 resolve. The error came from
`ls _site/*-videos.html 2>/dev/null | wc -l` returning 0. In zsh a glob that matches
nothing ABORTS the command, so `ls` never ran, `wc` counted an empty stream, and
`2>/dev/null` suppressed the `no matches found` message that would have revealed it.
A second check against `_site` was made before rebuilding, which agreed and reinforced
the mistake.

The rule: an absence claim about files is a claim, so test it the way you would test
any other. Enumerate the candidates and check each path explicitly, in Python, not by
reading a count out of a glob. The same discipline the site applies to ABSENCE CHECKED
footnotes applies to its own tooling, and this is the fourth variant of the unsupported
absence claim already noted in the external-feedback lessons.

## When several long scripts die at once, measure the machine before the code

On 2026-11-23 three mining scripts were killed at the 30-minute background ceiling in
one morning: `video_scan.py --scan`, `discover_hubs.py`, and earlier the same pattern
hit `sk publish` and plain `git commit`. The same video scan had finished in about
seven minutes the day before.

It was not the network and not the scripts. `uptime` showed load averages of 44 to 69
sustained, with macOS `contactsd` alone at 109% CPU and three Chrome processes adding
another 160%, while a probe to the PubMed API returned HTTP 200 in 0.22 seconds. The
work was CPU-starved by processes that have nothing to do with this project.

So when more than one long job dies in a session, spend thirty seconds on `uptime`,
`ps aux | sort -k3 -rn | head`, and one `curl -w "%{time_total}"` against a known-fast
API BEFORE reading any script. A machine under load of 50 makes every tick look like a
tooling bug, and the fix is not in this repo. Note also that the 30-minute background
limit is the maximum the harness allows, so a job that hits it cannot simply be given
more time: either wait for the load to clear or narrow the job (channel_health has
`--skip-tiktok`, scans take `--per`).

## Read the artifact before filing a defect

Three times in two days I asserted a problem that did not exist, each time reasoning
from plausibility instead of opening the thing itself:

1. 57 broken creator links, from a shell glob that silently never ran. All 57 resolved.
2. Two "wrong" reconcile matches. `licorice-root-extract` is NAMED "Licorice root
   extract (glabridin / dipotassium glycyrrhizate)", and `home-led-devices-for-body-acne`
   is NAMED "Home LED devices sold for body acne, by what their clearance actually
   covers". Both matches were right; I had not read either page's `name:`.
3. "Good Genes is lactic, not glycolic, so the row is wrong." Sunday Riley sells BOTH,
   same name and price, distinguished by SKU prefix, and the site already documented it
   and carried the glycolic name as an alias.

Each cost more than the check would have: a retraction, a reverted fix that was
working, and a queue row filed and closed within a day. The shape is always the same,
a confident claim about something one `cat`, `sk find` or `frontmatter.load` away.

So before filing a defect or rejecting a match: open the page and read its `name:` and
`aliases:`. Before claiming a file is missing, test the path. Before calling a match
wrong, check whether the target's own title contains the words you think are absent.
The site demands primary sources for claims about the world; a claim about this repo is
not exempt, and the repo is the easiest primary source there is.
