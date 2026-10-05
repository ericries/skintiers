# Token efficiency without losing efficacy

Written 2026-10-05 after a full day of servicing cron ticks in one session. Every
number below was measured in this repo, not estimated from intuition.

## The constraint first

The accuracy backbone is not a cost centre to be trimmed. Triple-sourcing, verbatim
quote checks, source caching, and the critic pass are the product. Everything in this
document attacks **overhead**: instructions re-sent, tools that return more than was
asked, loops that produce nothing, and work that re-fires because a decision was never
recorded. If a proposal here would reduce verification, it is the wrong proposal.

A useful test: *would this change let a wrong fact reach a page?* If yes, discard it
however many tokens it saves.

## 1. Repeated instruction text is the largest sink (~12k tokens/day, compounding)

Measured: each `fill-*` cron prompt is ~1,750 tokens, of which **1,537 tokens
(88%) are lines identical across all eight fill prompts**. The fleet fires ~25
times a day.

Worse than the per-firing cost: a cron prompt arrives as a user turn, so it stays
resident in context and is re-processed on every later turn in the session. Twenty-five
firings is ~44k tokens of prompt text accumulating before any work happens.

**Fix, already prepared:** `docs/cron-playbook.md` now holds that shared text
verbatim (all 39 shared lines, zero dropped, verified programmatically). A cron
prompt can shrink to its type, its one unique step, and a pointer:

```
[SkinTiers daily fill: INGREDIENT] Read docs/cron-playbook.md and service the
INGREDIENT tick against it. Type-specific: set a top-level `tier:` matching the
page's own rubric. Then stop.
```

Efficacy is preserved because the guardrails still bind: the agent reads them once
per session instead of receiving them twenty-five times. **This change is not yet
applied to the live fleet** (`data/cron-roster.yaml`) because flipping 18 live crons
is a judgment call: if a session somehow skips the playbook read, quality drops
silently. Recommend applying it to two low-risk crons (brand, person) first and
comparing output quality before the rest.

Estimated saving: ~1,500 tokens x ~25 firings = **~37k tokens/day**, plus the
compounding context cost, for zero loss of instruction.

## 2. Tools that cache a failure as a fact (fixed today)

`yt_transcript.py` treated "this video has no captions" and "the platform returned
HTTP 429" identically, and **cached both**. One throttled afternoon poisoned the
cache, so later ticks each: fetched, got a false negative, re-verified with
`yt-dlp --list-subs`, found captions did exist, purged the entry, and produced
nothing. That loop ran across four ticks in one day.

Fixed: a `RateLimited` exception, raised only when no caption file was produced *and*
stderr carries a throttle signature; the result is flagged `rate_limited` and
**never cached**; the CLI exits 2 with "caption status unknown" so a batch stops
after one call instead of collecting more false negatives.

**The general rule: a tool must distinguish "the answer is no" from "I could not
find out."** Caching the second as the first is how an agent ends up confidently
wrong *and* expensive. This also prevented the worse outcome: resolving a legitimate
video as transcript-less so it is never ingested again.

## 3. Work that re-fires because a decision was not recorded

`site_health` flags a hub whose `tier_list` omits pages that link to it. Several
flags were false positives (a product cannot join an actives-only ranking; a
stretch-mark product does not belong in a post-acne-marks ranking). The right call
was made each time, and **nothing was written down**, so the same task re-fired
indefinitely, costing a full investigation each cycle.

The tool already had the answer: `tier_list_reviewed:`. Four hubs were cleared with
it today and the flags stopped. **Rule: a declined candidate must be recorded as
declined.** A decision that is not persisted is a decision you will pay for again.

## 4. No-op ticks

An empty queue plus `site_health` returning `NONE` means a tick spends tokens to
discover there is nothing to do. PRODUCT hit this repeatedly once its queue drained.

This is mostly healthy design (the maintenance lane exists precisely so ticks are
not wasted), but two cheap improvements:

- Have the fill crons **check the cheap signal first** and exit immediately: one
  `queue-next` plus one `site_health` call, no survey, no file reads.
- Give PRODUCT a real producer. It is the only CORE type with no discovery source
  of its own: products arrive only via brand/ingredient/video cross-feed. A
  `products_with.py`-style sweep that finds real retail products for actives already
  on-site would keep the queue fed, which is cheaper than a tick waking up to find
  nothing.

## 5. Small recurring frictions, each cheap to remove

- **`sk publish --force` sets `assurance: opus` with no critic verdict**, so every
  post-cap publish needs a follow-up edit to downgrade it. Happened 5+ times in one
  day. `publish` should either preserve the existing value or take `--assurance`.
- **Backticks in `git commit -m` get shell-expanded.** One commit message today lost
  a word to command substitution. Use a heredoc or avoid backticks.
- **`timeout` does not exist on macOS.** Reach for `run_in_background` instead of
  rediscovering this.
- **`site_health.py` output is already well shaped** (one task, named target, literal
  ACTION line). It is the model other tools should copy: return the *decision*, not
  the data to make it with.

## 6. Habits that actually saved tokens today

- **Verify before building.** The ask included "give each video and creator its own
  page" and "optimize SEO". Auditing first showed 407 video pages, 56 creator feeds,
  canonical tags, OG images and OG image generation already existed. Only sitemap,
  robots and JSON-LD were genuinely missing. Building what exists is the most
  expensive possible mistake.
- **Grep for the verdict, not the document.** `grep -ohE "\*\*Effect size: [^.]{0,55}"`
  across nine pages replaced nine file reads when backfilling `tier:`.
- **Batch independent reads into one call**, and batch mechanical edits into one
  scripted pass with an assertion per edit, so a silent no-op cannot pass as success.
- **Check whether the data is already right.** Eight ingredient pages used tier
  spellings outside `best/good/mid/weak`; `_TIER_ALIASES` already mapped all of them.
  Five minutes of reading avoided a pointless 8-file rewrite.

## Priority order

| # | Change | Saving | Risk |
|---|---|---|---|
| 1 | Point cron prompts at `docs/cron-playbook.md` | ~37k tok/day + context | Medium: needs the playbook read; stage it |
| 2 | Distinguish cannot-tell from no (done) | 4 wasted tick-chains/day | None, shipped |
| 3 | Record declined candidates (`tier_list_reviewed`) | 1 investigation/cycle/hub | None |
| 4 | `publish` stops claiming unearned `opus` | 1 edit per publish | Low |
| 5 | A real producer for the PRODUCT queue | turns no-ops into pages | Low |

Items 2 and 3 are shipped. Item 1 is prepared and awaiting a decision on staging.
