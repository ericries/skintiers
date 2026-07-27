# SkinTiers — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a live, GitHub-Pages-deployed static site that renders at least one fully-sourced, lint-clean Product profile cross-linked to its Ingredient profiles, with all tooling built test-first.

**Architecture:** A "data-as-git" static site. Each entity type is a folder under `data/` holding markdown profiles (YAML frontmatter + cited prose). Pure, importable helpers live in `scripts/sklib.py`; the `scripts/sk` CLI and root `build.py` are thin wrappers over it. `build.py` filters `status: published`, renders markdown (tables + footnotes) through Jinja2 into `_site/`, and a GitHub Action deploys `_site/` to Pages on push to `main`.

**Tech Stack:** Python 3.12, python-frontmatter, markdown, jinja2, pyyaml, pytest. GitHub Pages via GitHub Actions. No custom domain in v1.

## Global Constraints

- **Name/identity:** SkinTiers. GitHub repo name `skintiers`. CLI command `sk`. No custom domain in v1 (build workflow omits any CNAME step).
- **Minimal frontmatter only** (schema-later): every profile has `name`, `slug`, `type` (`product` | `ingredient`), `status` (`stub` | `draft` | `published`), `updated` (date of most recent change, required), `analyzed` (date of most recent full LLM analysis; may be `null` for stubs).
- **Status ladder (reader-facing "done" signal, shown as a prominent badge):** `stub` = placeholder/link-target created prolifically so cross-links resolve; `draft` = unsynthesized collection of links; `published` = fully synthesized + two-pass reviewed. **The build renders every status** (stubs/drafts included), each badged. Only a genuinely missing file degrades to plain-text. (A `flagged`/`synthesized` rung can be added later.)
- **Freshness shown prominently on every profile:** `updated` and `analyzed` dates near the top.
- **Anti-hallucination (applies to authored content, Task 9):** sources-first; 3 independent primary sources or mark a claim `unresolvable`; every claim footnoted; re-fetch every cited URL; verbatim quotes only; show percentage math inline; two-pass review; publish only at 10/10.
- **TDD for all code:** red → green → refactor. TDD does NOT apply to markdown content.
- **Test isolation:** `sklib`, `sk`, and `build.py` read data/output/template locations from env vars (`SK_DATA`, `SK_OUTPUT`, `SK_TEMPLATES`, `SK_STATIC`), defaulting to repo paths, so tests run against temp dirs.
- **Deferred to later phases (do NOT build here):** research queues, crons, scrapers/freshness feed, the other five entity types (conditions/goals/brands/studies/people), structured/derived metadata, the effect×evidence visual, the routine builder.
- **Python interpreter:** always the project venv, `.venv/bin/python` / `.venv/bin/pytest`.

---

## File Structure

- `requirements.txt` — pinned-enough dependency list.
- `.gitignore` — `_site/`, `__pycache__/`, `*.pyc`, `.venv/`, `.DS_Store`.
- `LICENSE` — MIT (code). Data licensing (CC-BY 4.0) noted in README later; not blocking Phase 1.
- `meta/decisions.md` — the locked decisions record (from the design spec).
- `scripts/sklib.py` — pure, importable helpers: profile loading, footnote/frontmatter checks, markdown render, xref linkify, status setter. **The one place logic lives.**
- `scripts/sk` — executable CLI dispatch (argparse) over `sklib`: `status`, `lint`, `build`, `publish`, `draft`, `ship`, `queue-add`, `queue`, `queue-resolve`.
- `data/queue.yaml` — the simple research queue (created on first `queue-add`); consumed manually by a subagent in Phase 1 (no cron).
- `build.py` — site generator; imports `sklib`; renders published profiles + listings + index into `_site/`.
- `templates/` — `base.html`, `profile.html`, `listing.html`, `index.html`.
- `static/style.css` — minimal styling.
- `data/products/`, `data/ingredients/` — profile folders.
- `tests/` — `conftest.py`, `test_smoke.py`, `test_sklib_load.py`, `test_sk_status.py`, `test_sklib_lint.py`, `test_sk_lint.py`, `test_sklib_render.py`, `test_build.py`, `test_sk_publish.py`, `test_sklib_queue.py`, `test_sk_queue.py`.
- `.github/workflows/build.yml` — Pages deploy.

---

### Task 1: Project scaffold, environment, and git

**Files:**
- Create: `requirements.txt`, `.gitignore`, `LICENSE`, `meta/decisions.md`
- Create: `data/products/.gitkeep`, `data/ingredients/.gitkeep`, `scripts/` (dir)
- Test: `tests/__init__.py`, `tests/conftest.py`, `tests/test_smoke.py`

- [ ] **Step 1: Create `requirements.txt`**

```
python-frontmatter==1.1.0
Markdown==3.7
Jinja2==3.1.4
PyYAML==6.0.2
pytest==8.3.3
```

- [ ] **Step 2: Create `.gitignore`**

```
_site/
__pycache__/
*.pyc
.venv/
.DS_Store
```

- [ ] **Step 3: Create the virtualenv and install deps**

Run:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
Expected: installs complete without error.

- [ ] **Step 4: Create `LICENSE` (MIT) and `meta/decisions.md`**

`meta/decisions.md` records the locked decisions verbatim from `docs/superpowers/specs/2026-07-26-skincare-directory-design.md` (name = SkinTiers; primary entity = Products; 7-type model; labeled-tier rubric with named comparators; flat-markdown-first; tiered/labeled evidence; per-queue discovery; studies/papers flagship feed; routine builder; MIT code / CC-BY data; phased rollout). Keep it to a scannable bullet list. `LICENSE` = standard MIT text, year 2026.

