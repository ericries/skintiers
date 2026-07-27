# Cron Patterns — Freshness Feed + Fact-Check + Watchdog

Seedlist runs 3 recurring jobs. Copy the pattern; adapt the prompts.

## Overview

| Job | Schedule | What it does |
|-----|----------|--------------|
| Freshness feed monitor | Every 6h at :17 | Scrape sources, verify against 3+ primaries, publish new profiles, update xrefs |
| Fact specificity | Every 4h at :43 | Pick 3 vague/priority facts, verify via 3+ primaries, tighten, mark resolved |
| Watchdog | Daily at 8:03 AM | Run `CronList`, recreate any missing job |

**Two important properties of Claude Code crons:**
1. They are **session-only**. If the Claude Code process dies (restart, crash), the crons die with it.
2. They **auto-expire after 7 days**.

The **watchdog** exists to survive both — a daily job that recreates the other two if they've disappeared.

## Why off-minute times

Every user who asks for "hourly" gets `0 * * * *`. Every user who asks for "9am" gets `0 9 * * *`. The API gets slammed at :00 and :30. Pick minutes like :17, :43, :03 to spread load across the fleet.

## Job 1: Freshness feed monitor

**Schedule:** `17 */6 * * *` (every 6 hours at :17 past the hour)

**Prompt template (adapt for your topic):**

```
Freshness feed sweep. Run `/Users/EricRies2/Projects/<project>/.venv/bin/python3 scripts/scrape_<topic>.py` to refresh `data/pending-<items>.yaml`, then `scripts/sl pending-<items>` to view the queue.

Pick up to 5 high-confidence candidates. Verify each against 3+ primary press sources (the entity's own page + a second first-party source + contemporaneous tier-1 press).

Create profiles at `data/<entity_type>/{slug}.md` with:
- status: published
- YYYY-MM-DD dates
- names-only in table cells (no narrative text)
- PRESERVE original units/currency (€/£/$/₹/CHF — no conversion)

Only use validated slugs in frontmatter cross-references. If a referenced entity has no profile, use the name in body-text tables only and queue the entity.

Also web-search authoritative feeds for today's items (X, Y, Z) — feed must have at least one item from the most recent weekday.

Append touched entity slugs to `data/fact-check-priority.yaml` (use literal `$` not `\$` in reason strings).

Run `python3 build.py`, commit "Feed: [items] (YYYY-MM-DD)", push.

TRIPLE-CHECK every name against the cited primary press — when in doubt, LEAVE IT OUT. Never fabricate. Skip build.py if Bash classifier is blocked — the GitHub Action will build on push.
```

## Job 2: Fact specificity

**Schedule:** `43 */4 * * *` (every 4 hours at :43 past the hour)

**Prompt template:**

```
Fact Specificity Agent. First check `data/fact-check-priority.yaml` for unresolved entries — if present, sweep those first (full fact-check on each touched profile, fix all vague entries, mark resolved).

If empty/all resolved, pick 3 high-priority items from `data/vague-facts-queue.yaml` with REAL vague issues (skip already-specific entries).

For each: verify via 3+ INDEPENDENT primary sources (entity page + secondary primary + contemporaneous press). Extract exact YYYY-MM-DD/amount/round-type/lead/etc. Update ALL affected profiles (not just one). Add primary source citations.

Mark `status: resolved` or `unresolvable` in queue with a note.

Then commit "Fact Specificity: [names]" and push.

Anti-hallucination: triple-check every name against cited press; NEVER trust aggregators alone; when in doubt LEAVE IT OUT. Use literal `$` not `\$` in YAML reason strings. PRESERVE original currency/units.
```

## Job 3: Watchdog

**Schedule:** `3 8 * * *` (daily at 8:03 AM local)

**Prompt:**

```
Cron watchdog. Run CronList. Recreate any missing of these three recurring jobs:
(1) Freshness feed monitor `17 */6 * * *`
(2) Fact Specificity `43 */4 * * *`
(3) this watchdog `3 8 * * *`

Output a single line summary.
```

## How to create them (via CronCreate tool)

The Claude Code harness provides a `CronCreate` tool. Sequence:

1. Confirm the three prompts above are ready (with your topic's script paths substituted).
2. Call `CronCreate` three times, one per job.
3. Verify with `CronList`.

Example one-liner responses you should see:

```
Scheduled recurring job abc12345 (Every 6 hours at :17). Session-only. Auto-expires after 7 days.
```

## Handling failures

### Classifier temporarily unavailable
Reason: the safety classifier that gates `Agent` calls is under load. Symptoms: any `Agent` tool call returns "classifier is temporarily unavailable."

**Response:** call `ScheduleWakeup` with `delaySeconds: 270` (stays in the 5-minute prompt cache window). Do NOT retry immediately.

### API rate limit
Reason: too many concurrent requests across the fleet. Symptoms: `Server is temporarily limiting requests (not your usage limit)`.

**Response:** same — `ScheduleWakeup` for 270s. Do NOT loop.

### Parallel commit conflict
When freshness-feed and fact-specificity crons fire back-to-back and both try to push, one will get a rejection.

**Response:** inside the agent prompts, tell them to `stash → pull --rebase → push` on conflict. Both agents do this automatically.

### Prompt-side rate limits
If you're running many manual sweeps + the crons, you may hit rate limits more often. Either back off manual dispatches or accept some skipped tick cycles.

## What the watchdog should also check

Beyond just crons, a beefier watchdog can:
- Verify the freshness feed has an item from the most recent weekday. If stale, dispatch a catch-up sweep.
- Check `data/pending-<items>.yaml` isn't stuck (unchanged for >12h means scraper is dead).
- Verify GitHub Action last run was successful.

Start with the minimal (just CronList + recreate). Add checks as needed.

## Once you have crons running

Monitor for a week. If a job produces bad output (fabricated data, wrong dates), tighten the prompt. Document each tightening in a `_lessons/` file.
