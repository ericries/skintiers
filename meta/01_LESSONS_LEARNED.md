# Lessons Learned from Seedlist

Every rule in this file corresponds to a real failure. Read them all before touching data.

## Sourcing & accuracy

### L1. Sources-first, not text-first
Build the source list BEFORE writing any profile text. Every claim must trace back to a URL you actually visited. Writing plausible-sounding text and then hunting for citations to back it up is how agents produce fake URLs. The failure mode is: agent "remembers" a URL pattern (e.g. `techcrunch.com/2024/01/company-raises-series-a`) and confidently invents it.

**Rule:** WebFetch or WebSearch every source URL before adding it to a Sources section. If you can't find a source for a claim, delete the claim.

### L2. Triple-source verification for every non-trivial fact
Every date, amount, participant, ingredient concentration, patent — verify via 3+ INDEPENDENT primary sources:
- **Primary source A:** the entity's own site (company blog, press release, official statement)
- **Primary source B:** a second first-party source (co-participant's site, regulator filing, patent document)
- **Primary source C:** contemporaneous tier-1 press (WSJ, Bloomberg, TechCrunch, peer-reviewed journal, Cochrane review)

**Do NOT trust:** Wikipedia (cite its sources instead), aggregator databases (Crunchbase summaries, ingredient lookup sites without citations), AI-generated summaries, retailer product descriptions, or influencer content. Use these only as leads — always click through to the primary.

If only 2 sources agree, skip the fact and mark it `unresolvable` in the fact-check queue.

### L3. When in doubt, LEAVE IT OUT
A short accurate profile beats a long fabricated one. Every past incident in Seedlist involved an agent filling a gap by guessing. Mark facts as `unresolvable` rather than invent them.

### L4. Never present paraphrases as direct quotes
If you don't have the exact wording, write a factual statement instead. Only use quotation marks around text copied verbatim from a source. Fake quotes have been the single largest source of embarrassment.

### L5. Never invent percentages
Every percentage must be computed from counted data with the math shown inline: `12 of 28 products (43%)`. `~30%` without a denominator is a guess dressed as data. If sample is too small for percentages, use qualitative descriptions instead ("Predominantly retinoid-based; sample of 8").

### L6. Aggregator-only means unresolvable
If the only sources for a claim are aggregator databases, ingredient wikis, or AI summaries, the claim is `unresolvable`. Do not include it in a portfolio/product table. If it's already there, remove or flag it. Multiple aggregators agreeing does NOT count as multiple sources — they all crib from the same upstream data.

### L7. Preserve original units
Currency, weights, measurements — never convert. If a launch was announced in euros (€30M), record €30M. Same for GBP, INR, CHF. Currency conversion adds error and obscures the source figure. Same principle for skincare: if a study reports concentration as "% w/w" or "ppm", preserve — don't normalize.

### L8. Only use validated slugs in cross-references
When cross-referencing entities in frontmatter (`brands:`, `ingredients:`, etc.), only use slugs that correspond to existing files. Verify with `Glob data/{type}/{slug}.md` before including. If no profile exists yet, use the entity name in body-text tables only, and queue the entity for future research. Orphan slug references render as broken links on the site.

## Format & data hygiene

### L9. YAML: literal `$` in strings, not `\$`
Bash-style escaping (`\$100M`) breaks YAML parsing. Use `"appeared in Foo raise $100M"` verbatim. Multiple past sweeps corrupted `fact-check-priority.yaml` this way and had to be fixed with `Edit replace_all`.

### L10. Dates must be YYYY-MM-DD for the freshness feed
Month-only dates (`2026-03`) make the feed feel stale. Extract exact announcement dates from press. "Announced Tuesday" or "this week" → calculate the specific date. Feeds sort by exact date.

### L11. Table cells contain data only — no narrative
Never put phrases like "all seed investors participated above pro rata" or "undisclosed participants" in table cells. Lead / participants columns list names only. If unknown, leave blank. Narrative belongs in body text below the table.

### L12. Citation hygiene
- Sequential footnote numbering, no gaps
- No duplicate URLs in Sources section
- No dead URLs (403, 404) in published profiles — find alternatives or drop the claim
- Every footnote referenced in body; no orphans in Sources

## Workflow & tooling

### L13. Two-pass review
Draft → verify → publish. First pass writes. Second pass re-fetches every source URL, confirms each claim is supported, checks quotes verbatim, validates any percentages against counted data. Only publish when the profile is 10/10. A draft on disk is better than an inaccurate profile on the live site.

### L14. CLI toolkit collapses friction
Build a `scripts/sl` (or whatever you name it) that wraps every repeated operation: lint, publish, commit-push, batch-publish, queue-add, xref-check. Agents should never write ad-hoc git commands or file edits when a `sl` subcommand would do — this both avoids permission prompts and enforces conventions.

### L15. Batch commits, not per-file
Never `git commit` after every profile. Use a post-batch command that: reads discovered-queue files → auto-fixes lint issues → lints → publishes passing → rebuilds site → single commit + push.

### L16. Session-only crons with a watchdog
Cron jobs created via `CronCreate` are session-only and auto-expire after 7 days. Set up:
- A recurring **research feed** cron (every 6h)
- A recurring **fact-check** cron (every 4h)
- A daily **watchdog** cron that recreates the above if missing

The watchdog is the safety net for session restarts.

### L17. Rate limits and classifier outages happen
Both `Agent` classifier and API rate limits fail intermittently. Handle gracefully:
- On classifier failure: `ScheduleWakeup` with `delaySeconds: 270` (stays in prompt cache window)
- On rate limit: same — retry in ~5 min, do not spin
- Do NOT retry immediately or in a tight loop

### L18. Parallel agents where independent
Round monitoring (creates new profiles) and fact-check (tightens existing profiles) can run in parallel — they touch mostly different files. When git push conflicts, stash → pull --rebase → push. Warn the parallel agents in their prompts.

## Discovery & completeness

### L19. Freshness feed pattern
For any topic with continuous new information (new products, new studies, new brand launches), have a daily "monitor" agent that:
1. Scrapes RSS feeds and/or web-searches for the most recent weekday
2. Verifies each new item against 3+ primary sources
3. Publishes profiles + updates cross-references
4. Appends touched entities to a **fact-check-priority queue** for follow-up

The feed must always show at least one item from the most recent weekday. Staleness is the #1 quality signal for visitors.

### L20. Fact specificity queue
Vague data (`Unknown`, `--`, `Undisclosed`, year-only dates on recent items) gets accumulated in `data/vague-facts-queue.yaml` (via a scanning script) and worked through by a dedicated agent. Fixes 3 facts per run, each verified via 3+ primaries, updates ALL affected profiles (not just one), marks resolved/unresolvable.

### L21. Priority queue for touched entities
Every time an entity is touched by a new item (e.g. a brand mentioned in a new product launch), append to `data/fact-check-priority.yaml`. The fact-check agent works this before the general vague-facts queue. This keeps profiles-getting-traffic the most accurate.

### L22. Recursive discovery
Every profile you research should yield new leads. For skincare: a brand profile lists formulator names → queue formulators. A product mentions ingredient X → queue ingredient. An ingredient study cites researcher Y → queue researcher. Track discovery depth; stop at depth 3 unless the user requests more.

### L23. First-person quotes are the hardest and most valuable section
Founder/user quotes ("What Founders Say" in Seedlist; would be "What Users Say" or "What Dermatologists Say" for skincare) require dedicated search effort. Do NOT pad with marketing copy, brand-authored testimonials, or your own paraphrase. If you cannot find independently-sourced quotes after real searching, write: `"No independently sourced testimonials found."`

## Self-improvement

### L24. Write lessons after every batch
Create `_lessons/YYYY-MM-DD-description.md` after every batch of profiles or after any user feedback. Format:
```
# Lessons from [description]
Date: YYYY-MM-DD
## What went wrong
[Numbered list with specific examples]
## What went right
[What to keep doing]
## Rules going forward
[Concrete rules that can be checked mechanically]
```
Then update the project's `CLAUDE.md` if the lesson reveals a gap in the process.

### L25. Read lessons before starting new work
Before any new batch, skim `_lessons/` to avoid repeating past mistakes. This is not optional.

## Human collaboration

### L26. Terse status lines, not walls of text
The user watches the terminal but doesn't want to reply. One-liner after every batch:
```
Batch 3: +5 published, 1 flagged (smith-jones: missing dates) | Queue: 40 pending
```
Do NOT output multi-line status blocks between batches.

### L27. Ask before destructive actions
Never `rm -rf`, `git reset --hard`, `git push --force`, or bypass hooks (`--no-verify`) without explicit user OK. If a hook fails, fix the underlying issue.

### L28. Never bypass pre-commit hook lint failures
Pre-commit hook catches YAML errors, broken citations, and missing years. If it blocks, fix the underlying issue and create a NEW commit. Never `--no-verify`.

### L29. Don't ask questions during autonomous batches
When running an autonomous batch loop, make reasonable calls and keep going. Only stop for truly ambiguous decisions or destructive actions. But when a schema question comes up ("should we track X?"), STOP and ask — schema mistakes compound.
