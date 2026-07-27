# Lesson: design-mockup copy still has to pass the critic

**Date:** 2026-07-27

## What happened
While shipping the new evidence-dossier UI, the on-page copy was lifted verbatim from a design
mockup the user had approved ("nice, looks great"). One approved line, the overall-summary
blockquote, read: "The two studies of this specific cream did not show it works better than a
plain or cheaper emollient." The critic caught that only one of the two studies (Leshem 2020)
tested CeraVe at all; the other (Spada 2021) tested a different ceramide cream from a different
maker. The summary overstated the product-specific evidence and contradicted our own Leshem
bottom line one screen down. Fixed before the push; re-review returned publish.

## Five whys -> root cause
Copy written to look persuasive in a mockup optimizes for reading well, not for being exactly
true. It slipped toward a cleaner, stronger claim than the sources support. Because the user had
approved the *design*, it was tempting to treat the *words* as approved too and skip the gate.

## Rules going forward
1. User approval of a design/mockup is approval of the LAYOUT, not a fact-check of the COPY.
   Any factual sentence, even one the user liked in a mockup, goes through `sk lint/verify/style`
   and the critic before it ships. The review-gate (R1) is not optional for "already approved" text.
2. Summary/TL;DR lines are the highest-risk copy: they compress, and compression is where
   overstatement hides. Grade the headline claim against the sources as strictly as any body claim.
3. Watch for internal contradiction as a tell: when a page's summary and its own body disagree
   (here, "two studies of this cream" vs "the one study of this exact cream"), the summary is
   usually the one that drifted.
