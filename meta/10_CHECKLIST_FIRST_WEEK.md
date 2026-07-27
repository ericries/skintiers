# First-Week Checklist

Follow this sequence exactly. Each step unlocks the next. Do NOT skip ahead or you will end up rewriting.

Total time: ~2 focused days spread over a week.

---

## Day 1 — Foundation

### Step 1: Read all meta docs (files 00–09)
Estimated: 30 min. If any are unclear, note the question for the user.

### Step 2: Ask the user the schema questions
See `05_ADAPTING_TO_YOUR_TOPIC.md` and `09_QUESTIONS_TO_ASK.md`. Save the answers in `meta/decisions.md` for future reference.

Required answers:
- [ ] Repo name
- [ ] Entity types + primary entity
- [ ] Primary signal (the "inferred X")
- [ ] Frontmatter schema per entity type (draft)
- [ ] Required body sections per entity type
- [ ] Taxonomy design
- [ ] Freshness feed sources
- [ ] Out-of-scope list
- [ ] License

### Step 3: Set up local scaffold

```bash
cd ~/Projects/skincare  # or your project dir
python3 -m venv .venv
cp meta/reference/seedlist_requirements.txt requirements.txt
.venv/bin/pip install -r requirements.txt
```

### Step 4: Write a first `CLAUDE.md`
Model on `meta/reference/seedlist_CLAUDE.md`. Adapt for your topic. Include:
- Topic-specific entity schemas
- Section requirements per entity type
- Taxonomy design (or reference to a `data/taxonomy.yaml`)
- Freshness feed sources
- Anti-hallucination reminders (cite `meta/03_ANTI_HALLUCINATION_RULES.md`)
- Cron patterns (cite `meta/07_CRON_PATTERNS.md`)
- CLI toolkit reference (cite `meta/08_CLI_TOOLKIT_PATTERN.md`)

**Keep it under 1000 lines.** Long CLAUDE.md files get skipped.

---

## Day 2 — Tooling (TDD)

### Step 5: Set up the test harness
```bash
mkdir tests
touch tests/__init__.py
```

Write a smoke test:

```python
# tests/test_smoke.py
def test_smoke():
    assert True
```

Run:
```bash
.venv/bin/python -m pytest tests/ -v
```

Should PASS.

### Step 6: Build `scripts/sl status` (RED → GREEN → REFACTOR)

Following `04_TDD_WORKFLOW.md`:
1. Write `tests/test_sl_status.py` with a test that calls `sl status` on a temp data dir and asserts expected output.
2. Run it. Confirm RED (import error, or missing file).
3. Write minimum `scripts/sl` to make it pass.
4. Refactor.

Commit each stage. First real feature done TDD-style.

### Step 7: Build `scripts/sl lint SLUG`
Same TDD cycle. Tests should cover:
- Well-formed profile → exit 0
- Missing frontmatter → exit 1
- Broken cross-reference → exit 1
- Missing year in table → exit 2 (warning)
- Duplicate URL → exit 1

### Step 8: Build `scripts/sl build`
Wrap `python build.py`. But `build.py` doesn't exist yet — so this is where you build it.

Build.py starter:
1. Test that it reads `data/**/*.md`.
2. Test that it filters `status: published`.
3. Test that it renders one HTML page.
4. Test that broken cross-references render as plain text (not links).

Copy structure from `meta/reference/seedlist_build.py` but write your version test-first. Do NOT paste it — you'll copy assumptions that don't fit your schema.

---

## Day 3 — Repo + Deploy

### Step 9: Follow `06_GITHUB_SETUP.md`
- Create repo
- Enable Pages
- Add build workflow
- Push first commit
- Verify deploy works (an empty site with `_site/index.html` from `data/` = a stub is fine)

### Step 10: Add your first real profile
Create ONE profile in `data/{primary_entity_type}/example.md` with `status: draft`. Ensure `sl lint example` passes. Then `sl publish example`. Verify it renders live.

If any of this fails, fix the tooling before authoring more.

---

## Day 4 — Freshness Feed

### Step 11: Write the scraper (TDD)
`scripts/scrape_<topic>.py` should:
- Parse each RSS feed in your source list
- Deduplicate against `data/pending-<items>.yaml`
- Write new candidates to `data/pending-<items>.yaml`

Tests first. Live-web calls only outside tests.

### Step 12: Wire the scraper into a GitHub Action
`.github/workflows/scrape-<topic>.yml` running every 6h. See seedlist's `scrape-rounds.yml` for the pattern.

Now you have a scraper that runs 24/7 even when you're not around.

### Step 13: Do a manual freshness-feed cycle
Read `data/pending-<items>.yaml`. Pick one. Follow the workflow in `03_ANTI_HALLUCINATION_RULES.md` (3-source verification). Author the profile. Publish.

Do this manually 3-5 times so you know exactly what an agent needs to do.

---

## Day 5 — Cron

### Step 14: Configure the three crons
Read `07_CRON_PATTERNS.md`. Adapt the prompts for your topic. Create the crons via `CronCreate`.

Verify:
- `CronList` shows all three
- After the first firing, check the commit history to confirm the sweep ran

### Step 15: Write your first `_lessons/` file
`_lessons/YYYY-MM-DD-day-5-first-cron-cycle.md`. Document:
- What worked
- What agents got wrong on the first cron run
- Rules to tighten in the CLAUDE.md or cron prompts

---

## Day 6-7 — Backfill

### Step 16: Manually author 5-10 seed profiles
The freshness feed will grow the database going forward. You also need a seed set (e.g. the 10 biggest brands, the 15 most-studied ingredients) for the site to feel useful at launch.

Follow the two-pass review workflow. Publish only 10/10 profiles.

### Step 17: Announce
Once you have ~20 published profiles, share the site with the user. Get feedback. Write another lessons file.

---

## Ongoing

- Weekly: run `scripts/scan_vague_facts.py` (write one, TDD) to refresh `data/vague-facts-queue.yaml`.
- After every batch: write a lesson if anything new was learned.
- Watch cron output for hallucinations. Tighten prompts as needed.
- Update `CLAUDE.md` whenever a lesson reveals a gap.

---

## Milestones

| Day | Milestone |
|-----|-----------|
| 1 | Meta docs read, schema confirmed with user |
| 2 | Tests passing on `sl status`, `sl lint`, `sl build` |
| 3 | Site deployed to GitHub Pages with one live profile |
| 4 | Scraper running via GH Action; 1 profile authored from feed manually |
| 5 | Three crons live; first _lessons_ file written |
| 6-7 | 10-20 seed profiles published |

If you're behind on any milestone, ASK THE USER before continuing. Deadline pressure is the biggest driver of shortcut-taking, which is the biggest driver of fabricated data.