- [ ] **Step 5: Create empty data folders**

```bash
mkdir -p data/products data/ingredients scripts
touch data/products/.gitkeep data/ingredients/.gitkeep tests/__init__.py
```

- [ ] **Step 6: Write the smoke test**

`tests/test_smoke.py`:
```python
def test_dependencies_import():
    import frontmatter  # noqa: F401
    import markdown  # noqa: F401
    import jinja2  # noqa: F401
    import yaml  # noqa: F401


def test_python_version():
    import sys
    assert sys.version_info[:2] >= (3, 11)
```

`tests/conftest.py`:
```python
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
```

- [ ] **Step 7: Run the smoke test**

Run: `.venv/bin/pytest tests/test_smoke.py -v`
Expected: 2 passed.

- [ ] **Step 8: Initialize git and commit**

```bash
git init
git branch -M main
git add -A
git commit -m "chore: scaffold SkinTiers project (env, deps, data folders, smoke test)"
```

---

### Task 2: `sklib` profile loading

**Files:**
- Create: `scripts/sklib.py`
- Test: `tests/test_sklib_load.py`

**Interfaces:**
- Produces: `load_profiles(data_dir: Path) -> list[frontmatter.Post]` (each has `.metadata` dict and `.content` str; sorted by path). `filter_published(posts) -> list`. `find_profile(data_dir, slug) -> Path | None`. `DATA_DIR`, `OUTPUT_DIR`, `TEMPLATES_DIR`, `STATIC_DIR` module constants resolved from env vars.

- [ ] **Step 1: Write the failing test**

`tests/test_sklib_load.py`:
```python
import pathlib
import sklib


def _write(dirpath, slug, status, typ="product"):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: {typ}\nstatus: {status}\n---\n\nBody.\n"
    )


def test_load_and_filter(tmp_path):
    _write(tmp_path / "products", "good", "published")
    _write(tmp_path / "products", "wip", "draft")
    posts = sklib.load_profiles(tmp_path)
    assert {p["slug"] for p in posts} == {"good", "wip"}
    published = sklib.filter_published(posts)
    assert [p["slug"] for p in published] == ["good"]


def test_find_profile(tmp_path):
    _write(tmp_path / "ingredients", "niacinamide", "published", "ingredient")
    found = sklib.find_profile(tmp_path, "niacinamide")
    assert found is not None and found.name == "niacinamide.md"
    assert sklib.find_profile(tmp_path, "nope") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sklib_load.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'sklib'`).

- [ ] **Step 3: Write minimal implementation**

`scripts/sklib.py`:
```python
"""SkinTiers shared helpers. Pure, importable, test-first."""
import os
import pathlib

import frontmatter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = pathlib.Path(os.environ.get("SK_DATA", ROOT / "data"))
OUTPUT_DIR = pathlib.Path(os.environ.get("SK_OUTPUT", ROOT / "_site"))
TEMPLATES_DIR = pathlib.Path(os.environ.get("SK_TEMPLATES", ROOT / "templates"))
STATIC_DIR = pathlib.Path(os.environ.get("SK_STATIC", ROOT / "static"))

ENTITY_TYPES = ("product", "ingredient")


def load_profiles(data_dir):
    data_dir = pathlib.Path(data_dir)
    posts = []
    for md in sorted(data_dir.glob("*/*.md")):
        posts.append(frontmatter.load(md))
    return posts


def filter_published(posts):
    return [p for p in posts if p.get("status") == "published"]


def find_profile(data_dir, slug):
    for md in pathlib.Path(data_dir).glob("*/*.md"):
        if md.stem == slug:
            return md
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sklib_load.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/sklib.py tests/test_sklib_load.py
git commit -m "feat(sklib): profile loading, published filter, find_profile"
```

---

### Task 3: `sk status`

**Files:**
- Create: `scripts/sk`
- Test: `tests/test_sk_status.py`

**Interfaces:**
- Consumes: `sklib.load_profiles`.
- Produces: `scripts/sk` executable; `sk status` prints one line per status with counts and exits 0.

- [ ] **Step 1: Write the failing test**

`tests/test_sk_status.py`:
```python
import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _write(dirpath, slug, status):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n---\n\nBody.\n"
    )


def test_status_counts(tmp_path):
    _write(tmp_path / "products", "a", "published")
    _write(tmp_path / "products", "b", "published")
    _write(tmp_path / "products", "c", "draft")
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    out = subprocess.run([sys.executable, str(SK), "status"], env=env,
                         capture_output=True, text=True)
    assert out.returncode == 0
    assert "published: 2" in out.stdout
    assert "draft: 1" in out.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sk_status.py -v`
Expected: FAIL (file `scripts/sk` does not exist / non-zero return).

- [ ] **Step 3: Write minimal implementation**

`scripts/sk` (make executable):
```python
#!/usr/bin/env python3
"""SkinTiers CLI. Thin dispatch over sklib."""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sklib  # noqa: E402


def cmd_status(args):
    posts = sklib.load_profiles(sklib.DATA_DIR)
    counts = collections.Counter(p.get("status", "unknown") for p in posts)
    for status in ("published", "draft", "flagged", "unknown"):
        if counts.get(status):
            print(f"{status}: {counts[status]}")
    print(f"total: {len(posts)}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sk")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

Then: `chmod +x scripts/sk`

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sk_status.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/sk tests/test_sk_status.py
git commit -m "feat(sk): status subcommand"
```

---

