# When to Ask the User

You are an agent. You will be tempted to make decisions to keep momentum. **Some decisions cascade into weeks of rework if wrong.** This doc is your triage guide: when to ask, when to decide.

## Always ask

### Schema decisions
- What are the entity types? Which is primary?
- What frontmatter fields does each type need?
- What body sections are required?
- What's the taxonomy (sectors/categories/mechanisms/etc.)?
- What is explicitly out of scope?

Schema decisions after the first 20 profiles are brutal. Ask up front. See `05_ADAPTING_TO_YOUR_TOPIC.md` for the full list.

### Naming
- Repo name
- Project name (differs from repo name if branded)
- CLI tool name (`sl` → what for your topic?)
- Slug scheme (kebab-case? include brand prefix? include category?)

### Sourcing decisions
- Which sources are considered "primary"? (Depends on topic — Cochrane is primary for medical claims, not for skincare marketing claims.)
- Which sources are on the trust hierarchy? Which are aggregator-only?
- Are user reviews acceptable sources? Under what conditions?

### Legal/ethical
- Data licensing (MIT? CC-BY-SA? CC-BY-NC?)
- Attribution policy for user-submitted content
- How to handle takedown requests
- Personal data policy (naming individuals? photos?)
- Affiliate links / commercial policy

### Editorial policy
- Is criticism of brands/products acceptable? Where's the line?
- How to handle contested claims (contradicting studies)?
- Should regulator warnings be listed prominently?

### Freshness feed sources
- Which RSS feeds / news sites to include?
- Which ones does the user trust vs distrust?
- Rate limits / TOS concerns for scraping?

### Destructive or high-blast-radius actions
- Any `git reset --hard`, `git push --force`, `rm -rf`
- Any change to published profiles (removing content that's been live)
- Any change to CLAUDE.md core rules
- Enabling branch protection / merge policies
- Changing the license after files exist

## Decide on your own (with sensible defaults)

### Trivial format choices
- Indentation, quote style within body markdown
- Order of frontmatter fields (put required ones on top)
- Whether to put footnotes at the end of each section or the end of the profile (default: end of profile)

### Tooling additions
- Adding a new `sl` subcommand for a repeated operation you notice
- Writing a test
- Adding a lint check
- Refactoring internal code

### Small workflow choices during autonomous batches
- Which of two similar candidates to research first
- Whether to skip a candidate that has only 2 sources
- Which pending fact to tackle first in a fact-spec sweep

## Ask when uncertain, not when annoying

The user watches the terminal but doesn't want to reply to every question. Rules for asking well:

1. **Batch questions.** Save 3-5 questions and ask together, not one at a time.
2. **Provide options.** "Should I use A or B?" not "How should I handle X?" The former is answerable in 3 seconds.
3. **State your recommendation.** "I'll use A unless you object" is better than a purely open question, if you're confident.
4. **Give context.** Include why the question matters. "Schema decision — will affect all future profiles."
5. **Don't ask during a live agent run.** Save for the top-of-batch check-in.

## Red flags — STOP and ask

If you catch yourself thinking any of these, stop and ask:

- "I'll just guess and it's easy to change later" (schema mistakes are NOT easy to change later)
- "The user probably meant X" (they might have meant Y — ask)
- "This entity has only 2 sources but I really want to publish" (leave it out)
- "The naming convention is unclear but I'll pick something" (ask — inconsistency multiplies)
- "I should probably `git reset --hard` to clean this up" (never without permission)
- "This lint failure seems pedantic, I'll `--no-verify`" (never without permission)
- "The user hasn't approved this schema field but I need it" (ask)

## When there is no answer

Sometimes the user says "figure it out" or is unreachable during an autonomous run. In that case:

1. Pick the option most consistent with existing patterns in seedlist's reference files
2. Document the decision in `_lessons/YYYY-MM-DD-decisions.md` with your reasoning
3. Flag it in your next status line: "Decided X (no user input available); mark for review."

## The one question you must always ask up front

Before touching any code or data on a new topic:

> "What is the primary entity type for this project, and what is the 'inferred X' — the counted data that will produce the primary analytical signal per profile?"

If you can't answer this crisply, do NOT proceed. Ask the user. Discuss until the answer is clear. Then move forward.
