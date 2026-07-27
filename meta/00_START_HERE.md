# START HERE — Onboarding for a New Agent

You are picking up a brand-new project modeled after **Seedlist.com** (an LLM-researched directory of active startup investors). That project taught us a set of patterns for building an accurate, self-updating, statically-generated knowledge site backed by markdown-in-git as the database.

Your job is to build a similar site on a **different topic** (this working directory is `~/Projects/skincare/`, so unless the user tells you otherwise, the topic is skincare — brands, products, ingredients, formulators, dermatologists, reviews). The patterns generalize; the schema does not.

**Before you touch anything, read these files in order.** Each is short. Together they take ~20 minutes.

1. `01_LESSONS_LEARNED.md` — What went wrong on Seedlist and how we fixed it. **Non-negotiable rules.**
2. `02_ARCHITECTURE_PATTERNS.md` — Data-as-git, static site, feeds, discovery loops.
3. `03_ANTI_HALLUCINATION_RULES.md` — The single most important document. Every LLM-authored knowledge site dies without these.
4. `04_TDD_WORKFLOW.md` — Red/green TDD for the tooling. **Do NOT skip.**
5. `05_ADAPTING_TO_YOUR_TOPIC.md` — How to design entities and schemas for a new topic.
6. `06_GITHUB_SETUP.md` — Repo, Pages, Actions.
7. `07_CRON_PATTERNS.md` — Freshness feed + fact-check cron design.
8. `08_CLI_TOOLKIT_PATTERN.md` — The `scripts/sl` helper you'll build to reduce friction.
9. `09_QUESTIONS_TO_ASK.md` — When to stop and ask the user.
10. `10_CHECKLIST_FIRST_WEEK.md` — Sequenced setup checklist. Follow it.

## The three rules you must never break

1. **Triple-check every factual claim against 3+ INDEPENDENT primary sources.** Aggregators (Wikipedia, retailer summaries, AI summaries) are NOT primary. Click through to the actual company page / regulator filing / peer-reviewed paper / patent / press release.

2. **When in doubt, LEAVE IT OUT.** A short accurate profile beats a long fabricated one. Mark facts as `unresolvable` in the queue rather than guess. Every past failure in Seedlist traces back to an agent inventing data to fill a gap.

3. **Ask the user when you are not sure what to do.** Do not silently make schema decisions, invent taxonomies, or set policies. See `09_QUESTIONS_TO_ASK.md` for a triage guide.

## Reference materials (read on demand, not upfront)

- `reference/seedlist_CLAUDE.md` — the ~900-line instruction file from Seedlist. Skim its structure. Copy patterns, adapt content.
- `reference/seedlist_build.py` — the static site generator. Read when you start building your own.
- `reference/seedlist_sl.py` — the CLI toolkit. Read when you start building `scripts/sl` for your topic.
- `reference/seedlist_github_action_build.yml` — GitHub Action for build + deploy. Almost copy-paste.
- `reference/seedlist_requirements.txt` — Python deps.
- `reference/seedlist_sample_investor_profile.md` — the shape of a well-formed profile.
- `reference/seedlist_lesson_example.md` — the format of a `_lessons/` file.

## What is already in this directory

```
~/Projects/skincare/
├── meta/           <- YOU ARE HERE. Read files 00→10 first.
│   └── reference/  <- Seedlist source files to copy patterns from.
├── data/           <- (empty) You will define subdirs like brands/, products/, ingredients/.
├── scripts/        <- (empty) You will author scripts/sl and scripts/scrape_*.py.
├── tests/          <- (empty) Write tests FIRST for every script (red → green → refactor).
└── _lessons/       <- (empty) After every batch, write a lesson file here.
```

There is no `CLAUDE.md` at the project root yet. **You will write it** after reading these meta docs and confirming your schema decisions with the user. Model it on `reference/seedlist_CLAUDE.md`.

## Your first three actions

1. Read files 01–10 in order. Take notes on what generalizes and what needs schema work.
2. Ask the user the questions surfaced by `05_ADAPTING_TO_YOUR_TOPIC.md` — you cannot design the schema without their input.
3. Follow `10_CHECKLIST_FIRST_WEEK.md`. Do NOT jump to writing scrapers or authoring profiles before the checklist step that unlocks it.

Do this well and you will save yourself weeks of rework. Every rule in these docs came from a real failure.
