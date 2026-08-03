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
  web/           <slug>.md / .html  (saved article/search fetches)
```

## Transcripts (automated)

`scripts/yt_transcript.py` reads and writes `transcripts/` automatically: it caches
by YouTube video id, so the second call for a video is served from disk (`[cached]`),
never the network. Force a re-fetch with `--refresh`.

```
python scripts/yt_transcript.py <youtube-url-or-id>     # fetch (or cache hit) + print
```

## PDFs and web fetches (manual, for now)

When verifying a claim against a paper PDF or an article, save the fetched copy under
`pdfs/` or `web/` with a descriptive name so the next verification reads from disk.
The cache is verbatim: do not edit the stored copies; treat them as the source of record.

## Override location

Set `SK_RESEARCH_CACHE` to point the cache elsewhere (used by tests).
