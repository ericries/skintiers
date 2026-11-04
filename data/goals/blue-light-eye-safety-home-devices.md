---
aliases:
- Blue light and eye safety
- LED mask eye safety
- Are LED masks safe for your eyes
- IEC 62471
- Photobiological safety
analyzed: '2026-11-03'
assurance: sonnet
name: Blue light and eye safety in home skincare devices
slug: blue-light-eye-safety-home-devices
status: published
tier_list:
  by: how much ocular safety each device's own FDA clearance file actually documents,
    which in every case here is less than the marketing around these devices implies
  items:
  - note: The only file read for this page that names the photobiological safety standard
      at all. Its Non-Clinical Testing section lists conformity with IEC 62471 alongside
      electrical and EMC testing. That is one line in a bench list, and the words
      eye, ocular, retina and goggle appear nowhere in the document.
    slug: illumask-acne-light-therapy-mask
    tier: moderate
  - note: Its summary reports consensus-standard testing including a collateral standard
      for non-laser light sources, which is the family IEC 62471 belongs to, but the
      page recording that read did not capture a standard number. Better than silence,
      short of a named standard.
    slug: neutrogena-light-therapy-acne-mask-plus
    tier: weak
  - note: Nothing. The Testing section of the K223482 summary covers software validation
      only, and the whole document contains no occurrence of eye, ocular, scattering,
      photobiological, 62471 or 60601.
    slug: revive-light-therapy-lux-spot
    tier: minimal
  - note: The predicate behind the Neutrogena mask, and not separately examined for
      ocular content here. Listed so the chain is visible rather than implied.
    slug: pulsaderm-acne-mask-28
    tier: null
tier_list_reviewed: '2026-11-03'
type: goal
updated: '2026-11-03'
---

If you are wearing a panel of blue LEDs a few centimetres from your closed eyelids, the sensible question is what anyone has checked. The answer, read out of the clearance files themselves, is thinner than the category's marketing suggests.

> **There is a standard, and it is named in exactly one of the files read here.** IEC 62471 is the photobiological safety standard for non-laser light sources, and the illuMask clearance lists conformity with it in a single line of its Non-Clinical Testing section.[^k123999] In the same 18,535-character document, the words eye, ocular, retina and goggle do not appear once.[^k123999] A standard's name in a bench-testing list is the strongest ocular-safety statement found in any of these files.

## The Evidence

**What a clearance file actually contains.** The illuMask Non-Clinical Testing section reads, in full on this point: "This device is in conformnity with IEC 60601-1 3rd Edition electrical safety testing, TEC 60601-1-2 EMC testing and lEG 62471 photobiological safety testing."[^k123999] Two of those three standard names are mangled by the scan, and the sentence is the entire photobiological content of the submission. There is no exposure figure, no irradiance at the eye, no discussion of whether the eyelid is an adequate barrier, and no eye-protection instruction.

**What a clearance file can contain instead, which is nothing.** The reVive Light Therapy Wrinkle and Acne LED Device was cleared in 2022 as K223482. Its summary has a section headed Testing, and that section covers software: it reports that the device "software was tested and validated in accordance with" an FDA guidance on software contained in medical devices.[^k223482] Across the whole 13,526-character document there is no occurrence of eye, ocular, scattering, photobiological, 62471 or 60601.[^k223482] That is not a criticism of the device; it is a description of what a 510(k) for a software change establishes, which is that the change did not break anything, not that the light is safe to shine at your eyes.

**Why this happens.** These devices are cleared by showing substantial equivalence to an already-cleared predicate, so each new file inherits the ocular question rather than re-answering it. The Neutrogena mask's summary reports consensus-standard testing that includes a collateral standard for non-laser light sources, the family IEC 62471 sits in, which is as close as that chain gets to the question.[^neutrogena] The practical result is that the standard is applied somewhere upstream and is invisible by the time a current product is cleared.

