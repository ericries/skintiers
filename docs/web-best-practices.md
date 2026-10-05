# Web best practices for SkinTiers (human, agent, and search)

Written 2026-10-05. This is the external-guidance half of the UX work; the internal
reader contract lives in `skill/SKILL.md` and the token side in
`docs/token-efficiency.md`.

The site now has three distinct audiences and they want different things from the
same page. A **human** wants the answer and a reason to trust it. An **LLM agent**
wants to resolve an entity, read a grade, and cite a URL without crawling. A
**search engine** wants to know what the page is about, that it is trustworthy, and
that it loads. Most of what follows serves more than one at once, which is how to
prioritise it.

**Verification note.** Thresholds and required properties below were checked against
the sources listed at the end. Where something is marked *unverified*, I did not
confirm it from a primary source in this pass and it should not be treated as fact.

## 1. Structured data

Verified requirements for `VideoObject`: Google requires `name`, `thumbnailUrl` and
`uploadDate`, plus either `contentUrl` or `embedUrl`. Recommended are `description`,
`duration`, `contentUrl`, `interactionStatistic` (the current property; the old
`interactionCount` is deprecated) and `hasPart` for key moments. Thumbnails should be
treated as editorial content: stable, representative, and fetchable.

What SkinTiers should do:

- We emit `VideoObject` on all 407 video pages with name, url, description,
  `uploadDate`, `thumbnailUrl`, `embedUrl`, `contentUrl` and `author`. That clears the
  required set.
- **`duration` is the real gap.** It is recommended, we do not store it on cards, and
  yt-dlp already returns it. Backfilling `duration:` onto video cards and emitting it
  as ISO 8601 is the single highest-value structured-data improvement left.
- `interactionStatistic` (view count) is available from `video_views.py` but is not
  stored either. Lower value than duration, and it goes stale, so prefer duration first.
- Keep `Article` on profiles and `BreadcrumbList` on video and creator pages, both of
  which we now emit.
- **Do not add `Product` or `Review` markup to product pages.** We are an editorial
  reviewer that sells nothing and takes no prices from a merchant feed. Whether
  Google's policy formally forbids it for non-merchant editorial sites is *unverified*,
  so the argument for leaving it off is the honest one rather than the policy one: our
  grades are two-axis editorial judgements, and flattening them into a single
  `ratingValue` would misrepresent them in exactly the way rule 2 of the skill forbids.

## 2. Core Web Vitals

Verified thresholds, assessed at the 75th percentile of real page views over a rolling
28 day window: LCP 2.5s or less, INP 200ms or less, CLS 0.1 or less. A page passes only
when all three are green.

What SkinTiers should do:

- The Feed was the one real offender, loading 309 YouTube iframes in a single document.
  That is now a click-to-play facade, so the page ships lazy JPEG thumbnails and no
  third-party player JS until a click. This was an LCP and INP fix at once.
- Individual video pages keep one real iframe, which is correct: one embed is the
  content, and it is below the fold with `loading="lazy"`.
- **Reserve space for embeds to protect CLS.** `.vid-embed` already sets
  `aspect-ratio:16/9`, so the box does not collapse before the thumbnail loads. Keep
  that invariant if the markup changes.
- The remaining known weight is the Feed's own HTML (roughly 800KB for 407 cards).
  It is text and compresses well, but if INP ever regresses, paginating or
  virtualising the Feed is the next lever, not removing the filters.

## 3. E-E-A-T and health content

This site is squarely in the "your money or your life" category, where Google asks for
demonstrable expertise and trustworthiness. The precise current wording of Google's
quality-rater guidance was *not* re-verified in this pass, so treat the specifics below
as the general shape of the ask rather than quotation.

What SkinTiers should do, and mostly already does:

- Every load-bearing claim cites a primary source inline. Keep that absolute.
- **Disclose creator conflicts.** This is the strongest trust signal we have and almost
  nobody in the category does it. Video and creator pages now surface the roster's
  disclosed conflicts (own brands, affiliate storefronts, paid partnerships) and state
  that a restricted creator's product picks are not treated as independent
  recommendations. Extend the same treatment to person pages.
- **Show review recency.** Pages carry `updated` and `analyzed`; `dateModified` is in
  the `Article` JSON-LD. Surfacing "last checked" visibly on the page, not just in the
  frontmatter, is a cheap remaining win.
- Keep the quarantined marketing-claims section. Naming a brand's claim and then
  grading it is a trust signal, not a liability.
- Keep `assurance:` honest. Claiming `opus` without a critic pass, which `sk publish`
  used to do, actively damages this.

## 4. Definitive pages and internal linking

The pattern that external guidance converges on, under names like pillar page and topic
cluster, is: one page owns a topic, it links generously to the narrower pages that
support it, and those link back. Authority accrues to the hub through the structure, and
a reader can always get from a specific thing to its context and back.

