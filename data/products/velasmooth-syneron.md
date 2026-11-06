---
analyzed: '2026-11-06'
assurance: sonnet
brand: Syneron
category: Devices
grades:
- effect: modest
  evidence: preliminary
  note: 'cosmetic: the ceiling is regulatory, not editorial. FDA''s own classification
    for this device type defines it as intended "to temporarily alter the appearance
    of cellulite", so temporary and appearance-level is the most the clearance permits
    anyone to claim. This site has read no product-specific clinical data for VelaSmooth,
    and the 510(k) route it came through does not require any; class-level evidence
    for energy devices in cellulite is on [[cellulite]]'
  use: For temporarily altering the appearance of cellulite (cosmetic), as an in-clinic
    prescription device rather than something sold for home use
image_unresolvable: discontinued in-clinic device from 2005; no current FDA device
  listing under the Syneron proprietary name and no brand page remains
key_actives: []
name: VelaSmooth (Syneron)
slug: velasmooth-syneron
status: published
type: product
updated: '2026-11-06'
videos: []
---

VelaSmooth is Syneron's combined infrared, radiofrequency and vacuum-massage body device, cleared by FDA in June 2005 as K050397 and again in July 2007 as K070092, a filing titled "MODIFICATION TO VELASMOOTH, SHAPER".[^fda] Both are Traditional 510(k)s decided Substantially Equivalent, and both carry product code NUV.[^fda] The condition itself, and what does and does not work on it, is on [[cellulite]].

> **The ceiling on what it can claim is written into the product code, not into the marketing.** FDA's classification for NUV devices defines them as intended "to temporarily alter the appearance of cellulite".[^class] Temporary, and appearance. That is the most any device cleared under this code is permitted to claim, however it is advertised, and it is a useful thing to carry to any cellulite device you meet.

## Summary

The file describes a device working by the simultaneous application "of heat to the tissue with light energy at a controlled Infrared wavelength, conducted RF energy, and mechanical manipulations of the skin", that last being the vacuum rollers. The scan runs the first two words together, so the quotation starts after them.[^k050397] It was cleared for **prescription use**: on the Indications for Use form, the Prescription Use box is marked and the Over-The-Counter box is not.[^k050397] This was clinic equipment, not a consumer gadget.

Its Indications for Use section lists several uses, not only cellulite: relief of minor muscle aches and pains, temporary improvement of local blood circulation, and temporary reduction in the appearance of cellulite. Those are read from a degraded scan and are deliberately not quoted here; see the source note.[^k050397]

## The Rubric

**Temporarily altering the appearance of cellulite (in-clinic device, prescription)**

- **Effect size: modest.** Bounded by what the clearance permits rather than by a trial result: the device type is defined as altering appearance temporarily.[^class] [[cellulite]] summarises where energy-based devices sit as a class, and this page does not repeat it.
- **Evidence quality: preliminary.** Both filings are 510(k) Summaries, a route that establishes substantial equivalence to existing devices rather than reviewing a product's own efficacy data. No product-specific clinical trial has been read for this page, and the clearance did not require one to exist.

## The Evidence

There is none specific to this device on this page, and that is the finding rather than an omission. Both filings are 510(k) Summaries, which establish substantial equivalence to devices already on the market rather than reviewing a product's own trial data, so a clearance here is not evidence that the device works. No product-specific clinical study has been read for this page. What the class as a whole can claim, and how thin that is, belongs to [[cellulite]].

## What it was found equivalent to

The predicate chain is the most revealing thing in the file, and it is unusual. VelaSmooth was not matched to one earlier cellulite device; the submission claims equivalence to "a combination of the following devices", five in total.[^k050397] Each resolves cleanly in FDA's database:[^fda]

- **K990445**, LPG Therapeutic Massager (Lpg USA), the mechanical massage component
- **K013197**, WS-501 Heat Lamp (Lhasa Medical), a heat lamp
- **K003538**, TDP CQ-27 Heat Lamp (Lhasa Medical), a second heat lamp
- **K031988**, Aurora DS (Syneron), the applicant's own earlier light-and-RF platform
- **K030142**, ThermaCool TC System (Thermage), the RF comparator

