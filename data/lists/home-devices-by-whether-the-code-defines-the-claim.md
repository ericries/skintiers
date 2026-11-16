---
aliases:
- Home devices by cleared indication
- Device marketing versus cleared indication
- What a home device product code permits
analyzed: '2026-11-16'
kind: best-of
name: Home Devices, by Whether the FDA Code Defines What They May Claim
slug: home-devices-by-whether-the-code-defines-the-claim
status: published
tier_list:
  by: 'whether the FDA product code a device is cleared under carries a definition
    naming what the device is for, read from the openFDA classification API on 2026-11-16.
    The rungs rank CHECKABILITY, not quality: a device on the top rung has a claim
    you can hold the marketing against, and one on the bottom rung does not. Whether
    any of them works is a separate question answered on each product page'
  items:
  - note: Product code OLP, defined as intended for over-the-counter use "to treat
      patients with mild to moderate acne vulgaris". The claim is specific enough
      to test marketing against, including the severity range.
    slug: neutrogena-light-therapy-acne-mask-plus
    tier: top
  - note: Product code NUV, defined as intended "to temporarily alter the appearance
      of cellulite". Temporarily and appearance are both in the definition, which
      is more restraint than the category's advertising usually shows.
    slug: velasmooth-syneron
    tier: top
  - note: Product code OHS, light-based over-the-counter wrinkle reduction, defined
      by anatomical location. A wrinkle claim can be checked against where the clearance
      says the device was assessed.
    slug: nuface-trinity-wrinkle-remover
    tier: top
  - note: Product code QAI, Powered Microneedle Device, defined as using needles "to
      mechanically puncture and injure skin tissue for aesthetic use". That describes
      a mechanism and not an outcome, so it constrains what the device IS without
      constraining what it may claim to achieve.
    slug: banish-kit-3-0
    tier: moderate
  - note: Product code NFO, whose openFDA classification record has an EMPTY definition
      field and sits under 21 CFR 882.5890, a Neurology regulation. Its own page records
      that the predicate was a facial device for a body product.
    slug: nubody-skin-toning-device
    tier: weak
  - note: Product code GYB, Media Electroconductive, definition also empty. A conductive
      gel is cleared as a medium, which says nothing about any skin benefit claimed
      for it.
    slug: nuface-gel-primer
    tier: weak
  title: Six covered devices, by how much their product code actually says
type: list
updated: '2026-11-16'
---

Every cleared home device sits under an FDA product code, and each code has a one-line definition. Some of those definitions name the condition and the limits; some describe only a mechanism; and three of the nine codes in use across this site's device pages have **no definition at all**. This page sorts by that, because a marketing claim can only be checked against a definition that exists. Whether any device works is a separate question, answered on each product page.

> **Three codes in use here define nothing.** ILY, NFO and GYB all return an empty definition field from the FDA classification database.[^classification] Eight of this site's 52 device pages are cleared only under one of those three, and three more are cleared under a mix.[^census] For those eleven, the clearance establishes that the device resembles something already on the market and nothing whatever about what it may claim to do for your skin.

## Rung 1: the code names the condition

These definitions are specific enough to hold advertising against.[^classification]

- **OLP**, Over-The-Counter Powered Light Based Laser For Acne: "The device is intended for over-the-counter (otc) use to treat patients with mild to moderate acne vulgaris." Note the severity range, which is part of the definition.
- **NUV**, Massager, Vacuum, Light Induced Heating: "The device is intended to temporarily alter the appearance of cellulite" Both limiting words are the FDA's.
- **OHS**, Light Based Over The Counter Wrinkle Reduction: "Use of light based treatment to reduce wrinkles on the body in general or specific anatomical locations depending on the information provided."
- **PAY**, Over-The-Counter Radiofrequency Coagulation Device For Wrinkle Reduction, which describes radiofrequency energy producing localized heating.

## Rung 2: the code names a mechanism, not an outcome

**QAI**, Powered Microneedle Device: "A powered microneedle device is a device using one or more needles to mechanically puncture and injure skin tissue for aesthetic use."[^classification] That tells you what the thing does to skin, not what it is permitted to claim will result. A device here can be accurately described and still make a claim the code neither grants nor denies.

