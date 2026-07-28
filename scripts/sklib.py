"""SkinTiers shared helpers. Pure, importable, test-first."""
import os
import pathlib

import frontmatter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = pathlib.Path(os.environ.get("SK_DATA", ROOT / "data"))
OUTPUT_DIR = pathlib.Path(os.environ.get("SK_OUTPUT", ROOT / "_site"))
TEMPLATES_DIR = pathlib.Path(os.environ.get("SK_TEMPLATES", ROOT / "templates"))
STATIC_DIR = pathlib.Path(os.environ.get("SK_STATIC", ROOT / "static"))

ENTITY_TYPES = ("product", "ingredient", "condition", "goal")
# Gated profile types: they have their own research queues/crons but are drafted
# and human-signed-off rather than auto-published. Valid in frontmatter; they are
# cited roll-ups (a brand portfolio, a person's biography, a study writeup), not
# graded like products/ingredients, so they carry no Rubric/Evidence structure.
GATED_TYPES = ("brand", "person", "study")
PROFILE_TYPES = ENTITY_TYPES + GATED_TYPES


def load_profiles(data_dir):
    data_dir = pathlib.Path(data_dir)
    posts = []
    for md in sorted(data_dir.glob("*/*.md")):
        posts.append(frontmatter.load(md))
    return posts


def filter_published(posts):
    return [p for p in posts if p.get("status") == "published"]


def _type_rank(typ):
    try:
        return ENTITY_TYPES.index(typ)
    except ValueError:
        return len(ENTITY_TYPES)


def build_tag_index(posts):
    """Map each tag slug -> [posts declaring it], ordered by (type, name).

    A profile declares tags via a `tags:` frontmatter list. Profiles with no
    `tags` contribute nothing. Type order follows ENTITY_TYPES.
    """
    index = {}
    for post in posts:
        for tag in post.get("tags") or []:
            index.setdefault(tag, []).append(post)
    for tag, tagged in index.items():
        tagged.sort(key=lambda p: (_type_rank(p.get("type")), p.get("name") or ""))
    return index


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
    if metadata.get("type") and metadata["type"] not in PROFILE_TYPES:
        errors.append(f"invalid type: {metadata['type']} (must be one of {PROFILE_TYPES})")
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

    # Structural requirements. Stubs are placeholder pages and stay exempt.
    if metadata.get("status") != "stub":
        if not _has_section(content, "Sources"):
            errors.append("missing required section: Sources")
        # Products carry grades in frontmatter now; the old "## The Rubric"
        # body heading is still accepted for back-compat. A product must have
        # one or the other.
        if metadata.get("type") == "product":
            grades = metadata.get("grades")
            has_grades = isinstance(grades, list) and len(grades) > 0
            if not has_grades and not _has_section(content, "The Rubric"):
                errors.append(
                    "product requires a non-empty 'grades:' frontmatter list "
                    "or a '## The Rubric' section"
                )
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
    # Official US government publishers of federal law/regulation (primary,
    # same class as .fda.gov): the eCFR/CFR and the Federal Register.
    "govinfo.gov", "ecfr.gov", "federalregister.gov",
    # US Securities and Exchange Commission (EDGAR filings, full-text search):
    # a federal regulator/registry, the primary record for corporate facts
    # (ownership, M&A, filings) that brand/company pages rely on.
    ".sec.gov",
    # US National Plan and Provider Enumeration System (CMS/HHS): the
    # authoritative federal registry for clinician identity, license, and
    # specialty, the primary record person pages rely on for credentials.
    "npiregistry.cms.hhs.gov", ".cms.hhs.gov",
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

    # Required sections (D5). Product/ingredient carry the full rubric structure;
    # condition/goal profiles are kept lenient (finalized in content) — Sources is
    # the only hard requirement, with a warning when Evidence is absent.
    if metadata.get("type") in ("condition", "goal"):
        if not _has_section(content, "Sources"):
            errors.append("missing required section: Sources")
        if not _has_section(content, "The Evidence"):
            warnings.append("missing recommended section: The Evidence")
    elif metadata.get("type") in GATED_TYPES:
        # Brand/person/study pages are cited roll-ups, not graded dossiers: the
        # only hard structural requirement is Sources. No Rubric/Evidence, and no
        # quarantine warning (a brand page handles positioning claims in prose).
        if not _has_section(content, "Sources"):
            errors.append("missing required section: Sources")
    else:
        required = _REQUIRED_SECTIONS
        # Products now carry the rubric in `grades:` frontmatter; when present,
        # the "## The Rubric" body section is no longer required (matches
        # check_profile). Ingredients still require it.
        if metadata.get("type") == "product" and metadata.get("grades"):
            required = tuple(s for s in _REQUIRED_SECTIONS if s != "The Rubric")
        for name in required:
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