A device assembled, for regulatory purposes, out of a massager, two heat lamps and two energy platforms is a fair picture of what it does, and a reminder that substantial equivalence is a statement about predicates rather than about outcomes.

## Where to Buy

Not, as far as the FDA's own records show. A search of current device registration listings for the proprietary name returns a single entry, "Velasmooth Inner Ball" from Beijing Spiritlaser Science & Technology, which is not Syneron's device.[^listing] No current listing under Syneron's name appeared. That is what the listing database returns on this date and not proof the device has been withdrawn; registration listings reflect who is currently registered, not the full history of a cleared device.

## See Also

- [[cellulite]] for the condition and what the evidence supports
- [[home-rf-devices-by-whose-evidence-the-file-rests-on]] and [[home-use-skincare-devices-by-evidence]] for the same reading applied to devices sold for home use
- [[fda-approved-vs-cleared-skincare]] for why "FDA cleared" is not "FDA approved"

## Sources

[^fda]: openFDA device/510k API, queried 2026-11-06. K050397 "VELASMOOTH, SHAPER", applicant Syneron Medical, Ltd., received 2005-02-16, decision 2005-06-09, decision "Substantially Equivalent", product code NUV, statement_or_summary "Summary", clearance type "Traditional". K070092 "MODIFICATION TO VELASMOOTH, SHAPER", same applicant and product code, received 2007-01-10, decision 2007-07-27, same decision, summary and clearance type. The five predicate K numbers listed above were each queried individually against the same endpoint and returned, in order: LPG THERAPEUTIC MASSAGER, MODELS -ESI, THE (Lpg USA, Inc.); WS-501 HEAT LAMP (Lhasa Medical, Inc.); TDP CQ-27 HEAT LAMP (Lhasa Medical, Inc.); AURORA DS (Syneron Medical, Ltd.); THERMACOOL TC SYSTEM (Thermage, Inc.). They were verified this way precisely because the scanned summary renders two of them as "K03 1988" and "KO3Ol42". https://api.fda.gov/device/510k.json (accessed 2026-11-06)

[^class]: openFDA device/classification API for product code NUV, queried 2026-11-06. Device name "Massager, Vacuum, Light Induced Heating"; definition, quoted verbatim, "The device is intended to temporarily alter the appearance of cellulite"; regulation number 878.4810; device class 2; medical specialty "General, Plastic Surgery". https://api.fda.gov/device/classification.json?search=product_code:%22NUV%22 (accessed 2026-11-06)

[^k050397]: FDA 510(k) summary for K050397, retrieved from FDA's document archive and text-extracted with pdftotext on 2026-11-06. DEGRADED SCAN: the OCR is poor and renders the Indications for Use text as, for example, "Temporary reduction in the pppaarance of callnita". For that reason the indications are described above rather than quoted, and no figure is taken from this document. Two fragments are legible enough to quote and are given as they appear, including their OCR damage: the device description, which the scan renders as "si~nultaneousapplication of heat to the tissue with light energy at a controlled Infrared wavelength, conducted RF energy, and mechanical manipulations of the skin" with the first two words run together, and the predicate framing "a combination of the following devices". The Prescription Use / Over-The-Counter checkboxes are read from the form directly: the Prescription box carries a mark and the OTC box does not. Submitter address on the document is Syneron Medical Ltd., Yokneam, Israel. https://www.accessdata.fda.gov/cdrh_docs/pdf5/K050397.pdf (accessed 2026-11-06)

[^listing]: openFDA device/registrationlisting API, queried 2026-11-06 for proprietary_name "VELASMOOTH". One record is returned, proprietary name "Velasmooth Inner Ball", registrant BEIJING SPIRITLASER SCIENCE & TECHNOLOGY. A separate query for product code NUV returns 37 current listings from other manufacturers, so the code itself remains active. Absence of a Syneron listing in this database is reported as what the query returned and is not asserted as evidence of withdrawal. https://api.fda.gov/device/registrationlisting.json (accessed 2026-11-06)