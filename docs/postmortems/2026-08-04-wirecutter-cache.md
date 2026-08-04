# Postmortem: unverifiable Wirecutter quotes → local source cache

**Date:** 2026-08-04
**Trigger:** The Youth To The People product page shipped with ~1/3 of its content resting on verbatim
NYT Wirecutter quotes that neither the Opus critic nor the main loop could re-fetch (WebFetch is blocked
for nytimes.com and, intermittently, web.archive.org). The content had to be stripped late. Wirecutter had
been a recurring source (Medik8, Trader Joe's pages) with the same on-again/off-again access.

## Five whys
1. Why couldn't we verify it? WebFetch can't reach nytimes.com (paywall/bot-protection).
2. Why did unverifiable verbatim quotes enter the draft? The drafter got the content once (different tools:
   likely the Apify browser), but we cannot confirm a true fetch vs. reconstruction — we trust self-reports.
3. Why does verification depend on re-fetching? We keep only a URL + a claimed quote, never the retrieved
   bytes. "Verify" == "re-fetch and re-check", which breaks for intermittently-reachable sources.
4. Why nothing to fall back on? We don't persist fetched web sources; `research-cache/` was scoped only to
   the video pipeline's transcripts/PDFs.
5. Why never generalized? The anti-hallucination design assumed sources are re-fetchable on demand — true for
   PubMed/.gov/EUR-Lex, false for paywalled editorial, retailers, and intermittently archive.org. Availability
   is really (tool × session × time); we treated it as reliable.

**Root cause:** an intermittent external dependency treated as reliable, plus trust in agent self-reports —
so a page can carry load-bearing quotes that can't be re-verified or distinguished from fabrication.

## Fix (shipped 2026-08-04)
`scripts/source_cache.py` — a local verbatim cache of fetched source text.
- **Anti-bloat by construction:** only `sklib.classify_domain(url) == 'unknown'` sources are cached (the
  "verify manually" set). Durable primaries re-fetch on demand (skipped); aggregators aren't citable (skipped).
  `gc()` deletes any cache file no page cites. The cache converges to {cited, unknown-class sources} — bounded
  by the site, never a mirror of the internet. Text only; gitignored under `research-cache/web/`.
- **Workflow:** drafters `source_cache.py put <url>` right after fetching a non-primary source they cite;
  critics `get <url>` and verify against the cache first, live-fetching only on a miss.
- **Policy (writing-guide):** a load-bearing verbatim quote from a non-primary source requires a cache entry;
  a source that can neither be re-fetched nor cached is limited to corroborated facts, never verbatim quotes.

## What it does and does not fix
Fixes: re-verification no longer depends on the live site; an audit trail of exactly what was retrieved;
bridges the tool-availability gap (drafter has Apify, critic may not). Does NOT fix: a hard-paywalled source
no tool ever reaches still can't be cited verbatim; and caching alone can't prove non-fabrication — which is
why the policy also requires a *second independently fetchable corroborator* for load-bearing figures.
