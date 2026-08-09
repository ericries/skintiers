# Queue Drain Plan — complete all queues by EOD Sunday 2026-08-09

**Goal:** take every queue to 0 pending by end of Sunday (quota reset), preserving the
verification bar (Opus critic on all health-claim types; lean self-check for brand/person/list).

## The convergence problem
Every product/ingredient/study fill harvests 2-4 new candidates. A naive drain never
reaches zero. Two mechanisms force convergence:
1. **Dedup guard + accent-folded reconcile every cycle** — the catalog is saturating, so most
   harvested candidates already have pages and are skipped. Net-new per wave is already low
   (~1-3) and decaying.
2. **HARVEST FREEZE at Sunday 12:00.** After the freeze, fills stop `queue-add`-ing to the
   live queues; any genuinely new discovery goes to `data/queues/backlog-future.yaml` (explicitly
   OUT OF SCOPE for "drained"). This turns the remaining queues into a fixed target that can hit 0.

## Scope (pending, 2026-08-08 night)
products 69 · studies 54 · ingredients 51 · brands 28 · people 22 · lists 3 · conditions 0 · goals 0
Plus on-disk stubs: study 32, brand 12, ingredient 7, product 1.
Rough budget: ~20-25M output tokens, ~10-15h wall-clock of parallel waves.

## Priority ordering (degrade gracefully if quota tightens — core value lands first)
1. **CORE catalog: products + ingredients + lists** (the site's promise).
2. **Studies** (agent-facing infrastructure; load-bearing ones first).
3. **Discovery aids: brands + people** (lean, cheap, fast).

## Execution

### Phase 0 — running now
Product waves A+B (16 items), draft→Opus-critic→fix pipeline. Process on completion:
publish per verdict, review-log, harvest, dedup-reconcile, commit, push.

### Phase 1 — CORE catalog (Sat night → Sun AM)
- **Products (~69):** parallel wave-pairs of 8 (16/cycle). Each cycle: accent-folded reconcile →
  pull top real gaps → create stubs with house-aligned slugs (match red-links) → launch 2 waves →
  process → commit/push. ~9 cycles.
- **Ingredients (~58 incl. stubs):** author a `drain-ingredient-stubs` workflow (Sonnet "## The Rubric"
  draft with 3+ PubMed primaries → Opus critic verifies quotes/stats → fix). Batches of 6-8, 2 parallel.
  ~8 cycles. Interleave with product cycles.
- Lists: fill the 3 pending + regenerate tier lists as the catalog fills.

### Phase 2 — Studies (Sun AM)
Author a `drain-study-stubs` workflow (compact structured, Opus critic checks numbers only).
~86 total (pending + stubs). Prioritize studies REFERENCED by existing pages (load-bearing) first.
Batches of 8-10, higher parallelism (compact/cheap).

### Phase 3 — Lists + hub tier lists (Sun midday)
Curatorial (Sonnet, no Opus critic). Fill remaining best-of lists; add/refresh `tier_list` blocks on
condition + goal hubs now that the catalog is full.

### Phase 4 — Discovery aids (Sun afternoon)
Brands (~40) + people (~22): LEAN inline in the main loop (no subagent), batched — <=180 words brand
(what it is + founder line + linked list of its on-site products), <=150 words person (who + honest
credential + linked products/videos). ~15-20k tokens each, fast.

## Quality bar (unchanged)
- Opus profile-reviewer critic on every product/ingredient/study/condition/goal before publish;
  verdict publish → opus assurance, revise-then-fixed → `--force` sonnet.
- Never fabricate; 3+ independent primaries or mark unresolved; unverifiable claim → soften/remove.
- Every page lint+verify+style clean before publish. Cache non-primary sources.
- Dup-guard + accent-folded reconcile each cycle; drafters refuse dup/nonexistent SKUs (done:false) →
  I delete stray stub, repoint links, mark queue done.
- Commit + push per wave (never batch huge uncommitted trees).

## Checkpoints
After each phase: reconcile + recount all queues; report burn-down. A queue at 0 pending = drained.
Stop conditions: all queues 0 (success), or quota exhausted (report exact remaining, core-first so
the valuable work is already landed).
