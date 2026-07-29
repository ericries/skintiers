# SkinTiers Writing Guide (house voice). Read before authoring or reviewing any profile.

Read this together with `docs/anti-ai-ese.md` (style mechanics and the words to avoid). Run
`sk lint`, `sk verify`, and `sk style` on every page before publishing.

**Definition of done (every batch):** pages ship *live* the moment the critic clears them —
there is no draft-for-sign-off hold. Publishing (flip `status: published`, commit, push) is
part of the batch, not a follow-up. A batch is not done until `sk audit` reports **0 hard
leaks** (nothing drafted-but-uncommitted, nothing critic-cleared but still `draft`). See
`docs/postmortems/2026-07-28-stuck-drafts.md` for why this rule exists.

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

**Two rules that shape the whole page:**

**1. Results-first, jargon-later, for a lay audience.** The archetype reader knows a little from a
hardcore skincare forum but is intimidated by the science. Lead with what the product DOES, how to
use it, what it pairs with, and how credible it is overall, in plain accessible language modeled on
the anti-aging goal page. Push the scientific detail (mechanisms, surrogate markers, p-values,
study limitations) down into `## The Evidence`, where an expert reviewer can check our work. Never
open with jargon. Be clear and affirmative about what IS settled ("vitamin C is a well-evidenced
antioxidant, and this is a well-studied formulation of it") before getting into nuance.

**1a. Never instruct the reader; attribute usage guidance.** Do not tell the reader what to do.
Avoid imperatives such as "apply this in the morning", "use it twice a week", "start slow",
"pair it with sunscreen", "wait 20 minutes". Usage guidance is only allowed when it is SOURCED:
either (a) quote an authority (a named dermatologist, the manufacturer's own directions, a reputable
outlet) stating it, with a link, or (b) frame it as an attributed norm and link an example, e.g.
"vitamin C serums are typically recommended for morning use under sunscreen ([dermatologists in
Wirecutter describe that routine](url))". Report how a product is commonly used as a cited fact,
never as a command in our own voice. The same applies to routines and frequency.

**2. Attribute editorial opinions to credible sources; do not manufacture them.** When the page
needs a judgment that is not a plain fact (is it good, is it worth the price, is it the best or the
original version, is it worth the hype), do NOT invent our own verdict or let a house-generated
grade stand in for it. Find credible sources and quote them VERBATIM, and present the balance: if a
lot of dermatologists swear by a formula, quote one; if it is widely called the original or
best-studied of its kind, quote that; if critics say it is not worth the price, quote that too.
Admissible sources for these editorial/social claims are reputable named voices and publications
(board-certified dermatologists, cosmetic chemists, established review outlets) — this is a
lower bar than the primary-source rule for medical-efficacy facts, because "many derms rate it
highly" is a social fact, not a biological claim, but it must still be a real, quoted, attributed
source, never our own opinion or an anonymous consensus. Keep the factual evidence base
(is the active proven; is this a faithful formulation of it) stated clearly in our own voice and
cited to the concept/ingredient page. The grade must reflect the strength of the case for the
product's MAIN benefit (the proven active plus a credible formulation), not be dragged down to a
weak label just because the brand's own marketing studies are small; put those caveats in the
Evidence and in critics' quotes, not in a headline that misreads a proven product as unproven.

**3. Separate the CATEGORY verdict from the PRODUCT verdict, and state both.** A product page answers
two different questions, and must not let one stand in for the other: (a) does this category or
approach work (the ingredient-class evidence, graded skeptically and linked to the concept page), and
(b) is this a good example of that category (formulation quality, breadth, tolerability, price and
value, ease of access, and whether it is a best-in-class or notably cheap way in). A weak-category
verdict must NOT make a genuinely good product read as bad. If the category evidence is weak but the
product is well-formulated, inexpensive, or best-in-class, say BOTH plainly and up front: "the
evidence that [category] does much is [weak/mixed], but if you want [category], this is [a good / the
best / an unusually cheap] way to get it." Credit the product for what it is, value, formulation,
breadth, access, sourced, even while staying skeptical about the category. Grade the category
honestly; carry the product-quality/value judgment in the Summary (attributed where it is an
opinion). Do not lead with the better-evidenced ingredient's weakest cousin to make the whole product
look worse than it is.
- **First paragraph: what it is.** One neutral sentence. The build lifts it out as the
  standfirst at the top of the page (the "what is this" summary), so it must stand alone.
