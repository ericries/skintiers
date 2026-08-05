# Tier Lists / Rankings — Design Spec

**Goal:** Render sets of comparable items (products, ingredients) as visual, evidence-derived tier lists —
the feature the site is named for — reusing the grades the site already computes so a tier list never drifts
from the evidence and needs no separate ranking to maintain.

## Decisions (confirmed with user, 2026-08-04)
- **Tier source:** evidence-derived by default (from each item's existing grade), with an optional per-item
  manual override for special axes. Update a grade once and every tier list re-sorts.
- **Tier labels:** evidence words, not letters — **Top-evidenced / Strong / Moderate / Minimal** (+ **Unrated**
  for items with no graded signal), matching the site's evidence language.
- **Scope:** both the "best of" list pages AND topic/ingredient hubs (e.g. a "Retinoids by evidence" tier at
  the bottom of the retinoids page).

## Architecture
Static HTML/CSS, no JS (consistent with the rest of the site). A `build.py` function computes the tier model
from a page's new `tier_list:` frontmatter; a `profile.html` section renders it, reusing the existing tier
colors (`--tier-best/good/mid/weak`), the product/ingredient badges (`gen_icon` / photo thumb), and the
evidence badge. It slots in next to `routine_summary` / `routine_catalog` as another data-derived view.

## Schema — `tier_list:` frontmatter (any page: list, ingredient, goal)
```yaml
tier_list:
  title: "Retinoids by evidence"          # optional; omitted → no heading override
  by: "overall evidence for photoaging"   # optional one-line criterion caption
  items:
    - tretinoin                           # bare slug → tier auto-derived
    - slug: bakuchiol
      note: "gentle, lower-evidence alternative"   # optional one-line rationale
      tier: minimal                       # optional manual override (top|strong|moderate|minimal)
```
An item is either a bare slug string or a mapping `{slug, note?, tier?}`. Unknown/unpublished slugs are
skipped (surfaced in a returned `missing` list), never breaking the build.

## Tier derivation — `entity_tier(target_profile)` → tier key or None
Precedence (first that applies):
1. The `tier_list` **item's own `tier:`** override, if present (accepts `top|strong|moderate|minimal`,
   mapped to keys `best|good|mid|weak`).
2. A page-level **`tier:`** frontmatter field on the target (a machine-readable summary tier; how ingredient
   hubs, which grade in prose with no `grades:` block, participate — see below).
3. Derived from the target's **`grades:`** (products): take the best HEALTH grade's `effect` via `EFFECT_SEGS`
   (none 0 … strong 4); **demote one segment** if that grade's `evidence` is `anecdotal` or `preliminary`
   (so a strong-effect / thin-evidence item can't sit in the top tier); then map
   `>=4 → best (Top-evidenced)`, `3 → good (Strong)`, `2 → mid (Moderate)`, `<=1 → weak (Minimal)`.
4. Otherwise **None → Unrated**.

**Ingredient tiers (the prose-rubric wrinkle):** ingredient pages use the prose `## The Rubric`, not a
`grades:` block, so step 3 can't fire for them. They participate via an optional page-level **`tier:`**
frontmatter field (step 2) — a single summary tier reflecting the rubric's overall verdict. This spec adds
that field to the retinoid family (tretinoin, adapalene, retinaldehyde, retinol, bakuchiol) as the first
topic tier list; going forward the ingredient drafter/critic sets `tier:` when filling an ingredient page.
Products need no new field (step 3 covers them).

## Rendering — `tier_list_view(profile, by_slug)` → model
Returns `{title, by, tiers: [{key, label, items: [{slug, name, badge_html, evidence?, note?}]}], missing: []}`.
- Tiers appear in fixed order: Top-evidenced → Strong → Moderate → Minimal → Unrated; empty tiers omitted.
- Within a tier, items sort by effect segs desc when available (products), else keep the declared
  frontmatter order (ingredient hubs, which have no numeric effect) — so an author's intended order holds.
- `badge_html` reuses the product photo thumb when present, else `gen_icon(slug, monogram, name)`.
- `evidence` is the item's evidence badge label (from `EVIDENCE_MAP`) when derivable, for the quality axis.
- The `profile.html` template renders a `<section class="tierlist">` when `tier_list` is present: a heading
  (`title` + `by` caption), then one labelled row per tier (label chip in the tier color, items as linked
  badge + name + evidence badge + note).

## Consumers (this phase)
- **Best-of list pages:** add `tier_list:` to `best-vitamin-c-serums` and `best-peptide-serums` (their picks;
  the existing prose stays as the rationale). The queued ranking lists (retinoid potency, moisturizing,
  glass-skin) become tier-list pages via the same field, filled by the list cron.
- **One topic hub:** the retinoids ingredient page gets a `tier_list:` of the retinoid family, using the new
  page-level `tier:` fields. (Sunscreen/moisturizing hubs are an identical fast-follow.)

## Error handling
- Unknown/unpublished item slug → skipped + reported in `missing` (page still builds).
- Item with no derivable tier and no override → Unrated tier (honest, not hidden).
- `tier_list` absent → the section simply doesn't render.

## Testing
- `entity_tier`: grades → tier mapping; the evidence demotion; page-level `tier:` and item override precedence;
  Unrated fallback.
- `tier_list_view`: tier grouping + within-tier ordering; a bare-slug and a `{slug,note,tier}` item; a missing
  slug lands in `missing`.
- Build test: a page with `tier_list:` renders `<section class="tierlist">` with the right tier labels + a
  linked item; a page without it renders no such section.

## Files
- Modify `build.py`: `entity_tier(profile)`, `tier_list_view(profile, by_slug)`; pass `tier_list` to the
  profile render.
- Modify `templates/profile.html`: the `tierlist` section.
- Modify `static/style.css`: `.tierlist` styles (reusing tier color vars).
- Modify data: `tier_list:` on the two best-of lists + the retinoids page; page-level `tier:` on the five
  retinoid ingredient pages.
- Modify `tests/test_build.py`: the three test groups above.

## Out of scope (fast-follow, not this spec)
Sunscreen/moisturizing/glass-skin topic tiers; an automatic products-in-a-category tier on every category
listing; the ingredient drafter/critic setting `tier:` routinely (documented, applied to retinoids here).
