---
analyzed: '2026-11-05'
assurance: sonnet
kind: best-of
name: One FDA applicant, several shelf brands
slug: one-fda-applicant-several-shelf-brands
status: published
type: list
updated: '2026-11-05'
---

Four companies in this site's home-device coverage file their FDA clearances under one applicant name and sell the results under several different brands. A shopper comparing two devices on a shelf can be comparing two products from the same filing cabinet.

> **Why this is worth knowing.** Brand names are a marketing choice; the 510(k) applicant is a legal one. When the same applicant's name sits behind two devices, their clearances often share predicates, test reports and sometimes the hardware, so the brands are not the independent alternatives a shelf implies. It does not mean the devices are identical, and it is not an accusation of anything. It is a reason to compare clearances rather than packaging. Every count below was taken from openFDA's 510(k) endpoint on 2026-11-05 and is a count of clearances, not of products.[^openfda]

## LED Technologies: dpl, reVive and NUVE

Fifteen clearances, filed under two spellings of the same company, "Led Technologies, Inc." for twelve and "Led Technologies, LLC" for three.[^openfda] They carry three consumer names. The dpl line covers [[dpl-therapy-system]], [[dpl-nuve]], [[dpl-ii-panel]], [[dpl-iia-panel]], [[dpl-spectralite]], [[dpl-spotlite]] and [[dpl-faceware]]. The reVive line covers [[revive-light-therapy-essentials]], [[revive-light-therapy-led-cleansing-system]] and [[revive-light-therapy-wrinkle-and-acne-led-device]], among others on [[revive-light-therapy]]. A third name, NUVE, appears in the device name for K141181, "NUVE FOR WRINKLES, DPL NUVE FOR WRINKLES", which carries both brands at once.[^openfda]

This is the clearest case on the site, because the dpl and reVive pages already cite each other's filings: the irradiance chart used on several reVive pages comes from K172662, a reVive filing, while the dpl figures come from separate dpl ones.

## Home Skinovations and Silk'N Beauty: Silk'n, Flash n' Go, HeatLux, Glide, ToothWave

Sixteen clearances split across two similarly named entities, fifteen under "Home Skinovations , Ltd." and one under "Silk'N Beauty , Ltd." ([[silkn-titan-allways]], K230013).[^openfda] The device names run through Silk'n, Flash n' Go, HeatLux, Glide and ToothWave.[^openfda]

Read this count carefully, because it is the one most likely to mislead. Not all sixteen are skin devices: ToothWave is a toothbrush, and its first entry, DEN190039, is a De Novo authorisation rather than a 510(k) clearance, though the 510(k) endpoint returns it.[^openfda] The brand breadth is real; the number is a count of filings across a product range that reaches beyond skin.

## Theragun and Therabody: TheraFace, RecoveryAir, JetBoots

Five clearances across two corporate names, three under "Theragun, Inc." and two under "Therabody, Inc.".[^openfda] Only three of the five are TheraFace devices: TheraFace Microcurrent (K212238), TheraFace LED (K212155, the clearance behind [[theraface-led-light-ring]]) and TheraFace Mask (K230293). The other two, RecoveryAir PRO and JetBoots PRO Plus, are compression devices and have nothing to do with skin.[^openfda]

The distinction matters because "five clearances" and "five TheraFace clearances" are different claims, and only the first is true.

## El Global Trade: CurrentBody, sensiLight, sensiLift, sensiFirm, RF-Relief, IPL400, DeepSkin

Twelve clearances, all under "El Global Trade, Ltd.", and the widest spread of shelf names in this group.[^openfda] They include [[currentbody-skin-rf]] (K232424) alongside sensiLight and Sensilight Pro, sensiLift and Sensilift Pro, sensiFirm, micro IPL, RF-Relief, IPL400 and DeepSkin.[^openfda] A shopper who knows [[currentbody]] as a brand would have no way to tell from the box that the same applicant files under seven other names.

## What to do with this

- **Compare K numbers, not brands.** Each device page here names its clearance. Two devices sharing an applicant may share a predicate chain, which is the thing worth checking.
- **A shared applicant is not a shared device.** Clearances under one company can cover genuinely different hardware, and this list does not claim otherwise.
- **The counts are filings.** They include withdrawn, superseded and non-skin products, which is why each section says what its number actually contains.

## See Also

[[home-led-devices-by-what-the-file-publishes]], [[home-device-wrinkle-claims-by-cleared-scope]], [[home-use-skincare-devices-by-evidence]], [[manufacturer-authored-studies-by-what-they-disclosed]], [[revive-light-therapy]], [[silkn]], [[currentbody]]

## Sources

[^openfda]: openFDA device/510k API, queried by applicant on 2026-11-05, one query per company, limit 100, with the returned record count checked against the meta total so no result set was truncated. Counts and device names as returned: applicant "LED Technologies" returns 15 records, 12 under "Led Technologies, Inc." and 3 under "Led Technologies, LLC", with device names including DPL THERAPY SYSTEM, DPL NUVE, "NUVE FOR WRINKLES, DPL NUVE FOR WRINKLES" (K141181), dpl II Panel, dpl SpectraLite, dpl IIa Panel, dpl SpotLite, dpl Faceware, reVive Perioral (K172662) and several reVive Light Therapy entries. Applicant "Home Skinovations" returns 15 under "Home Skinovations , Ltd." and applicant "Silk'N Beauty" returns 1 under "Silk'N Beauty , Ltd." (K230013, Silk'n Titan Allways), 16 together; device names include SILK'N, FLASH N' GO, HEATLUX, GLIDE DEVICE, Silk'n HST, Silk'n Infinity, ToothWave and Silkn Toothwave, and the ToothWave entry DEN190039 carries a De Novo number rather than a K number. Applicant "Theragun" returns 3 under "Theragun, Inc." (TheraFace Microcurrent K212238, RecoveryAir PRO K211745, TheraFace LED K212155) and applicant "Therabody" returns 2 under "Therabody, Inc." (TheraFace Mask K230293, JetBoots PRO Plus K241256). Applicant "El Global Trade" returns 12 under "El Global Trade, Ltd.", device names SENSILIGHT MINI, "SENSILIGHT/ SENSILIGHT PLUS", sensiLight Mini, sensiLift, sensiFirm, micro IPL, RF-Relief, "Sensilight Pro / Pistol IPL", CurrentBody Skin RF (K232424), IPL400, "Sensilift Pro (ST300XXYYZZZ)" and "DeepSkin (DEP100)". The applicant field is matched as text, so a company filing under a spelling not searched here would be missed; the two-spelling cases above were found precisely because the counts were grouped by the exact applicant string rather than assumed. https://api.fda.gov/device/510k.json (accessed 2026-11-05)