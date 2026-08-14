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
GATED_TYPES = ("brand", "person", "study", "list")
PROFILE_TYPES = ENTITY_TYPES + GATED_TYPES
# `list` is a curated collection that cross-references products/ingredients. Its
# `kind` says what shape it is: a best-of ranking or a step-by-step routine.
VALID_LIST_KIND = ("best-of", "routine")


def load_profiles(data_dir):
    data_dir = pathlib.Path(data_dir)
    posts = []
    for md in sorted(data_dir.glob("*/*.md")):
        posts.append(frontmatter.load(md))
    return posts


def filter_published(posts):
    return [p for p in posts if p.get("status") == "published"]


def audit_stuck(data_dir, tracked_files, review_log):
    """Surface work that got drafted but never reached the live site.

    The failure mode this catches: a page is drafted and critic-cleared inside a
    workflow, but the publish tail (flip status -> published, commit, push) is a
    separate manual step that a context-switch can drop. The page then sits
    invisibly in the working tree. Three categories, each a distinct leak:

      untracked        - a data/*/*.md file git is not tracking: drafted, never
                         committed. Would vanish on a clean checkout.
      stuck_publish    - status==draft but the review-log verdict is 'publish'.
                         Under ship-live this is a bug: the critic said ship it,
                         nothing shipped it.
      unreviewed_draft - status==draft with no publish verdict yet: legitimately
                         in flight, listed so it is never simply forgotten.

    `tracked_files` is a set of absolute paths git tracks under data/; `review_log`
    is the parsed data/review-log.yaml (slug -> {verdict, ...}). Both are passed in
    so this stays a pure function the tests can drive without git or disk state.
    """
    data_dir = pathlib.Path(data_dir)
    review_log = review_log or {}
    untracked, stuck_publish, unreviewed_draft = [], [], []
    for md in sorted(data_dir.glob("*/*.md")):
        post = frontmatter.load(md)
        slug = post.get("slug") or md.stem
        status = post.get("status")
        verdict = (review_log.get(slug) or {}).get("verdict")
        if str(md.resolve()) not in tracked_files:
            untracked.append((slug, status))
        if status == "draft" and verdict == "publish":
            stuck_publish.append((slug, verdict))
        elif status == "draft":
            # any draft not yet cleared to publish (no verdict, or revise/sign-off)
            unreviewed_draft.append((slug, verdict or "unreviewed"))
    return {
        "untracked": untracked,
        "stuck_publish": stuck_publish,
        "unreviewed_draft": unreviewed_draft,
    }


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
# `assurance` is an OPTIONAL, separate axis from `status` (publish state): it
# records how much scrutiny the page's content has had, shown as a reader-facing
# badge. stub = placeholder; sonnet = auto-drafted + lint/verify/style/voice
# clean, single pass; opus = independently critic-verified (sources re-fetched,
# quotes/stats checked); reviewed = human sign-off. Backfilled from review-log.
VALID_ASSURANCE = ("stub", "sonnet", "opus", "reviewed")

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
    if metadata.get("assurance") and metadata["assurance"] not in VALID_ASSURANCE:
        errors.append(f"invalid assurance: {metadata['assurance']} (must be one of {VALID_ASSURANCE})")
    if metadata.get("type") == "list":
        kind = metadata.get("kind")
        if not kind:
            errors.append("list requires a 'kind' field (one of {})".format(VALID_LIST_KIND))
        elif kind not in VALID_LIST_KIND:
            errors.append(f"invalid kind: {kind} (must be one of {VALID_LIST_KIND})")

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


# Per-type required body sections (the summary-first + how-to-know standards).
# Kept SEPARATE from check_profile so it does not perturb the core lint contract;
# cmd_lint appends these warnings. Advisory (WARNING): pre-standard pages predate
# these requirements, so it must not break the build. Stubs are exempt.
REQUIRED_SECTIONS = {
    "product": ("Summary", "'## Summary' (summary-first standard)"),
    "condition": ("How to know you have this", "'How to know you have this' (condition-page opener)"),
}