# --- Anti-AI-ese style linter (advisory) ---------------------------------
# Enforces docs/anti-ai-ese.md. All checks are warnings only. Keep this list
# extendable: add phrases here and they are picked up automatically.
AI_ESE_TERMS = (
    "delve", "tapestry", "testament to", "underscore", "underscores",
    "underscoring", "boasts", "meticulous", "meticulously", "pivotal",
    "showcase", "showcases", "showcasing", "plays a crucial role",
    "plays a vital role", "plays a key role", "plays a pivotal role",
    "plays a significant role", "stands as", "serves as a testament",
    "it is worth noting", "it's worth noting", "it is important to note",
    "in the realm of", "ever-evolving", "game-changer", "game changer",
    "seamless", "leverage", "harness", "unlock", "elevate", "myriad",
    "plethora", "cutting-edge", "state-of-the-art", "rich tapestry",
    "vibrant", "renowned", "nestled", "in the heart of",
    "at the end of the day", "in conclusion", "when it comes to",
    "not just", "it's not just", "not only ... but",
)

_CURLY_QUOTES = ("‘", "’", "“", "”")  # ‘ ’ “ ”
_EM_DASH = "—"  # —
_EN_DASH = "–"  # –


def _term_pattern(term):
    """Word-boundary-ish regex for an AI-ese term.

    Multi-word terms allow flexible whitespace; the special "not only ... but"
    entry matches "not only <anything> but". Hyphenated terms are matched
    literally. Boundaries use \\b where the term edges are word chars.
    """
    if term == "not only ... but":
        return re.compile(r"\bnot only\b.*?\bbut\b", re.IGNORECASE | re.DOTALL)
    parts = [re.escape(w) for w in term.split()]
    core = r"\s+".join(parts)
    left = r"\b" if term[:1].isalnum() else ""
    right = r"\b" if term[-1:].isalnum() else ""
    return re.compile(left + core + right, re.IGNORECASE)


_AI_ESE_PATTERNS = [(t, _term_pattern(t)) for t in AI_ESE_TERMS]


def _style_body(content):
    """The text to lint: everything before the ## Sources heading."""
    m = _SOURCES_HEADING_RE.search(content)
    return content[: m.start()] if m else content


def check_style(content):
    """Advisory anti-AI-ese warnings for a markdown body.

    Excludes the ## Sources section (citation text/URLs are not flagged).
    Returns a list of WARNING strings, one per distinct hit (repeated hits of
    the same term are de-duped into a single line).
    """
    body = _style_body(content)
    warnings = []

    if _EM_DASH in body:
        warnings.append(
            "em dash (—) is AI-ese; use a period/comma/colon/parentheses"
        )
    if _EN_DASH in body:
        warnings.append(
            "en dash (–) is AI-ese; use a period/comma/colon/parentheses"
        )
    if any(q in body for q in _CURLY_QUOTES):
        warnings.append("curly quote; use ASCII")

    for term, pat in _AI_ESE_PATTERNS:
        if pat.search(body):
            warnings.append(f"AI-ese phrase: '{term}'")

    return warnings


import markdown as _markdown

_XREF_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def render_markdown(text):
    # `toc` gives every heading a slug `id` (e.g. "## The Evidence" -> id
    # "the-evidence") so in-page summary links like [phrase](#the-evidence) resolve.
    return _markdown.markdown(text, extensions=["tables", "footnotes", "smarty", "toc"])


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

