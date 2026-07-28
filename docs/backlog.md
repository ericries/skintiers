# SkinTiers backlog (future-phase ideas)

Deferred work, not yet scheduled. Entity research goes in `data/queue.yaml` instead; this file
is for tooling, capabilities, and page-type ideas. Keep entries short: what, why, open questions.

## Embed short-form expert video (with transcript) on relevant pages
Added 2026-07-27 (user request). Some dermatologist/influencer evidence is delivered as short
videos (for example Shereene Idriss, `@DrIdriss` on YouTube; she is queued as a `person`). We want
to cite and embed that video type on the relevant product/ingredient page.
- **Grab the transcript** so the claim is quotable and citable in our voice (a video alone is not
  a verifiable primary the way a quoted transcript line is). YouTube exposes captions/transcripts;
  investigate `youtube-transcript-api` (Python) or the timedtext endpoint. Store the verbatim
  transcript excerpt + timestamp + video URL as the citation.
- **Embed** the clip on the page (privacy-friendly `youtube-nocookie.com` iframe, or a thumbnail
  that links out) scoped to the timestamp of the relevant claim.
- **Open questions:** copyright/fair-use of embedding vs linking; how influencer claims are
  graded (they are anecdotal-tier evidence unless they cite a trial); where the embed sits in the
  page (probably a quoted line in `## The Evidence` with the clip beside it, contextualized, never
  presented as proof on its own). Consistent with "we accept influencer/derm/aesthetician
  evidence, each contextualized in its own section."

## Generated canonical badge / QR image per product
Square badge (brand monogram, color by entity type, QR to the page). The monogram badge shipped
2026-07-27 is the placeholder; this is the full version. Plus a composite "routine-signature"
image a user can post to Reddit/forums.

## Client-side routine builder
URL-addressable, user-buildable routine page that computes ingredient/goal coverage from the
structured layer. Needs grades and ingredient data as queryable JSON (partially in place).

## Studies scraper as a no-LLM GitHub Action
Parse chosen feeds (PubMed/Cochrane) into `data/pending-*.yaml` candidates. Keep it off the LLM
budget (deterministic parsing only), per the free-Actions-plan constraint.

## Anti-aging: full coverage of non-topical interventions (LATER PHASE)

The anti-aging + perimenopause goal page (drafted 2026-07-28) brackets these as context but does NOT
link to object pages, per user decision "full coverage, but in a later phase; for now don't link":
- Systemic hormone replacement therapy (HRT)
- Topical/prescription estrogen (estriol/estradiol creams)
- In-office procedures (laser resurfacing, microneedling, biostimulator/HA injectables, PDRN/polynucleotides)
- Behavior (smoking cessation, sun-avoidance habits)
- Ingestible supplements as their own type (oral collagen, oral HA) and devices (red-light/LED)

Later phase = decide entity types (treatment? procedure? device? supplement?) with the user, then
give each its own profile and wire the anti-aging goal page to link them.
