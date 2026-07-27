# Reference Files from Seedlist

Verbatim copies from `~/Projects/seedlist/`. Use these as **patterns to adapt**, not files to paste. Every one embodies decisions specific to Seedlist's schema (firms/investors/startups) — you'll need to translate to your topic.

| File | Original path | Purpose |
|------|---------------|---------|
| `seedlist_CLAUDE.md` | `CLAUDE.md` | The ~900-line master instruction file. Skim its structure. |
| `seedlist_build.py` | `build.py` | Static site generator. ~1500 lines. Read when authoring your own. |
| `seedlist_sl.py` | `scripts/sl` | The `sl` CLI toolkit. ~3400 lines. Reference when building your topic's CLI. |
| `seedlist_github_action_build.yml` | `.github/workflows/build.yml` | Build + deploy workflow. Copy-adapt. |
| `seedlist_requirements.txt` | `requirements.txt` | Python deps. Usable as-is. |
| `seedlist_lesson_example.md` | `_lessons/2026-03-13-first-batch-review.md` | Format for `_lessons/` files. |
| `seedlist_sample_investor_profile.md` | `data/investors/adam-dangelo.md` | Shape of a well-formed profile with citations. |

## How to use these

- **Do NOT** paste `seedlist_CLAUDE.md` into your project. Half of it is startup-specific vocabulary that will confuse a skincare agent.
- **DO** copy the structure: table of contents, section on schema, section on workflow, section on anti-hallucination rules, etc.
- **DO** copy `seedlist_github_action_build.yml` almost verbatim (adjust CNAME).
- **DO** copy `seedlist_requirements.txt` verbatim initially — add your topic-specific libs as needed.
- **DO** use `seedlist_lesson_example.md` format for every `_lessons/` file you write.
