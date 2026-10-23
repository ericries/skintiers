---
aliases:
- Prescription acne and rosacea topicals by regulatory status
- Rx acne topicals FDA approval status
- which acne prescriptions are FDA-approved
- acne rosacea NDA numbers
analyzed: '2026-10-23'
assurance: sonnet
kind: best-of
name: Prescription Acne and Rosacea Topicals by Regulatory Status
slug: prescription-acne-rosacea-topicals-by-regulatory-status
status: published
type: list
updated: '2026-10-23'
---

Every prescription topical for acne or rosacea with a page on this site, sorted by what the FDA actually did about it. Two of them were never reviewed at all, and one is approved but no longer marketed. What the regulatory tiers mean in general is on [[fda-approved-vs-cleared-skincare]]; this page only applies them.

> **Regulatory status is not a quality ranking.** A drug approved in 2024 is not thereby better than one approved in 1990, and an unapproved product may work perfectly well. The axis here is how much scrutiny the specific formulation received, which is a different question from whether it helps your skin. Each product's own evidence is on its own page.

## Approved under their own NDA and currently marketed

Each holds a New Drug Application, meaning FDA reviewed efficacy and safety data for that exact formulation. Listed newest application first, which roughly tracks how recently the dossier was examined. Application numbers verified against the openFDA NDC directory on 2026-10-23.[^openfda]

- [[cabtreo-clindamycin-adapalene-benzoyl-peroxide-gel]], NDA216632. The only approved triple combination.
- [[epsolay-benzoyl-peroxide-5-cream]], NDA214510. Encapsulated benzoyl peroxide for rosacea papules.
- [[zilxi-minocycline-foam]], NDA213690. Topical minocycline for rosacea.
- [[winlevi-clascoterone-1-cream]], NDA213433. The first topical androgen receptor inhibitor for acne.
- [[amzeeq-minocycline-4-topical-foam]], NDA212379. The same active as Zilxi at a different strength, approved for acne instead.
- [[arazlo-tazarotene-0-045-lotion]], NDA211882.
- [[aklief-trifarotene-0-005-cream]], NDA211527.
- [[altreno-tretinoin-0-05-lotion]], NDA209353.
- [[rhofade-oxymetazoline-1-cream]], NDA208552. For rosacea redness.
- [[epiduo-forte-adapalene-benzoyl-peroxide-gel]], NDA207917, with the lower-strength [[epiduo-adapalene-benzoyl-peroxide-gel]] now also sold over the counter under a separate approval, NDA220736.
- [[aczone-dapsone-7-5-gel]], NDA207154.
- [[finacea-azelaic-acid-15-gel]], NDA207071.
- [[soolantra-ivermectin-1-cream]], NDA206255.
- [[mirvaso-brimonidine-gel]], NDA204708. For rosacea redness rather than the bumps.
- [[metrogel-metronidazole-1-gel]], NDA021789. The 1% strength is the marketed one; the older 0.75% MetroGel, NDA019737, is listed as discontinued.[^drugsfda]
- [[differin-gel-0-3-adapalene]], NDA021753, which the directory records as adapalene 3 mg/g. The 0.1% strength is the one that later became available over the counter.
- [[tazorac-tazarotene-gel-cream]], two applications: NDA020600 for the gel and NDA021184 for the cream.
- [[retin-a-micro-tretinoin-gel-microsphere]], NDA020475.
- [[onexton-clindamycin-benzoyl-peroxide-gel]], NDA050819.
- [[klaron-sodium-sulfacetamide-10-lotion]], NDA019931, the oldest approval here. Its page cites a generic equivalent sold under ANDA078649, which is the abbreviated pathway: a generic shows it matches an approved drug rather than repeating the efficacy trials.

## Approved, then discontinued

- [[benzaclin-clindamycin-benzoyl-peroxide-gel]], NDA050756. Drugs@FDA lists both of its product entries with marketing status "Discontinued", and the brand returns no record in the active NDC directory.[^drugsfda][^openfda] It was reviewed and approved; it is simply not sold under that name now. The same two actives remain available in [[onexton-clindamycin-benzoyl-peroxide-gel]] and in generics.