# Per-type queue storage. Each entity type gets its own prioritized list file
# under data/queues/<plural>.yaml so a research cron can work one list at a time.
TYPE_TO_LIST = {
    "product": "products",
    "ingredient": "ingredients",
    "condition": "conditions",
    "goal": "goals",
    "brand": "brands",
    "person": "people",
    "study": "studies",
}
LIST_TO_TYPE = {v: k for k, v in TYPE_TO_LIST.items()}
QUEUE_TYPES = tuple(TYPE_TO_LIST)

# Types whose profiles a research cron may auto-publish (rather than draft).
AUTOPUBLISH_TYPES = {"product", "ingredient"}


def type_autopublishes(type):
    return type in AUTOPUBLISH_TYPES


def queue_path(data_dir, type):
    """Path to the per-type queue file, data/queues/<plural>.yaml."""
    plural = TYPE_TO_LIST[type]
    return pathlib.Path(data_dir) / "queues" / f"{plural}.yaml"


def load_queue(data_dir, type):
    path = queue_path(data_dir, type)
    if not path.exists():
        return []
    return _yaml.safe_load(path.read_text()) or []


def save_queue(data_dir, type, items):
    path = queue_path(data_dir, type)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_yaml.safe_dump(items, sort_keys=False))


def load_all_queues(data_dir):
    """Return {type: [items]} for all queue types (empty list if file missing)."""
    return {t: load_queue(data_dir, t) for t in QUEUE_TYPES}


def queue_add(data_dir, name, type, priority=5, discovered_from=None, source=None):
    items = load_queue(data_dir, type)
    for it in items:
        if it.get("name") == name and it.get("type") == type:
            return False
    items.append({
        "name": name, "type": type, "priority": int(priority),
        "status": "pending", "discovered_from": discovered_from, "source": source,
    })
    save_queue(data_dir, type, items)
    return True


def queue_next(data_dir, type):
    """Highest-priority PENDING item for a type, FIFO on ties, or None."""
    pending = [it for it in load_queue(data_dir, type) if it.get("status") == "pending"]
    if not pending:
        return None
    # Stable sort on descending priority keeps original (FIFO) order for ties.
    return sorted(pending, key=lambda it: -it.get("priority", 0))[0]


def migrate_queue(data_dir):
    """Split a legacy flat data/queue.yaml into per-type queue files.

    Merges into any existing per-type files, deduping by (name, type) and
    preserving all fields and statuses (including 'done'). Renames the legacy
    file to queue.yaml.migrated. Idempotent: a no-op returning 0 when the
    legacy file is absent. Returns the number of legacy items migrated.
    """
    legacy = pathlib.Path(data_dir) / "queue.yaml"
    if not legacy.exists():
        return 0
    legacy_items = _yaml.safe_load(legacy.read_text()) or []
    buckets = load_all_queues(data_dir)
    seen = {t: {(it.get("name"), it.get("type")) for it in items}
            for t, items in buckets.items()}
    migrated = 0
    for it in legacy_items:
        typ = it.get("type")
        if typ not in TYPE_TO_LIST:
            continue
        key = (it.get("name"), typ)
        if key in seen[typ]:
            continue
        seen[typ].add(key)
        buckets[typ].append(it)
        migrated += 1
    for typ, items in buckets.items():
        if items:
            save_queue(data_dir, typ, items)
    legacy.rename(legacy.with_suffix(".yaml.migrated"))
    return migrated


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


def queue_resolve(data_dir, name, type=None):
    """Mark items named `name` as done. If `type` is given, act only on that
    type's file; otherwise search all queue files. Returns True if anything
    changed."""
    types = [type] if type is not None else list(QUEUE_TYPES)
    changed = False
    for typ in types:
        items = load_queue(data_dir, typ)
        touched = False
        for it in items:
            if it.get("name") == name and it.get("status") != "done":
                it["status"] = "done"
                touched = True
        if touched:
            save_queue(data_dir, typ, items)
            changed = True
    return changed


def profile_counts(data_dir, type):
    """Return {status: count} for profiles of `type` (statuses stub/draft/published)."""
    counts = {s: 0 for s in VALID_STATUS}
    for post in load_profiles(data_dir):
        if post.get("type") != type:
            continue
        status = post.get("status")
        if status in counts:
            counts[status] += 1
    return counts
