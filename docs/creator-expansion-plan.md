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

## 5. Audit trail

`data/creator-vetting-log.yaml`: one entry per candidate ever vetted — verdict, reason,
resolved platforms, rubric summary, date. Because additions are automatic, this log is how
a human spot-checks the gate and catches a bad call after the fact.
