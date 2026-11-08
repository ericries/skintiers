---
aliases:
- Acne combinations tested against their own ingredients
- Combination acne products by trial design
analyzed: '2026-11-08'
assurance: sonnet
kind: best-of
name: Prescription acne combinations, by whether their trials beat the single ingredients
slug: acne-combinations-by-whether-they-beat-their-own-ingredients
status: published
tier_list:
  by: whether the product's own FDA label reports a trial that compared it against
    its individual active ingredients, rather than only against the vehicle. A LOW
    GRADE HERE IS NOT A VERDICT ON THE PRODUCT. It means the trial was never designed
    to answer whether combining the ingredients beats using one of them, so nobody
    can say from the label
  caption: Combination acne products, by what their own trials were designed to answer
  items:
  - note: The only one here whose label reports monotherapy arms. Two 12-week trials
      compared it against clindamycin alone, benzoyl peroxide alone and vehicle, and
      it beat all three on every co-primary measure, by single-digit margins over
      the monotherapies. Set out on [[acanya-clindamycin-benzoyl-peroxide-gel]].
    slug: acanya-clindamycin-benzoyl-peroxide-gel
    tier: good
  - note: 'Vehicle only. The label states the design in one sentence: the trial "evaluated
      ONEXTON Gel compared to vehicle gel". Striking because Onexton shares application
      number NDA050819 with Acanya and the same company, so one product under that
      application was tested against its own ingredients and the other was not.'
    slug: onexton-clindamycin-benzoyl-peroxide-gel
    tier: weak
  - note: Vehicle only. Two identical "randomized, double-blind, vehicle-controlled
      trials" in 858 subjects. Neither tretinoin alone nor benzoyl peroxide alone
      appears as an arm, which matters because the formulation's whole selling point
      is that it puts two normally incompatible actives in one cream.
    slug: twyneo-tretinoin-benzoyl-peroxide-cream
    tier: weak
  - note: Vehicle only, and it is a TRIPLE. Subjects were "randomized 2:1 to receive
      CABTREO or vehicle", so a product combining clindamycin, adapalene and benzoyl
      peroxide was never compared against any of the three two-drug combinations it
      contains, each of which is separately marketed.
    slug: cabtreo-clindamycin-adapalene-benzoyl-peroxide-gel
    tier: weak
type: list
updated: '2026-11-08'
---

A combination costs more than one ingredient and is prescribed on the premise that the pair beats either half. This ranks the prescription acne combinations covered here by whether anyone actually tested that premise, which is a question about trial design rather than about the drugs.

> **Of the four whose labels could be read, one was tested against its own ingredients.** Acanya's trials included a clindamycin arm and a benzoyl peroxide arm, and it beat both.[^acanya] Onexton, Twyneo and Cabtreo were each compared only against vehicle.[^onexton][^twyneo][^cabtreo] A vehicle-controlled win answers whether the product beats a blank cream. It cannot answer whether the second ingredient is doing anything.

## What a low grade here means

It means the question was not asked. Twyneo beating vehicle is real evidence that Twyneo works; it is no evidence at all that tretinoin plus benzoyl peroxide beats tretinoin. Those are different claims and only the first was tested. How well each product treats acne is graded on its own page.

## The sharpest case is two products under one application

Acanya and Onexton are both clindamycin and benzoyl peroxide, both from Bausch Health, and both sit under application number NDA050819.[^ndc] Acanya's label reports four-arm trials. Onexton's reports one sentence of design: "This trial evaluated ONEXTON Gel compared to vehicle gel."[^onexton] Same company, same application, same two drugs, two different standards of proof.

## Two the labels could not answer

Epiduo and BenzaClin both have pages here, and neither could be graded. openFDA's current label record for Epiduo carries no Clinical Studies section at all, and a brand-name search for BenzaClin returns no label record.[^gaps] Both absences describe one database on one day. Leaving the two products off the list is the honest option; guessing a grade for them is not.

## See Also

- [[acanya-clindamycin-benzoyl-peroxide-gel]], the one with monotherapy arms
- [[clindamycin-topical]], [[benzoyl-peroxide]], [[adapalene]] and [[tretinoin]] for what each ingredient does alone
- [[acne]] for the condition and the wider treatment ladder

## Sources

[^acanya]: ACANYA (clindamycin phosphate and benzoyl peroxide) Gel FDA label, openFDA drug/label API, effective 2020-09-30, read 2026-11-08. Its Clinical Studies section states the two trials "compared ACANYA Gel to clindamycin in the vehicle gel, benzoyl peroxide in the vehicle gel, and the vehicle gel alone". The results, including the single-digit margins over each monotherapy, are set out in full on [[acanya-clindamycin-benzoyl-peroxide-gel]] and are not repeated here. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22ACANYA%22 (accessed 2026-11-08)

[^onexton]: ONEXTON (clindamycin phosphate and benzoyl peroxide) Gel FDA label, openFDA drug/label API, effective 2025-07-23, application number NDA050819, read 2026-11-08. Clinical Studies states: "The safety and efficacy of once-daily use of ONEXTON Gel was assessed in a 12-week multi-center, randomized, blinded trial in subjects 12 years and older with moderate to severe acne vulgaris. This trial evaluated ONEXTON Gel compared to vehicle gel." Checked by reading that section in full on 2026-11-08, and this is load-bearing for the grade: it names no comparator other than vehicle. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22ONEXTON%22 (accessed 2026-11-08)

[^twyneo]: TWYNEO (tretinoin and benzoyl peroxide) Cream FDA label, openFDA drug/label API, effective 2025-08-11, application number NDA214902, read 2026-11-08. Clinical Studies describes "two multicenter, randomized, double-blind, vehicle-controlled trials [Trial 1 (NCT03761784), Trial 2 (NCT03761810)], which were identical in design", "conducted in 858 subjects 9 years of age and older". Checked by reading that section in full on the same date: no monotherapy arm is named. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22TWYNEO%22 (accessed 2026-11-08)

[^cabtreo]: CABTREO (clindamycin phosphate, adapalene and benzoyl peroxide) Gel FDA label, openFDA drug/label API, effective 2025-04-24, application number NDA216632, read 2026-11-08. Clinical Studies describes "two multicenter, randomized, double-blind clinical trials (Trial 1 and Trial 2, NCT04214639 and 2 NCT04214652, respectively) in 363 adult and pediatric subjects 10 years of age and older", in which "Subjects were randomized 2:1 to receive CABTREO or vehicle applied once daily for 12 weeks". Checked by reading that section in full on the same date: no two-drug comparator appears. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22CABTREO%22 (accessed 2026-11-08)

[^ndc]: openFDA drug/ndc API, queried 2026-11-08. Acanya returns product 13548-132, application number NDA050819. Onexton returns product 0187-3050, marketing category NDA, application number NDA050819, labeler Bausch Health US, LLC. The shared application number is the basis for the comparison above and was checked in the NDC directory rather than inferred from the labels. https://api.fda.gov/drug/ndc.json?search=brand_name:%22Onexton%22 (accessed 2026-11-08)

[^gaps]: openFDA drug/label API, queried 2026-11-08. A brand-name search for BenzaClin returns NOT_FOUND. A brand-name search for Epiduo returns a single record, brand name "Differin Epiduo", application number NDA220736, effective 2026-05-20, whose clinical_studies field is empty. Neither absence is evidence about the products; both are limits of this database on this date, and both products are covered on their own pages here. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22Epiduo%22 (accessed 2026-11-08)