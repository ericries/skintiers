---
aliases:
- Infrared heat lamp
- Heat lamp vs LED
- Red light vs infrared
analyzed: '2026-11-06'
assurance: sonnet
name: Infrared heat lamps versus LED skin devices
slug: infrared-heat-lamps-vs-led-skin-devices
status: published
type: goal
updated: '2026-11-07'
---

Two kinds of device glow red and are sold with overlapping language, and the FDA treats them as different things entirely: one is a heating lamp reviewed by the Physical Medicine panel, the other is a skin device reviewed by General and Plastic Surgery. Knowing which you are looking at tells you what it was actually cleared to do.

> **The clearest case is one product line that crossed the boundary.** LED Technologies' first clearance, the DPL Therapy System in 2008, sits under product code ILY, "Lamp, Infrared, Therapeutic Heating", regulation 890.5500, Physical Medicine.[^ily] All fourteen later clearances in that family moved to regulation 878.4810 under the General and Plastic Surgery panel: eleven under OHS, "Light Based Over The Counter Wrinkle Reduction", including the dpl II Panel and the reVive wrinkle and acne device, and three under the acne code OLP.[^codes] Same brand family, same red glow, two different regulatory animals.

## How to tell which one you are holding

Not by the marketing, and not by the colour. The product code on the clearance is the only reliable answer, and it is public.

- **ILY, Lamp, Infrared, Therapeutic Heating.** Regulation 890.5500, Physical Medicine panel.[^ily] This is a heating device. The clearances in this family are about delivering therapeutic heat, not about changing skin.
- **OHS, Light Based Over The Counter Wrinkle Reduction.** Regulation 878.4810, General and Plastic Surgery. FDA defines it as the "Use of light based treatment to reduce wrinkles on the body in general or specific anatomical locations depending on the information provided".[^codes]
- **OLP, Over-The-Counter Powered Light Based Laser For Acne.** Same regulation, same panel. Defined as intended "to treat patients with mild to moderate acne vulgaris" and to "emit energy in the red and blue region of the spectrum".[^codes]

A fourth code worth recognising sits in the same regulation: NUV, the vacuum-and-light-heating massager code, whose definition caps its claim at temporarily altering the appearance of cellulite.[^nuv] That one is worked through on [[velasmooth-syneron]].

## The Evidence

A product code tells you what a device was permitted to claim. It tells you nothing about whether it works, and the two are easy to confuse because both sound official.

That gap is the subject of the device lists on this site rather than this page. [[home-led-devices-by-what-the-file-publishes]] ranks these filings by whether they disclose a dose at all, and finds most do not. [[home-led-light-therapy]] covers what the clinical literature supports by colour and indication. Neither question is answered by the code, and a device can hold a perfectly valid clearance while publishing nothing about its output.

The practical consequence for a buyer is narrow but real: if a device's clearance is ILY, its cleared purpose is heating, and any wrinkle or acne claim attached to it in marketing is not what the agency reviewed.

## See Also

- [[dpl-therapy-system]], the ILY heating lamp the dpl line began as, and [[dermillume-red-hr1000]], the 2005 LED array under the same code that predicates it
- [[dpl-ii-panel]], [[theraface-led-light-ring]] and [[revive-light-therapy-wrinkle-and-acne-led-device]], all cleared under OHS
- [[home-led-devices-by-what-the-file-publishes]] and [[home-led-light-therapy]] for disclosure and evidence, which this page does not cover
- [[fda-approved-vs-cleared-skincare]] for what clearance means at all

## Sources

[^ily]: openFDA device/510k and device/classification APIs, queried 2026-11-06. K081570, device name "DPL THERAPY SYSTEM", applicant "Led Technologies, LLC", decision 2008-11-07, product code ILY. The ILY classification record gives device name "Lamp, Infrared, Therapeutic Heating", regulation number 890.5500, device class 2, medical specialty "Physical Medicine". That record carries no definition text, so no definition is quoted for ILY above; the device name and the panel are what the database states. https://api.fda.gov/device/classification.json?search=product_code:%22ILY%22 (accessed 2026-11-06)

[^codes]: openFDA device/classification API, queried 2026-11-06. OHS: device name "Light Based Over The Counter Wrinkle Reduction", regulation 878.4810, class 2, specialty "General, Plastic Surgery", definition quoted verbatim above. OLP: device name "Over-The-Counter Powered Light Based Laser For Acne", regulation 878.4810, class 2, same specialty, definition quoted verbatim above. Product codes for the individual devices named here were each confirmed against device/510k on the same date: K171390 (dpl II Panel) OHS, K212155 (TheraFace LED) OHS, K223482 (reVive Light Therapy Wrinkle and Acne LED Device) OHS. The eleven/three split is the full applicant query rather than a sample: device/510k for applicant "LED Technologies" returns 15 records, K081570 under ILY and the other fourteen under 878.4810 — eleven OHS and three OLP, the OLP ones being K180447 (reVive Light Therapy LED Cleansing System, 2018-06-04), K183118 (dpl SpotLite, 2019-02-07) and K210968 (reVive Light Therapy Essentials, 2021-12-21). This count corrects an earlier draft of this page, which said every later device in the family sat under OHS. https://api.fda.gov/device/classification.json (accessed 2026-11-06)

[^nuv]: openFDA device/classification API, queried 2026-11-06. NUV: device name "Massager, Vacuum, Light Induced Heating", regulation 878.4810, class 2, specialty "General, Plastic Surgery", definition "The device is intended to temporarily alter the appearance of cellulite". https://api.fda.gov/device/classification.json?search=product_code:%22NUV%22 (accessed 2026-11-06)
