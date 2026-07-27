# Anti-Hallucination Rules

**This is the single most important document in the project.** Every LLM-authored knowledge site dies without these disciplines. Every rule below corresponds to a real failure in Seedlist.

## The seven cardinal sins

### Sin 1: Fabricating URLs
Agents "remember" a URL pattern (e.g. `techcrunch.com/2024/01/company-raises-series-a`) and construct plausible-looking URLs from memory. These URLs are almost always wrong.

**Rule:** Every URL in a Sources section must come from a `WebSearch` result or a `WebFetch` response. If you cannot find a source URL, do NOT invent one. A missing citation is infinitely better than a fake one.

### Sin 2: Presenting paraphrases as direct quotes
Wrong: `"We love technical founders" — Jane Smith, TechCrunch interview, 2024` (when the exact words don't appear anywhere).
Right: `Jane Smith has said the firm prioritizes technical founding teams [^3].`

**Rule:** Only use quotation marks around text copied verbatim from a source. If you can't find the exact wording, write a factual statement instead.

### Sin 3: Guessing portfolio/product data
Every entry in a Portfolio/Products/Ingredients table must come from a specific source. If you "know" that Brand X uses ingredient Y but cannot find a source, do NOT include it.

**Rule:** Every table row needs a citation footnote proving the relationship. Garbage in → garbage out for the inferred analysis.

### Sin 4: Inventing percentages
`~30% niacinamide-heavy` without a denominator is a guess dressed as data.

**Rule:** Every percentage must be computed from counted data with the math shown: `12 of 28 products (43%)`. If sample size is too small, use qualitative descriptions.

### Sin 5: Padding "What Users Say" (or equivalent)
Marketing testimonials from the brand's own site written in third person are NOT user quotes. The investor's own anecdote about a user is NOT a user quote.

**Rule:** "What Users Say" (or "What Founders Say", "What Patients Say", etc. depending on topic) contains ONLY quotes from actual users/patients/founders sourced independently. If you cannot find any, write: `"No independently sourced testimonials found."`

### Sin 6: Trusting aggregators as primary sources
Wikipedia, retailer product descriptions, ingredient wiki sites, Crunchbase summaries, AI-generated summaries — none are primary. All summarize other sources with variable fidelity.

**Rule:** Use aggregators only as leads. Click through to the actual company blog, press release, patent, peer-reviewed paper, regulator filing. Cite the primary.

### Sin 7: Verifying with search but citing the wrong URL
Agents sometimes WebSearch, find the right info in snippet, then cite a URL that's not the one containing the info.

**Rule:** After writing a profile, re-fetch each source URL with `WebFetch` and confirm (a) the URL loads, (b) the page contains the information you cited, (c) any quotes match verbatim. If mismatch, remove the citation and the claim.

## The three-source rule (mandatory)

Every non-trivial fact — date, amount, participant, ingredient, concentration, patent number, mechanism of action — needs:
- **Source A:** The entity's own page (brand blog, press release, product page, official statement)
- **Source B:** A second first-party source (co-participant's page, regulator filing, patent, clinical trial registration, formulator's site)
- **Source C:** Contemporaneous tier-1 press (WSJ, Bloomberg, TechCrunch, Nature, Cochrane, Allure, Vogue Business, peer-reviewed journal in the topic area)

**When only 2 sources agree, mark the fact `unresolvable` in the queue rather than publish.**

## Never trust without click-through

Trust hierarchy for skincare specifically:

| Level | Sources | Trust |
|-------|---------|-------|
| Primary | Brand press release, patent (USPTO/EPO), regulator filing (FDA, EMA, INCI directory), peer-reviewed journal, clinical trial registration | ✅ Cite directly |
| Contemporaneous press | TechCrunch, Bloomberg, WSJ, Allure, Vogue Business, Financial Times | ✅ Cite directly |
| Reference | Wikipedia | ⚠️ Follow its citations; cite the primary |
| Aggregators | Product review databases, ingredient lookup sites, ratings sites | ❌ Lead only — never cite |
| AI-generated summaries | Retail search results with AI overviews, ChatGPT output | ❌ Never |

## Currency and unit preservation

Never convert. If a launch was announced in euros, record €30M. If a study reports concentration as 0.5% w/w, keep it that way — don't convert to ppm or mg/mL. Conversion adds error and obscures the source figure. The reader can convert if they care.

## When the primary source contradicts contemporaneous press

Prefer the primary. Note the discrepancy. Example:
> The company's press release [^1] says $50M; TechCrunch [^2] reported $45M based on unnamed sources. This profile follows the company's stated figure.

## Verification pass checklist

After writing any profile, run this checklist mechanically:

- [ ] Every factual claim in the body has a footnote citation
- [ ] Every Source URL has been loaded via WebFetch and confirmed to exist
- [ ] Every quoted string matches its source verbatim (search page for the exact quote)
- [ ] Every percentage in "Inferred Thesis" shows its denominator inline
- [ ] Every entry in Portfolio/Products has a source and a year (or founding-year proxy marked as such)
- [ ] Every cross-referenced slug in frontmatter exists in `data/{type}/`
- [ ] No table cells contain narrative prose (names and dates only)
- [ ] "What Users Say" contains only independently sourced quotes (or an honest "None found" note)
- [ ] All footnotes are numbered sequentially with no gaps
- [ ] No duplicate URLs in the Sources section
- [ ] No 403/404 URLs left in published profile

If any check fails, set `status: flagged` with `review_notes`, do not publish.

## When in doubt, LEAVE IT OUT

This is repeated in every meta doc because it is the most important rule. Every past incident in Seedlist involved an agent guessing to fill a gap. Marking something `unresolvable` is a success. Publishing a fabricated fact is a permanent stain on the site's credibility.