- **`## Summary` (required, comes first, after the standfirst): orient the reader before any
  evidence.** A short section, in plain language, that says: what the product is and who it is
  designed for; what (if anything) makes it distinct from a plainer or cheaper product in its
  category; how it has actually been studied; what it is good at and what it is not; and roughly
  where it sits on price. **Every load-bearing claim in the Summary must be verified later on the
  page and carry a link to that verification** — either a `[[link]]` to the concept/ingredient
  page that carries the general evidence, or an in-page link to the section below where the
  product-specific study is cited (link the exact phrase, e.g. `[studied only in small,
  inventor-run trials](#the-evidence)`). The Summary asserts nothing it does not later
  substantiate. Keep it honest and skeptical: if the distinctive claim is marketing, say the
  evidence for it is thin and link to where that is shown. Price is stated approximately and
  relatively (e.g. "premium-priced, about $X for 30 ml as listed"), sourced to the manufacturer
  SKU in `## Where to Buy` with its access date; do not assert a price as a permanent fact.
- **`grades:` frontmatter drives the dossier** (there is no `## The Rubric` prose section any
  more). Each row is one use: `use`, an optional short `note` comparator, `effect`
  (none/minimal/modest/notable/strong) and `evidence`
  (anecdotal/preliminary/mixed/solid/gold-standard). Every grade must be traceable to the cited
  evidence in `## The Evidence`. Grades are relative and name comparators. No "pick it / skip it".
- **Overall bottom line:** right after the first paragraph, one blockquote (`>`) giving the
  plain-English overall picture, cited. Blockquotes render as an italic callout.
- `## The Evidence`: **product-specific or very closely adjacent studies ONLY.** Do NOT rehash the
  general evidence for the active ingredient here. The question "does this ingredient work" lives on
  the ingredient/concept page; summarize what that page establishes in one AFFIRMATIVE sentence,
  then LINK OUT. Say what we DO know, not what we don't (for example "Topical vitamin C is a
  well-studied antioxidant with evidence for brightening and helping sunscreen work harder; see
  [[ascorbic-acid-vitamin-c]]"), never "it is unclear whether vitamin C works, see [[...]]". The
  one-line summary must match the linked page's actual graded verdict (do not overclaim). What
  belongs here is:
  a study of THIS product, or of its exact formula/combination, or one narrow step adjacent (e.g. a
  trial of the same fixed-combination formula, or a head-to-head against a named peer). If a study
  only tests the isolated ingredient at a generic concentration, it belongs on the ingredient page,
  not here, and you cite it there by link. Report what the product-specific study found, cited: does
  it show this product does more than a plainer or cheaper option, or not? **After each cited study,
  add one blockquote bottom line**: a plain-English restatement 100% faithful to the finding (no new
  claim, no spin). It renders in italics. If there is NO product-specific study, say so factually in
  one sentence and grade on the category evidence via the comparator note (a composition/evidence
  fact, not a hedge), then link out.
- `## What's In It`: the ingredient list, split into the notable/functional ones (linked to their
  own pages) and the base/texture/preservative system (plain). Optionally a composition-fact line
  of conspicuous absences (see Omit-empty). Do NOT narrate which ingredients lack evidence or that
  no study isolates them; the grade and The Evidence carry the efficacy question.
