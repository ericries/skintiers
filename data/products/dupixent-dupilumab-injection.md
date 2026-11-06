---
analyzed: '2026-11-05'
assurance: sonnet
brand: Regeneron
category: Treatments
grades:
- effect: strong
  evidence: established
  note: 'health: the efficacy figures and the evidence grade for the molecule are
    on [[dupilumab]], which holds tier best, and are not repeated here. What is graded
    here is the marketed product: a label with nine indications of which four are
    skin diseases, an atopic dermatitis indication reaching down to six months of
    age, a position one step earlier in the ladder than the oral JAK inhibitors, and
    no boxed warning'
  use: For moderate-to-severe atopic dermatitis from six months of age, its principal
    skin use (health), after topical prescription therapies rather than after other
    systemics
key_actives:
- dupilumab
name: DUPIXENT (Dupilumab Injection)
slug: dupixent-dupilumab-injection
status: published
type: product
updated: '2026-11-05'
videos: []
---

DUPIXENT is Regeneron's injectable dupilumab, an interleukin-4 receptor alpha antagonist, licensed under BLA 761055 and first approved on 28 March 2017.[^drugsfda] It is the drug both oral JAK inhibitors on this site name as the therapy you are expected to have tried first.[^label]

> **Nine indications, and four of them are skin.** [[rinvoq-upadacitinib-tablets]] also carries nine, of which exactly one names a skin disease. Dupixent's cover atopic dermatitis, prurigo nodularis, chronic spontaneous urticaria and bullous pemphigoid, alongside asthma, nasal polyps, eosinophilic esophagitis, COPD and allergic fungal rhinosinusitis.[^label] Two other things separate it from the oral drugs in practice: its eczema indication starts at six months of age rather than twelve years, and its label carries no boxed warning at all.

## Summary

The atopic dermatitis indication covers "adult and pediatric patients aged 6 months and older with moderate-to-severe AD whose disease is not adequately controlled with topical prescription therapies or when those therapies are not advisable", and the label adds that it "can be used with or without topical corticosteroids".[^label]

Read that against the oral JAK inhibitors and the ladder becomes explicit. [[cibinqo-abrocitinib-tablets]] and [[rinvoq-upadacitinib-tablets]] are both restricted to disease not controlled by other systemic drugs "including biologics", which is this one.[^label] Dupixent asks only that topical prescriptions have failed. It sits one rung lower, and the age floor differs by more than eleven years.

Dosing in eczema is weight-banded and starts with a loading dose in everyone except the youngest group. Adults take "an initial dose of 600 mg (two 300 mg injections), followed by 300 mg given every 2 weeks".[^label] Children aged 6 months to 5 years get no loading dose at all, taking 200 mg or 300 mg every four weeks by weight; those 6 to 17 get a 400 mg or 600 mg load and then 200 mg or 300 mg every two or four weeks depending on which of three weight bands they fall into.[^label]

The marketed presentations are prefilled glass syringes at 200 mg/1.14 mL and 300 mg/2 mL, listed in cartons of two under NDCs 0024-5918 and 0024-5919 for the 200 mg and 0024-5914 and 0024-5915 for the 300 mg.[^ndc]

## The Rubric

**Moderate-to-severe atopic dermatitis (subcutaneous injection, prescription)**

- **Effect size: strong.** Graded on [[dupilumab]], which holds tier best; the trial figures are not repeated here. [[systemic-atopic-dermatitis-treatments-by-evidence]] explains why it is not ranked against the oral JAK inhibitors on that page, which is that the two syntheses behind that ranking do not report the same figures for it.
- **Evidence quality: established.** A biologics licence with nine separate approved indications and 33 approved submissions on the application since 2017.[^drugsfda]

## The Evidence

The efficacy evidence belongs to [[dupilumab]]. The product-level fact worth stating here is the one the oral drugs make unavoidable: the openFDA label record for DUPIXENT contains no boxed warning section at all.[^label]

