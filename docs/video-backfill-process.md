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

Parked 2026-11-07: Jen Novakovich (The Eco Well), cursor 45 against a 12-video
`/videos` tab, all 12 already carded. Worth recording because her case has a
second layer the Aamna Adel case did not: a `ytsearch` for the channel surfaces
many more Eco Well uploads that the `/videos` tab does not list, and they are
almost entirely e-summit and panel recordings. Those are her own paid product,
named in her roster conflict, so they are excluded from carding on their own
terms rather than merely missing. The tab being empty and the catalog being
genuinely mined out happen to coincide here; do not reopen her on the strength
of a search result.

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

## The demand-driven fallback needs a `--type` (2026-11-13)

`video_gaps.py` orders its output core-types-first and then alphabetically, so a
bare `--limit 40` returns product pages and nothing else: on 2026-11-13 the gap
counts were product 387, ingredient 167, condition 27, goal 32. Most of the
HIGH-tier roster is `product_recs: restricted`, and a product video from a
restricted creator is precisely the category this cron may not card. So the
fallback could never fire for them, and four backfill ticks in a row advanced the
cursor with zero cards and no error.

Run `--count` first, then ask for one type. For a restricted creator, ask for
`--type ingredient`, `--type condition` or `--type goal`. The condition and goal
lists are short enough to read whole, and they are where a dermatologist's
evergreen educational back catalog actually fits: the card added on 2026-11-13
was Dr. Aanchal Panth on recurrent fungal infection, which filled
`tinea-corporis-ringworm`, a condition gap, from a catalog slice whose own 15
titles contained no usable single-topic match at all.

### When to hold the cursor instead of advancing it (2026-11-16)

STEP 4 says to advance the cursor by the slice. Do NOT, when both of these
hold: the slice contains a candidate that passes the popularity floor and
matches an existing page, and the only reason it was not carded is a transcript
429. A slice whose transcripts could not be fetched has not been evaluated, and
advancing past it discards good candidates permanently in exchange for a new
slice that is equally unfetchable. Advancing is right when the slice was
genuinely assessed and found wanting; it is wrong when the assessment never
happened.

Worked example. Davin Lim's slice 49-63 holds "Getting Rid of Acne Scars at
Home: Microneedling" at 123,109 views and "Subcision: Does it cause facial
sagging?" at 74,157, both matching existing pages. The cursor has been held at
48 since 2026-11-15 across three ticks, all blocked by 429 on the first request.
Re-ranked on 2026-11-16 at 123,181 and 74,268 views: both still PASS, which is
the hold working as intended rather than a stale note.
Re-listing the slice costs one yt-dlp call and the same two candidates re-rank
to the top automatically, so the hold is self-healing and cheap.

**The hold freezes the WHOLE LANE, not one creator (2026-11-19).** This is the
cost the rule above missed. `roster_next.py backfill --all-high` always returns the
smallest walkable cursor, so while one creator is held every backfill tick selects
that same creator and fails. On 2026-11-19 Davin Lim had been held at 48 for five
ticks, and in that time none of the other 33 walkable HIGH-tier back catalogs was
touched. The next cursors sat at 52, 57 and 60.

So the hold is only cheap when it blocks one creator's progress. It is expensive
when it blocks everyone's. The resolution is to advance the cursor AND record the
held candidate ids somewhere durable, which loses nothing: the ids are still
cardable by id whenever the throttle clears, and the lane starts moving again.
Holding is right for a tick or two; past that, write the ids down and move on.

**HELD CANDIDATES, cardable by id once YouTube captions are fetchable.** Both passed
the popularity floor and both match existing pages:

- `byq-AndfCbg` Getting Rid of Acne Scars at Home: Microneedling, Dr Davin Lim,
  123,181 views, matches [[microneedling]]
- `6uisyTDXwkg` Subcision: Does it cause facial sagging?, Dr Davin Lim,
  74,268 views, matches [[acne-scars]]
