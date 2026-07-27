# Skincare Index (bootstrap)

A fresh project directory bootstrapped from **Seedlist.com**'s patterns for building an accurate, LLM-researched, statically-generated knowledge site.

Topic: **skincare** — brands, products, ingredients, formulators, dermatologists. (Adaptable to any topic — see `meta/`.)

## Status

**Not yet built.** This directory contains:
- `meta/` — full instruction manual for a Claude Code agent to bootstrap the project
- `meta/reference/` — reference files from Seedlist (CLAUDE.md, build.py, sl CLI, GH Action, sample profile)
- Empty `data/`, `scripts/`, `tests/`, `_lessons/` — the agent will populate these

## Agents: start here

Read `CLAUDE.md` (in this directory) first. It points you to the meta docs and the first-week checklist.

## Humans: what to expect

An agent following the meta docs will (over ~1 week):
1. Confirm the schema with you
2. Set up a git repo + GitHub Pages + build workflow
3. Author a small seed set of profiles (3-source verified)
4. Wire up a scraper + three research cron jobs
5. Deliver a live site that self-updates daily

Every fact on the site will trace back to 3+ independent primary sources. Anything less is marked `unresolvable` rather than published.

## Files here

```
skincare/
├── CLAUDE.md               <- Agent entry point
├── README.md               <- You are here
├── meta/
│   ├── 00_START_HERE.md    <- Agent's first meta doc
│   ├── 01_LESSONS_LEARNED.md
│   ├── 02_ARCHITECTURE_PATTERNS.md
│   ├── 03_ANTI_HALLUCINATION_RULES.md
│   ├── 04_TDD_WORKFLOW.md
│   ├── 05_ADAPTING_TO_YOUR_TOPIC.md
│   ├── 06_GITHUB_SETUP.md
│   ├── 07_CRON_PATTERNS.md
│   ├── 08_CLI_TOOLKIT_PATTERN.md
│   ├── 09_QUESTIONS_TO_ASK.md
│   ├── 10_CHECKLIST_FIRST_WEEK.md
│   └── reference/          <- Seedlist source files (CLAUDE.md, build.py, sl, workflow)
├── data/                   <- (empty; agent will populate)
├── scripts/                <- (empty; agent will populate)
├── tests/                  <- (empty; agent will populate, TDD-style)
└── _lessons/               <- (empty; agent writes lessons after every batch)
```
