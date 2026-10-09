# Aluris HP Plus: strength variants and local evidence retrieval

Recorded: 2026-10-09T14:00:35-07:00 (America/Los_Angeles).

## Question and confirmed context

The dermatologist offered Aluris HP Plus Cream as a replacement for the previously discussed tretinoin 0.02% / azelaic acid 5% / niacinamide 4% compound. The user confirmed that the existing compound is currently used twice weekly, updating the earlier introductory once-weekly schedule. The user subsequently supplied the proposed label text: niacinamide 4% / tretinoin 0.1% / cream 30GM. Thirty grams is package size, not another concentration.

Earlier discussion concerned a 48-year-old woman with perimenopause, PCOS-associated acne, possible rosacea, and aging concerns. The more recent wording is “my derm”; do not silently assign every previously described medical detail to the user if patient identity matters. The formulation comparison and confirmed use frequency do not depend on resolving that ambiguity.

## Local sources and retrieval lesson

No Aluris/Oxiazar/011035/72934-2569 match was located in authored data or Markdown/text research-cache records. This supports a product identification gap within the searched scope, not a claim that all possible formats or sources lack it.

The clinically important concentration comparison already exists in `data/ingredients/tretinoin.md`, particularly its “The Evidence” section and source 1: Griffiths et al., 1995, a 99-person, 48-week comparison of 0.025% and 0.1% tretinoin. The profile reports similar photoaging improvement with greater irritation at 0.1%. No new clinical-evidence search was necessary. Do not tell the creator to add supposedly absent evidence that is already in an ingredient profile.

The initial large frontmatter/search output obscured the relevant body text. Reading headings and then bounded body sections resolved this. An ingredient-to-primary-study index would help, but the reader must also inspect the body before concluding evidence is missing. A missing standalone study filename is not missing evidence.

`data/ingredients/azelaic-acid.md` supports azelaic acid's acne, papulopustular rosacea, and pigmentation roles; the strongest clinical evidence discussed there concerns 15–20% formulations. It does not establish the efficacy of this patient's 5% compound used twice weekly. `data/ingredients/hyaluronic-acid.md` supports a hydration role, not a guarantee that adding it makes 0.1% tretinoin as tolerable as a lower concentration.

## Necessary web lookup audit

External lookup was needed for the unidentified brand, exact strength variant, and declared formulation. The manufacturer product page and catalog were sufficient. Sources used:

- https://sknv.com/product/aluris-hp-plus-cream/ — HP formulation, product identifiers, former name, packaging, and compounded-product status.
- https://sknv.com/wp-content/uploads/2024/12/1024_MostPopularMedications_checkandsymbolsDIGITAL.pdf — independent document from the same manufacturer confirming HP ingredients and distinguishing LP/standard/HP variants.

The manufacturer's topical-medication listing and marketing article also surfaced during discovery; they were not needed as independent clinical evidence. Reopening the product page/catalog after context compaction confirmed the same details rather than filling a new evidence gap.

The HP product page contains a material internal contradiction: its heading/formulation specifies niacinamide 4% / tretinoin 0.1%, but its descriptive paragraph names Aluris LP Plus and tretinoin 0.025%. The catalog resolves the variant mapping, and the user's reported label independently matches HP. Preserve this conflict in any future product record instead of copying the erroneous paragraph as HP instructions.

Catalog mapping:

| Product | Code | Tretinoin | Niacinamide | Additional listed ingredient |
| --- | --- | --- | --- | --- |
| Aluris LP Plus | 011032 | 0.025% | 4% | Hyaluronic acid sodium salt 0.5% |
| Aluris Plus | 011034 | 0.05% | 4% | Hyaluronic acid sodium salt 0.5% |
| Aluris HP Plus | 011035 | 0.1% | 4% | Hyaluronic acid sodium salt 0.5% |

HP is also identified as formerly Oxiazar Cream, NDC 72934-2569-02, in a 30 g airless pump. The active-ingredient label may omit hyaluronic acid because it is a vehicle ingredient; the catalog documents it. Full excipient lists for both compounds were not established, so do not assert vehicle equivalence or that the old blend lacks hyaluronic acid.

## Interpretation and improvements for the next agent

- Treat concentration and application frequency as separate variables. A fivefold increase from 0.02% to 0.1% does not imply fivefold benefit or permit calculating an equivalent weekly schedule by multiplication.
- The 1995 trial concerns photoaging with different formulations and a 0.025% comparator. It is not a head-to-head test of these two compounded products, of 0.02% twice weekly, or of hormonal-acne outcomes. Similar observed improvement does not establish universal equivalence for every indication or regimen.
- In the tretinoin profile, “benefits scale with irritation” conflicts with the immediately following dose-comparison finding. Recommend clearer wording that greater irritation did not produce greater observed photoaging benefit in that study. Avoid extrapolating this to all strengths and endpoints.
- HP keeps niacinamide at 4%, raises tretinoin substantially, and removes the declared azelaic-acid component. Hyaluronic acid supplies hydration rather than replacing azelaic acid's treatment role. A separate azelaic product may preserve that role, but its need depends on the rest of the current regimen.
- For a person currently tolerating 0.02% only twice weekly, discuss the reason for jumping to 0.1% with the prescriber. Increasing tolerated frequency or considering an intermediate strength is a reasonable discussion, not a proven superior regimen or an instruction to override the dermatologist.
- This is a compounded product. FDA registration of a 503B facility and possession of an NDC are not FDA approval of the finished medication. Ingredient evidence should not become an unsupported claim that this branded compound is clinically superior to other tretinoin formulations.
- A useful product record should include variant aliases, identifiers, dated sources, explicit source conflicts, known actives, separately declared vehicle ingredients, and unknown excipients. This would prevent repeated brand searches and incorrect strength selection.

Only this feedback file was created. No underlying product, ingredient, study, or cache files were changed.
