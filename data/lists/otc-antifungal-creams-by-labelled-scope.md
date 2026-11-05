---
aliases:
- OTC antifungal creams by regulatory footing
- antifungal cream labels compared
- NDA versus monograph antifungals
- athlete foot cream label scope
analyzed: '2026-10-28'
assurance: sonnet
kind: best-of
name: OTC Antifungal Creams by What the Label Actually Claims
slug: otc-antifungal-creams-by-labelled-scope
status: published
type: list
updated: '2026-10-28'
---

Four antifungal creams from the same aisle, compared on two things the box does not make obvious: whether FDA reviewed the product itself or it rides a monograph, and exactly which part of the foot the label claims to cure. Which drug has the better trial evidence is a different question, ranked on [[otc-antifungals-by-evidence]].

> **Regulatory footing does not predict how broad the claim is.** The two FDA-approved products here disagree with each other about the same body site, and the broadest claim on the shelf belongs to a monograph product. Approval tells you a product-specific review happened; it tells you nothing about how confident the label sounds, as [[fda-approved-vs-cleared-skincare]] sets out for devices.

## FDA-approved, and it tells you where it does not work

**Lotrimin Ultra, butenafine 1%.** openFDA records it with marketing category NDA, so the product itself was reviewed.[^openfda] Its Uses section volunteers a limit most labels would leave out: "cures most athlete's foot between the toes. Effectiveness on the bottom or sides of foot is unknown."[^ultra] The directions match that scope, between and around the toes twice a day for one week or once a day for four weeks.[^ultra] Full treatment on [[lotrimin-ultra-athletes-foot-cream]].

## FDA-approved, and it claims the rest of the foot

**Lamisil AT Cream, terbinafine 1%.** Also NDA.[^openfda] Its directions cover exactly the area Lotrimin Ultra says it cannot speak to: "between the toes only: apply twice a day (morning and night) for 1 week" and "on the bottom or sides of the foot: apply twice a day (morning and night) for 2 weeks".[^lamisil] Two products on the same regulatory footing, treating the same infection, taking opposite positions on whether the sole is in scope. Full treatment on [[lamisil-at-cream-terbinafine-1]].

## Monograph, and the broadest claim of the four

**Tinactin, tolnaftate 1%.** Marketing category OTC Monograph Drug, so it rides the agency's standing rule for the ingredient rather than a product review.[^openfda] Its Uses are the least qualified here: "proven clinically effective in the treatment of most athlete's foot (tinea pedis) and ringworm (tinea corporis)", with no site qualifier anywhere in the label, plus a prevention claim neither approved product makes, "helps prevent most athlete's foot with daily use".[^tinactin] Checked by string search, the words bottom and sides do not appear in it at all.[^tinactin] Full treatment on [[tinactin-antifungal-cream]].

## Monograph, and it does not claim athlete's foot at all

**Lotrimin AF, clotrimazole 1%.** On the label this site examined, the Uses section reads "cures most ringworm relieves itching, redness, irritation and discomfort which accompany this condition", with no athlete's foot cure claim in it, which is striking for a product most people reach for precisely to treat athlete's foot.[^lotaf] That page also records the marketing category as OTC Monograph Drug. Full treatment, including the label variation across this brand, on [[lotrimin-af-antifungal-cream]].

## The brand name is the least informative thing on the box

**One shelf name, four actives, two regulatory footings.** openFDA returns 16 records for brand names beginning Lotrimin, and they are not one product line: butenafine under NDA, and miconazole nitrate, clotrimazole and tolnaftate each under the OTC monograph, plus a corn-starch powder with no antifungal active at all.[^openfda] So "Lotrimin" on a package tells you the manufacturer, not the drug, not the dose and not the regulatory basis. The Ultra suffix is doing more work than the brand.

## What this list does not do

**It does not rank efficacy.** Nothing above compares cure rates, and a broader claim is not a better drug; the direct head-to-head evidence between these actives is on [[otc-antifungals-by-evidence]], and the ingredient cases are on [[butenafine]], [[terbinafine]], [[tolnaftate]] and [[clotrimazole]].

**It reads labels, not formulations.** Two products with the same active can carry different Uses text, and the clotrimazole entry above is explicitly the label this site examined rather than every clotrimazole package sold. Where a condition is diagnosed wrongly in the first place, none of this applies; [[athletes-foot]] covers that, including that clinical diagnosis alone is unreliable.

## See Also

[[otc-antifungals-by-evidence]], [[athletes-foot]], [[lotrimin-ultra-athletes-foot-cream]], [[lamisil-at-cream-terbinafine-1]], [[tinactin-antifungal-cream]], [[lotrimin-af-antifungal-cream]], [[butenafine]], [[terbinafine]], [[tolnaftate]], [[fda-approved-vs-cleared-skincare]].

## Sources