What SkinTiers should do:

- Video pages were orphan embeds. They now carry provenance, topic links split into
  cited-as-evidence-on versus also-relevant-to, other vetted videos sharing those
  topics, and a creator panel. 401 of them now link sibling videos.
- **The hub-and-spoke invariant to preserve:** a hub ranks and links out, a spoke owns
  its own evidence and links back. The recurring failure is duplication, a hub
  re-explaining what a spoke owns. `NEVER re-explain what another page already owns`
  in the writing guide is the rule that protects this.
- Breadcrumbs now exist on video and creator pages. Adding them to profile pages would
  complete the pattern.
- Related-content blocks should be computed from real relationships (shared topics,
  shared actives), never from a hand-maintained list that rots.

## 5. Accessibility

Not separately verified against WCAG 2.2 text in this pass, so this is the practical
subset rather than a compliance claim.

What SkinTiers should do:

- Keep one `h1` per page and a sane heading order. The new video sections use `h2` with
  `h3` beneath, which is correct.
- Keep visible focus. The Feed filters and the video facade both set
  `:focus-visible`. Any new interactive control must too.
- The facade is a real `<button>` with an `aria-label` naming the video, not a div.
  Keep that: it is the difference between keyboard-operable and not.
- Filtering uses the `hidden` property, so hidden cards leave the accessibility tree
  rather than being merely invisible. The live count is `aria-live="polite"`.
- Link text should name its destination. "Watch on YouTube" and "All videos from X"
  are fine; a bare "here" never is.
- Both themes need checking when colours change: the site is theme-aware and the
  conflict badge uses the mid-tier colour in both.

## 6. Agent-readable conventions

Verified: `llms.txt` is a markdown file at the site root. The only required section is
an `h1`; an optional blockquote summary and body may follow, then `h2` sections of
markdown links with optional colon-separated descriptions. An `llms-full.txt` variant
carries whole content rather than links. Google confirmed in May 2026 that it is not
required for Google AI features but is useful for agent readiness.

What SkinTiers should do:

- We now emit `llms.txt` to spec. It deliberately front-loads the two things agents get
  wrong here (effect and evidence are separate axes; `key_actives` is not an ingredient
  list) above the link lists, because those cost accuracy when missed.
- **Entity resolution is the thing agents actually lack.** Observed external agents
  grepping the tree for a named product and concluding it was absent. `sk find` and
  `lookup.json` now answer that, and both are advertised first in `llms.txt`, the
  README and `SKILL.md`. Any new agent affordance should be judged the same way: does
  it stop a guess?
- Make the failure mode explicit everywhere: a name that does not resolve is **not
  indexed**, which is a different claim from **not covered**. Agents conflate these and
  it produces confidently wrong answers.
- `llms-full.txt` is not worth it here. The corpus is ~931 pages of long-form evidence;
  a single bundled document would be enormous and immediately stale. The per-type
  listings plus `lookup.json` are the better shape.

## Priority order

| Change | Impact | Effort |
|---|---|---|
| Backfill `duration:` on video cards, emit in `VideoObject` | High, only missing recommended property | Medium, needs a data pass |
| Surface "last checked" date visibly on profile pages | High trust/E-E-A-T, cheap | Low |
| Breadcrumbs on profile pages | Medium, completes the pattern | Low |
| Conflict disclosure on person pages | Medium, extends our best trust signal | Low |
| `interactionStatistic` on video JSON-LD | Low, and goes stale | Medium |
| Paginate or virtualise the Feed | Only if INP regresses | Medium |

Deliberately not doing: `Product`/`Review` schema (misrepresents two-axis grades),
`llms-full.txt` (too large, stale immediately).

## Sources

- [llms.txt specification](https://llmstxt.org/) (fetched: required h1, optional
  blockquote and body, h2 link sections, `llms-full.txt` variant)
- [Google Search Central, video SEO best practices](https://developers.google.com/search/docs/appearance/video)
- [Video schema markup guidance](https://swarmify.com/blog/video-schema-markup/) and
  [structured data for video content 2026](https://contadu.com/structured-data-video-content-2026/)
  (required vs recommended `VideoObject` properties, `interactionCount` deprecation)
- [Core Web Vitals thresholds 2026](https://prooflytics.io/blog/core-web-vitals-thresholds-2026-lcp-inp-cls)
  and [Core Web Vitals in 2026](https://dev.to/mecanik-dev/core-web-vitals-in-2026-how-to-actually-pass-2cm2)
  (LCP 2.5s, INP 200ms, CLS 0.1, 75th percentile over 28 days)
- [Meet llms.txt, a proposed standard](https://searchengineland.com/llms-txt-proposed-standard-453676)
  and [what is llms.txt](https://www.semrush.com/blog/llms-txt/) (adoption status, Google's May 2026 position)