def check_required_sections(metadata, content):
    """Warn if a page of a given type lacks its required body section."""
    if metadata.get("status") == "stub":
        return []
    req = REQUIRED_SECTIONS.get(metadata.get("type"))
    if not req:
        return []
    heading, label = req
    if _has_section(content, heading):
        return []
    return [f"missing required section: {label}"]


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


# --- House-voice violations (docs/writing-guide.md, docs/anti-ai-ese.md) ---
# Deterministic guardrail for the voice rules a critic used to catch by hand:
# site self-reference, defensive meta-commentary, and process/roadmap language.
# Advisory (WARNING), surfaced through check_style so `sk style` catches them.
# Patterns are deliberately specific to avoid false positives (e.g. the
# substantive phrase "not a finding of harm" must NOT match).
_VOICE_PATTERNS = [
    (re.compile(r"SkinTiers"),
     "site self-reference by name (never name the site on a content page)"),
    (re.compile(r"This page grades", re.I),
     "defensive meta-commentary ('This page grades ...')"),
    (re.compile(r"What follows is", re.I),
     "defensive meta-commentary ('What follows is ...')"),
    (re.compile(r"not (?:our|a) verdict", re.I),
     "defensive meta-commentary ('not a/our verdict')"),
    (re.compile(r"not a finding(?! of harm)", re.I),
     "defensive meta-commentary ('not a finding')"),
    (re.compile(r"matching INCI is not proof", re.I),
     "defensive meta-commentary ('a matching INCI is not proof')"),
    (re.compile(r"\bqueued\b", re.I),
     "process/roadmap language ('queued')"),
    (re.compile(r"a later phase", re.I),
     "process/roadmap language ('a later phase')"),
    (re.compile(r"not yet on the site", re.I),
     "process/roadmap language ('not yet on the site')"),
    (re.compile(r"coming soon", re.I),
     "process/roadmap language ('coming soon')"),
    (re.compile(r"first\b.{0,40}\bon the site", re.I),
     "self-referential meta ('first ... on the site')"),
    (re.compile(r"in-house", re.I),
     "process meta ('in-house' / 'assembled in-house')"),
]


def check_voice(content):
    """Advisory house-voice warnings for a markdown body (excludes ## Sources).

    Returns one WARNING string per distinct violated pattern. Catches the class
    of voice violations (self-reference, defensive meta, process language) that
    previously depended on a critic or a manual grep.
    """
    body = _style_body(content)
    warnings = []
    for pat, msg in _VOICE_PATTERNS:
        if pat.search(body):
            warnings.append(msg)
    return warnings


