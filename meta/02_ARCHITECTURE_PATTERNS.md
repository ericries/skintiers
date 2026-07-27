# Architecture Patterns

The Seedlist stack is deliberately simple. Every piece can be replaced independently. Understand the pattern first; then adapt each layer to your topic.

## Layer 1: Data-as-git

- **Database:** a git repo. Every fact is in a markdown file. Every change is a commit. Full audit trail. Trivially forkable. No database to back up.
- **Format:** markdown with YAML frontmatter. Frontmatter holds structured queryable data (name, slug, dates, cross-references). Body holds prose sections with markdown footnote citations.
- **Layout:**
  ```
  data/
    {entity_type_A}/     e.g. brands/
      {slug}.md
    {entity_type_B}/     e.g. products/
      {slug}.md
    queue.yaml           <- what to research next
    fact-check-priority.yaml   <- profiles needing follow-up (touched by recent activity)
    vague-facts-queue.yaml     <- generic backlog of vague facts to tighten
    pending-rounds.yaml        <- (for feed topics) scraper output awaiting agent processing
  ```

**Why this works:**
- LLM agents can read/write markdown natively.
- Git handles concurrency (rebase-and-push).
- Reviewers can diff a change.
- No server dependency = free hosting.

**When it doesn't work:**
- If your topic has millions of entities. Seedlist is comfortable at ~10k markdown files. Beyond that, consider SQLite + a build step that emits markdown.

## Layer 2: Static site generation

- `build.py` reads all markdown files with `status: published`, renders HTML via Jinja2 templates, writes to `_site/`.
- Templates live in `templates/`. Static assets in `static/`.
- Only `status: published` profiles appear on the live site. `draft` and `flagged` are excluded from build.
- Rebuild is O(seconds) on ~10k files. Trigger on every push.

**Files to copy from Seedlist:**
- `reference/seedlist_build.py` — the whole generator, ~1500 lines. Copy structure, adapt entity types.
- `reference/seedlist_requirements.txt` — `python-frontmatter`, `markdown`, `jinja2`, `pyyaml`, `scipy`, `numpy`.

## Layer 3: Deployment

- **Hosting:** GitHub Pages (free, custom domain support, no CI cost for a static site).
- **Deploy:** GitHub Action on push to `main`. Checkout → install deps → `python build.py` → upload artifact → deploy.
- **File:** `reference/seedlist_github_action_build.yml`. Copy it to `.github/workflows/build.yml`, change the domain in the `Configure custom domain` step (or delete that step if you don't have a custom domain).

**One-time GitHub setup:**
- Create repo (`gh repo create`).
- Enable Pages in repo Settings → Pages → Source = GitHub Actions.
- Point your DNS at `<user>.github.io` (A records) if using a custom domain.

See `06_GITHUB_SETUP.md` for the full sequence.

## Layer 4: Research workflow

Three roles, all driven by markdown files as state:

1. **Queue** (`data/queue.yaml`) — list of entities to research, with priority.
   ```yaml
   - name: "Brand Name"
     type: brand
     source: "discovered from Product X ingredient list"
     discovered_from: product-x
     priority: high  # high | normal | low
     status: pending  # pending | in_progress | completed | skipped
     added: 2026-07-30
   ```
2. **Research agent** — picks top pending item, sets `in_progress`, does the work (WebSearch, WebFetch, extract facts), writes profile in `data/{type}/{slug}.md` with `status: draft`, sets queue item to `completed`.
3. **Review agent** — verifies drafts against sources, publishes on pass, flags on fail.

## Layer 5: Freshness feed (for topics with continuous news)

For any topic where new items appear daily (product launches, funding rounds, published studies), add a "feed" layer:

1. **Scraper** (GitHub Action, cron-scheduled, no LLM needed): parses RSS/HTML from source feeds, writes candidates to `data/pending-rounds.yaml` (rename for your topic). Runs every 6h. Survives Claude Code sessions being offline.
2. **Monitor agent** (Claude-driven cron, every 6h): reads `pending-rounds.yaml`, verifies each via 3+ primaries, creates profiles, updates cross-references, appends touched entities to `fact-check-priority.yaml`, commits + pushes.
3. **Rendering:** `build.py` produces a reverse-chronological feed page (`/rounds.html` in Seedlist; would be `/launches.html` or `/studies.html` for another topic).

The hybrid (durable GitHub-Action scraper + session-based Claude monitor) means the pipeline never fully goes cold.

## Layer 6: Fact specificity loop

Vague data accumulates over time. Two queues + one agent:

1. **`fact-check-priority.yaml`** — touched entities (see L21). Worked first.
2. **`vague-facts-queue.yaml`** — generic backlog, populated by `scripts/scan_vague_facts.py` (runs weekly-ish). Worked when priority queue is empty.
3. **Fact specificity agent** (Claude-driven cron, every 4h): picks 3 items, verifies via 3+ primaries, updates ALL affected profiles, marks resolved/unresolvable.

See `07_CRON_PATTERNS.md` for exact schedules and prompts.

## Layer 7: Self-improvement

- `_lessons/` — a lesson file after every batch or user feedback. Format in `reference/seedlist_lesson_example.md`.
- `CLAUDE.md` — the master instruction file that all Claude Code sessions auto-load. Update when a lesson reveals a gap.
- Agents should read `_lessons/` before starting new work.

## What changes for a different topic

The pattern is topic-agnostic. Only these layers need topic-specific content:
- **Entity schemas** — brands/products/ingredients vs firms/investors/startups (see `05_ADAPTING_TO_YOUR_TOPIC.md`)
- **Freshness feed sources** — retail news vs VC press
- **Sector taxonomy** (if applicable) — e.g. `data/sector-taxonomy.yaml`
- **Renderer** — a different landing page, different profile templates

## What NEVER changes

- Data-as-git model
- Static site generation via Jinja2
- GitHub Pages deploy via Action
- Two-pass review workflow
- Three-source verification rule
- Fact-specificity + freshness-feed cron pattern
- Sources-first discipline
- Anti-hallucination rules
