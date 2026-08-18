# Video mining: two-track process (new uploads + back catalog)

Goal: for the highest-quality creators, surface not just their NEW videos but also the
deep evergreen back catalog (each flagship has hundreds of single-topic explainers that a
recent-15 skim never reaches). Two independent tracks, so fresh content and back-catalog
depth both progress without blocking each other.

## Track 1 - New uploads (existing daily video-pull cron)
Picks the creator with the oldest/null `last_pulled`, lists the recent ~15 uploads, cards
the eligible ones, advances `last_pulled`. Catches fresh content at the top of each channel.
Diminishing returns once a channel is freshly mined (re-skims the same top-15 -> mostly dups).

## Track 2 - Back catalog (new: `backfill-mine.js` + video-backfill cron)
For a curated set of **flagship** creators only, walk the ENTIRE catalog in bounded chunks
over time using a per-creator **cursor**.

- **Flagship marker**: in `data/video-sources.yaml`, a flagship creator carries
  `flagship: true` and `backfill_cursor: <int>`. Flagships are the highest-quality,
  science-rigorous creators with deep evergreen YouTube catalogs (initial set:
  michelle-wong, andrea-suarez-dr-dray, victoria-fu, dustin-portela, sam-bunting,
  davin-lim, stephen-alain-ko, scott-walter). Cursor starts at 15 (the daily-pull window
  covers uploads 1-15).
- **Each sweep**: for the flagship(s) with the SMALLEST cursor (least-explored), the
  `backfill-mine.js` workflow pulls the slice `--playlist-start {cursor+1} --playlist-end
  {cursor+15}` (older videos), cards every eligible single-topic educational one
  (transcript-verified, deduped, sponsorship-scanned, own-brand-promo skipped), and returns
  a `new_cursor`. The main loop applies the cards centrally and advances that creator's
  `backfill_cursor` to `new_cursor`.
- **Termination**: when a slice returns fewer than the chunk (catalog exhausted at that
  depth), the sweep sets the cursor to the true end reached; once cursor >= catalog length
  the creator's back catalog is fully explored (mark done or stop selecting it).
- **Feed ordering**: back-catalog cards carry their real (old) upload date, so they sort
  low on the date-ordered Feed but still enrich the relevant ingredient/condition pages.
  Back-catalog mining is about page DEPTH, not Feed recency.

## Cadence
The `video-backfill` cron runs a sweep on the least-explored flagships a couple times a day,
in parallel (workflow bypasses the session agent cap). Over weeks the cursors walk each
flagship's full catalog. The daily new-uploads pull runs independently.

## Guardrails (same as all video intake)
Transcript-grounded self-contained theses; mandatory sponsorship scan; dedup by video id;
own-brand-promo skip; only attach to EXISTING pages (never invent); link every mentioned
page via `related`. See [[video-card-standard]] and docs/creator-expansion-plan.md.

## Why only flagships get Track 2
Back-catalog mining is expensive (transcript per video). It pays off only for creators whose
older content is (a) still accurate/evergreen and (b) rigorously science-aligned. Lower-tier
or format-mismatched creators (podcast/haul channels) are not worth a deep sweep; they stay
on Track 1 only.