- `## Cheaper Alternatives` (dupes; required WHEN the product is expensive for its category):
  list the lower-cost "dupes" that established third-party "dupe of X" articles or lists identify as
  similar-formula alternatives. **Do NOT guess or infer dupes yourself from ingredient lists** —
  cite the existing dupe article/list as the source (that citation IS the claim's evidence), report
  what it says the dupe matches (e.g. "the same 15% C + 1% E + 0.5% ferulic acid combination at
  about $25"), and link each named dupe to its SkinTiers page (create a `status: stub` target if it
  has none, and queue it). If no credible source names a dupe, omit the section rather than invent
  one. For inexpensive products this section is usually unnecessary.
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
- **Product photos: several, from various sites, required.** They render as a concise photo RAIL
  floated into the side whitespace (no captions, no labels on the photos). Gather a handful of real
  photos of THIS exact SKU from different sites: the manufacturer plus two or more retailers (e.g.
  Target, Ulta, Dermstore, Amazon) so the reader sees packaging, texture, and label from several
  sources. The `source`/`source_url` are still recorded in the frontmatter (for provenance) but are
  NOT shown on the page. Each `images:` entry SHOULD be a mapping that records where the photo came
  from:
  ```yaml
  images:
    - file: skinceuticals-c-e-ferulic.jpg      # self-hosted under static/images/
      source: SkinCeuticals                     # the site it came from (shown as the caption)
      source_url: https://www.skinceuticals.com/...   # link to that site
    - file: skinceuticals-c-e-ferulic-target.jpg
      source: Target
      source_url: https://www.target.com/...
  ```
  A bare string entry (filename or URL) is still accepted for back-compat but carries no source
  caption. **Self-host: download each image into `static/images/` and reference it by filename.**
  Retailer/manufacturer CDNs frequently block hotlinking, and a curl/HEAD 200 does NOT prove a
  browser will render it, so do not rely on a remote URL as the `src`. Confirm the built page
  actually shows every image (not a broken box). Use the product's own promotional/retail photos to
  identify the SKU; do not restyle or crop out marks. If nothing can be verified, the page shows no
  gallery, which is a gap to fill, not the goal.

Everything a reader could follow is a link: ingredient, brand, study, person, and product names
use `[[slug]]`. If no profile exists yet, create a `status: stub` profile so the link resolves
(a stub is one neutral sentence, no fabricated facts) rather than leaving plain text.

**Inline "learn more" links carry an affirmative one-line summary.** When prose points the reader to
another page ("covered on [[X]]", "see [[X]]", "learn more on [[X]]"), first say, positively and
factually, what they will find there, then link: "Vitamin C is a well-studied antioxidant good for
brightening and boosting sun protection; learn more on [[ascorbic-acid-vitamin-c]]." Never a bare
pointer ("vitamin C is covered on [[X]]") and never a negative framing ("we don't know if vitamin C
helps, see [[X]]"). The summary must be faithful to that page's actual graded verdict. (The `## See
Also` list is the exception: it stays bare `[[links]]`, no summaries.)

Do not on a product page: re-explain whether the category works (link out), narrate the
research process, write "no X found", pad a tier, add disclaimers, or editorialize a citation.

## Condition pages: open with "How to know you have this"
Condition pages (acne, rosacea, eczema, and every subtype/deep-dive) MUST open, immediately after
the standfirst, with a plain-language **"How to know you have this"** section written for a
layperson. Describe, in everyday words: the recognizable signs and symptoms; where on the face or
body it typically appears; how it tends to feel (itch, sting, burn, flush); how long it lasts and
how it comes and goes; and how it is told apart from common look-alikes (e.g. rosacea's redness and
bumps vs acne's blackheads/whiteheads). Ground every feature in the clinical diagnostic criteria and
cite them, but frame it as recognition, not self-diagnosis: "these are the features clinicians look
for", never "you have X". Do not instruct the reader. Keep it accessible first; mechanism, evidence,
and treatment come after. Pair it with the standing note that only a clinician can diagnose. This
section is required on every condition page (retrofit existing ones).

## Study pages: a stub on encounter, then a very detailed lay summary
When research on any page relies on a study worth its own page, create a `status: stub` study landing
page immediately (one neutral sentence naming the paper) so the `[[link]]` resolves, and queue it for
a full write-up. It is fine to GROUP closely related studies onto ONE page (e.g. a drug's pivotal
trials together, or a systematic review with its key underlying RCTs) rather than one page per paper.
The full study page is a VERY DETAILED, plain-language summary written for a LAY audience: what the
study set out to answer and why it matters, who was in it (how many, who), what they actually did,
what they found (report the real numbers and explain what each means in everyday terms, with
denominators/CIs/p-values), how strong the evidence is (design, certainty, limitations), who funded
it and any conflicts, and what it does and does NOT show. Accessible first, with the exact statistics
available for an expert reviewer. Neutral voice; every number traceable to the paper; no site
self-reference, no process language.

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

## Health effects vs cosmetic effects (emphasize health)
The site's main purpose is to surface HEALTH effects, so every page must keep the two kinds of
effect distinct and lead with health where one is established.
- **Health effects** are measurable effects on skin biology or medical outcomes: barrier repair and
  transepidermal water loss, protection of DNA from UV (thymine dimers) and reduced skin-cancer
  risk, collagen synthesis, wound healing, and treatment of medical conditions (acne, eczema,
  rosacea, disordered pigmentation). This is what we foreground.
- **Cosmetic effects** are appearance only: radiance and glow, brightening, smoothing, evening tone,
  softening the look of fine lines, texture, finish. These are legitimate and worth reporting, but
  they are secondary to health.
Rules: label a claim or study endpoint as cosmetic when it is cosmetic, and never let a cosmetic
surrogate stand in for a health effect ("reduces the appearance of wrinkles" is cosmetic;
"increases collagen I synthesis" or "reduces UV-induced thymine dimers" is a health effect). In the
`## Summary` and in each `grades:` note, lead with the health effect when one is established and mark
cosmetic-only benefits as cosmetic. Where a grade row is for a cosmetic use, make that explicit in
its `use`/`note`. Do not upgrade a grade on the strength of cosmetic endpoints alone.

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