- `NG1950GE2TI` All Things Perioral Dermatitis: Reaction & Treatment Tips,
  Dr. Joyce Park, 50,001 views, matches [[perioral-dermatitis]]. Her roster is
  `product_recs: restricted`, so the higher-viewed Teen and Tween Routines video
  from the same slice (138,515) is NOT eligible and should not be substituted.

CORRECTION 2026-11-20: the three Dr Dray candidates recorded here earlier today
(`MYiOWPf354A`, `EbC6oTVlkAM`, `NEhoD-6m4BY`) are NOT waiting on the throttle. All
three are cached NEGATIVES: a fetch succeeded at some point and found no English
captions at all, so they can never be carded and have been removed from this list.
Recording them as pending was misleading.

**Check the cache before banking a candidate.** A 429 is deliberately never cached,
so a cached entry with `has_transcript: false` is a definitive no-captions answer, not
a throttle. Of 932 cached transcripts, 77 are such negatives, roughly 8%. Run
`yt_transcript.py <id>` and read whether the output says `[cached]`: if it does and
reports no transcript, the video is uncardable regardless of what the throttle does
later. The three banked candidates above (`byq-AndfCbg`, `6uisyTDXwkg`,
`NG1950GE2TI`) are genuinely uncached and so genuinely still pending.

**Bound it.** If a cursor has been held for more than about a week, stop holding
silently: the blockage is no longer a transient throttle and the right move is to
say so in the tick summary rather than keep deferring. A permanently stalled walk
that nobody mentions is worse than a walk that skipped two videos.

### The throttle is the SUBTITLE endpoint, not the account or the IP (2026-11-16)

Measured directly, on one video id, seconds apart, in the same tick:

    yt_transcript.py byq-AndfCbg       -> HTTP Error 429: Too Many Requests
    yt-dlp --print "%(view_count)s"    -> 123174, returned immediately

So this is not an IP ban, not a yt-dlp block, and not an exhausted quota on
anything the backfill needs for ranking. Metadata, view counts, upload dates and
`--flat-playlist` slices all keep working normally while `timedtext` refuses. Two
consequences worth acting on. STEP 2 and STEP 2b are fully functional during a
429, so a tick can still list a slice, rank it by views and identify the right
candidates; only STEP 3a fails, which is why holding the cursor loses nothing.
And anyone debugging this should look at the caption request path specifically
rather than at rate limiting in general, because the general case is demonstrably
fine. TikTok subtitles also fetched normally on 2026-11-16 with no cookies at
all, which narrows it further to YouTube's caption endpoint.

### ESCALATION: single-video metadata is now blocked too (2026-11-20)

This supersedes the 2026-11-16 note below, which said metadata works normally while
only `timedtext` refuses. That was true then and is not true now. Measured today:

    yt-dlp --flat-playlist --print "%(id)s\t%(title)s" <channel>   -> WORKS
    yt-dlp --flat-playlist --print "%(view_count)s"                 -> NA (not in flat mode)
    yt-dlp --print "%(view_count)s" <single video url>              -> "Sign in to confirm you're not a bot"
    yt_transcript.py <id>                                           -> HTTP 429

So the block has moved up a level. Channel listings still work, which means STEP 2
still works. But STEP 2b, the popularity ranking, calls single-video metadata and is
now blocked as well, not just STEP 3a.

Practical consequence for this cron: a tick can still list a slice and title-match
candidates against existing pages, but it CANNOT rank them by view count. Record the
title-matched candidates without view figures rather than pretending to a ranking,
and say in the summary that ranking was unavailable. Do not treat an unranked
candidate as having passed the 30k floor; it has not been checked against it.

### Successes are per-request, not a window (2026-11-17)

Observed in one day: V05NVkMwbQ4 fetched successfully in the afternoon, and both
YiGNHfJicgY and byq-AndfCbg returned 429 within hours of it. So the throttle does
not open and close in windows that a tick can wait out; individual caption requests
succeed or fail more or less independently.

Two practical consequences. Retrying a held candidate every tick is the correct
strategy rather than a waste, because each attempt is a fresh roll and one will
eventually land. And a 429 on the first request says nothing about the second, so
the "stop the batch" rule is about not extending the throttle, not about the batch
being hopeless.