### Task 4: `sklib` profile linting + `sk lint`

**Files:**
- Modify: `scripts/sklib.py`, `scripts/sk`
- Test: `tests/test_sklib_lint.py`, `tests/test_sk_lint.py`

**Interfaces:**
- Produces: `check_profile(metadata: dict, content: str) -> tuple[list[str], list[str]]` returning `(errors, warnings)`. `sk lint SLUG` exits `0` (clean), `1` (errors), `2` (warnings only).

- [ ] **Step 1: Write the failing unit test**

`tests/test_sklib_lint.py`:
```python
import sklib

GOOD_META = {"name": "X", "slug": "x", "type": "product", "status": "draft", "updated": "2026-07-26"}


def test_clean_profile_passes():
    content = "Claim.[^1]\n\n## Sources\n[^1]: Title. https://example.com (2026-07-26)\n"
    errors, warnings = sklib.check_profile(GOOD_META, content)
    assert errors == [] and warnings == []


def test_stub_with_no_footnotes_is_clean():
    meta = {"name": "X", "slug": "x", "type": "ingredient", "status": "stub", "updated": "2026-07-26"}
    errors, warnings = sklib.check_profile(meta, "One link placeholder.\n")
    assert errors == [] and warnings == []


def test_missing_updated_is_error():
    meta = {"name": "X", "slug": "x", "type": "product", "status": "draft"}
    errors, _ = sklib.check_profile(meta, "Body.\n")
    assert any("updated" in e for e in errors)


def test_missing_frontmatter_field_is_error():
    errors, _ = sklib.check_profile({"name": "X", "slug": "x", "type": "product"}, "Body.\n")
    assert any("status" in e for e in errors)


def test_bad_type_is_error():
    meta = {**GOOD_META, "type": "banana"}
    errors, _ = sklib.check_profile(meta, "Body.\n")
    assert any("type" in e for e in errors)


def test_footnote_reference_without_definition_is_error():
    errors, _ = sklib.check_profile(GOOD_META, "Claim.[^1]\n")
    assert any("[^1]" in e for e in errors)


def test_orphan_definition_is_warning():
    content = "No refs.\n\n## Sources\n[^1]: Title. https://example.com\n"
    errors, warnings = sklib.check_profile(GOOD_META, content)
    assert errors == []
    assert any("[^1]" in w for w in warnings)


def test_duplicate_definition_is_error():
    content = "A.[^1]\n\n## Sources\n[^1]: One. https://a.com\n[^1]: Two. https://b.com\n"
    errors, _ = sklib.check_profile(GOOD_META, content)
    assert any("duplicate" in e.lower() for e in errors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sklib_lint.py -v`
Expected: FAIL (`AttributeError: module 'sklib' has no attribute 'check_profile'`).

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/sklib.py`:
```python
import re

REQUIRED_FIELDS = ("name", "slug", "type", "status", "updated")
VALID_STATUS = ("stub", "draft", "published")

_REF_RE = re.compile(r"\[\^([^\]]+)\](?!:)")
_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)


def check_profile(metadata, content):
    errors, warnings = [], []
    for field in REQUIRED_FIELDS:
        if not metadata.get(field):
            errors.append(f"missing frontmatter field: {field}")
    if metadata.get("type") and metadata["type"] not in ENTITY_TYPES:
        errors.append(f"invalid type: {metadata['type']} (must be one of {ENTITY_TYPES})")
    if metadata.get("status") and metadata["status"] not in VALID_STATUS:
        errors.append(f"invalid status: {metadata['status']}")

    refs = set(_REF_RE.findall(content))
    defs = _DEF_RE.findall(content)
    seen = set()
    for d in defs:
        if d in seen:
            errors.append(f"duplicate footnote definition: [^{d}]")
        seen.add(d)
    for r in sorted(refs):
        if r not in seen:
            errors.append(f"footnote [^{r}] referenced but never defined")
    for d in sorted(seen):
        if d not in refs:
            warnings.append(f"footnote [^{d}] defined but never referenced")
    return errors, warnings
```

- [ ] **Step 4: Run unit test to verify it passes**

Run: `.venv/bin/pytest tests/test_sklib_lint.py -v`
Expected: 6 passed.

- [ ] **Step 5: Write the failing CLI test**

`tests/test_sk_lint.py`:
```python
import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _run(tmp_path, slug):
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    return subprocess.run([sys.executable, str(SK), "lint", slug], env=env,
                          capture_output=True, text=True)


def _write(tmp_path, slug, body, status="draft"):
    d = tmp_path / "products"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{slug}.md").write_text(
        f"---\nname: {slug}\nslug: {slug}\ntype: product\nstatus: {status}\n"
        f"updated: 2026-07-26\n---\n\n{body}"
    )


def test_lint_clean_exits_0(tmp_path):
    _write(tmp_path, "ok", "Claim.[^1]\n\n## Sources\n[^1]: T. https://e.com (2026-07-26)\n")
    assert _run(tmp_path, "ok").returncode == 0


def test_lint_error_exits_1(tmp_path):
    _write(tmp_path, "bad", "Claim.[^1]\n")
    assert _run(tmp_path, "bad").returncode == 1


def test_lint_warning_exits_2(tmp_path):
    _write(tmp_path, "warn", "No refs.\n\n## Sources\n[^1]: T. https://e.com\n")
    assert _run(tmp_path, "warn").returncode == 2
```

- [ ] **Step 6: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sk_lint.py -v`
Expected: FAIL (`invalid choice: 'lint'`).

- [ ] **Step 7: Wire `lint` into `scripts/sk`**

