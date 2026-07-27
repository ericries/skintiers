# Project Not Yet Bootstrapped

This is a fresh project directory modeled on Seedlist.com's patterns for building an accurate, LLM-researched, statically-generated knowledge site. The topic for this instance is **skincare** (brands, products, ingredients, formulators, dermatologists) unless the user says otherwise.

**Before doing anything, read the meta docs.**

## First read (in order, ~30 min total)

1. `meta/00_START_HERE.md` — Onboarding overview
2. `meta/01_LESSONS_LEARNED.md` — Non-negotiable rules from Seedlist
3. `meta/02_ARCHITECTURE_PATTERNS.md` — Data-as-git, static site, feeds
4. `meta/03_ANTI_HALLUCINATION_RULES.md` — Critical accuracy discipline
5. `meta/04_TDD_WORKFLOW.md` — Red/green TDD for all tooling
6. `meta/05_ADAPTING_TO_YOUR_TOPIC.md` — Schema design
7. `meta/06_GITHUB_SETUP.md` — Repo + Pages + Actions
8. `meta/07_CRON_PATTERNS.md` — Freshness feed + fact-check crons
9. `meta/08_CLI_TOOLKIT_PATTERN.md` — The `sl`-style command tool
10. `meta/09_QUESTIONS_TO_ASK.md` — When to stop and ask the user
11. `meta/10_CHECKLIST_FIRST_WEEK.md` — Sequenced setup plan

After you've read them, follow `meta/10_CHECKLIST_FIRST_WEEK.md`. Do not skip steps.

## Three rules you must never break

1. **Triple-check every factual claim against 3+ INDEPENDENT primary sources.** Aggregators (Wikipedia, retailer descriptions, AI summaries) are NOT primary.
2. **When in doubt, LEAVE IT OUT.** Mark facts as `unresolvable` rather than guess. Every past failure in Seedlist traces back to an agent inventing data to fill a gap.
3. **Ask the user when you are unsure.** Do not silently make schema decisions, invent taxonomies, or set policies. See `meta/09_QUESTIONS_TO_ASK.md`.

## Overwrite this file after Day 1

Once you have the schema confirmed with the user (per `meta/10_CHECKLIST_FIRST_WEEK.md` Step 4), overwrite this CLAUDE.md with a proper topic-specific instruction file modeled on `meta/reference/seedlist_CLAUDE.md`. Keep it under 1000 lines. Long CLAUDE.md files get skipped.
