# UX & readability audit — the nervous-newcomer archetype

**Date:** 2026-07-29 · **Scope:** one bounded pass, design *proposal* only (no page restructuring done).
**Reader modeled:** knows a little from r/SkincareAddiction, intimidated by the science, wants to sort
truth from marketing fast. Grounded in the current templates (`profile.html`, `listing.html`, `base.html`,
`method.html`, `whats_new.html`) and `static/style.css`. Ranked by impact for that reader.

> Note: written during an account spend-limit pause, so this is analysis from the templates/CSS and the
> pages shipped this session rather than a fresh multi-agent crawl. Treat as the morning design brief; it
> dovetails with review-queue.md items #1 (tier-list format) and #11 (wall-of-text pass).

## Top improvements

1. **Every tier list needs a click-down tier summary at the top** (content+template). A newcomer hitting
   a barrier/anti-aging/glass-skin page sees a wall of `## Tier 1…4`. Add a compact summary card at the top:
   the four tier labels as chips, each linking to its anchor, with a one-line "what's in it." This is
   already review-queue #1(a); it is the single highest-impact scannability win. Template: render from the
   `## Tier N:` headings (or a small `tiers:` frontmatter block) into a `<nav class="tier-summary">`.

2. **Stronger visual separation between items within a tier** (CSS). Items are `**Bold lead.** prose…`
   runs that blur together. Give each a left-accent card so the eye can count them:
   ```css
   .prose .tier-item{border-left:3px solid var(--rule-strong);padding:2px 0 2px 14px;margin:14px 0}
   .prose .tier-item strong:first-child{color:var(--ink)}
   ```
   Needs a content convention (wrap each item) or a build-time transform of `**lead.**`-initial paragraphs.

3. **Lead every page with the verdict in one scannable line** (content). Product pages have the grades
   dossier, but condition/goal pages bury the "so what." A standfirst is present; make it always answer
   "what actually works / what to ignore" in the first sentence, before mechanism.

4. **Grade dossier needs a plain-language legend on hover/first use** (template). "effect: modest ·
   evidence: preliminary" is jargon to this reader. Add a one-line inline gloss or a `?`→Method tooltip so
   the two axes are self-explanatory without leaving the page.

5. **Sticky in-page table of contents on long pages** (CSS+template). Condition/ingredient pages run
   1,000+ words of `##` sections. A slim sticky TOC (desktop side rail, collapsible on mobile) built from
   the existing heading IDs turns a scroll-hunt into a click. `position:sticky;top:1rem` in the margin the
   photo-rail already uses.

6. **Distinguish health vs cosmetic claims visually, not just in prose** (CSS). The house rule separates
   them; the reader can't see it. A small pill — `health` (accent) vs `cosmetic` (muted) — on the relevant
   bullets makes the site's core value legible at a glance.

7. **"What's Overhyped" / marketing-claim sections deserve a distinct treatment** (CSS). This is the
   truth-from-marketing payload the archetype came for. A subtle warning-tinted block (not alarmist) sets
   it apart from the neutral evidence sections.

8. **Listing pages: add a one-line descriptor under each linked title** (template). `products.html` groups
   by category but is a bare link list. A muted one-liner (pull the standfirst's first clause) tells a
   nervous reader which page answers their question before they click.

9. **Trust signals above the fold** (template). The reader's whole reason to trust this over a forum is
   sourcing. Surface "N sources, last verified <date>" near the top of each profile (data already exists in
   frontmatter/footnotes), linking to `## Sources`.

10. **Numbers need tabular alignment and emphasis** (CSS). Stats (`SMD -1.04`, `96%`, `$39.97`) are inline
    in prose. `font-variant-numeric: tabular-nums` where they cluster, and consider a `<mark>`-style
    highlight for the one headline number per section so a skimmer catches it.

11. **Mobile type scale + line length** (CSS). Verify body stays ~60–70ch and headings don't crowd on
    360px; the existing `@media (max-width:560px)` bumps body to 18px — confirm `h2/h3` rhythm and
    `.tier-summary` reflow there too.

12. **Condition pages: make "How to know you have this" a visually anchored opener** (CSS). It's now the
    first section (good, shipped this session) — give it a light callout treatment so the anxious reader
    immediately sees "am I in the right place?" without reading a paragraph to find out.

13. **Consistent "See Also → tier list" everywhere** (content+template). Per the 2026-07-28 request, bare
    See-Also lists should become ranked tier lists (retinoids by potency, etc.). Same component as #1/#2.

14. **Dark-theme contrast spot-check on the new components** (CSS). The changelog, photo-rail, and any new
    tier cards must be checked against `:root[data-theme="dark"]` tokens, not just the media query — the
    theme toggle stamps `data-theme` and must win both directions.

15. **A short "how to read this page" affordance, once** (content). A single muted line near the masthead
    ("grades are relative and named; jargon is defined in The Evidence") lowers the intimidation barrier
    without the banned defensive meta-commentary — phrased as orientation, not apology.

## Suggested sequencing
Items 1–2 (tier summary + item cards) unlock the most scannability and are prerequisites for #13. Then the
trust/legibility set (3, 4, 9, 6). Then the polish (5, 7, 10, 12). Build 1–2 as a shared `tier-list`
component so every tier page and every See-Also-turned-tier renders identically.

## Not done tonight (by design)
No page restructuring; no schema/policy changes. No CSS was committed this pass (spend-limit pause + to keep
the proposal reviewable as one unit). Each item above says whether it is CSS/template or a content convention.
