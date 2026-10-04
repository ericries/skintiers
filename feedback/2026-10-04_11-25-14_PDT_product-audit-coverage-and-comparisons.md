# Product audit: ingredient coverage and comparative judgments

Recorded: 2026-10-04 11:25:14 PDT (America/Los_Angeles; UTC−07:00)

## Task and confirmed identities

The user requested a product-by-product assessment and an assessment of the combined ingredient mix. They confirmed CeraVe Skin Renewing Night Cream and Beauty of Joseon Relief Sun Rice + Probiotics as the exact products. They report good tolerance of the current routine; recommendations must not assume existing irritation merely because rosacea is suspected.

## What the local material supported well

Product profiles made it possible to identify repeated niacinamide, hyaluronic acid, glycerin, ceramides, and soothing ingredients. The confirmed CeraVe cream contributes niacinamide, sodium hyaluronate, glycerin, three ceramides, cholesterol, phytosphingosine, dimethicone, and emollients. COSRX supplies several overlapping humectants and niacinamide as well as its six peptides. These overlaps support simplification without automatically creating an ingredient gap.

Important interpretation: ingredient presence does not establish the delivered dose. Percentages from separately layered products cannot simply be added. A consumer does not need a separate serum for every named ingredient, nor every molecular weight of hyaluronic acid. More ingredient types and more peptide names are not demonstrated clinical advantages by themselves.

## Specific issues for review

1. **Prequel vitamin C contradiction.** `data/lists/best-vitamin-c-serums-by-evidence.md` describes Lucent-C as containing vitamin E. `data/products/prequel-lucent-c-vitamin-c-serum.md` says it does not, and the current official ingredient declaration contains no vitamin E. Reconcile the list with the product profile and source. The official page also explicitly advises against use with diagnosed rosacea, eczema, or psoriasis; this affects suitability even when the ingredient-level vitamin C evidence looks attractive. Do not convert that manufacturer guidance into a universal claim that every person with rosacea cannot tolerate any vitamin C.
2. **Sunscreen comparisons exceed the measurements.** `data/products/dr-g-green-mild-up-sun.md` infers weaker protection from zinc oxide being the only filter, despite reporting SPF50+ PA++++ and no independent test of that finished product. The Beauty of Joseon profile extends a cited comparison with its own US counterpart into broader superiority claims over other US-filter sunscreens. Compare the actual tested products and methods. A filter's identity, concentration, or age is not a substitute for testing the finished formula, and stabilized avobenzone should not be judged solely by the photostability of the isolated molecule.
3. **Peptide breadth is not efficacy.** `data/lists/best-peptide-serums.md` ranks partly on the number/types of peptides. That can describe composition, but should not imply that broader blends have demonstrated better aging outcomes. The Ordinary's copper serum contains the Matrixyl variants absent from COSRX, yet its manufacturer's pairing restrictions also make it less convenient in a routine with vitamin C, tretinoin, and glycolic acid. Store manufacturer guidance separately from clinically demonstrated interactions.
4. **Niacinamide ranking appears sensitive to uneven citation assignment.** `data/lists/best-niacinamide-products.md` gives Some By Mi's 10% product an added oil-control case from a 2% niacinamide moisturizer trial while treating similar claims on other 10% serums as less supported. Review whether the differing grades reflect formulation-specific evidence or simply which profile received a shared ingredient citation. Do not assume any 10% serum was tested in that 2% trial.
5. **Missing exact product records.** No dedicated profile was found for the standard Anua Heartleaf Pore Control Cleansing Oil or Peach 70 Niacinamide Serum. A text hit for their names in the web cache was a large Anua Rice Milk page containing other-product references, not a source record for the requested formula. This illustrates why search hits need source-identity checking.

## Suggested additions to the data model or reader guide

- Record exact product/version/region and distinguish a complete ingredient declaration from selected `key_actives`.
- Make ingredient synonyms explicit, such as sodium hyaluronate under hyaluronic acid, while preserving chemically distinct peptides and vitamin C forms.
- Record known concentrations separately from presence-only evidence; distinguish rinse-off exposure from leave-on use.
- Separate comparative judgments into demonstrated superiority, stronger supporting evidence, a tolerability/texture preference, and an untested alternative.
- Treat a formula change as a versioned event, rather than silently attaching old finished-product trials to a new formula.
- Explain that a well-tolerated moisturizer or cleanser is not automatically improved by a longer ingredient list or higher catalog grade.

No underlying profiles, lists, scripts, or caches were changed. This is feedback for review, not an implemented correction.
