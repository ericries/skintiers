# The private research cache (`research-cache/`)

A local, **gitignored** verbatim cache of source material we fetch while verifying
claims: video transcripts, PDFs of papers, and saved web fetches. Its whole job is
so we **never re-fetch the same source** when re-checking a fact.

## Why it is private (gitignored, never on the site)

- **Not on the public site.** `build.py` only copies `static/` and renders `data/`
  into `_site/`; `research-cache/` is neither, so it is never published.
- **Not committed to git.** It holds verbatim copyrighted material (full transcripts,
  paper PDFs). Storing that in the (potentially public) repo would be redistribution,
  so it is in `.gitignore`. It is a working cache, local to the machine.

## Layout

```
research-cache/
  transcripts/   <video-id>.json  (canonical) + <video-id>.txt (readable)
  pdfs/          <slug-or-doi>.pdf  + optional .txt extraction
  web/           <16-hex-url-hash>.md  (saved article/brand-page fetches, keyed by URL)
```

## Transcripts (automated)

`scripts/yt_transcript.py` reads and writes `transcripts/` automatically: it caches
by YouTube video id, so the second call for a video is served from disk (`[cached]`),
never the network. Force a re-fetch with `--refresh`.

```
python scripts/yt_transcript.py <youtube-url-or-id>     # fetch (or cache hit) + print
```

## Web fetches (`scripts/source_cache.py`, keyed by URL)

`web/` is managed by `scripts/source_cache.py`, not by hand. Filenames are **not**
descriptive: the key is `sha1(stripped-url)[:16]`, so you look an entry up by its exact
URL rather than by guessing a slug.

```
# read a cached source (read-only; -B avoids writing .pyc)
.venv/bin/python -B scripts/source_cache.py get '<exact-source-url>'

# store one (pipe the fetched text in; it refuses empty content)
curl -sL -A "Mozilla/5.0" '<url>' | .venv/bin/python scripts/source_cache.py put '<url>'
```

Each stored file opens with a `cached-source` header recording the URL, the key, and the
content length. The URL must match the footnote's URL character for character, or the hash
differs and you get a MISS.

**Only non-primary sources are cached.** `put` classifies the domain via
`sklib.classify_domain` and stores only `unknown`-class sources (brand stores, retailer and
article pages) -- the ones that bot-block or disappear. Durable primaries (PubMed, DailyMed,
`.gov`, journals) are skipped on purpose because they re-fetch cleanly, so **a cache miss on
a PubMed or DailyMed citation is not a missing source.** Aggregators are refused outright.

A load-bearing verbatim quote from an `unknown`-class source requires a cache entry, so that
a later reviewer can verify it even if the live page changes or blocks.

PDFs under `pdfs/` are still saved manually with a descriptive name. The cache is verbatim:
do not edit stored copies; treat them as the source of record.

## Override location

Set `SK_RESEARCH_CACHE` to point the cache elsewhere (used by tests).
