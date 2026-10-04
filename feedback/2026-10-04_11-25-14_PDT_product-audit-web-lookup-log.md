# Product audit: web lookup log and lessons

Recorded: 2026-10-04 11:25:14 PDT (America/Los_Angeles; UTC−07:00)

The user explicitly asked that every needed web search become feedback for the creator, with reflection after each iteration. The entries below account for the external lookups in this product-audit iteration, including repeated requests and a failed opening. Brand pages establish declared formulation and manufacturer instructions, not independent clinical effectiveness.

## 1. Anua cleansing oil and peach serum: missing exact local product coverage

Local work: searched product filenames, profile text, and cached web material. The only relevant-looking cache hit was an Anua Rice Milk page with references to other products. No dedicated oil or peach-serum profile was located.

Opened:

- https://pages.anua.com/products/heartleaf-pore-control-cleansing-oil-200ml
- https://pages.anua.com/products/peach-70-niacinamide-serum-30ml

The oil page supplied the full declaration, including fragrance and its cleansing esters/oils. The peach page supplied a labeled 5% niacinamide concentration and the declaration containing humectants, alpha-arbutin, betaine salicylate, lactobionic acid, a vitamin C derivative, ceramide NP, and fragrance. Most supporting concentrations are unspecified, so their presence should not be graded as if each were a separate full-strength treatment.

A subsequent `find` on the peach page extracted the relevant concentration and ingredient section. This was navigation within the same source, not discovery of another independent source. Both official pages had also been visited earlier in the broader conversation; their missing local coverage does not make every repeat visit necessary.

Suggested feedback: add the two exact product profiles if useful to the directory's scope, with aliases, formulation date/region, and source pointers. Label brand percentages as declarations and keep tolerability inferences distinct from observed reactions.

## 2. Prequel Lucent-C: suitability guidance and a local contradiction

Opened https://prequelskin.com/products/lucent-c-vitamin-c-serum, then used `find` for its pH and surrounding instructions.

Local context: the individual product profile describes 15% L-ascorbic acid at pH 3.2, without vitamin E; `best-vitamin-c-serums-by-evidence.md` incorrectly describes it as including vitamin E.

The official declaration supports the individual profile on the absence of vitamin E. Its usage disclaimer also advises against the product for diagnosed rosacea, eczema, or psoriasis. That changed its suitability as a proposed default replacement in this case. The brand reports an eight-week study with 31 female subjects, but the page does not establish a controlled comparison against the user's existing serum.

Suggested feedback: reconcile the list, add the relevant manufacturer suitability guidance with attribution, and preserve the distinction between stronger ingredient evidence and a better choice for this individual. One page opening with targeted extraction could have combined the two requests more efficiently.

## 3. The Ordinary copper serum: ingredient breadth versus routine fit

Used `find` on https://theordinary.com/en-us/multi-peptide-copper-peptides-1-serum-100625.html for pairing guidance, then for the ingredient list.

The local profile already establishes copper tripeptide-1, Matrixyl 3000 peptides, and palmitoyl tripeptide-38. The manufacturer's current page confirms them and lists pairing restrictions involving direct acids, direct vitamin C, retinoids, and certain antioxidants.

What this added: the pairing guidance affects whether the serum is a convenient replacement in the existing routine. It does not establish a clinically proven dangerous interaction for all copper-peptide products. The second ingredient check mostly repeated information already present locally and previously confirmed in the conversation.

Suggested feedback: include dated manufacturer pairing instructions separately from evidence-based interaction claims. Do not score an ingredient-rich replacement without checking whether it disrupts better-supported treatments.

## 4. SkinCeuticals C E Ferulic: current identity and possible reformulation

An attempted opening of https://www.skinceuticals.com/skincare/vitamin-c-serum/c-e-ferulic-with-15-percent-l-ascorbic-acid/S17.html returned an access error. This was not evidence that the product was discontinued or absent.

A targeted official-domain search for the product and its three concentrations returned the current address:

https://www.skinceuticals.com/skincare/vitamin-c-serums/c-e-ferulic-with-15-l-ascorbic-acid/S17.html/

The official results confirm the 15% L-ascorbic acid, 1% vitamin E, and 0.5% ferulic acid combination already described locally. Some official result excerpts also describe an enhanced formula with carnosine and another added ingredient. I did not complete a full ingredient/version audit of that enhanced formula; this is a flagged follow-up, not a verified historical formulation timeline.

Suggested feedback: verify the current version and distinguish evidence for the established antioxidant combination and older studied formula from evidence for a newly revised finished product. The failed URL plus search could have been avoided by better versioned source links, although a live formulation check can still be warranted when recommending a purchase.

## Reflection and next-iteration workflow

The local profiles supplied most of the audit. The useful external additions were exact missing product declarations, manufacturer suitability/pairing guidance, and a possible formulation update. Some repeat checks added little. Before a future lookup, identify the precise unresolved fact; after it, record the result here without classifying every lookup as a directory failure. Prefer one targeted retrieval per source and reuse the retrieved material during the iteration.

The original source cache was not modified; only feedback notes were written, consistent with the user's authorization.
