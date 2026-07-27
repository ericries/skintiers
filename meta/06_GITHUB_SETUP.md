# GitHub Setup — Repo, Pages, Actions

You will need a public GitHub repo, GitHub Pages hosting, and (optionally) a custom domain. This whole setup takes ~15 minutes if you have `gh` (GitHub CLI) authenticated.

## Prerequisites

Confirm with the user:
- [ ] What is the repo name? (e.g. `skincare-index`, `openskin`)
- [ ] Public or private? (Pages requires public unless the user has a paid plan)
- [ ] Custom domain? (Y/N — if Y, they need to control DNS)
- [ ] License? (MIT is a good default for CC-BY-SA data; ask)

**Do not** create the repo without confirming these. Bad repo names are painful to change.

## Step 1: Initialize local repo

From `~/Projects/skincare/` (this directory):

```bash
git init
git branch -M main
```

Add a `.gitignore`:

```gitignore
_site/
__pycache__/
*.pyc
.venv/
.DS_Store
node_modules/
```

Add a `LICENSE` (paste the user's choice).

## Step 2: Set up Python venv + install deps

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Copy `requirements.txt` from `meta/reference/seedlist_requirements.txt`:

```bash
cp meta/reference/seedlist_requirements.txt requirements.txt
```

If your topic needs additional libs (e.g. RSS parsing → `feedparser`), add them.

## Step 3: First commit

```bash
git add .
git commit -m "Initial project scaffolding (from Seedlist patterns)"
```

## Step 4: Create GitHub repo

```bash
gh repo create <name> --public --source=. --remote=origin --description="[Topic] index built with LLM research"
git push -u origin main
```

If you don't have `gh`, do it via the web UI and then:

```bash
git remote add origin git@github.com:<user>/<name>.git
git push -u origin main
```

## Step 5: Enable GitHub Pages

Via web UI:
1. Repo Settings → Pages
2. Source: **GitHub Actions** (NOT Deploy from a branch)
3. Save

Via CLI (requires `gh` >= 2.40):
```bash
gh api -X PUT repos/:owner/:repo/pages -f source[branch]=main -f source[path]=/ 2>/dev/null
# then set to actions source in Settings — this API endpoint is limited
```

## Step 6: Add the build workflow

Copy the workflow file:
```bash
mkdir -p .github/workflows
cp meta/reference/seedlist_github_action_build.yml .github/workflows/build.yml
```

Edit `build.yml`:
- If you have a custom domain, change the CNAME in the `Configure custom domain` step
- If you don't, DELETE the `Configure custom domain` step entirely
- Confirm the Python version matches your local venv

Commit and push:
```bash
git add .github/workflows/build.yml
git commit -m "Add build + deploy workflow"
git push
```

The first Action run will fail if you don't have `build.py` yet — that's fine. Get the workflow in place first.

## Step 7: Custom domain (optional)

If the user has one:

1. Add a `CNAME` file at repo root:
   ```bash
   echo "yourdomain.com" > CNAME
   git add CNAME && git commit -m "Add CNAME" && git push
   ```
2. In DNS provider, add:
   - A record → `185.199.108.153`
   - A record → `185.199.109.153`
   - A record → `185.199.110.153`
   - A record → `185.199.111.153`
   - (Or a single CNAME record → `<user>.github.io` for `www` subdomain)
3. Wait 5–30 min for DNS propagation.
4. In repo Settings → Pages → Custom domain: enter the domain, tick "Enforce HTTPS".

## Step 8: Add a linter workflow (optional but recommended)

Modeled on Seedlist's `.github/workflows/lint.yml`. Runs on every PR, checks:
- YAML frontmatter parses
- Slugs are kebab-case
- Cross-references resolve
- No duplicate URLs in Sources
- Sequential footnotes

Write tests for the linter first (TDD, see `04_TDD_WORKFLOW.md`), then wrap them in a workflow.

## Step 9: Scraper workflow (once you have a `scripts/scrape_*.py`)

Seedlist has `.github/workflows/scrape-rounds.yml` that runs every 6h, scrapes RSS feeds, and commits candidates to `data/pending-rounds.yaml`. This survives Claude Code being offline.

Wait until Step 6 in the first-week checklist to set this up.

## Step 10: Issues/PRs template

Nice-to-have: an issue template for user-submitted sources (`.github/ISSUE_TEMPLATE/source-submission.md`) and a PR template.

## What NOT to do

- Do NOT push placeholder profiles ("Coming soon") — they'll get indexed and hurt credibility. Only push profiles with `status: published` set explicitly.
- Do NOT force-push to `main`. Use `git push` — if it rejects due to a race with a cron commit, `git pull --rebase && git push`.
- Do NOT enable branch protection until you have a stable workflow. Solo dev = branch protection just gets in your way.
- Do NOT use `git commit --no-verify` to bypass pre-commit hooks. Fix the underlying issue.

## Verify the deploy

After the first push with a working `build.py`:
1. Watch the Action run in the repo's Actions tab.
2. On success, visit `https://<user>.github.io/<repo>/` (or your custom domain).
3. Confirm at least one profile renders.

If the site is blank, check:
- Are there profiles with `status: published` in `data/`?
- Did the build succeed? (check `_site/` locally by running `python build.py`)
- Are templates in `templates/`?
