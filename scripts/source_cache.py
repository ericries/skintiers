#!/usr/bin/env python3
"""Local verbatim cache of citable-but-not-durably-re-fetchable web sources.

Verification (a critic re-checking a quote) must not depend on a live site that is
paywalled / bot-protected / intermittent (NYT/Wirecutter, retailer product pages,
archived brand pages). When such a source is fetched, its TEXT is saved here so any
later agent verifies against the exact bytes that were retrieved - not a re-fetch that
may fail.

ANTI-BLOAT (the whole point): only sources classified 'unknown' by sklib.classify_domain
are cacheable. That is precisely the set that needs it:
  - 'primary'    (PubMed, .gov, EUR-Lex, journals): durably re-fetchable -> never cached.
  - 'aggregator' (Sephora, Amazon, Wikipedia): not citable here at all   -> never cached.
  - 'unknown'    (editorial/retailer/brand/archive): intermittent + citable -> cached.
Combined with gc(), which deletes any cache file whose URL is no longer cited by ANY
page, the cache converges to exactly {cited, unknown-class sources} - bounded by the
site, never a mirror of the internet. Only cache sources you actually CITE, not pages
you merely browse. Lives in gitignored research-cache/web/. Text only (no assets).

CLI:
    <fetched text on stdin> | python scripts/source_cache.py put <url>
    python scripts/source_cache.py get <url>            # exact cached bytes
    python scripts/source_cache.py get <url> --text     # VERIFY QUOTES WITH THIS:
        # strips markup so a quote that spans tags still matches; keeps ld+json
    python scripts/source_cache.py gc            # prune cache files no page cites
"""
import glob
import hashlib
import html as _html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sklib  # noqa: E402

CACHE_DIR = sklib.ROOT / "research-cache" / "web"
_URL_RE = re.compile(r"https?://[^\s)<>\]\"']+")


def should_cache(url):
    """True only for 'unknown'-class domains - the sources that truly require it."""
    return sklib.classify_domain(url) == "unknown"


def cache_key(url):
    return hashlib.sha1(url.strip().encode("utf-8")).hexdigest()[:16]


def path_for(url, cache_dir=None):
    d = pathlib.Path(cache_dir) if cache_dir else CACHE_DIR
    return d / f"{cache_key(url)}.md"


def put(url, content, cache_dir=None):
    """Cache content for url iff it is an 'unknown'-class source. Returns the path, or
    None if the domain is re-fetchable/non-citable (deliberately not cached)."""
    if not should_cache(url):
        return None
    if not (content or "").strip():
        raise ValueError("refusing to cache empty content")
    f = path_for(url, cache_dir)
    f.parent.mkdir(parents=True, exist_ok=True)
    header = (f"<!-- cached-source\nurl: {url}\nkey: {cache_key(url)}\n"
              f"bytes: {len(content)}\n-->\n\n")
    f.write_text(header + content)
    return f


def as_text(content):
    """Render a cached HTML page down to the visible text a quote was read from.

    A cache entry is often raw HTML, and markup interleaves the prose: the phrase
    "97.4% saw visible improvement" is stored as "97.4%</p><p>saw visible...".
    A critic checking a verbatim quote against the raw bytes therefore gets a FALSE
    NEGATIVE and may "correct" an accurate quote. Script and style bodies go, but
    any application/ld+json block is KEPT, because structured product data (price,
    currency, variant name) is cited from it and lives nowhere else on the page."""
    if not content:
        return ""
    if not re.search(r"<\s*(html|!doctype html|div|p|body)\b", content, re.I):
        return content  # already plain text; leave it exactly as cached
    keep = re.findall(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        content, flags=re.S | re.I)
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", content,
                  flags=re.S | re.I)
    body = _html.unescape(re.sub(r"<[^>]+>", " ", body))
    # Collapse ALL whitespace runs, not just spaces. A removed tag often sat on its
    # own line, so "97.4%</p>\n<p>saw" becomes "97.4% \n saw" and a grep for the
    # real sentence still misses. Readability is not the job here; matching is.
    body = re.sub(r"\s+", " ", body)
    out = body.strip()
    if keep:
        out += "\n\n<!-- preserved application/ld+json blocks -->\n" + "\n".join(
            k.strip() for k in keep)
    return out


def get(url, cache_dir=None, text=False):
    f = path_for(url, cache_dir)
    if not f.exists():
        return None
    c = f.read_text()
    return as_text(c) if text else c


def cited_urls(data_dir=None):
    dd = pathlib.Path(data_dir) if data_dir else sklib.DATA_DIR
    urls = set()
    # .yaml as well as .md: a source can back a non-page fact, e.g. the credential
    # in data/video-sources.yaml that a video card prints verbatim. Globbing only
    # *.md meant gc() pruned the sole evidence behind a claim about a real person.
    for pattern in ("*.md", "*.yaml"):
        for f in glob.glob(str(dd / "**" / pattern), recursive=True):
            for u in _URL_RE.findall(pathlib.Path(f).read_text(encoding="utf-8")):
                urls.add(u.rstrip(".,);'\""))
    return urls


def gc(cache_dir=None, data_dir=None):
    """Delete cache files whose URL is no longer cited by any page. Returns removed names."""
    d = pathlib.Path(cache_dir) if cache_dir else CACHE_DIR
    if not d.exists():
        return []
    keep = {cache_key(u) for u in cited_urls(data_dir) if should_cache(u)}
    removed = []
    for f in sorted(d.glob("*.md")):
        if f.stem not in keep:
            f.unlink()
            removed.append(f.name)
    return removed


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "put" and len(sys.argv) > 2:
        f = put(sys.argv[2], sys.stdin.read())
        print(f"cached -> {f.relative_to(sklib.ROOT)}" if f
              else f"skip (re-fetchable or non-citable domain, not cached): {sys.argv[2]}")
    elif cmd == "get" and len(sys.argv) > 2:
        c = get(sys.argv[2], text="--text" in sys.argv[3:])
        if c is None:
            print("MISS (no cache for this url)", file=sys.stderr)
            sys.exit(1)
        sys.stdout.write(c)
    elif cmd == "gc":
        removed = gc()
        print(f"pruned {len(removed)} orphan cache file(s)"
              + (": " + ", ".join(removed) if removed else ""))
    else:
        print("usage: source_cache.py put <url> (text on stdin) | "
              "get <url> [--text] | gc",
              file=sys.stderr)
        sys.exit(2)
