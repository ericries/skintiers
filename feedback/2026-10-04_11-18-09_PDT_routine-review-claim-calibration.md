# Routine review: claim calibration and cross-profile consistency

Recorded: 2026-10-04 11:18:09 PDT (America/Los_Angeles; UTC−07:00)

## Context

The user asked what else to add or change once tretinoin introduction succeeds. Local ingredient, product, condition, and study profiles supplied the substantive evidence. The observations below are review findings; no underlying profiles were edited.

## 1. Hormonal-acne guidance overlooks an existing topical antiandrogen profile

`data/conditions/hormonal-acne.md` says that topicals treat the follicle rather than the androgen signal and frames treatments targeting the hormonal mechanism as outside topical scope. However, `data/ingredients/clascoterone.md` and `data/products/winlevi-clascoterone-1-cream.md` describe a prescription topical androgen-receptor inhibitor with randomized acne trials.

Suggested correction: distinguish common nonhormonal topicals from topical antiandrogen therapy. Link clascoterone as an option for discussion with a prescriber, without implying that it has demonstrated equivalence to oral spironolactone or established efficacy specifically for menopausal/PCOS acne or facial hair. A cross-profile consistency check would catch this contradiction.

## 2. The perimenopause page's comparative claims exceed the cited designs

`data/goals/anti-aging-perimenopause.md` calls hormonal treatment the largest lever for menopause-driven aging and says its effects rival the sunscreen-and-retinoid foundation. The same page appropriately discloses small or uncontrolled studies, measurements away from the face, and the absence of a placebo arm in a topical estrogen study.

Those limitations do not erase possible biological or clinical benefit, but the page has not established the comparative ranking expressed in its headline claims. Review and soften the ranking unless direct comparative evidence supports it. Preserve the existing distinction that systemic menopausal hormone treatment is considered for appropriate menopausal indications and individual benefit/risk, rather than initiated as a skincare purchase. Do not convert a mechanistic explanation into a recommendation to add estrogen to a routine.

## 3. Naturium's ingredient order cannot settle relative efficacy

`data/products/naturium-vitamin-c-complex-serum.md` states that sodium ascorbyl phosphate outweighs ascorbic acid by concentration based on their ingredient-list order, then uses that inference to weaken the product's collagen case.

The useful, supported observations are that both forms are listed, their percentages are undisclosed, and the cited manufacturer study does not provide enough detail to establish the product's clinical performance. Avoid treating ingredient order alone as a quantitative assay, a delivery measurement, or proof of inferior results. A known-strength L-ascorbic-acid formulation may be easier to relate to particular studies, but switching is not thereby proven superior to this serum.

## 4. Record when wash recommendations are extrapolations

`data/products/panoxyl-acne-creamy-wash-benzoyl-peroxide-4.md` usefully discloses that its concentration-comparison rationale comes from leave-on products. Retain that caveat in summaries: starting with a lower-strength wash is a reasonable practical choice, but it is not a direct demonstration that this 4% wash equals a particular 10% wash in efficacy or causes less irritation.

## Web-use record for this iteration

I made one web-tool call opening two AAD clinician-organization patient guides:

- https://www.aad.org/public/diseases/acne/derm-treat/hormonal-therapy
- https://www.aad.org/public/diseases/rosacea/treatment/diagnosis-treat

Purpose: check the clinical framing of prescription escalation and the distinction between acne and rosacea treatment. The local directory already covered these treatments; these visits are verification, not evidence of missing local coverage. No broad product search was performed. Some of this guidance had already been checked earlier in the conversation, so repeated verification should not be counted as new research added by this iteration.

## What helped

The local SAFA study summary clearly separates its adult-female acne population from assumptions about a specific menopausal population. The rosacea profiles distinguish inflammatory bumps from persistent vascular redness. These distinctions directly improve recommendations and should be preserved in shorter indexes and generated summaries.