## Rung 3: the code defines nothing

**ILY** (Lamp, Infrared, Therapeutic Heating), **NFO** (Stimulator, Transcutaneous Electrical, Aesthetic Purposes) and **GYB** (Media, Electroconductive) each return an empty definition.[^classification]

NFO is the significant one here, because it covers the largest device family this site tracks. Six covered pages are cleared under it alone, including [[nuface-plus]], [[nuface-mini-microcurrent-device]] and [[nubody-skin-toning-device]].[^census] Its regulation is 21 CFR 882.5890, in the Neurology specialty, which is the transcutaneous electrical nerve stimulator family. A microcurrent device marketed for facial lifting therefore reaches the market through a nerve-stimulator regulation whose code says nothing about faces, lifting, or skin.

## Rung 4: no clearance found at all

[[banish-kit-3-0]] is listed above under QAI because that is the only FDA classification naming microneedles, but its own page records the more basic finding: two openFDA searches, by company name and by device name, returned no 510(k) record at all. It is a manual stamp, so QAI, which covers *powered* devices, would not be its category anyway. A device with no clearance has no cleared indication to compare marketing against.

## What this sorting is and is not

A product code is a regulatory classification, not an efficacy finding, and a 510(k) clearance establishes substantial equivalence to an existing device rather than proof that anything works. Nothing on the top rung is thereby better than anything on the bottom one. What the top rung has is a published sentence you can read the advertising against; the bottom rung does not.

The census above counts only the codes recorded on this site's own device pages. Ten device pages record no product code at all and are not placed.[^census]

## See Also

- [[cellulite-devices-by-what-their-fda-code-permits]], the same method applied to one category in depth
- [[home-led-light-therapy]] and [[led-dose-j-per-cm2-and-wavelength]] for what the light devices are claimed to do
- [[microneedling]] and [[cellulite]] for the evidence behind two of the categories above

## Sources

[^classification]: openFDA device classification API, queried 2026-11-16 for each product code recorded on this site's device pages. Definitions quoted verbatim as returned: OLP "The device is intended for over-the-counter (otc) use to treat patients with mild to moderate acne vulgaris."; NUV "The device is intended to temporarily alter the appearance of cellulite"; OHS "Use of light based treatment to reduce wrinkles on the body in general or specific anatomical locations depending on the information provided."; QAI "A powered microneedle device is a device using one or more needles to mechanically puncture and injure skin tissue for aesthetic use."; and PAY, an electrosurgical device for over-the-counter aesthetic use using radiofrequency energy to produce localized heating within tissues. ILY (Lamp, Infrared, Therapeutic Heating), NFO (Stimulator, Transcutaneous Electrical, Aesthetic Purposes) and GYB (Media, Electroconductive) each returned an EMPTY definition field; that emptiness is a property of the record as returned on that date and is not an inference. All nine codes are returned as device_class 2. The identification of 21 CFR 882.5890 as NFO's regulation is from the same API, and its characterisation as the transcutaneous electrical nerve stimulator family, along with the NuBODY's facial predicate, is recorded on [[nubody-skin-toning-device]] from that device's own clearance documents. https://api.fda.gov/device/classification.json (accessed 2026-11-16)
[^census]: Census of this site's own pages, computed 2026-11-16 by reading every product page whose category is Devices and extracting the product codes its text records. It returns 52 device pages: 31 cleared only under a code with a definition, 8 cleared only under ILY, NFO or GYB, 3 under a mix of the two kinds, and 10 recording no product code at all. The eight on empty-definition codes alone are dermillume-red-hr1000, dpl-therapy-system, el-global-trade-deepskin-dep100, nubody-skin-toning-device, nuface-fix-serum-activator, nuface-gel-primer, nuface-mini-microcurrent-device and nuface-plus; the three mixed are nuface-trinity-ele-attachment, nuface-trinity-plus-wrinkle-reducer and omnilux-clear-u. This counts what THIS SITE has recorded, not what FDA holds: a device whose page does not state its product code is not placed, and no page was re-fetched from openFDA for this census.