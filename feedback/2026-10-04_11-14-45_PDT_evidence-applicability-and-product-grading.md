# Evidence applicability and product grading

Recorded: 2026-10-04 11:14:45 PDT (America/Los_Angeles; UTC−07:00)

## Why this matters

Applying the directory to an actual routine exposed a recurring distinction: evidence that an ingredient can work, evidence for a particular formulation and schedule, and evidence that adding it improves an existing routine are different questions. Weak evidence should not automatically be translated into a small effect, and matching a trial's concentration does not establish equivalent performance.

## Concrete cases

### Glycolic acid: evidence was present locally

Relevant files include `data/ingredients/glycolic-acid.md`, `data/products/the-ordinary-glycolic-acid-7-toning-solution.md`, and `data/goals/anti-aging.md`.

The ingredient profile already cites human evidence relevant to photoaging and collagen, including Ditre 1996 and Stiller 1996. I should have retrieved and explained this before implying that the local evidence was missing. That was an assistant retrieval/communication failure.

The application question was narrower: The Ordinary's 7% glycolic product once weekly, alongside gradually introduced tretinoin. Stiller studied an 8% cream used twice daily for 22 weeks and measured photoaging outcomes; it does not directly prove extra collagen from the user's once-weekly toner schedule. Ditre's study involved substantially different AHA exposure and biopsy outcomes. The product profile's bridge to an 8% cream should keep frequency, vehicle, duration, and outcome alongside concentration.

Do not infer either "no benefit" from the absence of an exact-regimen trial or "proven added collagen" from a higher-exposure ingredient study. Similarly, a suggestion to pause an exfoliant during retinoid introduction is a cautious practical strategy, not proof that a well-tolerated combination is harmful.

### Azelaic acid: concentration is not formulation equivalence

Relevant files include `data/products/anua-azelaic-acid-serum.md`, `data/products/cos-de-baha-az20-azelaic-acid-20-serum.md`, `data/lists/best-azelaic-acid-products.md`, and `data/ingredients/azelaic-acid.md`.

The AZ20 profile acknowledges that no finished-product trial is cited, but assigns solid evidence to its expected acne benefit largely by matching a prescription cream's labeled 20% concentration. The Anua profile places expected benefit at the minimal end based on its lower 10% concentration and lack of product trials. Those judgments risk communicating an established difference in clinical effect that has not been demonstrated between these formulations.

Suggested change: represent ingredient-level certainty separately from the confidence in transferring that evidence to a product. Include the reason for transfer and the relevant uncertainties in formulation, delivery, concentration, and frequency. Retain the possibility of benefit from lower-strength cosmetics without promising prescription-equivalent results from higher-strength ones.

### Matrixyl: the directory's molecule distinctions are useful

`data/ingredients/palmitoyl-pentapeptide-4-matrixyl.md` explicitly distinguishes original Matrixyl, Matrixyl 3000, and Matrixyl synthe'6. This was valuable and should be preserved in any index or shorter summaries.

The original palmitoyl pentapeptide-4 trial involved 93 women aged 35–55 and measured fine-line/wrinkle appearance. Its result should not automatically be attributed to the different peptides marketed as Matrixyl 3000 or synthe'6, nor equated with measured new collagen in participants' skin. Similarly, copper-peptide cell and wound-healing findings should remain distinct from cosmetic serum outcomes.

### Salicylic acid: separate cleanser evidence from other delivery forms

`data/ingredients/salicylic-acid.md` includes a locally available Dr Dray video summary specifically addressing salicylic cleansers and deposition despite rinsing. This is expert explanation, not a controlled trial, but it is relevant and should not be missed when searching only the main evidence section.

Some cleanser profiles infer less efficacy from shorter contact time. Shorter contact is a formulation consideration, not by itself proof that a particular wash is clinically inferior. Record direct wash trials, leave-on trials, peel trials, and expert guidance separately.

**Unverified issue to investigate:** the salicylic ingredient profile presents a Cochrane salicylic-versus-tretinoin comparison under the 0.5–2% acne discussion. I have not verified the original intervention behind that comparison. Check its concentration, delivery form, and trial design before using it to support cleanser efficacy or equivalence to tretinoin. A nonsignificant difference alone also does not establish equivalence.

## Suggested evidence fields

For an individual study or product-to-study inference, make these easy to retrieve together: tested molecule, formulation/vehicle, concentration, application frequency, duration, population, comparator, measured outcome, sponsorship, source completeness, and applicability limits. Distinguish human clinical outcomes from biomarkers, laboratory findings, and expert opinion.

These are proposed improvements and review questions, not edits to the profiles. No underlying data was changed.
