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


_SOURCES_HEADING_RE = re.compile(r"^##\s+sources\s*$", re.IGNORECASE | re.MULTILINE)
_URL_RE = re.compile(r"https?://\S+")


def _sources_block(content):
    """Return the text of the ## Sources section (footnote defs), or ""."""
    m = _SOURCES_HEADING_RE.search(content)
    if not m:
        return ""
    rest = content[m.end():]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def _source_defs(content):
    """Return the raw text of each footnote definition line in ## Sources."""
    return [ln for ln in _sources_block(content).splitlines() if _DEF_RE.match(ln)]


def extract_source_urls(content):
    """Every URL found in ## Sources footnote definition lines."""
    urls = []
    for line in _source_defs(content):
        m = _URL_RE.search(line)
        if m:
            urls.append(m.group(0))
    return urls


_PRIMARY_DOMAINS = (
    "pubmed.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
    "cochrane.org", "cochranelibrary.com", "clinicaltrials.gov", ".fda.gov",
    "dailymed.nlm.nih.gov", "jamanetwork.com", "thelancet.com", "nature.com",
    "nejm.org", "bmj.com", "sciencedirect.com", "onlinelibrary.wiley.com",
    "karger.com", "dpcj.org", "jaad.org", "ema.europa.eu", "bfr.bund.de",
    "who.int", "medicaljournals.se",
)
_AGGREGATOR_DOMAINS = (
    "ewg.org", "incidecoder.com", "wikipedia.org", "reddit.com", "healthline.com",
    "webmd.com", "byrdie.com", "realself.com", "medium.com", "blogspot.",
    "amazon.", "sephora.", "ulta.",
)


def classify_domain(url):
    """Classify a URL as 'primary', 'aggregator', or 'unknown' (case-insensitive)."""
    u = url.lower()
    if any(d in u for d in _AGGREGATOR_DOMAINS):
        return "aggregator"
    if any(d in u for d in _PRIMARY_DOMAINS):
        return "primary"
    return "unknown"


_REQUIRED_SECTIONS = ("The Rubric", "The Evidence", "Sources")
_QUARANTINE_SECTIONS = ("Manufacturer Claims", "Common Marketing Claims")
_STAT_RE = re.compile(r"\d+(\.\d+)?\s*%|\bn\s*=\s*\d+|95%\s*C[rI]|\bP\s*[<=]\s*\.?\d")
# Uncited-statistic check fires only under evidence-bearing section headings.
_EVIDENCE_SECTION_KEYWORDS = ("rubric", "evidence", "what we actually know")


def _has_section(content, name):
    name = name.lower()
    for line in content.splitlines():
        if line.startswith("## ") and name in line.lower():
            return True
    return False


def verify_profile(metadata, content):
    """Deterministic, offline source-quality / structure / uncited-stat checks."""
    errors, warnings = [], []

    # Source quality (D1) — runs for stubs and non-stubs alike.
    for line in _source_defs(content):
        n = _DEF_RE.match(line).group(1)
        m = _URL_RE.search(line)
        if not m:
            errors.append(f"source [^{n}] has no URL")
            continue
        url = m.group(0)
        kind = classify_domain(url)
        if kind == "aggregator":
            errors.append(f"aggregator/marketing source cited as evidence: {url}")
        elif kind == "unknown":
            warnings.append(f"source domain not on primary allowlist (verify manually): {url}")

    if metadata.get("status") == "stub":
        return errors, warnings

    # Required sections (D5).
    for name in _REQUIRED_SECTIONS:
        if not _has_section(content, name):
            errors.append(f"missing required section: {name}")
    if not any(_has_section(content, q) for q in _QUARANTINE_SECTIONS):
        warnings.append("no quarantined marketing-claims section")

    # Uncited statistics (D1/D2) — only in evidence-bearing sections, outside ## Sources.
    body = content
    m = _SOURCES_HEADING_RE.search(body)
    if m:
        body = body[: m.start()]
    current_section = ""
    for para in re.split(r"\n\s*\n", body):
        if not para.strip():
            continue
        # Track the nearest preceding ## / ### heading (may appear in this block).
        for line in para.splitlines():
            if line.startswith("## ") or line.startswith("### "):
                current_section = line
        section_lc = current_section.lower()
        if not any(k in section_lc for k in _EVIDENCE_SECTION_KEYWORDS):
            continue
        if _STAT_RE.search(para) and not _REF_RE.search(para):
            snippet = " ".join(para.split())[:60]
            warnings.append(f"uncited statistic in paragraph: '{snippet}...'")

    return errors, warnings


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


def review_verdict(data_dir, slug):
    """Return the review verdict for slug from review-log.yaml, or None if absent.

    review-log.yaml maps slug -> {last_reviewed, score, verdict, note}.
    """
    path = pathlib.Path(data_dir) / "review-log.yaml"
    if not path.exists():
        return None
    data = _yaml.safe_load(path.read_text()) or {}
    entry = data.get(slug)
    if not isinstance(entry, dict):
        return None
    return entry.get("verdict")


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
