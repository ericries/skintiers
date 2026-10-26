# Plan: identifying & vetting credible skincare creators (video-ingestion expansion)

Status: ACTIVE (started 2026-08-16, at user direction). Goal: grow the vetted
`data/video-sources.yaml` roster with more credible experts, and bias intake toward
videos that **cite specific studies** or **suggest specific routines** — turning the
Feed into a research-intake engine, not a link dump.

Settled decisions (user, 2026-08-16):
- **Platforms:** YouTube + TikTok/Instagram. YouTube via `yt_transcript.py`; **TikTok now
  works via `scripts/tiktok_transcript.py`** (yt-dlp exposes eng VTT captions), so
  TikTok-primary creators ARE cardable (transcript-verified) — this unlocked the credible
  derms we'd rostered/rejected for lacking YouTube (Hirsch, Fahs, Esther Olu, Wedgeworth,
  Mamina). Instagram remains pending (yt-dlp IG support is flaky/auth-gated). No transcript,
  no load-bearing claim, on any platform.
- **COI policy (user, 2026-08-16):** a "worked-on-it" product COI (a creator helped
  formulate a product they recommend) is NOT a blanket disqualifier. Such a creator can be
  rostered (product_recs: restricted, COI in `conflict`); their endorsement of THAT product
  is usable ONLY on that product's own page WITH context, never elsewhere. General
  educational content from them is fine. Reject only for pseudoscience, unverifiability, or
  heavy undisclosed sponsorship. (This rehabilitated Mamina Turegano, first rejected for a
  Beauty Pie retinoid COI.)
- **Roster additions:** AUTO-ADD any candidate that passes the rubric (no per-creator
  human gate). The rubric IS the gate, so it is conservative: **reject when uncertain.**
  Every decision (added AND rejected, with reason) is logged to
  `data/creator-vetting-log.yaml` for audit.
- **Study intake:** ACTIVATED. When a vetted video cites a specific study, capture it as
  a mention -> queue/build the agent-facing study page and cross-link (the feed-driven
  intake shift, see [[feed-driven-research-intake]]).
- **Scale:** ~15-20 candidates per identification pass.

## 1. Discovery — how candidates are found (highest-precision first)

1. **Referral graph** from existing vetted creators: derms/chemists they collaborate
   with, cite, or appear alongside are pre-filtered for credibility. (Reflection pass on
   creators, mirroring the product/ingredient reflection pass.)
2. **Credential seeding:** board-certified dermatologists (FAAD) and cosmetic chemists
   (SCC) who are active science-communicators — an enumerable set.
3. **Study-citation overlap:** creators who cite the same primary literature our
   ingredient pages already cite. Double-scores (credibility signal + surfaces the
   study-citing videos we want).
4. **Counter-signal filter:** actively exclude the pseudoscience / "toxic ingredient" /
   detox / fear-mongering cluster regardless of follower count.

## 2. Vetting rubric (per candidate — the auto-add gate)

A parallel subagent per candidate (`scripts/creator-vetting.js`) resolves their channels,
confirms they are a living active creator, samples 4-6 recent videos, and scores:

- **cites_literature** — cites primary studies AND represents them accurately (checked
  against our own `data/ingredients/*.md` grades). *Strongest signal.*
- **claims_aligned** — 3 sampled claims align with our graded evidence; not overstated.
- **no_pseudoscience** — avoids detox/"toxic"/absolutism/scaremongering. Any present = DQ.
- **sponsorship / conflict** — sponsorship density; own-brand line; affiliate storefront
  that monetizes picks (-> `product_recs: restricted`, picks treated as paid).
- **credential_verified** — board-cert/chemistry verifiable from public info. BONUS, not
  required; a rigorously science-aligned non-credentialed educator can still be MED.

Verdict: `add-high` (credentialed or clearly science-rigorous) / `add-med` (non-credentialed
but science-aligned / routine-focused) / `reject` (pseudoscience, unverifiable,
deceased/inactive, duplicate, or not-confident). Same schema as the existing roster:
`name, creator_slug, credential, tier (HIGH/MED), channel, conflict, product_recs, last_pulled: null`.

Living-person safety: never roster a deceased or unverifiable person as active; reject on
any doubt.

## 3. Prioritized intake (what we card)

Bias card intake to two signatures, harvested during vetting and on each future pull:
- **study-citing** ("the science of…", a named trial/author-year) -> card + queue/build the
  study page + cross-link every entity mentioned.
- **routine-suggesting** ("PM routine", "how to layer", "routine for <condition>") -> card
  on the most relevant condition/goal hub + feed the Routine Builder.

Every card remains transcript-grounded, self-contained (names the subject, introduces the
creator + credential), sponsorship-scanned, and deduped by video id.

## 4. Mechanics & pacing

Vet (workflow, bypasses the session agent cap) -> auto-add passers to the roster + write the
audit log -> queue harvested videos -> parallel read-only intake drafts cards -> apply
centrally, each linking every mentioned page. Then the daily video-pull cron keeps the
expanded roster fresh on rotation. Bounded passes (~15-20 candidates), repeatable.

## 4b. Rotation jams: when the oldest `last_pulled` is a creator we always skip

`roster_next.py pull` and `roster_next.py noyt` return the creator with the
oldest `last_pulled`. A creator whose content the pull crons are instructed to
skip therefore becomes the permanent head and is re-offered on every tick, since
skipping does not advance their date. The fallback path then costs a tick and
yields nothing.

Observed twice on 2026-10-25: `noyt` returned **Kristin Leite** both times. Her
roster conflict is an Amazon affiliate storefront, and the pull crons treat an
affiliate-storefront creator's picks and favourites as effectively paid, which is
most of what she posts. Nothing is wrong with the rule or with her vetting; the
rotation simply has no way to express "eligible, but only for part of their
output".

How to handle it, in order of preference:

1. **Pull them for the eligible slice.** Her conflict line already says to prefer
   educational, how-to and ingredient-explainer clips, so those ARE cardable. A
   tick that pulls her catalog and cards an explainer is the intended outcome,
   not a workaround.
2. **If the eligible slice is genuinely empty**, that is a roster decision rather
   than a per-tick one: either set `product_recs: never` so the restriction is
   explicit, or drop the creator from the rotation. Leave it to a human; do not
   quietly advance `last_pulled` for a creator you did not actually pull, which
   fakes the bookkeeping and hides the jam.

Do not advance `last_pulled` to clear the head. The analogous Track 2 problem and
its `9999` sentinel are in docs/video-backfill-process.md; Track 1 has no
equivalent sentinel yet, and a `rotation_skip: true` flag would be the clean fix.

## 5. Audit trail

`data/creator-vetting-log.yaml`: one entry per candidate ever vetted — verdict, reason,
resolved platforms, rubric summary, date. Because additions are automatic, this log is how
a human spot-checks the gate and catches a bad call after the fact.
