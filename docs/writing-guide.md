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
- `## What's In It`: the ingredient list, split into the notable/functional ones (linked to their
  own pages) and the base/texture/preservative system (plain). Optionally a composition-fact line
  of conspicuous absences (see Omit-empty). Do NOT narrate which ingredients lack evidence or that
  no study isolates them; the grade and The Evidence carry the efficacy question.
- `## See Also`: one line of bare `[[links]]` to broadly similar products. Do NOT announce that
  no comparison exists. If a real cited head-to-head comparison exists, report it instead.
- `## Where to Buy`: verified SKU-level links only. No disclaimer text.
- `## Sources`: only what this page cites. Renders as the numbered reference list.
- **`category:` frontmatter (required):** the high-level bucket the Products index groups this
  product under. Use one of the existing category labels (Sunscreens, Moisturizers, Retinoids,
  Vitamin C serums, Azelaic acid, Peptide serums) when the product fits; the two format buckets
  (Sunscreens, Moisturizers) take precedence over active-based ones. A product with no `category`,
  or one whose label is not in `PRODUCT_CATEGORY_ORDER` in `build.py`, falls into an "Other" bucket
  at the bottom of the index. If a genuinely new high-level category is needed, do not invent it
  silently: add the label to `PRODUCT_CATEGORY_ORDER` (with a matching test) and flag it for review.
- `recommended_in:` frontmatter (optional): external best-of lists that recommend this product,
  each `title` + `url` + `source`. Every URL must be verified to load AND to actually recommend
  the product. Omit the field entirely if none verify. Never fabricate a list or a URL.
- **Product image(s): required.** Every product page shows the actual product. Use `images:`
  (a YAML list) for one or more, or `image:` for a single one. Each entry is a verified
  manufacturer or retailer product-photo URL (prefer the manufacturer's own hosted image), or a
  file committed under `static/images/`. Confirm the URL loads and shows THIS product/SKU before
  using it. These are the product's own promotional images, shown to identify the product; do not
  restyle or crop out marks. If no image can be verified, the page falls back to the generated
  monogram badge, but that is a gap to fill, not the goal.

Everything a reader could follow is a link: ingredient, brand, study, person, and product names
use `[[slug]]`. If no profile exists yet, create a `status: stub` profile so the link resolves
(a stub is one neutral sentence, no fabricated facts) rather than leaving plain text.

Do not on a product page: re-explain whether the category works (link out), narrate the
research process, write "no X found", pad a tier, add disclaimers, or editorialize a citation.

## Sunscreens: grade in a global context, and explain SPF
Sunscreen is a special case. Evaluate every sunscreen against the GLOBAL field, not just its home
market. Several modern UV filters standard in the EU, Korea, and Australia (bisoctrizole / Tinosorb
M, and the Mexoryl filters) are still outside the US OTC monograph, and bemotrizinol / Tinosorb S
was only added to it in 2026, so most sunscreens on US shelves still rely on older filters
(avobenzone, homosalate, octocrylene, octisalate) whose UVA protection and photostability are
weaker. A US "Broad Spectrum SPF 60" built on those older filters is not equivalent to a Korean or
European broad-spectrum product built on modern filters.
- **Explain the mechanism, cited.** SPF measures protection against UVB (sunburn). UVA (photoaging,
  and a cancer contributor) is a separate axis that the older US filters cover less well. State
  which filters the product uses and what part of the spectrum each covers, per the label.
- **The rating must reflect real spectral coverage, not the SPF number or the "Broad Spectrum"
  checkbox.** A high SPF built on an older, photounstable UVA filter set does not earn a top effect
  grade for overall photoprotection; name the modern-filter comparators (Tinosorb, Mexoryl) it
  falls short of. Grade UVB and UVA honestly rather than collapsing them into one "sunscreen" grade.
- The general SPF/UVA mechanism and the global filter landscape live on [[sunscreen-uv-filters]];
  the product page links out and applies it to the specific filter set.

## General category or mechanism evidence lives on its own page, linked
"Does moisturizing work and how" goes on the Moisturizing page. Retinoid mechanism goes on the
retinoid ingredient page. Product pages borrow it with a link and stay on the product question.

## Omit-empty (all page types)
Never announce an absence of EVIDENCE. State only what the evidence DOES show and let the reader
infer the rest. Delete hedges such as "no study of this product isolates X", "the presence of an
ingredient is not proof it works", "evidence is limited", "no head-to-head trial exists". If a
section, tier, or comparison has nothing cited to say, delete the whole section. Never invent. The
choice is silence, not fabrication.

One narrow exception: a concrete COMPOSITION fact that corrects a likely misconception or matters
to the reader is content, not a hedge. "The formula contains no niacinamide (some other CeraVe
products do), no added fragrance, and no drying alcohol" is a verifiable fact about what is IN the
product, and is allowed. "No study isolates each ingredient's effect" is an evidence gap, and is
not. Test: is it a fact about the product's makeup (allowed) or about what research has not done
(delete it)?

## Related resources (link out, never copy)
Where a better external source exists, link it and add our value (the cited grade). INCIDecoder
for full INCI, LabMuffin or Cochrane for deeper science, DermNet for conditions, YesStyle or
Stylevana for K-beauty buying, relevant subreddits for community. Never copy their text.

## Voice
Plain, neutral, cited, concrete. Lead with the cited bottom line. A trustworthy briefing, not a
marketing page and not a journal abstract.

*History: see `_lessons/2026-07-27-editorial-voice.md`.*