A failing request is also slow: byq-AndfCbg took over two minutes to return its 429,
because yt-dlp retries internally before giving up. Budget for that when a tick
looks hung.

### The cookie workaround is not always available to the agent (2026-11-15)

Recorded because the section above reads as though the fix is always within
reach, and for several days it has not been. In this session every attempt to
set `YTDLP_COOKIES_FROM_BROWSER=chrome` is refused before it runs, classified as
bot-check circumvention, so the documented bypass cannot be used and a 429 is
simply terminal for that tick.

What that looks like in practice, 2026-11-11 to 2026-11-15: the YouTube pull and
backfill crons fired roughly fifteen times and produced one card between them.
The causes were a Shorts-only queue (now addressed by the `--min-duration`
filter) and, four ticks running, HTTP 429 on the subtitle endpoint.

Two things are worth knowing for whoever picks this up:

- **Only the subtitle endpoint is blocked.** Verified 2026-11-15: a plain
  `yt-dlp --skip-download --print` metadata call on the same video returns
  normally in the same minute that a subtitle fetch returns 429. So the daily
  scan, duration capture, upload dates and view counts all keep working; it is
  specifically transcript retrieval that stops, which is also the one step the
  sponsorship scan depends on.
- **The queue does not lose anything.** `yt_transcript.py` says explicitly not to
  mark a 429'd video transcript-less, so blocked candidates stay pending and are
  retried. The backlog drains slowly rather than silently shrinking.
- **The throttle is intermittent, not a standing block.** Corrected 2026-11-15:
  a backfill tick fetched a full transcript cleanly, and a pull tick about an hour
  later returned 429 on its first request. So it is worth attempting on every tick
  rather than assuming the endpoint is down. After a 429 the script arms a roughly
  30 minute global cooldown and then SKIPS later probes rather than extending the
  throttle, which means one unlucky first request costs the whole tick. Trying the
  highest-value candidate first is therefore the right order, and
  `--ignore-cooldown` is not a workaround to reach for, since the cooldown exists
  to stop the block getting longer.
- **It is not video-specific, and trying a different id does not help.** An earlier
  version of this note guessed that one video, dZTTnH7BgyU, might be a repeat
  offender after six failures, and advised leading with a different candidate.
  Tested on 2026-11-15: a pull tick led with a completely different video,
  V05NVkMwbQ4, and got 429 on its first request too. The throttle is broad and
  sporadic, and that id had simply been tried most often. Ordering candidates by
  value is still right, because the first request is the only one a tick gets, but
  do not expect it to raise the hit rate.
- **The hit rate, measured rather than guessed.** On 2026-11-15 the pull and
  backfill crons attempted roughly six transcript fetches across the day and one
  succeeded. Plan ticks on the assumption that most will fail and nothing will be
  lost, rather than on the assumption that a retry is due.

If the bypass is wanted, it needs to come from the operator rather than from a
tick: either run the cookie-bearing fetch by hand, or arrange transcript access
by a route that does not require an agent to impersonate a browser session.

**The YouTube caption block is now 3 days old (checked 2026-11-20).** The newest
successfully cached YouTube transcript is `YiGNHfJicgY.json`, 2026-11-17 23:06. Every
fetch since has returned 429. TikTok is NOT affected: a TikTok transcript cached at
03:21 on 2026-11-20, so the block is YouTube-specific rather than a network or tooling
fault. Sort the cache by real mtime (`ls -lat`) when checking this; `ls -la | sort`
sorts month NAMES alphabetically and will tell you the newest file is from September.

Candidates confirmed uncached and still pending, so still worth retrying when the block
lifts: `-IT6N0tVEaA` (Aleksandra Brown, "Why Your Retinol Isn't Working", educational so
eligible despite her picks restriction), plus `byq-AndfCbg`, `6uisyTDXwkg` and
`NG1950GE2TI` from earlier. Pass a leading-dash id as a full URL, not a bare id, or
argparse reads it as a flag.
