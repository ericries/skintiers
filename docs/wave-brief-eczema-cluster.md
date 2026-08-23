# Wave brief: eczema / atopic-dermatitis cluster (+ next waves)

**Purpose:** quota-efficient parallel drafting for a fresh session (subagents + workflows
available, context < 150k). This session (3e441cba) exhausted the 200-agent cap and is at
>150k context, so it grinds sequentially and expensively — do NOT run the wave here.

**Pattern (product-drain wave):** one Sonnet drafter per product (parallel) → Opus critic
verifies quotes/composition/price against the REAL source → Sonnet fix → publish at the
critic's verdict. One item per agent, flat inputs, pass the setid/URL (don't ask the agent
to rediscover identity). Resolve queue items by EXACT queued name after publish.

**Global rules (all agents):** DailyMed = durable primary (quote active/purpose/uses/inactives
verbatim, no cache needed). Product-specific evidence ONLY; link general ingredient science
out in one clause ([[colloidal-oatmeal]], [[atopic-dermatitis]], [[ceramides]] all exist).
Separate HEALTH grade (labeled OTC use) from COSMETIC grade. When in doubt, LEAVE IT OUT —
never invent a price/%/claim. Keep status:draft until the Opus critic returns verdict publish;
record each review in data/review-log.yaml. Match the voice/structure of
data/products/selsun-blue-itchy-dry-scalp-pyrithione-zinc.md (a DailyMed-based page).

## Wave 1 — eczema products (VERIFY each setid's page title matches the active before drafting;
DailyMed search titles are unreliable — confirm on the live page)

Re-resolve setids fresh with:
`curl -sL "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=<name>&pagesize=6"`
then open each candidate's drugInfo.cfm?setid=... and read the ACTUAL <title> + Drug Facts active.

1. **CeraVe Itch Relief Moisturizing Lotion** — active **pramoxine hydrochloride 1%** (external
   analgesic), inactives include ceramides NP/AP/EOP + shea butter. Confirmed setid family
   7c78d980-fc94-498c-aec5-464c0c76c8f4 (verify live). Slug: cerave-itch-relief-moisturizing-lotion.
   Queue name: "CeraVe Itch Relief Moisturizing Lotion (pramoxine 1%)".
2. **Eucerin Eczema Relief (Body) Cream** — active **colloidal oatmeal 1%** (skin protectant).
   setid 9895f3c3-b00b-462c-ace0-696d688e2e04 (verify). Slug: eucerin-eczema-relief-cream.
   Queue name: "Eucerin Eczema Relief Cream (colloidal oatmeal 1%)".
3. **Aveeno Eczema Therapy (Nighttime) Itch Relief Balm** — active **colloidal oatmeal 1%**.
   setid e3350a8f-b983-7c4d-e053-2a95a90a53f5 (verify). Slug: aveeno-eczema-therapy-itch-relief-balm.
   Queue name: "Aveeno Eczema Therapy Itch Relief Balm (colloidal oatmeal 1%)".
4. **Aveeno Skin Relief Moisturizing Lotion (fragrance-free)** — IDENTITY WARNING: search
   returned a "(DIMETHICONE) LOTION" title but the setid served a different SPL on 2026-08-22.
   Re-resolve by name and confirm the ACTUAL active (dimethicone skin-protectant vs pramoxine)
   before drafting; name the page to match what the label actually is.
   Queue name: "Aveeno Skin Relief Moisturizing Lotion (colloidal oatmeal, fragrance-free)".

Then: **pramoxine** ingredient page (topical anesthetic/antipruritic; backs #1 and any pramoxine
products) and a **`atopic-dermatitis-treatments-by-evidence`** tier list on the existing
atopic-dermatitis hub (emollients/colloidal oatmeal as maintenance; topical corticosteroids +
calcineurin inhibitors [[pimecrolimus]]/[[tacrolimus-topical]] as the Rx anti-inflammatory
first-line named above OTC, mirroring the psoriasis hub pattern).

## Wave 2 — ingredients that back EXISTING tier lists (highest leverage)
- Antidandruff list: Ketoconazole (topical), Zinc pyrithione, Selenium sulfide (topical),
  piroctone-olamine, ciclopirox — each with FDA monograph + the Cochrane/Farris evidence linked out.
- Psoriasis list: Calcipotriene (vitamin D analog, first-line), Tapinarof — then UPGRADE the
  psoriasis tier_list to include the Rx first-line, not just OTC.

## Wave 3 — product breadth (62 pending): CeraVe/LRP/Vichy/Bioderma/Paula's Choice/Vanicream,
lighter research each, DailyMed where OTC.
