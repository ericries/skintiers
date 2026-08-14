# Routine strength spec (canonical)

**This is the single source of truth for how SkinTiers scores a routine.** The browser
Routine Builder (`assets/routine-builder.js`, function `computeDashboard`) and the build-time
rollup (`build.py`, function `routine_summary`) both implement this algorithm, and the
installable agent skill (`skill/SKILL.md`) tells an agent to replicate it inline. If any of
those three disagree with this document, this document wins and the code is the bug.

> Maintenance note: `assets/routine-builder.js` and `build.py:routine_summary` do not yet
> literally read this file — they hardcode the same numbers. Keep them in lockstep with this
> spec, and prefer changing this spec first. A drift test lives in `tests/test_skill_bundle.py`.

The scores are a **summary of the graded products in a routine, not a clinical trial of the
routine as a whole.** Say so when you present them.

---

## Inputs

Per product you need two things, both of which come straight from the product page's YAML
frontmatter (see `skill/SKILL.md` for the schema and where to fetch it):

1. `grades:` — a list of `{effect, evidence, use}` rows.
2. `key_actives:` — a list of ingredient slugs the author declared as the product's actives.

The pre-computed machine-readable form is `routine-catalog.json`, whose `p[code]` carries the
already-derived `g` (effect segments 0–4) and `a` (active slugs) so a client need not re-read
markdown. Working from raw markdown gives the same answer if you follow steps 1–2 below.

---

## Step 1 — Per-product effect strength (0–4)

Effect words map to filled segments out of four:

| effect word | segments |
|-------------|----------|
| none        | 0 |
| minimal     | 1 |
| modest      | 2 |
| notable     | 3 |
| strong      | 4 |

A product's effect strength is the **best HEALTH effect** among its grades:

1. Select grades whose `use` contains the literal `(health)`.
2. If none are health-labeled, fall back to **all** grades.
3. Take the single highest `effect` segment value from that pool.
4. A product with no grades scores **0**.

Use effect only. Do **not** apply the evidence-quality demotion here — that demotion is used
for the per-ingredient *tier lists*, not for routine strength. (This is deliberate: the
Routine Builder reads the pre-derived `g` value, which is effect-only.)

## Step 2 — Routine strength label

Compute the **mean** of the per-product effect strengths across the **distinct** products in
the routine (deduplicate; a product listed in both AM and PM counts once). Map the mean:

| mean effect segments | label    |
|----------------------|----------|
| ≥ 3.0                | Strong   |
| ≥ 2.25               | Solid    |
| ≥ 1.5                | Moderate |
| < 1.5                | Light    |

An empty routine has mean 0 → Light (or simply report "no products yet").

## Step 3 — Actives covered

Take the **union of `key_actives`** across the distinct products. For each active, `count` =
how many distinct products in the routine carry it (so a layered active reads "×2", "×3").
A product with no `key_actives` contributes nothing. Present non-filter actives most-layered
first, then alphabetically.

## Step 4 — Sunscreen coverage

An active is a **UV filter** if it appears in the site's UV-filter table (in the catalog it is
an ingredient `i[slug]` carrying a band field `f` of `uvb`, `uva`, or `both`). Collect the
filters present and report coverage as the union of bands:

- any filter reaching below 320 nm → **UVB**
- any filter reaching above 320 nm → **UVA**
- coverage string: `"UVB + UVA"`, or a single band, or `"UV"` if a filter is present but
  unbanded.

If the routine has no filters, sunscreen is **absent** — call that out, because daily
broad-spectrum sunscreen is the single most evidence-backed step.

## Step 5 — Notable actives NOT present (informational)

For each notable-active family, report it as absent if **none** of its member slugs are
present in the routine. This is informational (a neutral "does not contain" line), not a flaw.

The notable families (label → member slugs), from `_NOTABLE_ACTIVES` in `build.py` and the
`notable` array in `routine-catalog.json`:

| label       | member slugs |
|-------------|--------------|
| Retinoid    | retinol, retinaldehyde, adapalene, tretinoin, retinyl-esters, retinyl-retinoate, bakuchiol |
| Vitamin C   | ascorbic-acid-vitamin-c, vitamin-c |
| Niacinamide | niacinamide |
| Exfoliant   | salicylic-acid, glycolic-acid, lactic-acid, mandelic-acid |

Treat this list as data: read the live `notable` array from `routine-catalog.json` rather than
memorizing it, so you stay in sync as the site evolves.

---

## Worked example

Routine: CeraVe Foaming Cleanser (AM+PM), The Ordinary Niacinamide 10% + Zinc 1% (PM),
La Roche-Posay Anthelios SPF 60 (AM).

1. Per-product effect (illustrative — read the live grades):
   - Foaming cleanser: best health effect `minimal` → 1
   - Niacinamide serum: best health effect `modest` → 2
   - Anthelios sunscreen: best health effect `notable` → 3
2. Mean = (1 + 2 + 3) / 3 = **2.0** → **Moderate**.
3. Actives union: niacinamide (×1), zinc, + sunscreen filters.
4. Filters present (avobenzone/homosalate/…) → coverage **UVB + UVA**, sunscreen **present**.
5. Absent notable families: **Retinoid, Vitamin C, Exfoliant** (none present) — informational.

Result to present: *"Moderate strength (a summary of the graded products, not a trial of the
routine). Sunscreen present with UVB + UVA coverage. Niacinamide covered. No retinoid,
vitamin C, or exfoliant — add one if your goals call for it. Every number links back to the
product and ingredient pages it came from."*