**A record finding about the paperwork.** The reVive 510(k) summary's own header reads "K223842" while the clearance letter it is bound with reads K223482, a transposition in the applicant's document.[^k223482] On a device line where naming has already been recorded as a recurring problem, see [[revive-light-therapy-lux-spot]], the number is wrong in the file itself.

## What this means in practice

- **Close your eyes, and treat eye-protection advice as coming from the manufacturer, not from a regulator.** None of the files read here instructs on eye protection at all.
- **"FDA cleared" does not mean eye-tested.** For K223482 it means a software change was validated.
- **IEC 62471 is the term to look for** if a brand makes a photobiological safety claim. It is a real standard with a real meaning, and a brand naming it is saying more than a brand saying its light is gentle.
- **A claim about eye safety that appears only in marketing is not in the file.** This page deliberately quotes no brand's eye-safety copy, because the two such claims that prompted it could not be found in the clearance document they were attributed to.

## See Also

- [[home-led-light-therapy]] for whether these devices work at all
- [[illumask-acne-light-therapy-mask]], [[neutrogena-light-therapy-acne-mask-plus]], [[revive-light-therapy-lux-spot]] and [[pulsaderm-acne-mask-28]], the four files behind the ranking above
- [[home-led-devices-by-what-the-file-publishes]] for the same reading applied to output figures

## Sources

[^k123999]: FDA 510(k) Summary for K123999, "illuMask Acne Light Therapy Mask", La Lumiere LLC, decision 2013-08-28, product code OLP. Retrieved as PDF from the FDA document archive and read in full as extracted text on 2026-11-03; the extracted text is 18,535 characters. The Non-Clinical Testing sentence is quoted above exactly as the scan renders it, including its OCR damage: "conformnity" for conformity, "TEC" and "lEG" for IEC. Nothing else in the quotation is altered. Two absences are reported as absences, by case-insensitive search of that extracted text on 2026-11-03: it contains zero occurrences of each of the terms eye, ocular, retina and goggle, and exactly one occurrence each of 62471 and photobio. https://www.accessdata.fda.gov/cdrh_docs/pdf12/K123999.pdf (accessed 2026-11-03)

[^k223482]: FDA 510(k) clearance letter and 510(k) Summary for K223482, "reVive Light Therapy Wrinkle and Acne LED Device", LED Technologies Inc., Largo, Florida; submission dated 18 November 2022, letter dated 21 December 2022; regulation 21 CFR 878.4810, class II, product codes OHS/OLP. Retrieved as PDF and read in full as extracted text on 2026-11-03; the extracted text is 13,526 characters. Quoted verbatim from the Testing section: "software was tested and validated in accordance with". The guidance it names, on the content of premarket submissions for software contained in medical devices, is paraphrased rather than quoted because the source renders its title inside curly quotation marks that cannot be reproduced inline without altering them. The summary's own header reads "K223842" against the letter's K223482. Six absences are reported as absences, by case-insensitive search of that extracted text on 2026-11-03: zero occurrences of each of the terms eye, ocular, goggle, scatter, photobio, 62471 and 60601. https://www.accessdata.fda.gov/cdrh_docs/pdf22/K223482.pdf (accessed 2026-11-03)

[^neutrogena]: FDA 510(k) Summary for K180847, "Neutrogena Light Therapy Acne Mask+", Johnson & Johnson Consumer Inc., decision 2018-06-19, product code OLP. This document was read in full on 2026-10-16 for [[neutrogena-light-therapy-acne-mask-plus]], where its quotations are set out. The statement used here is that page's own reading of the Performance Data section, that it reports consensus-standard testing for basic safety and essential performance including a collateral standard for the home healthcare environment and one for non-laser light sources. That is a paraphrase recorded on that page rather than a quotation, and no standard number is claimed for this file because none was captured in that read. https://www.accessdata.fda.gov/cdrh_docs/pdf18/K180847.pdf (accessed 2026-10-16)