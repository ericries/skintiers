---
aliases:
- SPF lip balms by label claims
- lip balm sunscreen labels
- what SPF lip balms actually claim
- lip sunscreen broad spectrum
analyzed: '2026-10-31'
assurance: sonnet
kind: best-of
name: SPF Lip Balms by What Their FDA Label Actually Claims
slug: spf-lip-balms-by-label-claims
status: published
tier_list:
  by: how much of the sunscreen monograph claim set the product's own Drug Facts label
    carries, read from each label on the product pages here
  caption: This ranks what the label says, not how well the product protects. Neither
    product here is tested against the other, and a fuller claim set is a sign the
    maker did the testing the monograph requires for those claims, not proof of better
    performance on lips. The UV filters themselves are graded on sunscreen-uv-filters.
  items:
  - note: 'States its SPF, declares two filters at strength (avobenzone 3.0% and octinoxate
      7.5%) and makes the narrow claim the monograph allows without broad-spectrum
      testing: "Helps prevent sunburn and chapped lips." What is missing is still
      the larger half, no broad spectrum, no water resistance, no reapplication interval
      and no skin-cancer or early-aging claim.'
    slug: jack-black-intense-therapy-lip-balm-spf-25
    tier: good
  - note: Sold as a sunscreen lip balm and its Drug Facts panel never states an SPF
      value for itself at all, alongside no broad spectrum and no water resistance.
      Four filters are declared, so the product is a sunscreen in composition; the
      label simply does not tell a buyer how much of one.
    slug: trader-joes-sunscreen-lip-balm
    tier: weak
tier_list_reviewed:
- '[[revive-light-therapy-lux-lip-care]] (an LED lip device, not a sunscreen, so it
  is out of scope for this ranking rather than at the bottom of it)'
- the other 370 lip products in the federal drug listing that declare avobenzone (see
  the prose); none has a page here yet, so none is graded, and the two above are the
  only ones whose labels have been read in full
- lip balms with no sunscreen active at all, which are cosmetics rather than OTC drugs
  and carry no Drug Facts panel to rank
type: list
updated: '2026-10-31'
---

A lip balm sold for sun protection is a regulated OTC drug, and its Drug Facts panel is the only place its claims have to be true. Reading the two whose labels have been read in full here, the striking thing is not what they claim but what they leave out.

## The claim set a sunscreen label can carry

Under the US sunscreen monograph a product may state an SPF value, and separately may be designated broad spectrum, may claim water resistance for a stated number of minutes, and may claim to reduce the risk of skin cancer and early skin ageing. Those last claims are gated: they require a broad-spectrum designation at SPF 15 or higher. A label that carries only an SPF number is making the narrowest claim available, which is prevention of sunburn.

Neither product graded here carries a broad-spectrum designation, a water-resistance claim, a reapplication interval, or a skin-cancer claim. One of them does not state an SPF value for itself at all.

## How big the category is

Searching the federal drug listing for products whose brand name contains "lip" and which declare avobenzone returns 372 records, every one in the returned sample submitted as an over-the-counter monograph drug rather than approved under its own application.[^ndc] Across that sample the filters pair up predictably, avobenzone with octisalate, octocrylene, octinoxate and homosalate.[^ndc] The names range from supermarket own-brands to Coppertone Sport.

That number is the reason this page ranks only two products. Both of the labels below were read line by line; the other records were not, and a category this large should not be characterised from brand names alone.

## What this does not tell you

Lips are a high-risk site, thin-skinned, hard to cover and constantly rubbed and licked, which is exactly why water resistance and reapplication intervals would be useful things for these labels to carry. None of that is evidence about which product performs better; it is evidence about which maker did the testing the monograph requires before a claim may be printed. The filters themselves are graded on [[sunscreen-uv-filters]] and lip care generally on [[lip-care]].

## See Also

[[lip-care]], [[sunscreen-uv-filters]], [[jack-black-intense-therapy-lip-balm-spf-25]], [[trader-joes-sunscreen-lip-balm]], [[fda-approved-vs-cleared-skincare]], [[best-mineral-sunscreens-by-evidence]].

## Sources

Every label claim and absence quoted on this page was read from that product's own FDA Structured Product Label and is already sourced, dated and quoted on its page: [[jack-black-intense-therapy-lip-balm-spf-25]] and [[trader-joes-sunscreen-lip-balm]]. This page adds no new reading of either label and no statistic beyond the listing count below.

[^ndc]: openFDA drug/ndc API, queried on 2026-10-31 for brand_name "lip" together with active_ingredients.name "AVOBENZONE", returning 372 records. In the 50-record sample returned, every record carried marketing_category "OTC MONOGRAPH DRUG", avobenzone appeared in all 50, octisalate in 37, octocrylene in 34, octinoxate in 28 and homosalate in 23, with petrolatum, oxybenzone and dimethicone appearing once or twice as declared actives. Brand names in that sample run from own-label balms to Coppertone Sport. This query matches only products whose brand_name field contains the string "lip" and which declare avobenzone, so it undercounts lip sunscreens using other filters or named differently, and no total for the category is claimed. https://api.fda.gov/drug/ndc.json?search=brand_name:%22lip%22+AND+active_ingredients.name:%22AVOBENZONE%22 (accessed 2026-10-31)