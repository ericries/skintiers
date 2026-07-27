# SkinTiers — Locked Decisions

Recorded verbatim from `docs/superpowers/specs/2026-07-26-skincare-directory-design.md`.
Scannable record of the design decisions that are locked for the project.

- **Name / identity:** SkinTiers. GitHub repo `skintiers`. CLI command `sk`. No custom domain in v1.
- **Primary entity:** Products (the flagship profile type readers land on).
- **7-type model:** Products, Ingredients, Conditions/Goals, Brands, Studies/Papers, People
  (formulators/dermatologists), plus the connective tissue between them. Phase 1 ships only
  Products + Ingredients; the other five types are deferred.
- **Labeled-tier rubric with named comparators:** every Product graded on a two-axis rubric
  (effect size × evidence quality) with explicit, named comparators — not vague adjectives.
- **Flat-markdown-first:** each entity is a markdown file (YAML frontmatter + cited prose) under
  `data/<type>/`. Structured/derived metadata is a later phase.
- **Tiered & labeled evidence:** evidence presented in ranked, labeled tiers
  (clinical trials → dermatologist consensus → aesthetician practice → influencer claims).
- **Per-queue discovery:** new entities are discovered and tracked through a simple research
  queue (`data/queue.yaml`), consumed manually by a subagent in Phase 1 (no cron).
- **Studies/papers flagship feed:** the studies/papers feed is the flagship freshness surface
  (deferred past Phase 1).
- **Routine builder:** a reader-facing routine builder is a planned feature (deferred).
- **Licensing:** MIT for code; CC-BY 4.0 for data.
- **Phased rollout:** build in phases; Phase 1 = tooling + one fully-sourced product profile
  cross-linked to its ingredients, deployed to GitHub Pages.

## Minimal frontmatter (schema-later)

Every profile has: `name`, `slug`, `type` (`product` | `ingredient`), `status`
(`stub` | `draft` | `published`), `updated` (required), `analyzed` (may be `null` for stubs).

## Status ladder (reader-facing "done" signal)

- `stub` — placeholder / link target, created prolifically so cross-links resolve.
- `draft` — unsynthesized collection of links.
- `published` — fully synthesized + two-pass reviewed.

The build renders every status (stubs/drafts included), each badged. Only a genuinely missing
file degrades to plain text. A `flagged`/`synthesized` rung can be added later.
