# Adapting the Pattern to Your Topic

Seedlist tracks investors. Your project (this one is set up for skincare) tracks something different. Same infrastructure, different schema. This doc walks you through the design decisions you need to make BEFORE writing any code or data.

## Step 1: Identify your entity types

Seedlist has three:
- **Firms** (VC funds)
- **Individuals** (partners, angels)
- **Startups** (portfolio companies)

Every topic has 2–4 entity types with cross-references between them. Some possibilities:

| Topic | Entity types |
|-------|-------------|
| Skincare | Brands, Products, Ingredients, Formulators, Dermatologists |
| Restaurants | Restaurants, Chefs, Dishes, Cuisines, Critics |
| Board games | Games, Designers, Publishers, Mechanics, Reviewers |
| Academic labs | Labs, PIs, Papers, Techniques, Funders |
| Music | Artists, Labels, Songs, Producers, Venues |
| Fitness | Programs, Coaches, Exercises, Studios, Athletes |

**Ask the user:** which entity types are core vs derived? Which one is the "primary" (the thing readers most often browse to)? For Seedlist that's the individual investor. For skincare it could be brands, products, or ingredients depending on the reader's mental model.

## Step 2: Decide the primary entity

The primary entity is the star of the show. It gets:
- The richest schema (most frontmatter fields)
- The longest profile (most required sections)
- The most rigorous verification
- The primary landing page and navigation

Seedlist's primary is **Individuals**. Firms and Startups exist mostly to feed investor discovery.

For skincare, ask the user: is it Brands (people follow brands) or Ingredients (readers ask "what actually works")? The answer changes the whole schema.

## Step 3: Define the primary signal

Every profile has a **Stated Thesis** (what the entity says publicly) and an **Inferred Thesis** (what the data actually shows). The delta is where the value lives.

- Seedlist: Stated = "we back technical founders in fintech." Inferred = counted portfolio actually shows 48% consumer, 12% fintech. The delta is the story.

- Skincare analog for a brand: Stated = "we're clean beauty." Inferred = counted products show 34% contain fragrance, 8% contain formaldehyde releasers. The delta is the story.

- Skincare analog for an ingredient: Stated (per the ingredient's marketing) = "clinically proven to reduce wrinkles." Inferred = 2 of 8 peer-reviewed studies show statistically significant effect. The delta is the story.

**Design question for the user:** What is the "portfolio equivalent"? What data will you count to compute the Inferred X?

## Step 4: Design the frontmatter schema

Start minimal. Add fields when you have a concrete use for them (rendering, sorting, filtering, cross-reference). Do NOT design a maximalist schema up front.

Example minimal starter schema for a skincare brand:

```yaml
---
name: "The Ordinary"
slug: the-ordinary
type: brand
website: "https://theordinary.com"
parent_company: "DECIEM"
founded: 2016
country: Canada
sector: [budget-serums, active-ingredients]
product_count_estimate: 65
last_researched: 2026-07-30
status: draft   # draft | published | flagged
---
```

And for a product:

```yaml
---
name: "Niacinamide 10% + Zinc 1%"
slug: the-ordinary-niacinamide-10-zinc-1
type: product
brand: the-ordinary
category: serum
launched: 2016-11
price_usd: 6
size_ml: 30
key_ingredients:
  - niacinamide
  - zinc-pca
inci_url: "https://..."
last_researched: 2026-07-30
status: draft
---
```

Every cross-reference (`brand: the-ordinary`, `key_ingredients: [niacinamide]`) must correspond to an existing file OR be tracked in the queue.

## Step 5: Define required body sections

Every profile has a required section list. Seedlist's investor profile requires:
1. Background
2. Stated Thesis
3. Inferred Thesis (PRIMARY signal)
4. Portfolio (table with citations)
5. In Their Own Words (verified quotes)
6. What Founders Say (independently sourced quotes)
7. Connections (optional)
8. Sources (footnotes)

Analog for a skincare **brand** profile:
1. About (history, ownership, story)
2. Stated Positioning
3. Inferred Positioning (based on counted product data)
4. Product Catalog (table)
5. In Their Own Words (founder/CEO/formulator quotes)
6. What Users Say (independently sourced reviews from dermatologists / peer-reviewed comparisons)
7. Regulatory History (recalls, FDA warnings, EU compliance issues)
8. Sources

Analog for an **ingredient** profile:
1. About (INCI name, chemistry, discovery)
2. Claimed Benefits (per the industry)
3. Evidence Review (peer-reviewed studies, meta-analyses)
4. Products Containing It (table, sorted by concentration)
5. Safety Profile (known interactions, contraindications, EU/FDA status)
6. In the Words of Researchers (verified quotes from study authors)
7. Sources

**Ask the user** to confirm each section list before you write any profile. Section-list mistakes cascade into re-writes.

## Step 6: Decide your freshness feed source

What's the daily "new stuff" for your topic?
- Seedlist: funding round announcements (Axios Pro Rata, TechCrunch, Crunchbase News).
- Skincare launches: brand press releases, Beauty Independent, Cosmetics Business, WWD, Retail Bum, Byrdie.
- New peer-reviewed skincare studies: PubMed RSS filtered by MeSH terms, Cochrane, JAMA Dermatology feeds.
- Regulatory actions: FDA warning letters, EU Cosmetics Notification Portal, Health Canada recalls.

**Ask the user** which feeds to include. Then confirm the source is authoritative and machine-parseable before wiring it in.

## Step 7: Decide your taxonomy

Seedlist has `sector_focus` (fintech, developer-tools, etc.) with a parent-category roll-up in `data/sector-taxonomy.yaml`.

Skincare could have:
- `concern` taxonomy: acne, hyperpigmentation, aging, dryness, rosacea, sensitivity
- `mechanism` taxonomy: exfoliant, antioxidant, humectant, occlusive, retinoid, peptide
- `formulation` taxonomy: serum, cream, cleanser, mask, mist

Design questions:
- Which taxonomies are needed for the browse UI?
- What's the roll-up (parent categories)?
- What's the naming convention (kebab-case)?
- Where do new tags get added when a profile invents one?

## Step 8: Design the queue schema

Copy Seedlist's queue.yaml pattern:
```yaml
queue:
  - name: "Ingredient or Brand Name"
    type: ingredient    # or brand, product, etc.
    source: "how this lead was found"
    discovered_from: slug-of-profile
    discovery_depth: 1
    priority: normal    # high | normal | low
    status: pending
    added: 2026-07-30
```

## Step 9: Decide what NOT to include

Seedlist doesn't cover: LP relationships, exit multiples, IRR, personal history beyond career.

Ask the user for your topic: what's out of scope? Some skincare examples:
- Individual person's routines (privacy)
- Anecdotal Reddit reviews (unreliable)
- Ingredient concentrations below labeled minimums (unverifiable)
- Pricing (changes constantly)

Document scope decisions in `CLAUDE.md`. Every out-of-scope item saves future rework.

## Step 10: Confirm everything with the user before writing

**Do NOT** start authoring profiles until the user has confirmed:
- [ ] Entity types (and which is primary)
- [ ] Primary signal (what "inferred X" means)
- [ ] Frontmatter schema for each entity type
- [ ] Required body sections for each entity type
- [ ] Freshness feed sources
- [ ] Taxonomies
- [ ] Queue schema
- [ ] Out-of-scope list

Schema changes after the first 20 profiles are painful. Get it right up front.

## Once schema is confirmed

Move to `10_CHECKLIST_FIRST_WEEK.md`. Follow the sequence.
