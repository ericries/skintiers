# Further feedback: routine scoring, reader contract, and handoff priorities

Recorded: 2026-10-04T20:46:53-07:00 (America/Los_Angeles).

## Outcome and scope

The most important new issue is that the documented routine score is not a sound proxy for how well a routine meets a person's needs. A second issue is that absence claims in the scoring specification contradict the reader guide's accurate warning that selected key actives are incomplete. These affect recommendations across the whole collection, not just the current skincare case.

This is an assessment and proposed handoff, not implementation. Only this feedback file was created. No research, documentation, application code, generated artifacts, or caches were changed. No web search was needed. Findings below come from the current local reader guide and canonical specification; I did not execute the builder or test its interface.

## First: recognize progress and recheck old feedback

The directory has changed since the earlier feedback. Targeted reads now show:

- `README.md` correctly describes a live collection and provides a local-first reading workflow. The earlier stale-bootstrap README finding should not be treated as still open.
- `skill/SKILL.md` now explains the local cache, long YAML, generated-output staleness, and why `key_actives` is not full INCI. These are useful improvements.
- `data/conditions/hormonal-acne.md` includes and links clascoterone and distinguishes approved from investigational/compounded topical antiandrogens. The original complaint that it overlooks clascoterone is no longer applicable in that form.
- The clascoterone and Winlevi profiles now include the 2011 tretinoin comparator pilot and its limitations. The earlier “no comparison exists” criticism has been addressed in the passages checked.
- `data/goals/anti-aging-perimenopause.md` now qualifies hormone-treatment magnitude, gives the 10-person biopsy denominator and prolactin result, and includes Rittie 2008 with appropriate age/site/duration caveats. This addresses several earlier findings; it is not a complete re-audit of the estrogen evidence.
- The Aestura Cream tolerability section now explicitly treats fragrance status as unresolved rather than inferring nonzero fragrance from a less-than threshold. Some older phrasing remains elsewhere, so propagation through summaries still deserves checking.

Do not use the timestamped feedback folder as an undifferentiated open-issue list. Keep historical notes, but attach resolution status and a checked source revision/date to individual findings. A later clarification should reference the earlier note rather than silently rewriting its history. These spot checks establish current text, not who changed it or whether every related page is synchronized.

## Priority 1: routine “strength” is not routine suitability

Sources: `docs/routine-strength-spec.md`, especially Steps 1–2, and the routine-analysis recipe in `skill/SKILL.md`.

The specified algorithm selects a product's highest health effect grade (falling back to all grades), converts ordinal labels to 0–4, and averages across distinct graded products. Evidence quality is explicitly excluded from this calculation.

Problems that follow directly from that definition:

1. **A useful supporting product can lower the score.** With hypothetical graded products of 4 and 3, the mean is 3.5, labeled Strong. Adding a gentle cleanser rated 1 produces 8/3, approximately 2.67, labeled Solid. That arithmetic does not show the routine became worse. These are illustrative inputs, not asserted ratings of actual products.
2. **The number rewards product mix rather than added patient benefit.** A redundant high-scoring product can raise the average without solving an unmet concern. Whether an item is assigned a grade also changes whether it contributes to the denominator.
3. **The endpoints are not commensurate.** A product's best effect could concern a different condition, comparator, population, or body site. Averaging ordinal labels across acne treatment, cleansing, pigmentation, and moisturization does not create an interpretable clinical effect size. Equal numeric distances between Minimal, Modest, Notable, and Strong are an editorial convention, not measured units.
4. **Frequency and actual use are lost.** The specification deduplicates AM/PM products and does not incorporate once-weekly versus regular treatment, rinse-off exposure, amount, adherence, or individual tolerance. These were central distinctions in this conversation.
5. **“Strong” can appear more certain than its evidence.** A high estimated effect on preliminary evidence can boost a score because evidence quality is excluded. The disclaimer that this is not a routine trial does not fully prevent a reader from interpreting the label as a recommendation.

Suggested direction: lead with goal-specific coverage, adequacy of the current baseline, expected incremental benefit, tolerability, evidence applicability, and practical burden. If retaining the number for an existing UI, label it clearly as a descriptive average of editorial product ratings and do not optimize treatment recommendations around it. This proposal does not require inventing another composite score.

## Priority 2: propagate “unknown” through composition and sunscreen logic

The reader guide correctly says that absence from `key_actives` does not establish absence from the formula. But the canonical specification's Step 5 reports notable actives as absent based on a union of exactly that selected list. Step 4 similarly calls sunscreen absent if no filter slugs are present.

Suggested distinctions:

- **Present:** verified in a sufficiently identified formula/source.
- **Absent from the declared formula:** a complete applicable ingredient declaration has been checked.
- **Not indexed / unknown:** only selected actives, an unrecognized product, or incomplete composition data are available.

Say “not listed in the indexed key actives” rather than “does not contain” when only that index is available. For sunscreen, verify the finished product's sunscreen identity and labeled protection. A union of constituent filter bands is not the same as a tested broad-spectrum/SPF/UVA claim, nor evidence of adequate real-world application. Unknown product coverage should prompt source resolution rather than an instruction to buy another product.

