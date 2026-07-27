# Red/Green TDD Workflow

Every piece of tooling in this project — `build.py`, `scripts/sl`, `scripts/scrape_*.py`, YAML validators, cross-reference checkers — must be built test-first. Red → Green → Refactor. No exceptions.

## Why TDD here (and where it doesn't apply)

**TDD DOES apply to:**
- `build.py` and its taxonomy/template code
- Every `scripts/sl` subcommand (lint, publish, xref, etc.)
- Every `scripts/scrape_*.py` (RSS parser, deduper, date extractor)
- YAML frontmatter validators
- Slug uniqueness / cross-reference checkers
- Any function that transforms data

**TDD does NOT apply to:**
- The data itself (markdown profiles). Data has a different verification pattern: the 3-source rule in `03_ANTI_HALLUCINATION_RULES.md`.
- Prose sections of profiles. Reviewed by the two-pass workflow, not unit tests.

## The Red/Green cycle

For every new tool or subcommand:

### 1. Red — write a failing test first
Create `tests/test_<feature>.py`. Write ONE test that expresses the desired behavior. Run it. Confirm it FAILS with a clear error message (import error, assertion mismatch, etc.).

```python
# tests/test_slug_validator.py
def test_slug_kebab_case_only():
    from scripts.sl import validate_slug
    assert validate_slug("valid-slug-here") is True
    assert validate_slug("Invalid_Slug") is False
    assert validate_slug("Invalid Slug") is False
```

Run:
```
$ .venv/bin/python -m pytest tests/test_slug_validator.py -v
FAILED — ImportError: cannot import name 'validate_slug' from 'scripts.sl'
```

**The failure is the point.** It proves the test can detect the absence of the feature.

### 2. Green — write the minimum code to pass
Now write the tiniest implementation that makes the test green. No extra features.

```python
# scripts/sl
def validate_slug(slug: str) -> bool:
    import re
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug))
```

Run:
```
$ .venv/bin/python -m pytest tests/test_slug_validator.py -v
PASSED
```

### 3. Refactor — clean up while green
Rename, extract helpers, remove duplication — but the test must stay green throughout. Run tests after every change.

### 4. Add the next test
Now add the NEXT case (edge case, error case, another normal case). It should fail. Make it pass. Refactor. Repeat.

## Sample TDD sequence for a real tool

Task: build `scripts/sl lint SLUG` that checks a profile for citation issues.

Test 1 (Red): Test that lint returns exit code 0 on a well-formed profile
Test 2 (Red): Test that lint returns exit code 1 when the profile has a duplicate URL in Sources
Test 3 (Red): Test that lint returns exit code 1 when a footnote is referenced but not defined
Test 4 (Red): Test that lint returns exit code 2 (warning) when a Portfolio row has no year
Test 5 (Red): Test that lint accepts `--no-fetch` to skip WebFetch verification (for CI)

Each is one commit. Each shows Red → Green in the commit history.

## Rules

### R1. Never write code without a failing test first
If you're tempted to skip because "it's obvious", stop. Write the test. Watch it fail. Then write the code.

### R2. One test at a time
Don't write 10 tests up front. Write one, make it pass, write the next. Otherwise you'll lose the discipline.

### R3. Tests are documentation
A well-named test file is the best docs for what a tool does. `test_lint_flags_duplicate_urls` is worth more than a README paragraph.

### R4. Run the full test suite before every commit
```
$ .venv/bin/python -m pytest tests/ -v
```
If anything fails, do NOT commit. Fix or revert.

### R5. Never skip a test to make CI pass
If a test is failing legitimately, fix the code. If the test itself is wrong, delete or rewrite it — don't `@pytest.skip` it.

### R6. Prefer integration tests for `sl` subcommands
For CLI subcommands, an integration test that runs the actual `sl` binary against a temp git repo is more valuable than mocked unit tests. Example:
```python
def test_sl_publish_moves_status(tmp_path):
    # Set up a tiny git repo with one draft profile
    # Run: sl publish some-slug
    # Assert: profile now has status: published
    # Assert: git log shows a new commit
```

### R7. Web-fetching in tests
Don't hit the live web in tests. Use fixtures with recorded responses (`responses` library or manual JSON fixtures). Only the actual runtime should call the network.

### R8. Test the build
Have a `test_build_smoke.py` that runs `python build.py` against a fixture repo with 3-5 sample profiles and asserts `_site/` contains expected files. Catches template regressions immediately.

## When to write a test AFTER writing code

Only for exploratory spikes you throw away. If you keep the code, retroactively write the test. Do not merge untested code.

## What to test for `build.py` specifically

- Only `status: published` profiles produce HTML files
- Frontmatter is parsed correctly
- Footnotes render as links
- Cross-references to non-existent slugs render as plain text (not broken links)
- Sector taxonomy roll-up works
- Feed page shows entries in reverse chronological order
- Build is deterministic (same input → identical output)

## What to test for `scripts/scrape_*.py`

- Parses each source RSS feed without crashing
- Deduplicates against `data/pending-rounds.yaml`
- Extracts dates from every source's date format
- Extracts entity names correctly (test with edge cases: names with apostrophes, non-ASCII, "&")
- Handles feed downtime gracefully (returns empty, doesn't corrupt yaml)

## What to test for `scripts/sl` subcommands

- Every subcommand has at least one happy-path test
- Destructive commands (publish, flag, draft) have tests confirming they update the correct file
- Commands that commit have tests confirming the commit exists and the message format is correct
- `--dry-run` flags actually don't modify state

## The test pyramid for this project

```
              ▲
             /=\        1-2 end-to-end tests (build a whole site from fixtures)
            /===\       
           /=====\      5-10 integration tests (sl subcommand vs temp repo)
          /=======\     
         /=========\    20+ unit tests (slug validator, footnote parser, etc.)
        /___________\   
```

## When you're stuck

If you can't figure out how to test something, that's a design signal. The code is probably doing too many things. Extract a pure function, test that. The remainder is often just I/O — an integration test covers it.
