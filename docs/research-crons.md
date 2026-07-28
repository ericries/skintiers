# SkinTiers research crons (one prioritized queue + one agent per entity type)

Each entity type has its own prioritized queue at `data/queues/<plural>.yaml` and its own
research cron. A cron does ONE bounded increment per firing: take that list's top pending item,
research and draft it, run the critic, and either publish (auto-publish types) or leave a draft
for sign-off (new page types). Session crons are in-memory and expire after 7 days; recreate them
from the template below (a future watchdog can automate this).

## Schedule (local time, off-minutes)
| List | Type | Cron | Cadence | Auto-publish |
|---|---|---|---|---|
| products | product | `23 */3 * * *` | every 3h | yes |
| ingredients | ingredient | `13 2 * * *` | daily | yes |
| conditions | condition | `19 3 * * *` | daily | no (exemplar then pause) |
| goals | goal | `17 4 * * *` | daily | no |
| brands | brand | `23 5 * * *` | daily | no |
| people | person | `29 6 * * *` | daily | no |
| studies | study | `31 7 * * *` | daily | no |

A separate self-healing review cron (`~ */6h`) drains `data/review-feedback.yaml` and re-reviews
published profiles; it is not one of the research crons.

Auto-publish types are `AUTOPUBLISH_TYPES` in `scripts/sklib.py` (currently product, ingredient).
Promote a new type only after the user signs off on its exemplar: add it to that set.

## Cron prompt template (fill `<TYPE>` and `<PLURAL>`)

```
[SkinTiers research cron: <TYPE> list] Make ONE small, bounded increment, then stop.

0. Read docs/writing-guide.md, docs/anti-ai-ese.md, and docs/profile-review-rubric.md and follow
   them exactly (inform not instruct; every claim cited to a named authority; no AI-ese; omit-empty;
   product pages answer only how THIS product compares to peers, general evidence on a linked page;
   one profile = one buyable SKU; product pages REQUIRE verified product image(s)).

1. Pick the top item: `.venv/bin/python scripts/sk queue-next --type <TYPE>`. If it prints "empty:",
   STOP (nothing to do). Then read the gate: `.venv/bin/python scripts/sk gate-check --type <TYPE>`.

2. PAUSE GUARD (new page types only): if gate-check shows `autopublish: false` AND `draft: N` with
   N >= 1, STOP and do nothing — a draft of this type is already awaiting the user's exemplar
   sign-off. Do not draft another until the type is promoted.

3. Dispatch ONE subagent (isolation: worktree) to research + draft that entity SOURCES-FIRST:
   WebFetch and verify every URL; 3 independent PRIMARY sources or mark the claim unresolvable;
   verbatim quotes only; quarantine marketing. Follow the writing guide for a <TYPE> page and match
   the structure of an existing published exemplar of this type. For PRODUCTS: include verified
   product image(s) in `images:` (prefer the manufacturer's own hosted image; confirm the URL
   returns an image before using it) and SKU-level `## Where to Buy` links. Encounter-enqueue any
   novel entity with `sk queue-add "<name>" --type <t> --priority <1-10> --from <slug>`. Run
   `sk lint <slug>`, `sk verify <slug>`, `sk style <slug>` and fix until lint+style are clean and
   verify is clean (a single benign manufacturer/aggregator-URL warning, correctly attributed, is
   acceptable).

4. Critic gate: dispatch the profile-reviewer critic (general-purpose agent told to read
   `.claude/agents/profile-reviewer.md` + the rubric) to re-fetch sources and verify quotes/stats
   and grading. Apply the critic's fixes; re-run if load-bearing.

5. PUBLISH DECISION:
   - If gate-check `autopublish: true` AND critic verdict == publish: add a review-log.yaml entry
     (verdict publish), `.venv/bin/python scripts/sk publish <slug>`, git commit, git push
     (on non-fast-forward: `git pull --rebase` then push; retry once).
   - Otherwise (autopublish false, OR verdict revise/flag): keep `status: draft`, git commit
     LOCALLY (do NOT push), and append an item to data/review-feedback.yaml describing what is
     needed — for a NEW page type: "exemplar drafted for <TYPE>, needs your sign-off before this
     list scales"; for a revise: the critic's punch-list. Do NOT publish.

6. `.venv/bin/python scripts/sk queue-resolve "<name>" --type <TYPE>`; git commit (and push only if
   you published in step 5, same rebase-retry).

NEVER (need the user; note it in data/review-feedback.yaml and STOP): publish a new page type
without sign-off; create or push a repo; make a schema or policy decision. Guard: if the tooling is
broken, do read-only research only and report it. Report a one-line summary.
```