That is not a small difference. Both oral JAK inhibitors for the same disease carry a five-headed boxed warning covering serious infections, mortality, malignancy, major adverse cardiovascular events and thrombosis, and on both labels the mortality and cardiovascular parts rest on a study of a different drug in rheumatoid arthritis patients. A reader choosing between an injection and a pill for eczema is choosing between a drug with no boxed warning and a drug class that carries one, and the labels say so plainly.

What Dupixent does carry is its own set of warnings in the ordinary sections rather than a boxed one, which this page does not enumerate; that is what the label and a prescriber are for.

## What's In It

One active, dupilumab, a monoclonal antibody given by subcutaneous injection.[^drugsfda] Nothing about this product is topical or cosmetic, and nothing in it is an active a skincare routine would otherwise contain.

## See Also

- [[dupilumab]] for the molecule, its mechanism and its evidence grade
- [[cibinqo-abrocitinib-tablets]] and [[rinvoq-upadacitinib-tablets]], the oral drugs whose labels place them after this one
- [[systemic-atopic-dermatitis-treatments-by-evidence]] for how the systemics compare, and why this one is not tiered there
- [[atopic-dermatitis]], [[prurigo-nodularis]] and [[bullous-pemphigoid]], three of the four skin diseases on its label that have hubs here

## Where to Buy

Prescription only, given by subcutaneous injection and usually self-administered at home after training. No price appears on this page: US list and net prices for biologics are not available from a primary source, and what a patient pays turns on insurance and on the manufacturer's assistance programme.

## Sources

[^label]: FDA prescribing information for DUPIXENT (dupilumab) injection, retrieved via the openFDA drug label API on 2026-11-05; label effective date 2026-04-22. The indications section numbers nine indications, 1.1 to 1.9: atopic dermatitis, asthma, chronic rhinosinusitis with nasal polyps, eosinophilic esophagitis, prurigo nodularis, chronic obstructive pulmonary disease, chronic spontaneous urticaria, bullous pemphigoid and allergic fungal rhinosinusitis. Four of those nine name skin diseases. Quotations verified verbatim against the API response: the atopic dermatitis indication wording, the corticosteroid sentence, and the adult loading-dose text from section 2.3. The paediatric weight bands are reproduced from the same section's tables. ABSENCE CLAIM, STATED PRECISELY: the record returned by this endpoint has no boxed_warning field, which is how the other two systemic drug pages on this site established that their labels do carry one. That is a statement about this label record as retrieved on this date, not a general claim that no warning of any kind applies; Dupixent carries warnings in the ordinary Warnings and Precautions section. The comparison with the oral JAK labels is drawn from the records quoted on [[cibinqo-abrocitinib-tablets]] and [[rinvoq-upadacitinib-tablets]]. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22DUPIXENT%22 (accessed 2026-11-05)

[^drugsfda]: openFDA Drugs@FDA record for DUPIXENT. Application BLA761055, sponsor REGENERON PHARMACEUTICALS, product DUPIXENT, dosage form INJECTABLE, strength 150MG/ML, marketing status Prescription. The original submission was approved 2017-03-28 and the application carries 33 approved submissions in total as of this query; the subject of each supplement is not stated in the record and none is attributed to a particular indication here. https://api.fda.gov/drug/drugsfda.json?search=openfda.brand_name:%22DUPIXENT%22 (accessed 2026-11-05)

[^ndc]: openFDA NDC directory, queried for brand name DUPIXENT on 2026-11-05, which returns four records, all injection solutions in glass prefilled syringes packaged two to a carton: 0024-5918 and 0024-5919 at 200 mg/1.14 mL, and 0024-5914 and 0024-5915 at 300 mg/2 mL. Dupixent is also supplied in a pre-filled pen; no pen presentation appeared in this query's four results, so none is described above. https://api.fda.gov/drug/ndc.json?search=brand_name:%22DUPIXENT%22 (accessed 2026-11-05)