[^openfda]: openFDA drug/ndc API, queried 2026-10-28. A query on brand_name "Lotrimin" returns 16 records whose marketing categories and actives split four ways: Lotrimin Ultra, Lotrimin Ultra Athletes Foot, Lotrimin Ultra Jock Itch and Lotrimin Ultra Ringworm all carry marketing category NDA with BUTENAFINE HYDROCHLORIDE 1 g/100g; Lotrimin AF, Lotrimin AF Jock Itch, Lotrimin AF Deodorant and Lotrimin Antifungal carry OTC MONOGRAPH DRUG with MICONAZOLE NITRATE 20 mg/g; Lotrimin and Lotrimin Antifungal also appear with OTC MONOGRAPH DRUG and CLOTRIMAZOLE 10 mg/g; Lotrimin Daily Prevention and Lotrimin Daily Prevent Deodorant carry OTC MONOGRAPH DRUG with TOLNAFTATE 10 mg/g; and Lotrimin Daily Sweat and Odor Control carries OTC MONOGRAPH DRUG with STARCH, CORN 837 mg/g and no antifungal active. Separate queries give Lamisil AT and Lamisil AT Cream as marketing category NDA with TERBINAFINE HYDROCHLORIDE 1 g/100g, and Tinactin and Tinactin Antifungal as OTC MONOGRAPH DRUG with TOLNAFTATE 10 mg/g. The directory indexes currently listed products, so a discontinued or reformulated package would not appear, and brand_name is indexed as filed, so a differently-spelled listing would not surface. https://api.fda.gov/drug/ndc.json?search=brand_name:%22Lotrimin%22 (accessed 2026-10-28)

[^ultra]: DailyMed Structured Product Label for LOTRIMIN ULTRA ATHLETES FOOT (BUTENAFINE HYDROCHLORIDE) CREAM, Bayer HealthCare LLC., SPL set id e258c4ac-53ef-4a99-b732-4985f890b938, fetched and text-extracted on 2026-10-28. Quotes verified verbatim against the extracted label: the active, "Butenafine hydrochloride 1%" with purpose "Antifungal"; the Uses, "cures most athlete's foot between the toes. Effectiveness on the bottom or sides of foot is unknown." followed by "cures most jock itch and ringworm"; and the Directions, "apply to affected skin between and around the toes twice a day for 1 week (morning and night), or once a day for 4 weeks, or as directed by a doctor." with jock itch and ringworm at "once a day to affected skin for 2 weeks". Full treatment of this product is on [[lotrimin-ultra-athletes-foot-cream]] and is not restated here. https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/e258c4ac-53ef-4a99-b732-4985f890b938.xml (accessed 2026-10-28)

[^lamisil]: DailyMed Structured Product Label for LAMISIL AT CREAM (TERBINAFINE HYDROCHLORIDE) CREAM, SPL set id 9dea4789-bf1c-1577-e053-2a95a90a5381, fetched and text-extracted on 2026-10-28. Quotes verified verbatim: the Directions for athlete's foot, "between the toes only: apply twice a day (morning and night) for 1 week or as directed by a doctor" and "on the bottom or sides of the foot: apply twice a day (morning and night) for 2 weeks or as directed by a doctor", with jock itch and ringworm at "apply once a day (morning or night) for 1 week". The contrast drawn above is between this label's explicit bottom-and-sides directions and the Lotrimin Ultra label's statement that effectiveness there is unknown; both are quoted in full so the comparison can be checked. https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/9dea4789-bf1c-1577-e053-2a95a90a5381.xml (accessed 2026-10-28)

[^tinactin]: DailyMed Structured Product Label for TINACTIN (TOLNAFTATE) CREAM, Bayer HealthCare LLC., SPL set id c3b715a9-233a-401a-ba60-f78c1ddf1ded, fetched and text-extracted on 2026-10-28. Quotes verified verbatim: the Uses, "proven clinically effective in the treatment of most athlete's foot (tinea pedis) and ringworm (tinea corporis)", "helps prevent most athlete's foot with daily use" and "for effective relief of itching, burning and cracking"; and from the Directions, "pay special attention to spaces between the toes" and "use daily for 4 weeks; if condition persists longer, ask a doctor". Absence checked by string search of the full extracted label on 2026-10-28, and it is load-bearing for the comparison above: the words bottom and sides do not appear anywhere in it, so the label carries no site qualifier for the foot. https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/c3b715a9-233a-401a-ba60-f78c1ddf1ded.xml (accessed 2026-10-28)

[^lotaf]: The clotrimazole entry is taken from this site's own page for that product, [[lotrimin-af-antifungal-cream]], which records its Uses section as reading "cures most ringworm relieves itching, redness, irritation and discomfort which accompany this condition" and its marketing category as "OTC Monograph Drug" (code C200263) under M005, NDC 11523-6549, each verified against the DailyMed label at the time that page was published. A fresh DailyMed search for a clotrimazole Lotrimin SPL on 2026-10-28 did not surface one in the first 40 clotrimazole records returned, so nothing new is derived here and the entry is attributed to the existing page rather than re-sourced. The absence of an athlete's foot cure claim is reported as a fact about the single label that page examined, not about every clotrimazole package on sale. The underlying label that page cites is SPL set id b584e17f-ed43-43bd-b643-dfa48edd78c6. https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b584e17f-ed43-43bd-b643-dfa48edd78c6 (accessed 2026-10-28)