Add to `scripts/sk` (new function + registration in `main`):
```python
def cmd_lint(args):
    import frontmatter
    path = sklib.find_profile(sklib.DATA_DIR, args.slug)
    if path is None:
        print(f"not found: {args.slug}", file=sys.stderr)
        return 1
    post = frontmatter.load(path)
    errors, warnings = sklib.check_profile(post.metadata, post.content)
    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        return 1
    if warnings:
        return 2
    print(f"{args.slug}: clean")
    return 0
```
And in `main`, after the `status` parser:
```python
    p_lint = sub.add_parser("lint")
    p_lint.add_argument("slug")
    p_lint.set_defaults(func=cmd_lint)
```

- [ ] **Step 8: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sk_lint.py -v`
Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
git add scripts/sklib.py scripts/sk tests/test_sklib_lint.py tests/test_sk_lint.py
git commit -m "feat(sk): profile lint (frontmatter + footnote integrity)"
```

---

### Task 5: Markdown render + cross-reference linkify

**Files:**
- Modify: `scripts/sklib.py`
- Test: `tests/test_sklib_render.py`

**Interfaces:**
- Produces: `render_markdown(text: str) -> str` (HTML, with `tables`, `footnotes`, `smarty`). `linkify_xrefs(text: str, published_slugs: set[str], slug_to_name: dict) -> str` — converts `[[slug]]` / `[[slug|Label]]` to a markdown link `[Label](slug.html)` when `slug` is published, else to the plain visible text (never leaves `[[ ]]`).

- [ ] **Step 1: Write the failing test**

`tests/test_sklib_render.py`:
```python
import sklib


def test_render_markdown_bold_and_table():
    html = sklib.render_markdown("**hi**\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    assert "<strong>hi</strong>" in html
    assert "<table>" in html


def test_linkify_resolvable():
    out = sklib.linkify_xrefs("See [[niacinamide]].", {"niacinamide"},
                              {"niacinamide": "Niacinamide"})
    assert "[Niacinamide](niacinamide.html)" in out


def test_linkify_with_label():
    out = sklib.linkify_xrefs("Try [[niacinamide|vitamin B3]].", {"niacinamide"},
                              {"niacinamide": "Niacinamide"})
    assert "[vitamin B3](niacinamide.html)" in out


def test_linkify_broken_is_plain_text():
    out = sklib.linkify_xrefs("See [[unobtainium]].", set(), {})
    assert "unobtainium" in out
    assert "unobtainium.html" not in out
    assert "[[" not in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sklib_render.py -v`
Expected: FAIL (`AttributeError: ... 'render_markdown'`).

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/sklib.py`:
```python
import markdown as _markdown

_XREF_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def render_markdown(text):
    return _markdown.markdown(text, extensions=["tables", "footnotes", "smarty"])


def linkify_xrefs(text, published_slugs, slug_to_name):
    def repl(m):
        slug = m.group(1).strip()
        label = (m.group(2) or slug_to_name.get(slug, slug)).strip()
        if slug in published_slugs:
            return f"[{label}]({slug}.html)"
        return label
    return _XREF_RE.sub(repl, text)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sklib_render.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/sklib.py tests/test_sklib_render.py
git commit -m "feat(sklib): markdown render + [[xref]] linkify (broken -> plain text)"
```

---

### Task 6: `build.py` site generator + templates + `sk build`

**Files:**
- Create: `build.py`, `templates/base.html`, `templates/profile.html`, `templates/listing.html`, `templates/index.html`, `static/style.css`
- Modify: `scripts/sk`
- Test: `tests/test_build.py`

**Interfaces:**
- Consumes: `sklib.load_profiles`, `filter_published`, `render_markdown`, `linkify_xrefs`, `OUTPUT_DIR`, `TEMPLATES_DIR`, `STATIC_DIR`.
- Produces: `build.py` `build()` writing `_site/<slug>.html` per published profile, `_site/products.html` + `_site/ingredients.html` listings, `_site/index.html`, and copying `static/`. `sk build` runs it.

- [ ] **Step 1: Write the failing test**

`tests/test_build.py`:
```python
import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _write(dirpath, slug, status, typ, body="Body.\n"):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: {typ}\nstatus: {status}\n"
        f"updated: 2026-07-26\nanalyzed: 2026-07-26\n---\n\n{body}"
    )


def test_build_renders_all_statuses_with_badge_and_xref(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    _write(data / "products", "serum", "published", "product",
           "Contains [[niacinamide]] and [[unobtainium]].\n")
    _write(data / "products", "secret", "draft", "product")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (out / "serum.html").exists()
    assert (out / "niacinamide.html").exists()
    assert (out / "secret.html").exists()              # draft renders as a link target
    assert (out / "index.html").exists()
    assert "draft" in (out / "secret.html").read_text().lower()   # status badge shown
    serum_html = (out / "serum.html").read_text()
    assert 'href="niacinamide.html"' in serum_html   # resolvable xref linked
    assert "unobtainium.html" not in serum_html        # broken xref is plain text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_build.py -v`
Expected: FAIL (`build.py` does not exist).

- [ ] **Step 3: Create the templates and stylesheet**

`templates/base.html`:
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}SkinTiers{% endblock %}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header><a href="index.html"><strong>SkinTiers</strong></a> &mdash; what the evidence actually says</header>
  <main>{% block content %}{% endblock %}</main>
  <footer>Educational, not medical advice. See a dermatologist for medical concerns.</footer>
