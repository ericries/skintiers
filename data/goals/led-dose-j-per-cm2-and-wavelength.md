---
aliases:
- LED dose
- J/cm2 LED
- joules per square centimetre skincare
- LED wavelength and dose
- irradiance LED mask
analyzed: '2026-10-23'
assurance: sonnet
name: 'LED Dose: What J/cm2 and Wavelength Actually Tell You'
slug: led-dose-j-per-cm2-and-wavelength
status: published
type: goal
updated: '2026-10-23'
---

Whether home LED works at all is argued on [[home-led-light-therapy]]. This page answers the narrower question that page does not touch: given a device in front of you, which published numbers mean something, and which only look like they do.

> **Three numbers get printed, and only one of them is a dose.** Wavelength (nm) says which light. Irradiance (mW/cm2) says how intensely it arrives. Dose, in J/cm2, is the two things a trial actually reports: intensity multiplied by time. If a brand gives you nm and nothing else, you cannot compute a dose, and nm alone tells you nothing about whether the device is strong enough to do what the study did.

## The arithmetic, once

Dose in J/cm2 equals irradiance in mW/cm2, times seconds, divided by 1000. That is a unit conversion rather than a claim, and it is the whole trick. A device that publishes irradiance and a treatment time has published its dose whether or not it says so.

Worked on the one clearance in this site's device coverage that prints the numbers. LED Technologies' perioral filing gives an Energy Level of 67.7 mW/cm2 over a 24 cm2 treatment area at "3 minutes per treatment".[^k172662] Three minutes is 180 seconds, so 67.7 times 180 divided by 1000 is about 12.2 J/cm2. Running the same arithmetic across the three predecessor devices in that filing's comparison chart, at 62.07, 70.16 and 61.59 mW/cm2 and the same three minutes, gives roughly 11.2, 12.6 and 11.1 J/cm2.[^k172662] Those four figures are calculated here from the published irradiance and time; the filing itself prints the inputs, not the J/cm2.

**The useful consequence.** Those four devices have treatment areas of 24, 30, 415 and 28 cm2, a seventeen-fold spread, and they all land within about a joule and a half of each other on dose.[^k172662] Area does not change the dose. It changes how much skin receives that dose at once, which is a claim about convenience and treatment time, not about strength. A large panel is not a stronger panel.

## Numbers that look like specifications and are not

**Power per emitter.** FOREO's hair device publishes "<5mW" as the energy per light source, with a treatment area of about 32 cm2.[^k242747] That cannot be converted into a dose. Power per diode times the number of diodes, divided by the illuminated area, would give irradiance only if you also knew the optical losses and the actual illuminated area, and none of that is published. Covered at [[foreo-faq-302]].

**A customer's guess.** One Lux page carried a repeated review speculating that the device was "maybe at least 50mW/cm2", which is a buyer's estimate and not a specification; the brand publishes no figure there at all.[^lux-clinical]

**Wavelength lists with no intensity.** Several devices publish wavelengths and nothing else. The same perioral filing lists 605, 630, 660 and 880nm for all four devices, which distinguishes none of them from each other.[^k172662] Wavelength tells you the mechanism being aimed at; it never tells you whether enough light arrived.

## What is actually published, across this site's LED pages

The honest summary is that disclosure is the exception. [[revive-light-therapy-lux-lip-care]] is the one page here that can quote a real irradiance, and only because a sibling clearance printed it. [[dpl-spotlite]] carries no irradiance or energy-dose figure anywhere, with the mW/cm2 unit appearing only inside an equivalence claim.[^spotlite] [[revive-light-therapy-lux-clinical]] has no irradiance or energy-dose figure on its page either.[^lux-clinical] [[dpl-faceware]] and [[revive-light-therapy-lux-panel]] publish treatment areas without the intensity that would make them mean anything.

## The Evidence

There is none to grade here, and saying so is the finding. The evidence reviews behind [[home-led-light-therapy]] grade LED by colour and by indication, and none of the figures they report is a dose: checked by string search on 2026-10-23, that page contains no occurrence of J/cm2, mW/cm2, joule, irradiance, fluence or dose anywhere in its text or its sources. So the published evidence supports blue and blue-red LED at a modality level while the trials' own intensities and exposure times do not reach the buyer. That gap is why a device cannot be matched to a studied protocol, and it is a reason to treat any specific dose claim on a product page with suspicion rather than a reason to pick a number.

**What to do with that.** Ask for two numbers: mW/cm2 and the treatment time. If a seller supplies both, you can check their device against a published protocol yourself. If they supply only wavelengths, a count of LEDs, or a panel size, you have been given marketing rather than a specification, and no amount of nm will fix it.

**Medical note.** This is educational content, not a substitute for a clinician. Nothing here says a particular dose is effective or safe for a particular person; it says what the published numbers do and do not let you work out. Whether home LED helps your skin at all is the question on [[home-led-light-therapy]].

## See Also

[[home-led-light-therapy]], [[revive-light-therapy-lux-lip-care]], [[dpl-spotlite]], [[dpl-faceware]], [[revive-light-therapy-lux-clinical]], [[foreo-faq-302]], [[home-use-skincare-devices-by-evidence]], [[fda-approved-vs-cleared-skincare]].

## Sources

[^k172662]: FDA 510(k) Summary K172662, LED Technologies, Inc., read for the figures quoted here and re-checked 2026-10-23. Its predicate comparison chart carries an Energy Level row giving "67.7 mW/cm" with a superscript two for the subject device against "62.07 mW/cm", "70.16 mW/cm" and "61.59 mW/cm" for three predecessor devices, with treatment areas of 24, 30, 415 and 28 cm2 respectively and "3 minutes per treatment" for all four, at wavelengths 605, 630, 660 and 880nm. The J/cm2 values given above (about 12.2, 11.2, 12.6 and 11.1) are calculated on this page from those published irradiance and time figures; the filing prints the inputs and not the dose, and no claim is made that the manufacturer states a J/cm2 value. The same figures and their full quoting caveats, including the superscript rendering, are set out on [[revive-light-therapy-lux-lip-care]]. https://www.accessdata.fda.gov/cdrh_docs/pdf17/K172662.pdf (accessed 2026-10-23)

[^k242747]: FDA 510(k) Summary K242747, "Faq (302)", Foreo, Inc., decision 2024-12-11, read 2026-10-23. Its predicate comparison table gives the energy per light source as "<5mW" for the subject device and both predicates, and the treatment area as "Approx. 32cm2". No irradiance in mW/cm2 and no treatment-time-based dose appears in the file, checked by reading the full six-page Summary. Full treatment at [[foreo-faq-302]]. https://www.accessdata.fda.gov/cdrh_docs/pdf24/K242747.pdf (accessed 2026-10-23)

[^spotlite]: FDA 510(k) Summary K183118. The absence statement for this device is carried and sourced on [[dpl-spotlite]], which records that no irradiance or energy-dose figure appears anywhere in its clearance file, the mW/cm2 unit being named only inside an equivalence claim. That page cites the underlying FDA document; it is referenced here rather than re-quoted so the finding has a single home. https://www.accessdata.fda.gov/cdrh_docs/pdf18/K183118.pdf (accessed 2026-10-23)

[^lux-clinical]: The absence statement and the customer speculation quoted here are carried and sourced on [[revive-light-therapy-lux-clinical]], which records that the brand page publishes no irradiance or energy-dose figure, and that the only occurrences of the unit are one duplicated customer review guessing "maybe at least 50mW/cm2". That page holds the cached source and the full context; it is referenced here rather than re-fetched. https://www.revivelighttherapy.com/collections/fda-cleared (accessed 2026-10-23)