# Morning brief — 2026-07-29

Reader we optimize for: a skincare-forum reader who knows a little, is intimidated by the science, and
wants to sort truth from marketing fast. Site now at **95 published pages**. Newest/most-important first.

## 1. What shipped / changed overnight

**Content (11 stuck/held pages recovered → live):** rosacea overview + type 1 + type 2, atopic-dermatitis,
La Roche-Posay Effaclar Mat, Some By Mi Yuja Niacin, skin-barrier-strengthening, skin-barrier-repair, CeraVe
(brand), Glass Skin, Samantha Ellis. `acne` was fixed part-way (verified "How to know" opener added) but is
**held as a draft** — the critic found real correctness errors and the auto-fix hit the account spend limit.

**Apify wired in and proven:** cracked iHerb/Stylevana/Amazon anti-bot blocks to verify held product figures;
LRP's US page beat even residential proxies, so figures were corroborated on Amazon and the one unverifiable
claim (a named-derm quote) was dropped.

**Reliability tooling (so this can't recur):** `sk audit` + build warning + a five-whys postmortem for the
"drafted-but-never-shipped" leak; a **voice deny-list** in `sk style` (auto-rejects site self-reference /
defensive meta / process language — already caught 2 live violations the critics missed); a per-type
**required-section** WARN in `sk lint` (`## Summary`, "How to know you have this").

**Reader-facing:** a **What's New** page (footer-linked, `sk log` command).

**Overnight passes written:** UX/readability audit, QC sweep (95 pages), five-whys root-cause, tooling report.
(See the other `docs/overnight/2026-07-29-*.md` files.)

## 2. Top 10 highest-leverage moves for today

1. **[needs-your-decision] Build the tier-list format** (at-a-glance tier nav + per-item cards). *Why:* turns
   walls of "Tier 1–4" into a ranking a nervous reader can scan in seconds. Prereq for #2.
2. **[needs-your-decision] Replace bare "See Also" lists with ranked tier lists** (retinoids by potency, etc.,
   your 2026-07-28 request). *Why:* ranked guidance beats an unordered list of names.
3. **[auto-doable] Write `## Summary` for the 8 pre-standard product pages** (now WARN-flagged by `sk lint`).
   *Why:* the summary-first block is how the reader gets the verdict without reading the whole page.
4. **[auto-doable] De-dash the 16 pages, then flip `sk style` to block publish.** *Why:* removes AI-slop
   punctuation and makes the whole class impossible going forward.
5. **[needs-your-decision] Finish `acne`** (held; has known errors). *Why:* acne is the #1 forum topic; needs
   the spend limit raised (or a careful main-loop fix) — it must not ship with the wrong stat.
6. **[auto-doable] Sticky in-page table of contents on long pages.** *Why:* 1,000-word condition/ingredient
   pages become click-navigable instead of a scroll-hunt.
7. **[auto-doable] Trust signal above the fold** ("N sources · last verified <date>"). *Why:* sourcing is the
   whole reason to trust us over a forum thread — surface it.
8. **[auto-doable] Visually separate health vs cosmetic claims** (pill/label, not just prose). *Why:* our core
   value — is this a health effect or a look effect? — should be legible at a glance.
9. **[needs-your-decision] Sunscreen filter-coverage visual** (which nm each filter blocks). *Why:* lets a
   reader see exactly what a given sunscreen covers, the truth-from-marketing payoff for SPF.
10. **[auto-doable] Resolve the 9 dangling `[[xrefs]]`** (create stub or unlink, per target). *Why:* no
    dead-end mentions; either it's a page or it's plain text.

## 3. Open questions that need your call

- **Raise the monthly spend limit?** It's blocking subagents/workflows (killed the `acne` fix) and any further
  overnight automation. Everything above marked [auto-doable] can proceed in minimal main-loop mode regardless.
- **Tier-list visual direction:** the UX audit proposes the component; the exact look (chips vs cards, density)
  is a design call. Approve a direction and it gets built once and reused everywhere (#1/#2/#9).
- **Scope of the 9 dangling xrefs:** should the referenced filters (DHHB, diethylhexyl-butamido-triazone) and
  comparator/dupe products become full pages, or be unlinked? (Taxonomy/scope decision the crons won't make.)
- **anti-aging hub split:** confirm splitting `anti-aging` into a health-first hub + an `anti-aging-perimenopause`
  child (backlog #2) — a structure decision.
- **Make `sk style` a hard publish gate now?** After the 16 dashed pages are cleaned, dashes/AI-ese would become
  blocking errors (with a `--force` escape hatch). Yes/no.

## Status flags
- **95 published**, `sk audit` = 0 hard leaks. **20 escalations pending** in review-feedback (acne, the 8
  missing-Summary pages, the 16 dashed pages, dangling xrefs, tretinoin comparator, anua rework, plus older).
- Guardrails green: full suite 132 tests passing.