</body>
</html>
```

`templates/profile.html`:
```html
{% extends "base.html" %}
{% block title %}{{ profile.name }} — SkinTiers{% endblock %}
{% block content %}
<article>
  <h1>{{ profile.name }}</h1>
  <p class="meta">
    <span class="badge badge-{{ profile.status }}">{{ profile.status }}</span>
    <span class="type">{{ profile.type }}</span>
  </p>
  <p class="freshness">
    Updated <strong>{{ profile.updated | default('—') }}</strong>
    · Last full analysis <strong>{{ profile.analyzed | default('—') }}</strong>
  </p>
  {{ body|safe }}
</article>
{% endblock %}
```

`templates/listing.html`:
```html
{% extends "base.html" %}
{% block title %}{{ heading }} — SkinTiers{% endblock %}
{% block content %}
<h1>{{ heading }}</h1>
<ul>
{% for item in items %}
  <li><a href="{{ item.slug }}.html">{{ item.name }}</a></li>
{% endfor %}
</ul>
{% endblock %}
```

`templates/index.html`:
```html
{% extends "base.html" %}
{% block content %}
<h1>SkinTiers</h1>
<p>A skeptical, evidence-first directory of skincare.</p>
<ul>
  <li><a href="products.html">Products ({{ product_count }})</a></li>
  <li><a href="ingredients.html">Ingredients ({{ ingredient_count }})</a></li>