The spec also lists **bakuchiol inside the “Retinoid” family**, whereas `data/ingredients/bakuchiol.md` explicitly says it is not a vitamin A derivative and is not on the retinoid pathway. If a navigation family intentionally includes alternatives, label it “retinoids and alternatives” and preserve the distinction when reporting whether a routine actually contains a retinoid. Do not use functional similarity as molecular identity or proof of equivalent efficacy.

## Priority 3: make the source-checkout reader contract internally consistent

Current observations from `skill/SKILL.md`:

- It says `routine-strength-spec.md` is “shipped alongside this file,” but the file is not at `skill/routine-strength-spec.md`; it is at `docs/routine-strength-spec.md` in this checkout. A direct read of the former failed. Distinguish source-checkout paths from paths inside a built/installable bundle. This is a source-path finding, not proof that the distributed bundle is broken.
- The opening retrieval section says “Fetch the JSON first,” while the local section says to read authored profiles first and warns that JSON can lag. State the branch clearly: local checkout uses local authored records; a remote reader may start with the discovery catalog.
- “Trust published” should mean published editorial status, not verified truth. We found claim errors on published pages. Treat publication state and evidence confidence as separate properties.
- “When in doubt, leave it out” can encourage omission of a relevant emerging option, as happened with facial estrogen. Prefer: disclose what is covered, what remains uncertain, and what was considered but not recommended. Distinguish “not covered by SkinTiers” from “not supported by science.” Honor a user's authorization to consult external sources and label those additions.
- The two-axis section says never to collapse effect and evidence, while the following tier definition does combine them by demoting for thin evidence. Clarify that a tier is an editorial composite and preserve its underlying dimensions. A reader should not present it as a measured clinical ranking.

## Priority 4: retain patient context without inventing deficiencies

For multi-turn routine advice, the working context should distinguish user-confirmed facts, assumptions, unknowns, and preferences. In this case, the relevant confirmed facts include no reported irritation, successful tretinoin ramp-up as an assumption requested by the user, exact compound strength, specified product variants, and a preference against pills. Possible rosacea remains unconfirmed; “perimenopause” does not establish that every symptom is estrogen deficiency.

A comprehensive review should cover each stated concern and explain relevant options that were considered but not recommended. It should ask what adding or replacing a product would change beyond the baseline. It should not assume that ingredient diversity, a higher percentage, a broader peptide list, or menopause branding means better outcomes. This is primarily a reader reasoning requirement, not a reason to store a personal medical record in the public product database.

## Priority 5: evaluate realistic questions, not merely schema validity

Consider a small set of manually reviewed example questions derived from this case, with required distinctions rather than one mandatory product answer:

| Question | Minimum properties of an adequate answer |
|---|---|
| Does COSRX contain copper peptides and Matrixyl? | Read full composition; distinguish Copper Tripeptide-1 from individual Matrixyl molecules; do not infer absence from a family-level catalog. |
| Would Aestura add missing cholesterol/ceramides? | Account for what the current CeraVe already contains; distinguish different formula from proven superior support. |
| Is weekly glycolic useful alongside tretinoin? | Retrieve local positive evidence; preserve vehicle, frequency, comparator, and added-benefit uncertainty. |
| What topical options exist when pills are unwanted? | Include clascoterone; distinguish off-label topical spironolactone evidence and facial-hair endpoints; do not repeat oral options as the only escalation. |
| What about menopause-specific treatments? | Consider facial estrogen, MEP, and phytoestrogens; distinguish routes, positive/negative findings, measured tissue changes, visible benefits, and safety uncertainty. |
| Is an ingredient absent from a routine? | Return unknown when composition data are incomplete instead of a confident absence. |
| Does adding a gentle cleanser make a routine worse? | Do not confuse a lower editorial average with worse care. |

Do not judge success by how often the assistant recommends a specific product. Judge source retrieval, completeness, applicability, uncertainty, and fidelity to patient preferences. These are suggested evaluation cases; no tests or fixtures were added or run.

## Improve the feedback loop itself

For each finding, capture the affected file/claim, observed text or revision, proposed change, evidence, priority, and resolution status. For each external lookup, separate:

- New topic/product coverage.
- Missing or inaccessible primary-source text.
- Current-label/regulatory verification.
- Investigation of a contradiction or surprising claim.
- Redundant lookup caused by the answering assistant.

The last category should lead to reader-workflow improvement, not indiscriminate expansion of the dataset. Conversely, deliberately not caching primaries does not guarantee reliable re-fetching: PubMed blank/interstitial responses and publisher/ACOG fetch failures occurred in this session. At minimum, preserve source-completeness and access-failure metadata so another reader knows why an answer could not be fully checked. Any broader caching policy should respect source rights and the project's existing design.

## Suggested order of work

1. Address routine-score interpretation and false absence conclusions, because they affect many answers.
2. Propagate substantive corrections through ingredient/product/list/goal summaries and generated outputs, with explicit evidence links.
3. Fix reader-contract ambiguities and source/bundle path resolution.
4. Add missing decision-relevant evidence already detailed in prior notes, after checking which additions have landed.
5. Evaluate a handful of complete case questions before expanding the catalog further.

Some failures were mine: repeated external verification despite adequate local INCI, and failing to include menopause-specific options in an otherwise comprehensive review. Better indexing helps, but the maintaining agent should not be asked to fix all reader mistakes by adding more pages.
