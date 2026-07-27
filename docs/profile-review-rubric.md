# SkinTiers Profile Review Rubric — the definition of 10/10

This is the shared standard used by both the deterministic tooling (`sk lint`, `sk verify`)
and the constructive critic (`.claude/agents/profile-reviewer.md`). A profile is **publishable
at 10/10** when every dimension below is green. The reviewer's job is not to find fault for its
own sake — it is to name the shortest path from where a profile is to 10/10, with concrete,
actionable fixes.

Scoring: each dimension is scored **0–10**. A profile's overall score is the **minimum** across
the first four (Sourcing, Fidelity, Grading, Skeptical honesty) — these are load-bearing and a
failure in any one blocks publication — blended with the last three (Structure, Clarity,
Metadata) as quality modifiers. **Publish only at overall 10/10.** A single fabricated URL,
misquote, or uncited load-bearing claim is an automatic 0 on its dimension.

---

## D1 — Sourcing integrity (load-bearing)

**10/10:** Every factual claim carries a footnote. Every load-bearing claim (a grade, an effect
size, a "beats X" comparison, a headline safety statement) is backed by **≥3 independent primary
sources** — or is explicitly softened / marked `unresolvable` when it isn't. Every source is a
**high-quality primary**: peer-reviewed journals, Cochrane / systematic reviews, trial registries
(ClinicalTrials.gov), regulator filings/labels (FDA/DailyMed, EMA, BfR, Health Canada), patents
for *composition* only. No aggregator, ratings site, retailer, or marketing page is cited *as*
evidence (they may be named as a pointer to follow, never as the source).

**Red flags:** an uncited sentence in The Evidence / What We Actually Know; a grade in the
dossier not traceable to the cited evidence; a grade
that rests on one source; a Sources entry pointing at EWG, INCIDecoder scores, Wikipedia,
Reddit, Healthline/WebMD, a brand site, or a retailer; "3 sources" that are really one study
reported three times (same cohort) presented as independent.

*Automatable:* footnote resolution (`sk lint`), source-domain quality (`sk verify`), citation
presence in evidence sections (`sk verify`). *Judgment:* independence of sources, whether a
claim is truly load-bearing, same-cohort detection.

## D2 — Quote & statistic fidelity (load-bearing)

**10/10:** Every quotation is **verbatim** from the cited source. Every statistic matches the
source and is reported with its **denominator, CI, or p-value** (`72.7% vs 55.8%, P<.001`;
`RR 0.40, 95% CI 0.23–0.70`). No paraphrase is presented inside quotation marks. No number is
invented, rounded misleadingly, or detached from its comparison group.

**Red flags:** a quoted phrase that isn't in the source; a bare "reduces wrinkles by 40%" with no
denominator; a percentage with no comparator; a CI or n silently dropped.

*Automatable:* bare-percentage-without-denominator heuristic (`sk verify`). *Judgment/network:*
verbatim quote match and statistic match against the **re-fetched** source (critic agent).

## D3 — Grading quality (load-bearing)

**10/10:** Effect-size and evidence-quality tiers live in the `grades:` frontmatter and render as
the dossier. They are assessed **per use** where the evidence differs by indication, framed
**relative** with **named comparators** (recorded in each grade's `note` and in The Evidence),
and never claim false precision (no invented 0-100 score). Each grade traces to the evidence
cited in `## The Evidence`.

**Red flags:** a grade no cited evidence supports; one blended grade where uses genuinely differ;
a grade with no comparator anywhere; over- or under-grading versus what the evidence shows.

*Judgment:* almost entirely the critic's call; the linter only checks that `grades:` is present
and that `## The Evidence` carries citations.

## D4 — Skeptical honesty (load-bearing)

**10/10:** Marketing/manufacturer claims are **quarantined** in their own section and explicitly
**discounted** against evidence. Real limits are stated plainly (single-cohort, low GRADE
certainty, category-level-vs-product-specific, wide CIs, industry funding). "No independently
sourced X found" is written where a tier is empty — **never padded**. The profile says "no
evidence" out loud when that's the truth, and does not let a true-but-overstated claim stand.

**Red flags:** marketing claim treated as fact; a limitation the sources note but the profile
omits; a padded "What Users Say"/tier with invented or non-independent quotes; overclaiming
("reverses aging") the evidence doesn't support.

*Judgment:* the critic's core skill. *Automatable:* presence of a quarantined
claims section (`sk verify`).

## D5 — Structure & completeness

**10/10:** All required sections present for the type (Product vs Ingredient), in order; evidence
tiers labeled and **never blended**; every `[[xref]]` resolves; footnotes sequential with no
duplicate or orphan definitions.

*Automatable:* sections-present, xref resolution, footnote sequence/dupes (`sk lint` + `sk verify`).

## D6 — Clarity & voice

**10/10:** Plain, precise, non-hype prose a motivated layperson can follow; defines jargon on
first use; leads with the honest bottom line; no filler. Reads like a trustworthy briefing, not
a marketing page or a journal abstract.

*Judgment:* the critic (light touch — don't over-edit voice that already works).

## D7 — Metadata & freshness

**10/10:** Frontmatter correct (`name`, `slug`, `type`, `status`, `updated`, `analyzed`); status
matches maturity (a synthesized, reviewed page is not left `draft`; a bare page is `stub`);
`analyzed` reflects the last full pass.

*Automatable:* `sk lint` / `sk verify`.

---

## The path to 10/10 (how the critic reports)

For each profile the critic returns:
1. **Per-dimension scores** (D1–D7) with a one-line reason each.
2. **Overall score** and the single **biggest blocker** to 10/10.
3. A **prioritized punch-list**: each item = the specific problem (quoted, line-anchored), *why*
   it matters, and the **concrete fix** (not "add sources" but "the melasma-vs-HQ4% equivalence
   claim rests only on the review [^1]; either find a second independent primary or soften to
   'trends toward equivalence'"). Ordered load-bearing-first.
4. **What's already excellent** (briefly) — so good work is reinforced, not just faults listed.
5. A **verdict**: `publish` (10/10) / `revise` (fixable, list above) / `flag` (a load-bearing 0).

Tone: constructive and specific. Skepticism is aimed at *making the claim bulletproof*, never at
withholding a verdict to seem rigorous. If a profile is already 10/10, say so plainly.
