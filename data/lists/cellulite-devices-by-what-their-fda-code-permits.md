---
aliases:
- Cellulite devices by FDA product code
- What cellulite devices are allowed to claim
- Cellulite device clearances
analyzed: '2026-11-14'
assurance: sonnet
kind: best-of
name: Cellulite Devices by What Their FDA Product Code Permits Them to Claim
slug: cellulite-devices-by-what-their-fda-code-permits
status: published
type: list
updated: '2026-11-14'
---

Every cleared cellulite device in the United States sits under a product code, and that code carries a one-line definition stating what the device is for. The definitions are public, short, and far more careful than the advertising. This page sorts the codes by how much they permit, and places the devices this site covers. What actually works on cellulite is a separate question, answered at [[cellulite]].

> **Two of the three cellulite codes contain the word "temporarily".** The FDA definition for product code NUV reads in full: "The device is intended to temporarily alter the appearance of cellulite".[^nuv] PBX is permitted "Mechanical massaging to provide a temporary reduction in the appearance of cellulite".[^pbx] Appearance, temporarily. A device cleared under either code has been cleared to change how cellulite looks, for a while.

## Rung 1: permitted to claim improvement, without the word temporary

**Product code OUP**, "Powered Surgical Instrument For Improvement In The Appearance Of Cellulite", defined as "Used for controlled release of subcutaneous tissue for improvement in the appearance of cellulite."[^oup] This is the only one of the three whose definition omits any time limit, and it is also the only surgical one: it cuts the fibrous bands that tether the skin. Devices cleared under it include The Cellfina System, K192185, and Avéli, K221336 and K232153.[^oup510k] This site has no page for either, which is a gap worth naming rather than hiding.

## Rung 2: permitted to claim a temporary change in appearance

**Product code NUV**, "Massager, Vacuum, Light Induced Heating", Class II under 21 CFR 878.4810.[^nuv]

- **[[velasmooth-syneron]]** carries this code. Its page records that both of its clearances are Traditional 510(k) Summaries decided Substantially Equivalent, which establishes likeness to an existing device rather than reviewing the product's own efficacy data.

**Product code PBX**, "Massager, Vacuum, Radio Frequency Induced Heat", whose definition pairs the temporary cellulite-appearance claim with heat for "minor relief of minor aches and pain".[^pbx] Devices under it include Viora's V30, V20 and V10 systems, K202247, and the Palm NRG cellulite and muscle toning body device, K191940.[^pbx510k] None has a page here.

## Rung 3: cleared under a code that does not mention cellulite at all

**[[nubody-skin-toning-device]]**, product code **NFO**. The openFDA classification record for NFO has an **empty definition field**, and its regulation is 21 CFR 882.5890, whose medical specialty is Neurology.[^nfo] That is the transcutaneous electrical nerve stimulator family. A body device marketed for toning therefore reaches the market through a neurology regulation with no cellulite claim attached to its code at all, and its own page records that its predicate was a facial device.

That is not a violation of anything. It is a demonstration that the product code tells you what a device was compared against, not what it will do for you.

## What this sorting is and is not

A product code is a regulatory classification, not an efficacy finding. None of these clearances required the device to be shown to work; the 510(k) route asks whether a device is substantially equivalent to one already marketed. The definitions are still worth reading, because they are the most conservative description of the product anyone has written down.

Every grade of whether these treatments actually reduce dimpling lives on [[cellulite]], which ranks the options on evidence and finds nothing better than modest and temporary.

## Sources

[^nuv]: openFDA device classification API, product code NUV, read 2026-11-14. Returns device_name "Massager, Vacuum, Light Induced Heating", definition "The device is intended to temporarily alter the appearance of cellulite", regulation_number 878.4810, device_class 2, medical_specialty_description "General, Plastic Surgery". https://api.fda.gov/device/classification.json?search=product_code:NUV (accessed 2026-11-14)
[^pbx]: openFDA device classification API, product code PBX, read 2026-11-14. Returns device_name "Massager, Vacuum, Radio Frequency Induced Heat" and definition "Generates heat in body tissues for minor relief of minor aches and pain. Mechanical massaging to provide a temporary reduction in the appearance of cellulite." https://api.fda.gov/device/classification.json?search=definition:%22cellulite%22 (accessed 2026-11-14)
[^oup]: openFDA device classification API, product code OUP, read 2026-11-14. Returns device_name "Powered Surgical Instrument For Improvement In The Appearance Of Cellulite" and definition "Used for controlled release of subcutaneous tissue for improvement in the appearance of cellulite." The observation that this definition contains no time-limiting word, while NUV and PBX both do, is a comparison made here across the three definitions as returned by the same query on 2026-11-14, not a statement the FDA makes. https://api.fda.gov/device/classification.json?search=definition:%22cellulite%22 (accessed 2026-11-14)
[^oup510k]: openFDA device 510(k) API, product code OUP, read 2026-11-14. The four most recent records returned were K192185 "The Cellfina System" (Ulthera, Inc., 2019-10-09), K221336 and K232153 both "Avéli" (Revelle Aesthetics, Inc., 2022-08-05 and 2023-08-18), and DEN110004 "CABOCHON SYSTEM" (Cabochon Aesthetics, Inc., 2013-07-12). The query returned a limited page of results, so this is not a complete list of devices under the code. https://api.fda.gov/device/510k.json?search=product_code:OUP (accessed 2026-11-14)
[^pbx510k]: openFDA device 510(k) API, product code PBX, read 2026-11-14. The four most recent records returned were K230037 "BACK 3" (Swims America Corp, 2023-07-19), K202247 "V30 system, V20 system, V10 system, V-VR Hand piece" (Viora, Ltd., 2020-12-09), K201475 "Ultimate Contour, Ultimate Contour Mini" (CAO Group, Inc., 2020-10-28) and K191940 "Palm NRG cellulite and muscle toning body device" (Heat IN A Click, 2020-11-03). The query returned a limited page of results, so this is not a complete list of devices under the code. https://api.fda.gov/device/510k.json?search=product_code:PBX (accessed 2026-11-14)
[^nfo]: openFDA device classification API, product code NFO, read 2026-11-14. Returns device_name "Stimulator, Transcutaneous Electrical, Aesthetic Purposes", regulation_number 882.5890, device_class 2, medical_specialty_description "Neurology", and an EMPTY definition field. The empty definition is reported as read from the API on that date; it is a property of the record returned, not an inference. The identification of 21 CFR 882.5890 as the transcutaneous electrical nerve stimulator regulation, and the NuBODY's facial predicate, are recorded on [[nubody-skin-toning-device]] from that device's own clearance documents. https://api.fda.gov/device/classification.json?search=product_code:NFO (accessed 2026-11-14)