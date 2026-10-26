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

## Exhausted catalogs: the `backfill_cursor: 9999` sentinel

A `backfill_cursor` can run past the end of a creator's catalog, and when it does
that creator becomes the permanent "smallest cursor" and gets selected on every
backfill tick while returning an empty slice. Observed 2026-10-18: Dr Aamna Adel
sat at cursor 45 against a 13-video YouTube catalog, 11 of which were already
carded.

When a slice comes back empty AND the full catalog is shorter than the cursor,
park the creator instead of setting the cursor to the true catalog length (which
would re-select them forever):

    .venv/bin/python scripts/sk roster-set <slug> --backfill-cursor 9999

9999 is a sentinel meaning "back catalog exhausted, stop selecting". Eight
creators carry it as of 2026-10-18 (count it from the roster rather than trusting
this line). Do NOT "correct" it back to a real number; a
new upload is Track 1's job, not Track 2's. A proper `backfill_done: true` flag
would be clearer and is still unbuilt.

## The subtitle 429 is bypassable: pass browser cookies

Before deferring anything for a 429, try cookies. `yt_transcript.py` honours
`YTDLP_COOKIES_FROM_BROWSER`, and the TikTok-pull cron sets it while the YouTube
pull, scan and backfill crons do not. Verified 2026-10-26 on one video: the
default call returned HTTP 429, `--extractor-args "youtube:player_client=tv"`
returned "The page needs to be reloaded", and `--cookies-from-browser chrome`
downloaded the full subtitle track.

    YTDLP_COOKIES_FROM_BROWSER=chrome .venv/bin/python scripts/yt_transcript.py <id> --ignore-cooldown

`--ignore-cooldown` is needed when an earlier cookie-less attempt already armed
the script's ~30 minute global cooldown. This supersedes the older belief that
cookies never helped for YouTube; re-test it rather than trusting either claim.

The deferred list below was built during the 2026-10-25 block, before this was
known. Those three are still worth carding, they no longer need to wait, and the
cookie call above is how to read them. Confirmed working on 2026-10-26, when a
Laura Soong slice was transcript-verified and carded with it.

## Deferred candidates: vetted, popularity-checked, blocked only on a transcript

A second way a creator jams the selector: the slice yields genuinely good
candidates, but YouTube's subtitle endpoint is returning HTTP 429, so they cannot
be transcript-verified and therefore cannot be carded. Holding the cursor keeps
them findable but re-selects the same creator every tick and the sweep stops
making progress. Observed 2026-10-25: Neal Schultz was selected on four
consecutive ticks at `backfill_cursor: None` for this reason.

The fix is to record the candidates here, where they survive cursor advancement,
and then advance the cursor normally. `video_scan.py --scan` cannot hold them:
it only looks at each channel's most recent uploads, so deep back-catalog
candidates never enter `video-candidates.yaml`. Do not hand-edit that queue.

Note that only the subtitle endpoint is affected. `yt-dlp` metadata and
`video_views.py` work normally during a 429, so vetting and the popularity check
can be completed and recorded in advance; the transcript is the only missing
input. When a transcript window reopens, card these from the list below and
delete the rows. Run the mandatory sponsorship scan then, as always, since none
of these has been read yet.

**Dr. Neal Schultz (DermTV)**, `neal-schultz`, vetted 2026-10-25. Own-brand
conflict is BeautyRx, so confirm each transcript is educational rather than a
product pitch before carding. All three are 2014 evergreen uploads and all three
PASS the 30k view floor.

| views | id | title | attach to |
|---|---|---|---|
| 215,592 | `U3wv2xV1DmI` | A Spotty Rash: Tinea Versicolor [DermTV.com Epi #560] | `pityriasis-versicolor`, which has ZERO video cards |
| 96,848 | `_eFzYS_V3qw` | What is the Best Type of Sunscreen [DermTV.com Epi #554] | `sunscreen-uv-filters` |
| 33,064 | `H2q3aa9qWgM` | Can You Exfoliate Skin Around Your Eyes [DermTV.com Epi #555] | an eye-area or exfoliation page; confirm the best target at carding time |

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
