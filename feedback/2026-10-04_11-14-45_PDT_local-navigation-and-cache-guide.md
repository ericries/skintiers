# Local navigation and cache documentation

Recorded: 2026-10-04 11:14:45 PDT (America/Los_Angeles; UTC−07:00)

## Context and scope

The user is using this directory to support iterative, science-backed skincare recommendations. They prefer local sources and want external lookups recorded so the directory's creator can distinguish missing data from retrieval mistakes. They authorized creating `feedback/` and writing feedback here; they have not authorized changes to the underlying data, tooling, or documentation.

The directory was sufficient to answer whether COSRX The 6 Peptide Skin Booster contains copper peptides or Matrixyl. My repeated web lookups were excessive for that question. Navigation improvements would help future readers, but do not excuse that retrieval mistake.

## Verified findings

1. **The root entry points are stale.** `README.md` describes the project as not yet built and says the data and scripts directories are empty. Much of `CLAUDE.md` still directs a reader through bootstrap instructions. These are poor entry points for someone consuming the existing research.
2. **A reader guide and catalogs already exist.** `skill/SKILL.md` explains the schema and public JSON endpoints. Local generated copies include `_site/routine-catalog.json`, `_site/products-filter.json`, and `_site/skill/endpoints.json`. Build on this infrastructure instead of creating a competing guide. The skill emphasizes public URLs and does not explain the local source-cache workflow.
3. **Catalog ingredients are incomplete for composition questions.** The COSRX entry in `_site/routine-catalog.json` has `a: ["peptides"]`. Its Markdown profile names the six individual peptides. The catalog can locate the product, but absence of a specific peptide from `key_actives` cannot establish absence from the formula.
4. **Long YAML metadata can hide the main evidence text.** At inspection, `data/ingredients/azelaic-acid.md` contained 241 metadata lines before its body, and `data/goals/anti-aging.md` contained 304. Many of these lines describe videos. Reading only the first screen or first 100 lines can miss the evidence discussion. Video commentary remains useful, but should be discoverable separately from the main research synthesis.
5. **The cache guide is out of sync with the tool.** `docs/research-cache.md` describes descriptive web filenames and manual storage. `scripts/source_cache.py` actually computes a 16-character SHA-1 prefix from the exact stripped URL and offers `get <url>`. Its generated header records URL, key, and content length, but not a capture timestamp.
6. **Primary-source text may intentionally be absent locally.** `source_cache.py` excludes domains classified as primary, including PubMed and government sources, on the assumption that they can be fetched again. Therefore, a cited paper may have a local synthesis without a cached abstract or full text. This is a source-availability limitation, not absence of evidence from the directory.

## Suggested improvements

- Add a short, authoritative local-reading section to the existing reader guide and link it from the root documentation. Map composition questions to product profiles, efficacy questions to ingredient/study profiles, and verification to the cited source or cached copy.
- Explain that `data/` contains authored profiles, `_site/` contains generated outputs, and a generated catalog may lag its source. Explicitly distinguish `key_actives` from a complete ingredient list.
- Document how to read the Markdown body separately from YAML, and how `[[slug]]` references resolve to profiles.
- Update the cache guide to describe the existing URL lookup. For read-only use without Python bytecode writes: `.venv/bin/python -B scripts/source_cache.py get '<exact-source-url>'`. Distinguish this from commands such as `put`, `gc`, transcript fetching, and `inci_lookup.py`, which can write or access the network.
- Consider a generated source manifest with URL/DOI/PMID, local path, capture date, content type, and completeness: full text, abstract, extracted notes, or unavailable. Include links back to citing profiles. Preserve distinctions between saved source text and an agent's synthesis.
- Include product aliases and regional/version names in discovery metadata. For example, the Anua azelaic profile is `anua-azelaic-acid-serum.md`, rather than the full marketed product name.

A short accurate guide is the first priority. The observed problems do not establish a need for a new search service or a directory reorganization.

## Assistant workflow correction

Read the local product/ingredient profile, follow relevant study references, and check available cached material before deciding what requires external verification. Record whether a web lookup addressed a missing product, missing source text, a formulation/freshness check, or redundant verification. Do not describe an incomplete search as proof that evidence is absent.

## Feedback-file convention

The user requested ongoing Markdown feedback in this folder. Use filenames in the form `YYYY-MM-DD_HH-MM-SS_TZ_short-topic-summary.md`, with the actual local time and timezone abbreviation at creation. Include a full timestamp and timezone in the body. Distinguish verified findings, hypotheses needing verification, suggested changes, and assistant mistakes. Keep entries focused and avoid overwriting an earlier entry to conceal a changed conclusion.

No underlying project changes were made for this feedback. No web searches were used for the directory-layout assessment.