def check_style(content):
    """Advisory anti-AI-ese + house-voice warnings for a markdown body.

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

    warnings.extend(check_voice(content))
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


def known_slugs(data_dir=None):
    """Every declared slug across all pages (published, draft, or stub). Used to
    tell an unresolved xref (a real broken link) from a resolved one."""
    import frontmatter
    data_dir = pathlib.Path(data_dir or DATA_DIR)
    slugs = set()
    for md in data_dir.glob("*/*.md"):
        try:
            s = frontmatter.load(md).metadata.get("slug")
        except Exception:
            s = None
        if s:
            slugs.add(s)
    return slugs


def check_xrefs(content, known):
    """Warn on a bare [[slug]] xref (no |display alias) whose target is not a real
    page slug: at build time an unresolved xref renders as its raw target text, so a
    hyphenated slug like [[sebaceous-glands]] shows as literal 'sebaceous-glands' to
    the reader (the iscotrizinol-on-Relief-Sun bug). An unresolved [[slug|alias]] is
    fine (it renders the alias), so only the alias-less form is flagged. Fix by
    creating the page, adding a |display alias, or correcting a mistyped slug."""
    warnings = []
    seen = set()
    for m in _XREF_RE.finditer(content):
        target = m.group(1).split("#")[0].strip()
        alias = m.group(2)
        if alias is not None or not target or target in known or target in seen:
            continue
        seen.add(target)
        # A single lowercase word renders acceptably as that word; a hyphenated or
        # spaced target renders as broken-looking raw slug text. Flag the latter.
        if "-" in target or " " in target:
            warnings.append(
                f"unresolved xref [[{target}]] renders as raw slug text "
                f"(create the page, add a |display alias, or fix the slug)")
    return warnings


import datetime as _datetime


# --- Cross-page consistency (Phase C) ------------------------------------
# Catches the class of bug that recurs and that a single-page lint can't see: a
# product mis-tagged relative to its own name, a key_active/tier-list slug that
# points at no published page (a 404 or raw-render), or an images: file that was
# renamed/untracked. All source-level, so they run in `sk lint` AND in CI (a test
# that scans the whole tree and fails the build), enforcing consistency by default.

# Product names that unambiguously imply one specific active. A product NAMED after
# one of these should carry it in key_actives; the value is the ingredient slug.
# Deliberately excludes ambiguous families (a "Vitamin C serum" may use any of
# several C forms; a "retinoid" may be retinol/retinal/an ester) to avoid false
# positives. Order matters: longer phrases first so "hyaluronic acid" wins over "acid".
NAME_ACTIVE_MAP = [
    ("hyaluronic acid", "hyaluronic-acid"),
    ("salicylic acid", "salicylic-acid"),
    ("glycolic acid", "glycolic-acid"),
    ("mandelic acid", "mandelic-acid"),
    ("lactic acid", "lactic-acid"),
    ("azelaic acid", "azelaic-acid"),
    ("ferulic acid", "ferulic-acid"),
    ("tranexamic acid", "tranexamic-acid"),
    ("gluconolactone", "gluconolactone-pha"),
    ("lactobionic acid", "lactobionic-acid"),
    ("niacinamide", "niacinamide"),
    ("benzoyl peroxide", "benzoyl-peroxide"),
    ("adapalene", "adapalene"),
    ("tretinoin", "tretinoin"),
    ("tazarotene", "tazarotene"),
    ("clascoterone", "clascoterone"),
    ("cysteamine", "cysteamine"),
    ("hydroquinone", "hydroquinone"),
    ("panthenol", "panthenol"),
    ("colloidal oatmeal", "colloidal-oatmeal"),
]


def published_indexes(data_dir=None):
    """Return (published_slugs, published_by_type, slug_to_name) over PUBLISHED pages
    only. Used by the consistency checks so a reference to a draft/stub/missing page
    is treated as broken (it would 404 or render raw for a reader)."""
    data_dir = pathlib.Path(data_dir or DATA_DIR)
    slugs, by_type, names = set(), {}, {}
    for p in filter_published(load_profiles(data_dir)):
        s = p.metadata.get("slug")
        if not s:
            continue
        slugs.add(s)
        by_type.setdefault(p.metadata.get("type"), set()).add(s)
        names[s] = p.metadata.get("name") or s
    return slugs, by_type, names


def check_key_actives(metadata, published_ingredient_slugs):
    """ERROR-level: every key_actives slug must be a PUBLISHED ingredient page. Catches
    a rename/typo (a key_active pointing at a draft or non-existent ingredient), which
    otherwise silently mis-derives the evidence box and drops the product from concern
    feeds."""
    errors = []
    for slug in metadata.get("key_actives") or []:
        slug = str(slug).strip()
        if slug and slug not in published_ingredient_slugs:
            errors.append(
                f"key_active '{slug}' is not a published ingredient page "
                f"(rename/typo, or the ingredient page is still a draft/stub)")
    return errors


def check_name_actives(metadata, published_ingredient_slugs):
    """If the product NAME names an unambiguous active (NAME_ACTIVE_MAP) whose page is
    published, that slug should be in key_actives. Returns (errors, warnings):
      - ERROR (a SUBSTITUTION): the named active is missing AND a DIFFERENT mapped
        active is present instead - the-ordinary-lactic bug (named 'Lactic Acid', but
        key_actives listed glycolic-acid). Near-zero false positive, so build-blocking.
      - WARN (plain absence): the named active is missing with no substitution - it may
        legitimately be a secondary ingredient (a sunscreen 'with niacinamide'), so
        surfaced for review rather than failing the build."""
    if metadata.get("type") != "product":
        return [], []
    name = (metadata.get("name") or "").lower()
    have = {str(s).strip() for s in (metadata.get("key_actives") or [])}
    map_slugs = {slug for _, slug in NAME_ACTIVE_MAP}
    named = {slug for term, slug in NAME_ACTIVE_MAP
             if term in name and slug in published_ingredient_slugs}
    missing = named - have
    if not missing:
        return [], []
    substituted = sorted(s for s in have if s in map_slugs and s not in named)
    errors, warnings = [], []
    for slug in sorted(missing):
        if substituted:
            errors.append(
                f"name implies active '{slug}' but key_actives lists {substituted} "
                f"instead and omits it (mis-tag, the-ordinary-lactic-acid class of bug)")
        else:
            warnings.append(
                f"name says '{slug}' but key_actives is missing it "
                f"(confirm it is not just a secondary ingredient)")
    return errors, warnings


def check_images_exist(metadata, static_dir=None):
    """ERROR-level: every images: entry must resolve to a real self-hosted file under
    static/images/. Catches a renamed/untracked image that would 404 for readers (the
    scoped-git-add glob-miss bug)."""
    static_dir = pathlib.Path(static_dir or STATIC_DIR)
    errors = []
    for entry in metadata.get("images") or []:
        f = entry.get("file") if isinstance(entry, dict) else entry
        if not f:
            continue
        f = str(f)
        if f.startswith("http"):
            continue  # a full URL is used as-is, nothing to self-host
        if not (static_dir / "images" / f).exists():
            errors.append(f"images: references missing file 'static/images/{f}'")
    return errors


def check_tier_list_slugs(metadata, published_slugs):
    """ERROR-level: every tier_list item slug must be a PUBLISHED page. A ladder or
    best-of that lists a draft/typo/unprofiled slug renders a dead link (404) or, for
    a ladder rung, raw text - the class the render-smoke test misses because it is a
    link target, not a bare [[xref]]."""
    tl = metadata.get("tier_list") or {}
    errors = []
    for raw in tl.get("items") or []:
        slug = (raw.get("slug") if isinstance(raw, dict) else str(raw)).strip()
        if slug and slug not in published_slugs:
            errors.append(
                f"tier_list item '{slug}' is not a published page "
                f"(renders a dead link / raw text; profile it or fix the slug)")
    return errors


# Structured price backing (accuracy gate). The `price:` frontmatter is a list of
# {amount, currency, size, as_of, source} entries. It exists ONLY to make a price the
# page already states in prose/sources queryable; it must never introduce a new number.
# So every structured amount has to be backed by a verbatim price string somewhere on
# the page. This check is the mechanical enforcement of that rule.
_PAGE_PRICE_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _page_price_floats(content):
    """Every dollar amount that literally appears in the page body, as a set of
    floats rounded to cents (so $185, $185.00 and $185.0 all compare equal)."""
    out = set()
    for m in _PAGE_PRICE_RE.finditer(content):
        raw = m.group(0).replace("$", "").replace(",", "").replace(" ", "")
        try:
            out.add(round(float(raw), 2))
        except ValueError:
            continue
    return out


def check_price_backing(metadata, content):
    """ERROR-level: every structured `price.amount` must correspond to a verbatim
    price string already present in the page prose or its ## Sources footnotes. This
    enforces the non-negotiable rule that the structured field only mirrors a price
    the page already states, never invents, rounds, or looks one up."""
    price = metadata.get("price")
    if not price:
        return []
    errors = []
    if not isinstance(price, list):
        return ["price: must be a list of {amount, currency, size, as_of, source} entries"]
    page_prices = _page_price_floats(content)
    for i, entry in enumerate(price):
        if not isinstance(entry, dict):
            errors.append(f"price[{i}]: must be a mapping, not {type(entry).__name__}")
            continue
        amount = entry.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            errors.append(f"price[{i}]: missing numeric 'amount'")
            continue
        as_of = entry.get("as_of")
        if as_of is not None and not _ISO_DATE_RE.match(str(as_of)):
            errors.append(f"price[{i}]: as_of '{as_of}' is not YYYY-MM-DD")
        if round(float(amount), 2) not in page_prices:
            errors.append(
                f"price[{i}]: amount {amount} has no verbatim price string on the page "
                f"(a structured price must mirror one the page already states, never invent one)")
    return errors


def consistency_issues(data_dir=None, static_dir=None):
    """Scan the whole tree, returning (errors, warnings) as lists of (slug, message).
    errors should fail the build; warnings surface for review. This is the cross-page
    accuracy gate: a page can be internally clean yet inconsistent with another page."""
    data_dir = pathlib.Path(data_dir or DATA_DIR)
    published_slugs, by_type, _ = published_indexes(data_dir)
    ing = by_type.get("ingredient", set())
    errors, warnings = [], []
    for p in filter_published(load_profiles(data_dir)):
        m = p.metadata
        slug = m.get("slug") or "?"
        for e in check_key_actives(m, ing):
            errors.append((slug, e))
        for e in check_images_exist(m, static_dir):
            errors.append((slug, e))
        for e in check_tier_list_slugs(m, published_slugs):
            errors.append((slug, e))
        for e in check_price_backing(m, p.content):
            errors.append((slug, e))
        na_errors, na_warnings = check_name_actives(m, ing)
        for e in na_errors:
            errors.append((slug, e))
        for w in na_warnings:
            warnings.append((slug, w))
    return errors, warnings


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


def set_assurance(path, level):
    """Set the assurance level. A human 'reviewed' sign-off is never downgraded
    by an automated caller (publish sets 'opus'; only a person confers 'reviewed')."""
    post = frontmatter.load(path)
    if post.get("assurance") == "reviewed":
        return
    post["assurance"] = level
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
    "list": "lists",
}
LIST_TO_TYPE = {v: k for k, v in TYPE_TO_LIST.items()}
QUEUE_TYPES = tuple(TYPE_TO_LIST)

# Types whose profiles a research cron may auto-publish (rather than draft).
# All types now ship live once the critic gate clears; there is no draft-for-
# sign-off hold. (GATED_TYPES still classifies brand/person/study as cited
# roll-up pages for lint/verify, but no longer gates publishing.)
AUTOPUBLISH_TYPES = {"product", "ingredient", "goal", "condition",
                     "brand", "person", "study", "list"}


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


_PAREN_RE = re.compile(r"\([^)]*\)")


def _slugify(text):
    t = (text or "").encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def page_exists_for(data_dir, name, type):
    """Dedup guard: True if a data page probably already exists for this queued name.

    Slugs are author-assigned, so a descriptive queue name ("Hydroquinone (topical
    depigmenting agent)") does not map deterministically to its page slug
    ("hydroquinone"). We check the slugified full name AND the name with any
    parenthetical stripped against data/<plural>/<slug>.md, which catches the common
    `<Existing thing> (descriptor)` harvest pattern that keeps re-queuing live pages."""
    plural = TYPE_TO_LIST.get(type)
    if not plural:
        return False
    base = pathlib.Path(data_dir) / plural
    cands = {_slugify(name), _slugify(_PAREN_RE.sub(" ", name))}
    cands.discard("")
    return any((base / (s + ".md")).exists() for s in cands)


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