</ul>
{% endblock %}
```

`static/style.css`:
```css
body { font: 16px/1.6 system-ui, sans-serif; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; }
header, footer { color: #555; font-size: .9rem; }
footer { margin-top: 3rem; border-top: 1px solid #ddd; padding-top: 1rem; }
.type { color: #888; text-transform: uppercase; letter-spacing: .05em; font-size: .8rem; }
.meta { display: flex; gap: .6rem; align-items: center; }
.freshness { color: #666; font-size: .85rem; margin-top: -.4rem; }
.badge { display: inline-block; padding: .1rem .5rem; border-radius: .8rem; font-size: .75rem;
  text-transform: uppercase; letter-spacing: .04em; font-weight: 600; color: #fff; }
.badge-stub { background: #9ca3af; }
.badge-draft { background: #d97706; }
.badge-published { background: #16a34a; }
.badge-flagged { background: #dc2626; }
```

- [ ] **Step 4: Write `build.py`**

`build.py`:
```python
#!/usr/bin/env python3
"""SkinTiers static site generator."""
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import sklib  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

LISTINGS = (("product", "products", "Products"), ("ingredient", "ingredients", "Ingredients"))


def build():
    env = Environment(loader=FileSystemLoader(str(sklib.TEMPLATES_DIR)), autoescape=True)
    out = sklib.OUTPUT_DIR
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # Render EVERY status (stubs/drafts included) so cross-links always resolve; each is badged.
    profiles = sklib.load_profiles(sklib.DATA_DIR)
    slugs = {p["slug"] for p in profiles}
    names = {p["slug"]: p["name"] for p in profiles}

    for p in profiles:
        linked = sklib.linkify_xrefs(p.content, slugs, names)
        body = sklib.render_markdown(linked)
        html = env.get_template("profile.html").render(profile=p.metadata, body=body)
        (out / f"{p['slug']}.html").write_text(html)

    counts = {}
    for typ, filename, heading in LISTINGS:
        items = [p.metadata for p in profiles if p.get("type") == typ]
        counts[typ] = len(items)
        html = env.get_template("listing.html").render(heading=heading, items=items)
        (out / f"{filename}.html").write_text(html)

    index = env.get_template("index.html").render(
        product_count=counts.get("product", 0),
        ingredient_count=counts.get("ingredient", 0),
    )
    (out / "index.html").write_text(index)

    if sklib.STATIC_DIR.exists():
        for f in sklib.STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy(f, out / f.name)
    print(f"built {len(published)} profiles -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_build.py -v`
Expected: 1 passed.

- [ ] **Step 6: Add `sk build`**

In `scripts/sk`, add:
```python
def cmd_build(args):
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return subprocess.call([sys.executable, os.path.join(root, "build.py")])
```
And register in `main`: `sub.add_parser("build").set_defaults(func=cmd_build)`

- [ ] **Step 7: Full suite + manual eyeball**

Run: `.venv/bin/pytest tests/ -v` → all pass.
Run: `.venv/bin/python build.py` then open `_site/index.html` in a browser to sanity-check rendering.

- [ ] **Step 8: Commit**

```bash
git add build.py templates static scripts/sk tests/test_build.py
git commit -m "feat(build): static site generator, templates, sk build"
```

---

### Task 7: Profile lifecycle — `sk publish` / `draft`

**Files:**
- Modify: `scripts/sklib.py`, `scripts/sk`
- Test: `tests/test_sk_publish.py`

**Interfaces:**
- Produces: `sklib.set_status(path, status, mark_analyzed=False)` rewrites `status` + bumps `updated` (and `analyzed` when `mark_analyzed`). `sk publish SLUG` / `sk draft SLUG` flip status and rebuild.

- [ ] **Step 1: Write the failing test**

`tests/test_sk_publish.py`:
```python
import os
import subprocess
import sys
import pathlib
import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def test_publish_flips_status(tmp_path):
    data = tmp_path / "data"
    (data / "products").mkdir(parents=True)
    path = data / "products" / "serum.md"
    path.write_text("---\nname: Serum\nslug: serum\ntype: product\nstatus: draft\n---\n\nBody.\n")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(tmp_path / "_site")}
    r = subprocess.run([sys.executable, str(SK), "publish", "serum"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    post = frontmatter.load(path)
    assert post["status"] == "published"
    assert post["updated"] is not None            # updated is bumped
    assert post["analyzed"] is not None           # publishing stamps the analysis date
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sk_publish.py -v`
Expected: FAIL (`invalid choice: 'publish'`).

- [ ] **Step 3: Add `set_status` to `sklib`**

Append to `scripts/sklib.py`:
```python
import datetime as _datetime


def _today():
    return _datetime.date.today().isoformat()


def set_status(path, status, mark_analyzed=False):
    post = frontmatter.load(path)
    post["status"] = status
    post["updated"] = _today()
    if mark_analyzed:
        post["analyzed"] = _today()
    with open(path, "wb") as f:
        frontmatter.dump(post, f)
```

- [ ] **Step 4: Add subcommands to `scripts/sk`**

```python
def _set_and_build(slug, status, mark_analyzed=False):
    path = sklib.find_profile(sklib.DATA_DIR, slug)
    if path is None:
        print(f"not found: {slug}", file=sys.stderr)
        return 1
    sklib.set_status(path, status, mark_analyzed=mark_analyzed)
    print(f"{slug}: {status}")
    return cmd_build(None)


def cmd_publish(args):
    return _set_and_build(args.slug, "published", mark_analyzed=True)


def cmd_draft(args):
    return _set_and_build(args.slug, "draft")
```
Register in `main`:
```python
    for name, fn in (("publish", cmd_publish), ("draft", cmd_draft)):
        pp = sub.add_parser(name)
        pp.add_argument("slug")
        pp.set_defaults(func=fn)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sk_publish.py -v`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/sklib.py scripts/sk tests/test_sk_publish.py
git commit -m "feat(sk): publish/draft/flag lifecycle"
```

---

### Task 8: Simple research queue (`sk queue-add` / `queue` / `queue-resolve`)

**Files:**
- Modify: `scripts/sklib.py`, `scripts/sk`
- Test: `tests/test_sklib_queue.py`, `tests/test_sk_queue.py`

**Interfaces:**
- Produces: `load_queue(data_dir) -> list[dict]`, `save_queue(data_dir, items)`,
  `queue_add(data_dir, name, type, priority=5, discovered_from=None, source=None) -> bool`
  (dedup by `(name, type)`; returns whether it was added), `queue_resolve(data_dir, name) -> bool`.
  Queue lives at `data/queue.yaml` (a YAML list of dicts with `name`, `type`, `priority` 1–10,
  `status` `pending|done`, `discovered_from`, `source`). `sk queue-add`, `sk queue [--type]`,
  `sk queue-resolve` CLI. **No cron in Phase 1 — the queue is consumed manually by a subagent.**

- [ ] **Step 1: Write the failing unit test**

`tests/test_sklib_queue.py`:
```python
import sklib


def test_queue_add_and_dedup(tmp_path):
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is True
    assert sklib.queue_add(tmp_path, "Niacinamide", "ingredient", 8) is False
    items = sklib.load_queue(tmp_path)
    assert len(items) == 1
    assert items[0]["status"] == "pending"
    assert items[0]["priority"] == 8


def test_queue_resolve(tmp_path):
    sklib.queue_add(tmp_path, "X", "product", 5)
    assert sklib.queue_resolve(tmp_path, "X") is True
    assert sklib.load_queue(tmp_path)[0]["status"] == "done"
    assert sklib.queue_resolve(tmp_path, "missing") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sklib_queue.py -v`
Expected: FAIL (`AttributeError: ... 'queue_add'`).

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/sklib.py`:
```python
import yaml as _yaml


def _queue_path(data_dir):
    return pathlib.Path(data_dir) / "queue.yaml"


def load_queue(data_dir):
    path = _queue_path(data_dir)
    if not path.exists():
        return []
    return _yaml.safe_load(path.read_text()) or []


def save_queue(data_dir, items):
    _queue_path(data_dir).parent.mkdir(parents=True, exist_ok=True)
    _queue_path(data_dir).write_text(_yaml.safe_dump(items, sort_keys=False))


def queue_add(data_dir, name, type, priority=5, discovered_from=None, source=None):
    items = load_queue(data_dir)
    for it in items:
        if it.get("name") == name and it.get("type") == type:
            return False
    items.append({
        "name": name, "type": type, "priority": int(priority),
        "status": "pending", "discovered_from": discovered_from, "source": source,
    })
    save_queue(data_dir, items)
    return True


def queue_resolve(data_dir, name):
    items = load_queue(data_dir)
    changed = False
    for it in items:
        if it.get("name") == name and it.get("status") != "done":
            it["status"] = "done"
            changed = True
    if changed:
        save_queue(data_dir, items)
    return changed
```

- [ ] **Step 4: Run unit test to verify it passes**

Run: `.venv/bin/pytest tests/test_sklib_queue.py -v`
Expected: 2 passed.

- [ ] **Step 5: Write the failing CLI test**

`tests/test_sk_queue.py`:
```python
import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scripts" / "sk"


def _sk(tmp_path, *args):
    env = {**os.environ, "SK_DATA": str(tmp_path)}
    return subprocess.run([sys.executable, str(SK), *args], env=env,
                          capture_output=True, text=True)


def test_queue_add_and_list(tmp_path):
    assert _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient", "--priority", "9").returncode == 0
    assert _sk(tmp_path, "queue-add", "CeraVe Cream", "--type", "product", "--priority", "6").returncode == 0
    out = _sk(tmp_path, "queue")
    assert out.returncode == 0
    # priority-sorted: higher first
    assert out.stdout.index("Retinol") < out.stdout.index("CeraVe Cream")


def test_queue_resolve_hides_item(tmp_path):
    _sk(tmp_path, "queue-add", "Retinol", "--type", "ingredient")
    _sk(tmp_path, "queue-resolve", "Retinol")
    assert "Retinol" not in _sk(tmp_path, "queue").stdout
```

- [ ] **Step 6: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sk_queue.py -v`
Expected: FAIL (`invalid choice: 'queue-add'`).

- [ ] **Step 7: Wire queue commands into `scripts/sk`**

Add functions:
```python
def cmd_queue_add(args):
    added = sklib.queue_add(sklib.DATA_DIR, args.name, args.type, args.priority,
                            args.discovered_from, args.source)
    print(f"{'added' if added else 'already queued'}: {args.name}")
    return 0


def cmd_queue(args):
    items = [i for i in sklib.load_queue(sklib.DATA_DIR) if i.get("status") == "pending"]
    if args.type:
        items = [i for i in items if i.get("type") == args.type]
    for i in sorted(items, key=lambda x: -x.get("priority", 0)):
        print(f"[{i.get('priority')}] {i.get('type')}: {i.get('name')}")
    return 0


def cmd_queue_resolve(args):
    ok = sklib.queue_resolve(sklib.DATA_DIR, args.name)
    print(f"{'resolved' if ok else 'not found'}: {args.name}")
    return 0
```
Register in `main`:
```python
    p_qa = sub.add_parser("queue-add")
    p_qa.add_argument("name")
    p_qa.add_argument("--type", required=True, choices=("product", "ingredient"))
    p_qa.add_argument("--priority", type=int, default=5)
    p_qa.add_argument("--from", dest="discovered_from", default=None)
    p_qa.add_argument("--source", default=None)
    p_qa.set_defaults(func=cmd_queue_add)
    p_q = sub.add_parser("queue")
    p_q.add_argument("--type", default=None)
    p_q.set_defaults(func=cmd_queue)
    p_qr = sub.add_parser("queue-resolve")
    p_qr.add_argument("name")
    p_qr.set_defaults(func=cmd_queue_resolve)
```

- [ ] **Step 8: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sk_queue.py -v`
Expected: 2 passed.

- [ ] **Step 9: Commit**

```bash
git add scripts/sklib.py scripts/sk tests/test_sklib_queue.py tests/test_sk_queue.py
git commit -m "feat(sk): simple research queue (add/list/resolve), consumed manually in phase 1"
```

---

### Task 9: `sk ship` + GitHub repo + Pages deploy

**Files:**
- Modify: `scripts/sk`
- Create: `.github/workflows/build.yml`

**Interfaces:**
- Produces: `sk ship [MSG]` runs `git add -A && git commit && git pull --rebase && git push` with a simple retry. Deploy workflow builds and publishes `_site/` to Pages on push to `main`. No CNAME.

- [ ] **Step 1: Add `sk ship`**

In `scripts/sk`:
```python
def cmd_ship(args):
    import subprocess
    msg = args.message or "content: update"
    subprocess.call(["git", "add", "-A"])
    subprocess.call(["git", "commit", "-m", msg])
    for _ in range(3):
        subprocess.call(["git", "pull", "--rebase"])
        if subprocess.call(["git", "push"]) == 0:
            return 0
    print("push failed after retries", file=sys.stderr)
    return 1
```
Register:
```python
    p_ship = sub.add_parser("ship")
    p_ship.add_argument("message", nargs="?", default=None)
    p_ship.set_defaults(func=cmd_ship)
```
Commit:
```bash
git add scripts/sk
git commit -m "feat(sk): ship (commit + rebase + push with retry)"
```

- [ ] **Step 2: Create the Pages workflow**

`.github/workflows/build.yml`:
```yaml
name: Build and Deploy
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python build.py
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site/
      - id: deployment
        uses: actions/deploy-pages@v4
```

Commit:
```bash
git add .github/workflows/build.yml
git commit -m "ci: GitHub Pages build-and-deploy workflow (no custom domain)"
```

- [ ] **Step 3: Create the GitHub repo and push**

Run:
```bash
gh repo create skintiers --public --source=. --remote=origin --push
```
Expected: repo created, `main` pushed.

- [ ] **Step 4: Enable Pages with Source = GitHub Actions**

In the repo Settings → Pages, set **Source = GitHub Actions** (not "Deploy from a branch"). (Or `gh api` equivalent.) Then check the Actions tab: the "Build and Deploy" run should succeed.

- [ ] **Step 5: Verify the live site**

Open the Pages URL (`https://<user>.github.io/skintiers/`). Expected: the index renders with Products/Ingredients links. (At this point profiles may be zero until Task 9; the index + empty listings must still render.)

---

### Task 10: First real content via the queue → stubs → research subagent

> This task produces markdown *content*, not code — it follows the anti-hallucination discipline and two-pass review, NOT TDD. Do not fabricate anything; when a claim lacks 3 independent primary sources, mark it `unresolvable` or leave it out. The queue is consumed **manually via a subagent** (no cron in Phase 1).

**Files:**
- Modify: `data/queue.yaml`
- Create: `data/products/<product-slug>.md`, `data/ingredients/<active-slug>.md` (one product + its key actives)

**Frontmatter shape for every profile authored here:**
```yaml
---
name: Niacinamide
slug: niacinamide
type: ingredient        # or product
status: draft           # stub | draft | published | flagged
updated: 2026-07-26
analyzed: 2026-07-26     # null on a bare stub
---
```

- [ ] **Step 1: Pick the first product and seed the queue**

Choose ONE well-studied product with real primary literature (confirm with the user): **The Ordinary Niacinamide 10% + Zinc 1%**, **CeraVe Moisturizing Cream** (ceramides), or a **tretinoin 0.025% cream**. Identify its 2–4 key actives. Seed the queue:
```bash
.venv/bin/python scripts/sk queue-add "<Product Name>" --type product --priority 9
.venv/bin/python scripts/sk queue-add "<Active 1>" --type ingredient --priority 8 --from "<product-slug>"
# ...one per active
.venv/bin/python scripts/sk queue     # confirm, priority-sorted
```

- [ ] **Step 2: Prolifically create stubs for the actives (so links resolve)**

For each active, create a `stub` profile immediately so the product's `[[active-slug]]` links resolve from the moment the product page exists. Each stub file:
```markdown
---
name: <Active>
slug: <active-slug>
type: ingredient
status: stub
updated: 2026-07-26
analyzed: null
---

Stub — placeholder link target; queued for research.
```

- [ ] **Step 3: Consume the queue with a research subagent**

Dispatch a research subagent (Agent tool) to take the **highest-priority pending** queue item and research it **sources-first** under the 3-independent-primary rule (peer-reviewed studies; manufacturer INCI/official page for *composition only*; regulator filings; tier-1 press — WebFetch every URL). It returns the verified sources + drafted profile content, records effect-size and evidence-quality tiers with **named comparators**, then the item is marked done: `sk queue-resolve "<name>"`. Repeat until the product + its actives are researched.

- [ ] **Step 4: Write the profiles (upgrade stubs → draft)**

Upgrade each active's stub to a full **draft**: mechanism, effect-size tier, evidence-quality tier (with comparators), `## Sources` footnotes; set `analyzed` to today. Write the product **draft** with the Product anatomy from the spec — **The Rubric** (two-axis grade + one-line justification), **What We Actually Know**, **Evidence tiered & labeled** (clinical → derm → aesthetician → influencer), **Manufacturer Claims** (quarantined), **Ingredient breakdown** (each active `[[linked]]` with its grade), **Comparators**, **Sources**. Link actives via `[[active-slug]]`.

- [ ] **Step 5: Lint every profile**

Run: `.venv/bin/python scripts/sk lint <slug>` for the product and each ingredient.
Expected: exit 0 (clean) for all. Fix any errors/warnings.

- [ ] **Step 6: Two-pass review, then publish**

Verification pass: re-fetch every URL; confirm quotes verbatim; every table row cited; percentages show denominators. Only at 10/10 (publishing stamps `analyzed`):
```bash
.venv/bin/python scripts/sk publish <active-slug>   # each active
.venv/bin/python scripts/sk publish <product-slug>
```

- [ ] **Step 7: Ship and verify live**

Run: `.venv/bin/python scripts/sk ship "content: first product + ingredient profiles"`
Then watch the Action and open the live Pages URL. Expected: the product profile renders with its status badge and freshness dates, its ingredient cross-links resolve, and it appears in the Products listing.

---

## Self-Review

**Spec coverage (Phase 1 scope only):** entity folders (Tasks 1, 10) ✓; flat-markdown-first + minimal frontmatter with the status ladder and `updated`/`analyzed` (Global Constraints, Tasks 4, 6, 7) ✓; status badge + freshness dates shown on every profile (Task 6 template) ✓; stubs render as link targets, all statuses build (Tasks 6, 10) ✓; labeled-tier rubric + tiered/labeled evidence in prose (Task 10) ✓; footnote/anti-hallucination lint gate (Task 4) ✓; simple research queue consumed manually by a subagent, no cron (Tasks 8, 10) ✓; static build + Pages deploy, no custom domain (Tasks 6, 9) ✓; broken xref → plain text (Tasks 5, 6) ✓; `sk` CLI (Tasks 3, 4, 6, 7, 8, 9) ✓; medical disclaimer in footer (Task 6 template) ✓. Deferred to later phases (no tasks, by design): crons, the scraper/freshness feed, the other 5 entity types, the structured metadata layer, the routine builder, the effect×evidence visual, and product badges.

**Placeholder scan:** every code/test step contains complete code; the only "choose here" points (Task 9 product choice) are genuine content decisions flagged for the user, not code placeholders.

**Type consistency:** `load_profiles`/`filter_published`/`find_profile`/`check_profile`/`render_markdown`/`linkify_xrefs`/`set_status(path, status, mark_analyzed=False)`/`load_queue`/`save_queue`/`queue_add`/`queue_resolve` names and signatures are defined in Tasks 2/4/5/7/8 and used consistently in `sk` and `build.py`. `build.py` renders **all** profiles via `load_profiles` (not `filter_published`, which is retained/tested for later-phase metrics). Env vars (`SK_DATA`/`SK_OUTPUT`/`SK_TEMPLATES`/`SK_STATIC`) are consistent across `sklib`, `build.py`, and tests. Frontmatter fields (`name`/`slug`/`type`/`status`/`updated`/`analyzed`) are consistent throughout; `status` values are `stub`/`draft`/`published` everywhere (Global Constraints, Task 4 `VALID_STATUS`, template badges).

## Verification (end-to-end)

- `.venv/bin/pytest tests/ -v` → all green.
- `.venv/bin/python build.py` → `_site/` renders; broken xrefs are plain text.
- `.venv/bin/python scripts/sk lint <slug>` → exit 0 on the published profiles.
- GitHub Action succeeds; the live Pages URL serves the first product profile with resolving ingredient cross-links.