## Never FDA-approved

Both entries here are sodium sulfacetamide and sulfur combinations, which is not a coincidence: that pairing predates modern approval requirements and has stayed on the market without ever being assessed.

- [[avar-sodium-sulfacetamide-10-sulfur-5]]. Marketing category "UNAPPROVED DRUG OTHER", no application number.[^openfda]
- [[plexion-sodium-sulfacetamide-10-sulfur-5-cleanser]]. Same category, no application number, and the directory lists a second variant, PLEXION NS, under the same status.[^openfda]

These are legally marketed prescription products that no agency has assessed for whether they work. This is the category most likely to surprise someone who assumes a prescription implies review, and it is why the question worth asking about any Rx topical is which application number it holds.

## How to check one yourself

Query the openFDA NDC directory for the brand name and read two fields: `marketing_category` and `application_number`. NDA means a full approval, ANDA means a generic of one, and "UNAPPROVED DRUG OTHER" means neither. If the brand returns nothing, it may be discontinued rather than unapproved, which Drugs@FDA will tell you.[^openfda][^drugsfda]

## See Also

[[fda-approved-vs-cleared-skincare]], [[acne]], [[rosacea]], [[rosacea-papulopustular]], [[benzoyl-peroxide]], [[azelaic-acid]].

## Sources


[^openfda]: openFDA drug/ndc API, queried by brand name on 2026-10-23 for each product listed above. Returned marketing_category "NDA" with the application numbers given for ACZONE (NDA207154), ALTRENO (NDA209353), AKLIEF (NDA211527), ARAZLO (NDA211882), AMZEEQ (NDA212379), CABTREO (NDA216632), DIFFERIN (NDA021753, recorded as adapalene 3 mg/g in a gel), EPIDUO FORTE (NDA207917), Differin Epiduo (NDA220736), EPSOLAY (NDA214510), KLARON (NDA019931, labeler Bausch Health US, LLC), FINACEA (NDA207071), MIRVASO (NDA204708), ONEXTON (NDA050819), Retin-A MICRO (NDA020475), RHOFADE (NDA208552), SOOLANTRA (NDA206255), Tazorac (NDA020600 for tazarotene gel at 0.5 and 1 mg/g, NDA021184 for tazarotene cream at 0.05 and 0.1 mg/g), WINLEVI (NDA213433) and ZILXI (NDA213690). Two products returned marketing_category "UNAPPROVED DRUG OTHER" with no application number: AVAR, and Plexion together with a second variant recorded as PLEXION NS. BENZACLIN and METROGEL returned no record in this directory, which indexes currently listed products; their status was resolved separately against Drugs@FDA rather than inferred from the absence. The directory is searched by indexed brand name, so a differently registered spelling could be missed. The roster of products on this page was assembled with `sk find` and a scan of every product page carrying both a prescription marker and an acne or rosacea indication, rather than by guessing slugs; oral drugs such as [[oracea-doxycycline-40-mg]] and [[emrosi-minocycline-extended-release]] are out of scope here because this list covers topicals. https://api.fda.gov/drug/ndc.json (accessed 2026-10-23)

[^drugsfda]: openFDA drug/drugsfda API, queried by products.brand_name on 2026-10-23. BenzaClin returns application NDA050756, sponsor BAUSCH, with both product entries carrying marketing_status "Discontinued" and active ingredients benzoyl peroxide 5% and clindamycin phosphate EQ 1% BASE. MetroGel returns three applications: NDA021789 (GALDERMA LABS LP, metronidazole 1%, marketing_status "Prescription"), NDA019737 (GALDERMA LABS LP, metronidazole 0.75%, "Discontinued") and NDA020208 (BAUSCH, METROGEL-VAGINAL, metronidazole 0.75%, "Discontinued"), the last being a different product that is not covered on this site. Discontinued here means not currently marketed under that application; it is not a safety withdrawal, and the 0.75% entry carries the Federal Register note that it was not withdrawn for safety or effectiveness reasons. https://api.fda.gov/drug/drugsfda.json (accessed 2026-10-23)