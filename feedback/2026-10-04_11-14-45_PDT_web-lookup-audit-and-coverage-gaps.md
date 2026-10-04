# Web lookup audit and coverage gaps

Recorded: 2026-10-04 11:14:45 PDT (America/Los_Angeles; UTC−07:00)

## Purpose and limitations

The user requested local sources wherever possible and a record of external lookups for eventual creator feedback. This is a retrospective summary of the relevant lookups in our skincare discussion, not a complete network-request log. It distinguishes new coverage from verification of information already available locally.

## COSRX peptides: redundant verification

- The local `data/products/cosrx-6-peptide-skin-booster-serum.md` already identifies all six peptides, including copper tripeptide-1, and supports the answer that the main Matrixyl variants are absent.
- I nevertheless searched and opened the official COSRX listing: https://www.cosrx.com/products/the-6-peptide-skin-booster-serum-mini-50ml . I also searched The Ordinary's official multi-peptide/copper serum as a possible alternative, although the final answer did not require a product replacement.
- Classification: excessive verification/expansion by the answering assistant, not a missing local ingredient record. No request to add duplicate COSRX research is warranted solely because I browsed.
- At the later cache inspection, the exact-URL cache paths for the COSRX main serum URL and the mini URL were absent. This does not mean the local product profile lacked composition information, or that every possible alternate cached URL was checked.

## Cos De BAHA AZ15: missing product coverage

- A targeted search found the local AZ20 profile, but no AZ15 or AZ12 profile in `data/` or a relevant matching source in `research-cache/web/`.
- I used the manufacturer's AZ15 pages to confirm its labeled 15% azelaic acid and declared formula:
  - https://cosdebahaofficial.com/products/az15
  - https://www.cosdebaha.com/products/15-azelaic-acid-high-strength-serum-with-msm-for-acne-hyperpigmentation-skin-clarity-30ml
- Classification: a useful product-coverage addition would be AZ15, with current ingredients and a clear distinction between manufacturer claims and clinical evidence for prescription azelaic formulations.
- The user also wrote "AZ12." I could not verify that identity and asked whether it meant AZ20. Do not silently create or assume an AZ12 product, and do not treat the absence of search results as proof that it cannot exist.

## Glycolic acid: local evidence plus additional external references

- Local profiles already cited Ditre 1996 and Stiller 1996. Opening their abstracts was verification of existing references, not discovery of a missing ingredient evidence base:
  - https://pubmed.ncbi.nlm.nih.gov/8642081/
  - https://pubmed.ncbi.nlm.nih.gov/8651713/
- Additional references encountered externally were not located in the targeted local searches of data, cache, and docs:
  - Bernstein 2001: https://pubmed.ncbi.nlm.nih.gov/11359487/
  - DiNardo 1996: https://pubmed.ncbi.nlm.nih.gov/8634803/
  - A 2020 skin-explant study: https://pubmed.ncbi.nlm.nih.gov/32583600/
- These are candidates for review, not automatically missing prerequisites for a useful recommendation. Preserve the distinctions between live-human outcomes, collagen markers, and explant findings.
- FDA AHA sun-sensitivity guidance was checked externally: https://www.fda.gov/cosmetics/cosmetic-ingredients/alpha-hydroxy-acids . I have not established in this audit whether an equivalent complete local copy exists; classify it as external guidance verification rather than a proven database gap.

## Salicylic acid and azelaic acid: clinical verification

- Local ingredient and study profiles supplied the main efficacy context.
- I also checked AAD acne guidance and the published guideline:
  - https://www.aad.org/public/diseases/acne/derm-treat/treat
  - https://www.aad.org/member/clinical-quality/guidelines/acne
  - https://pubmed.ncbi.nlm.nih.gov/38300170/
- Azelaic rosacea trial evidence was also checked through https://pubmed.ncbi.nlm.nih.gov/12789172/ during the discussion. An existing local randomized-trial summary, `data/studies/elewski-2003-azelaic-acid-15-vs-metronidazole-0-75-rosacea-rct.md`, supplied further context.
- Classification: clinical verification of an evidence base already represented locally. Do not count each external visit as evidence that the directory failed to cover the subject.

## Recommended practice for future feedback

For each material external lookup, record the question, local files searched, exact remaining uncertainty, source visited, what it added, and whether the issue belongs to coverage, freshness, source availability, or assistant retrieval. A brief grouped audit is preferable to repeatedly restating every routine verification.

No new web lookup was performed to write this note. No underlying research files were changed.
