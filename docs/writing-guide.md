# SkinTiers Writing Guide (house voice). Read before authoring or reviewing any profile.

Read this together with `docs/anti-ai-ese.md` (style mechanics and the words to avoid). Run
`sk lint`, `sk verify`, and `sk style` on every page before publishing.

## Prime directive
Every page has a purpose. A section or claim earns its place only if it serves that purpose.
Rigor is not exhaustiveness. Honesty is not announcing every absence. Concision is a virtue.

## Three rules that govern the voice
1. **Inform, do not instruct.** State what the evidence shows. Do not tell the reader what to
   do. No "pick it", "skip it", "don't be fooled", "don't overpay", "you should". Present the
   comparison and the reader decides.
2. **No uncited editorial or contestable claim.** Every substantive statement is backed by a
   named authority or a citation. Words like "oversold", "not worth it", or "the best" are
   opinions. Instead report the cited fact and let the reader draw the conclusion. This also
   limits our liability.
3. **No AI-ese.** Plain human prose. No em dashes, no LLM stock phrases, no rule-of-three, no
   negative parallelism. See `docs/anti-ai-ese.md`.

## Product page. Purpose: how does THIS product compare to others in its category?
Answer that, with cited facts, and let the reader decide. Include a section only if it has
substance. The linter requires `grades:` frontmatter and a `## Sources` heading.
- **First paragraph: what it is.** One neutral sentence. The build lifts it out as the
  standfirst at the top of the page (the "what is this" summary), so it must stand alone.
- **`grades:` frontmatter drives the dossier** (there is no `## The Rubric` prose section any
  more). Each row is one use: `use`, an optional short `note` comparator, `effect`
  (none/minimal/modest/notable/strong) and `evidence`
  (anecdotal/preliminary/mixed/solid/gold-standard). Every grade must be traceable to the cited
  evidence in `## The Evidence`. Grades are relative and name comparators. No "pick it / skip it".
- **Overall bottom line:** right after the first paragraph, one blockquote (`>`) giving the
  plain-English overall picture, cited. Blockquotes render as an italic callout.
- `## The Evidence`: the general category question belongs on a linked concept page, not here.
  State the category benefit and link out (for example `[[moisturizing]]`). Then give the
  product-specific evidence, cited: does a study of THIS product (or its formula) show it does
  more than a plainer or cheaper option, or not? Report what the study found. **After each cited
  study, add one blockquote bottom line**: a plain-English restatement that is 100% faithful to
  the finding (no new claim, no spin). It renders in italics.
- `## What's In It`: brief. Which ingredients have cited evidence and which do not. Link them.
- `## See Also`: one line of bare `[[links]]` to broadly similar products. Do NOT announce that
  no comparison exists. If a real cited head-to-head comparison exists, report it instead.
- `## Where to Buy`: verified SKU-level links only. No disclaimer text.
- `## Sources`: only what this page cites. Renders as the numbered reference list.
- `recommended_in:` frontmatter (optional): external best-of lists that recommend this product,
  each `title` + `url` + `source`. Every URL must be verified to load AND to actually recommend
  the product. Omit the field entirely if none verify. Never fabricate a list or a URL.
- `image:` frontmatter (optional): a verified product-photo URL or a file in `static/images/`.
  Omit to fall back to the generated monogram badge.

Everything a reader could follow is a link: ingredient, brand, study, person, and product names
use `[[slug]]`. If no profile exists yet, create a `status: stub` profile so the link resolves
(a stub is one neutral sentence, no fabricated facts) rather than leaving plain text.

Do not on a product page: re-explain whether the category works (link out), narrate the
research process, write "no X found", pad a tier, add disclaimers, or editorialize a citation.

## General category or mechanism evidence lives on its own page, linked
"Does moisturizing work and how" goes on the Moisturizing page. Retinoid mechanism goes on the
retinoid ingredient page. Product pages borrow it with a link and stay on the product question.

## Omit-empty (all page types)
Never announce an absence. If a section, tier, or comparison has nothing cited to say, delete
it. Never invent. The choice is silence, not fabrication.

## Related resources (link out, never copy)
Where a better external source exists, link it and add our value (the cited grade). INCIDecoder
for full INCI, LabMuffin or Cochrane for deeper science, DermNet for conditions, YesStyle or
Stylevana for K-beauty buying, relevant subreddits for community. Never copy their text.

## Voice
Plain, neutral, cited, concrete. Lead with the cited bottom line. A trustworthy briefing, not a
marketing page and not a journal abstract.

*History: see `_lessons/2026-07-27-editorial-voice.md`.*
