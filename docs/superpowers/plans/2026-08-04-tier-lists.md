# Tier Lists / Rankings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render sets of comparable items as visual, evidence-derived tier lists driven by a new `tier_list:` frontmatter block, reusing the grades the site already computes.

**Architecture:** Two pure build.py functions — `entity_tier(metadata)` derives one tier key from a page's grades (or an explicit summary `tier:`), and `tier_list_view(profile, by_slug)` turns a page's `tier_list:` block into a grouped, ordered render model. A `profile.html` section renders it with the existing tier-color CSS variables; no JavaScript. Then the schema is applied to two best-of lists and the retinoids hub.

**Tech Stack:** Python 3, `python-frontmatter`, Jinja2, pytest. Static-site build (`build.py` → `_site/`).

## Global Constraints

- Static HTML/CSS only — no JavaScript for this feature (consistent with the rest of the site).
- Tier keys are `best | good | mid | weak` (+ `unrated`); labels are the evidence words **Top-evidenced / Strong / Moderate / Minimal / Unrated**. Never letter grades.
- Tier colors come from the existing CSS variables `--tier-best / --tier-good / --tier-mid / --tier-weak` (defined in all four theme blocks of `static/style.css`); do not invent new colors.
- Unknown/unpublished item slugs are skipped and surfaced in a returned `missing` list — never break the build.
- Anti-hallucination: the retinoid `tier:` values (Task 4) must be read off each page's already-published `## The Rubric`, not invented. If a page's rubric does not clearly imply a tier, leave that item unrated and flag it — do not guess.
- Tests: `python -m pytest tests/ -q` must stay green. Run `python build.py` (with `SK_DATA`/`SK_OUTPUT`) to verify rendered output.

---

### Task 1: `entity_tier(metadata)` — evidence tier from a page's grades or summary field

**Files:**
- Modify: `build.py` (add constants + helpers + `entity_tier` immediately after `_top_health_effect`, which ends at ~line 336, before `def routine_summary`)
- Test: `tests/test_build.py` (append)

**Interfaces:**
- Consumes: `EFFECT_SEGS` (build.py:211).
- Produces:
  - `entity_tier(metadata: dict) -> str | None` — returns a tier key `"best"|"good"|"mid"|"weak"` or `None` (unrated).
  - `_best_health_grade(metadata: dict) -> tuple[int, str] | None` — `(effect_segs, evidence_word)` of the best HEALTH grade, or `None` if the page has no grades.
  - `_TIER_LABELS: tuple[tuple[str,str], ...]` — ordered `(key, label)` pairs, best first.
  - `_TIER_LABEL: dict[str,str]`, `_TIER_ALIASES: dict[str,str]`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build.py`:

```python
def test_entity_tier_from_grades_and_overrides():
    sys.path.insert(0, str(ROOT))
    import build
    et = build.entity_tier
    # strong effect + solid evidence -> top tier
    assert et({"grades": [{"effect": "strong", "evidence": "solid", "use": "X (health)"}]}) == "best"
    # strong effect but THIN evidence -> demoted one step -> good
    assert et({"grades": [{"effect": "strong", "evidence": "preliminary", "use": "X (health)"}]}) == "good"
    assert et({"grades": [{"effect": "modest", "evidence": "solid", "use": "X (health)"}]}) == "mid"
    assert et({"grades": [{"effect": "minimal", "evidence": "solid", "use": "X (health)"}]}) == "weak"
    # picks the best HEALTH grade, ignoring a stronger non-health grade
    assert et({"grades": [
        {"effect": "strong", "evidence": "solid", "use": "Cosmetic shine"},
        {"effect": "modest", "evidence": "solid", "use": "Barrier (health)"},
    ]}) == "mid"
    # page-level summary `tier:` (ingredient hubs, no grades) wins, accepts words
    assert et({"tier": "strong"}) == "good"
    assert et({"tier": "Top-evidenced"}) == "best"
    # unknown alias -> unrated; nothing to derive -> unrated
    assert et({"tier": "bogus"}) is None
    assert et({}) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_build.py::test_entity_tier_from_grades_and_overrides -q`
Expected: FAIL with `AttributeError: module 'build' has no attribute 'entity_tier'`.

- [ ] **Step 3: Write minimal implementation**

Insert into `build.py` right after `_top_health_effect` (after line ~336, before `def routine_summary`):

```python
# --- Evidence tiers (tier lists / rankings) -------------------------------
# One coarse evidence tier per entity, reused by tier-list pages. Products
# derive it from their `grades:`; pages that grade in prose (ingredient hubs)
# carry an explicit summary `tier:` field. Keys match the --tier-* CSS vars.
_TIER_LABELS = (
    ("best", "Top-evidenced"),
    ("good", "Strong"),
    ("mid", "Moderate"),
    ("weak", "Minimal"),
)
_TIER_LABEL = dict(_TIER_LABELS)
# Accepted manual / page-level tier spellings -> canonical key.
_TIER_ALIASES = {
    "top": "best", "best": "best", "top-evidenced": "best",
    "strong": "good", "good": "good",
    "moderate": "mid", "mid": "mid",
    "minimal": "weak", "weak": "weak",
}
_THIN_EVIDENCE = {"anecdotal", "preliminary"}


def _best_health_grade(metadata):
    """(effect_segs, evidence_word) of the HEALTH grade with the best effect,
    or None if the page has no grades. Mirrors _top_health_effect's health-first
    selection so a tier agrees with the routine dashboards."""
    grades = metadata.get("grades") or []
    if not grades:
        return None
    health = [g for g in grades if "(health)" in (g.get("use") or "").lower()]
    pool = health or grades
    best = None
    for g in pool:
        segs = EFFECT_SEGS.get((g.get("effect") or "").lower(), 0)
        if best is None or segs > best[0]:
            best = (segs, (g.get("evidence") or "").lower())
    return best


def _segs_to_tier(segs):
    if segs >= 4:
        return "best"
    if segs == 3:
        return "good"
    if segs == 2:
        return "mid"
    return "weak"


def entity_tier(metadata):
    """A single evidence tier key for a page, or None (unrated).
    Precedence: explicit page-level `tier:` (e.g. ingredient hubs that grade in
    prose) -> derived from `grades:`, demoting one segment for thin
    (anecdotal/preliminary) evidence -> None."""
    manual = (metadata.get("tier") or "").strip().lower()
    if manual:
        return _TIER_ALIASES.get(manual)          # unknown spelling -> None (unrated)
    best = _best_health_grade(metadata)
    if best is None:
        return None
    segs, evidence = best
    if evidence in _THIN_EVIDENCE:
        segs = max(0, segs - 1)
    return _segs_to_tier(segs)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_build.py::test_entity_tier_from_grades_and_overrides -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "feat(tiers): entity_tier — evidence tier from grades or summary field"
```

---

### Task 2: `tier_list_view(profile, by_slug)` — grouped, ordered tier model

**Files:**
- Modify: `build.py` (add `tier_list_view` right after `entity_tier`)
- Test: `tests/test_build.py` (append)

**Interfaces:**
- Consumes: `entity_tier` and `_best_health_grade` (Task 1), `images_and_monogram` (build.py:561), `EVIDENCE_MAP` (build.py:213).
- Produces: `tier_list_view(profile, by_slug) -> dict | None`. `profile` is a `frontmatter.Post` (has `.metadata`); `by_slug` maps slug -> `frontmatter.Post` (has `.metadata` and `.get("status")`). Returns `None` when the page has no `tier_list:`, else:
  ```
  {"title": str, "by": str,
   "tiers": [{"key": str, "label": str,
              "items": [{"slug","name","thumb","monogram","evidence","note","segs"}]}],
   "missing": [slug, ...]}
  ```
  Tiers appear in order best→good→mid→weak→unrated; empty tiers omitted. `evidence` is `None` for pages with no grades. `thumb` is `None` when the item has no photo.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build.py`:

```python
def test_tier_list_view_groups_orders_and_reports_missing():
    sys.path.insert(0, str(ROOT))
    import build, frontmatter

    def post(md):
        return frontmatter.loads(md)

    def graded(slug, effect, name):
        return post(
            f"---\nname: {name}\nslug: {slug}\ntype: product\nstatus: published\n"
            f"grades:\n- effect: {effect}\n  evidence: solid\n  use: X (health)\n---\nBody.\n"
        )

    by_slug = {
        "aa": graded("aa", "strong", "Alpha"),     # best, segs 4
        "bb": graded("bb", "modest", "Bravo"),     # mid, segs 2
        "cc": graded("cc", "notable", "Charlie"),  # good, segs 3
        "dd": post("---\nname: Delta\nslug: dd\ntype: product\nstatus: draft\n---\nBody.\n"),  # not published
    }
    page = post(
        "---\nname: List\nslug: list\ntype: list\nstatus: published\n"
        "tier_list:\n"
        "  title: Test ranking\n"
        "  by: overall evidence\n"
        "  items:\n"
        "  - aa\n"
        "  - slug: bb\n    note: gentle pick\n    tier: strong\n"   # override -> good
        "  - cc\n"
        "  - dd\n"                                                    # unpublished -> missing
        "  - nope\n"                                                  # unknown -> missing
        "---\nBody.\n"
    )
    v = build.tier_list_view(page, by_slug)
    assert v["title"] == "Test ranking" and v["by"] == "overall evidence"
    assert v["missing"] == ["dd", "nope"]
    keys = [t["key"] for t in v["tiers"]]
    assert keys == ["best", "good"]                     # empty tiers omitted, best-first
    best = v["tiers"][0]
    assert [i["slug"] for i in best["items"]] == ["aa"]
    good = v["tiers"][1]
    # cc (notable, segs 3) sorts above bb (override, segs 2) within the good tier
    assert [i["slug"] for i in good["items"]] == ["cc", "bb"]
    bb = [i for i in good["items"] if i["slug"] == "bb"][0]
    assert bb["note"] == "gentle pick" and bb["evidence"] == "Solid"
    # no tier_list -> None
    assert build.tier_list_view(post("---\nname: X\nslug: x\ntype: list\n---\nB.\n"), by_slug) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_build.py::test_tier_list_view_groups_orders_and_reports_missing -q`
Expected: FAIL with `AttributeError: module 'build' has no attribute 'tier_list_view'`.

- [ ] **Step 3: Write minimal implementation**

Insert into `build.py` right after `entity_tier`:

```python
_TIER_ORDER = ["best", "good", "mid", "weak", "unrated"]


def tier_list_view(profile, by_slug):
    """Build the tier-list render model from a page's `tier_list:` frontmatter,
    or None if absent. Each item is a bare slug or {slug, note?, tier?}. Tier
    precedence per item: its own `tier:` override -> entity_tier(target).
    Unknown/unpublished slugs are skipped and surfaced in `missing`. Within a
    tier, products sort by effect segs desc with declared order breaking ties;
    items with no numeric effect (segs -1, e.g. ingredient hubs) keep declared
    order."""
    tl = profile.metadata.get("tier_list")
    if not tl:
        return None
    buckets = {k: [] for k in _TIER_ORDER}
    missing = []
    for idx, raw in enumerate(tl.get("items") or []):
        if isinstance(raw, dict):
            slug = (raw.get("slug") or "").strip()
            note = raw.get("note") or ""
            override = (raw.get("tier") or "").strip().lower()
        else:
            slug, note, override = str(raw).strip(), "", ""
        target = by_slug.get(slug)
        if target is None or target.get("status") != "published":
            missing.append(slug)
            continue
        key = (_TIER_ALIASES.get(override) if override else entity_tier(target.metadata)) or "unrated"
        imgs, mono = images_and_monogram(target.metadata)
        best = _best_health_grade(target.metadata)
        segs = best[0] if best else -1
        ev_label = EVIDENCE_MAP.get(best[1], (None, None))[1] if best else None
        buckets[key].append({
            "slug": slug,
            "name": target.metadata.get("name") or slug,
            "thumb": imgs[0]["src"] if imgs else None,
            "monogram": mono,
            "evidence": ev_label,
            "note": note,
            "order": idx,
            "segs": segs,
        })
    tiers = []
    for key in _TIER_ORDER:
        rows = buckets[key]
        if not rows:
            continue
        rows.sort(key=lambda r: (-r["segs"], r["order"]))
        tiers.append({"key": key, "label": _TIER_LABEL.get(key, "Unrated"), "items": rows})
    return {"title": tl.get("title") or "", "by": tl.get("by") or "",
            "tiers": tiers, "missing": missing}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_build.py::test_tier_list_view_groups_orders_and_reports_missing -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "feat(tiers): tier_list_view — grouped, ordered tier model"
```

---

### Task 3: Render the tier-list section (build wiring + template + CSS)

**Files:**
- Modify: `build.py` (~line 841 compute `tier_list`; ~line 858 pass it to the profile template render)
- Modify: `templates/profile.html` (insert a `tierlist` section after the routine section's `{% endif %}` at line 88)
- Modify: `static/style.css` (append `.tierlist` styles)
- Test: `tests/test_build.py` (append an end-to-end build test)

**Interfaces:**
- Consumes: `tier_list_view` (Task 2), `by_slug` (build.py:804), the Jinja global `gen_icon` (build.py:790).
- Produces: a `tier_list` template variable and a `<section class="tierlist">` in rendered profile pages.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build.py`:

```python
def test_tier_list_section_renders_on_a_page(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write_graded_product(data / "products", "alpha", "strong", [])
    _write_graded_product(data / "products", "bravo", "modest", [])
    (data / "lists").mkdir(parents=True, exist_ok=True)
    (data / "lists" / "ranking.md").write_text(
        "---\nname: A Ranking\nslug: ranking\ntype: list\nkind: best-of\n"
        "status: published\nupdated: 2026-08-04\nanalyzed: 2026-08-04\n"
        "tier_list:\n"
        "  title: Serums by evidence\n"
        "  by: overall evidence\n"
        "  items:\n  - alpha\n  - bravo\n  - ghost\n"     # ghost is unknown -> skipped
        "---\n\nBody.\n\n## Sources\n\nNone.\n"
    )
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    html = (out / "ranking.html").read_text()
    assert 'class="tierlist"' in html
    assert "Serums by evidence" in html
    assert "Top-evidenced" in html and "Moderate" in html   # evidence-word labels
    assert 'class="tl-tier tl-tier-best"' in html
    assert 'href="alpha.html"' in html and 'href="bravo.html"' in html
    assert "ghost" not in html                               # unknown item not shown
    # a page WITHOUT tier_list renders no such section
    assert 'class="tierlist"' not in (out / "alpha.html").read_text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_build.py::test_tier_list_section_renders_on_a_page -q`
Expected: FAIL (no `class="tierlist"` in output — the variable is not computed or rendered yet).

- [ ] **Step 3a: Compute `tier_list` in the render loop**

In `build.py`, find the line (~841) `routine = routine_summary(p, by_slug)` and add immediately after it:

```python
        tier_list = tier_list_view(p, by_slug)
```

- [ ] **Step 3b: Pass it to the template**

In the `env.get_template("profile.html").render(` call (~line 858), add a keyword argument alongside `routine=routine,` (~line 876):

```python
            tier_list=tier_list,
```

- [ ] **Step 3c: Render the section in the template**

In `templates/profile.html`, insert after line 88 (the `{% endif %}` that closes the `routine-dash` section) and before the blank line preceding `{% if uv_spectrum %}`:

```html
  {% if tier_list %}
  <section class="tierlist" aria-label="Evidence tier list">
    {% if tier_list.title %}<h2 class="tl-title">{{ tier_list.title }}</h2>{% endif %}
    {% if tier_list.by %}<p class="tl-by">Ranked by {{ tier_list.by }}. Tier = the strength of the evidence behind each, from the site's own grades.</p>{% endif %}
    {% for t in tier_list.tiers %}
    <div class="tl-tier tl-tier-{{ t.key }}">
      <div class="tl-label">{{ t.label }}</div>
      <ul class="tl-items">
        {% for it in t.items %}
        <li class="tl-item">
          <a class="tl-badge" href="{{ it.slug }}.html" aria-hidden="true" tabindex="-1">{% if it.thumb %}<img src="{{ it.thumb }}" alt="" loading="lazy">{% else %}{{ gen_icon(it.slug, it.monogram, it.name)|safe }}{% endif %}</a>
          <a class="tl-name" href="{{ it.slug }}.html">{{ it.name }}</a>
          {% if it.evidence %}<span class="tl-ev">{{ it.evidence }}</span>{% endif %}
          {% if it.note %}<span class="tl-note">{{ it.note }}</span>{% endif %}
        </li>
        {% endfor %}
      </ul>
    </div>
    {% endfor %}
  </section>
  {% endif %}
```

- [ ] **Step 3d: Add CSS**

Append to `static/style.css`:

```css
/* Tier lists / rankings ---------------------------------------------------*/
.tierlist{margin:28px 0}
.tl-title{margin:0 0 4px;font-family:var(--serif);font-size:24px}
.tl-by{margin:0 0 16px;color:var(--ink-soft,#6b6f68);font-size:14px;max-width:60ch}
.tl-tier{display:grid;grid-template-columns:120px 1fr;gap:14px;align-items:start;
  padding:12px 0;border-top:1px solid var(--rule)}
.tl-tier:first-of-type{border-top:0}
.tl-label{font-family:var(--mono);font-size:12px;font-weight:600;letter-spacing:.04em;
  text-transform:uppercase;color:#fff;padding:5px 9px;border-radius:6px;text-align:center}
.tl-tier-best .tl-label{background:var(--tier-best)}
.tl-tier-good .tl-label{background:var(--tier-good)}
.tl-tier-mid  .tl-label{background:var(--tier-mid)}
.tl-tier-weak .tl-label{background:var(--tier-weak)}
.tl-tier-unrated .tl-label{background:var(--tier-weak);opacity:.55}
.tl-items{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.tl-item{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.tl-badge{flex:0 0 auto;width:34px;height:34px;border-radius:8px;overflow:hidden;
  display:inline-flex;border:1px solid var(--rule)}
.tl-badge img{width:100%;height:100%;object-fit:cover}
.tl-badge .genicon{width:100%;height:100%}
.tl-name{font-weight:600;text-decoration:none;color:var(--ink)}
.tl-name:hover{text-decoration:underline}
.tl-ev{font-family:var(--mono);font-size:11px;color:var(--ink-soft,#6b6f68);
  border:1px solid var(--rule);border-radius:4px;padding:1px 6px}
.tl-note{font-size:13px;color:var(--ink-soft,#6b6f68)}
@media(max-width:560px){.tl-tier{grid-template-columns:1fr;gap:8px}}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_build.py::test_tier_list_section_renders_on_a_page -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest tests/ -q`
Expected: all pass (1 node-parity test may skip locally — that is expected).

- [ ] **Step 6: Commit**

```bash
git add build.py templates/profile.html static/style.css tests/test_build.py
git commit -m "feat(tiers): render evidence tier-list section on profile pages"
```

---

### Task 4: Apply tier lists to two best-of lists + the retinoids hub

**Files:**
- Modify: `data/lists/best-vitamin-c-serums.md` (add `tier_list:` frontmatter)
- Modify: `data/lists/best-peptide-serums.md` (add `tier_list:` frontmatter)
- Modify: `data/ingredients/retinoids.md` (add `tier_list:` frontmatter)
- Modify: `data/ingredients/{tretinoin,adapalene,retinaldehyde,retinol,bakuchiol}.md` (add page-level `tier:`)
- Test: `tests/test_build.py` (append a build-against-real-data smoke test)

**Interfaces:**
- Consumes: the rendered `tierlist` section from Task 3. No new code.

All item slugs below are verified to exist, be `status: published`, and (for products) carry `grades:`.

- [ ] **Step 1: Add `tier_list:` to the two best-of lists**

Edit `data/lists/best-vitamin-c-serums.md` — add this block to the YAML frontmatter (keep existing keys; the prose body stays as the rationale):

```yaml
tier_list:
  title: "Vitamin C serums by evidence"
  by: "overall evidence for the product's stated skin benefits"
  items:
    - skinceuticals-c-e-ferulic
    - maelove-the-glow-maker
    - timeless-20-vitamin-c-e-ferulic-serum
    - beauty-of-joseon-light-on-serum-centella-vita-c
    - prequel-lucent-c-vitamin-c-serum
    - trader-joes-nourish-vitamins-c-e-facial-serum
```

Edit `data/lists/best-peptide-serums.md` — add to frontmatter:

```yaml
tier_list:
  title: "Peptide serums by evidence"
  by: "overall evidence for the product's stated skin benefits"
  items:
    - the-ordinary-multi-peptide-copper-peptides-serum
    - the-ordinary-multi-peptide-ha-serum
    - cosrx-6-peptide-skin-booster-serum
```

(Tiers auto-derive from each product's `grades:` — do not hand-assign product tiers.)

- [ ] **Step 2: Add page-level `tier:` to the five retinoid ingredient pages**

For EACH of `tretinoin, adapalene, retinaldehyde, retinol, bakuchiol`, open `data/ingredients/<slug>.md`, read its `## The Rubric` section, and add a single `tier:` line to the frontmatter whose value matches what that rubric already concludes. Use this mapping (word → what it means), and confirm against the page before committing:

- `tier: top` — a prescription-strength / gold-standard-evidenced retinoid.
- `tier: strong` — well-evidenced but a step below.
- `tier: moderate` — real but more limited evidence.
- `tier: minimal` — weak or preliminary evidence.

Starting proposal, to VERIFY against each page's rubric (adjust if the rubric disagrees; if a rubric does not clearly imply a tier, use no `tier:` line and note it in the commit body):

- `tretinoin` → `tier: top`
- `adapalene` → `tier: strong`
- `retinol` → `tier: strong`
- `retinaldehyde` → `tier: moderate`
- `bakuchiol` → `tier: minimal`

Example (tretinoin frontmatter): add the one line

```yaml
tier: top
```

- [ ] **Step 3: Add `tier_list:` to the retinoids hub**

Edit `data/ingredients/retinoids.md` — add to frontmatter:

```yaml
tier_list:
  title: "Retinoids by evidence"
  by: "overall strength of evidence for anti-aging and acne"
  items:
    - tretinoin
    - adapalene
    - retinol
    - retinaldehyde
    - bakuchiol
```

- [ ] **Step 4: Write the failing test**

Append to `tests/test_build.py`:

```python
def test_real_tier_list_pages_build(tmp_path):
    # The real data set must build with the tier-list sections present and no
    # items landing in `missing` (all referenced slugs exist + are published).
    out = tmp_path / "_site"
    env = {**os.environ, "SK_OUTPUT": str(out)}   # SK_DATA defaults to ./data
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr
    for slug in ("best-vitamin-c-serums", "best-peptide-serums", "retinoids"):
        html = (out / f"{slug}.html").read_text()
        assert 'class="tierlist"' in html, slug
    vitc = (out / "best-vitamin-c-serums.html").read_text()
    assert 'href="skinceuticals-c-e-ferulic.html"' in vitc
    retin = (out / "retinoids.html").read_text()
    assert 'href="tretinoin.html"' in retin and "Retinoids by evidence" in retin
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest tests/test_build.py::test_real_tier_list_pages_build -q`
Expected: PASS. If it fails on a `missing` slug, re-check the slug spellings in Steps 1–3 against `data/`.

- [ ] **Step 6: Run the full suite**

Run: `python -m pytest tests/ -q`
Expected: all pass (node-parity test may skip locally).

- [ ] **Step 7: Commit**

```bash
git add data/lists/best-vitamin-c-serums.md data/lists/best-peptide-serums.md \
        data/ingredients/retinoids.md data/ingredients/tretinoin.md \
        data/ingredients/adapalene.md data/ingredients/retinaldehyde.md \
        data/ingredients/retinol.md data/ingredients/bakuchiol.md \
        tests/test_build.py
git commit -m "content(tiers): tier lists on vitamin-C + peptide best-of lists and retinoids hub"
```

- [ ] **Step 8: Push and verify live**

```bash
git push
```

Then wait for the GitHub Action to finish and verify the live pages render the tier list (per the project's live-verification rule):
`https://ericries.github.io/skintiers/retinoids.html`,
`https://ericries.github.io/skintiers/best-vitamin-c-serums.html`,
`https://ericries.github.io/skintiers/best-peptide-serums.html` — each should show the tiered section with evidence-word labels and correct tier colors, in both light and dark themes.

---

## Self-Review

**Spec coverage:**
- Evidence-derived tiers + evidence demotion + manual override → Task 1 (`entity_tier`). ✓
- Evidence-word labels Top-evidenced/Strong/Moderate/Minimal (+Unrated) → Task 1 `_TIER_LABELS`, Task 3 rendering. ✓
- `tier_list:` schema (bare slug / `{slug,note,tier}`) + `missing` for bad slugs → Task 2. ✓
- Ingredient prose-rubric wrinkle via page-level `tier:` → Task 1 precedence + Task 4 Step 2. ✓
- Within-tier ordering (segs desc, else declared order) → Task 2 `sort(key=(-segs, order))`. ✓
- Consumers: two best-of lists + retinoids hub → Task 4. ✓
- Static, no JS, reuse `--tier-*` colors → Task 3 CSS. ✓
- Error handling (unknown slug skipped, unrated fallback, absent block → no section) → Tasks 2 & 3 tests. ✓
- Testing (entity_tier mapping/demotion/precedence; view grouping/ordering/missing; build render present/absent) → Tasks 1–3 tests. ✓

**Placeholder scan:** No TBD/TODO; every code step has concrete code. The only judgment step (retinoid `tier:` values, Task 4 Step 2) gives concrete proposed values plus the required verify-against-rubric instruction, per the anti-hallucination constraint. ✓

**Type consistency:** `entity_tier(metadata)` takes a dict; `tier_list_view` calls `entity_tier(target.metadata)`. Tier keys `best/good/mid/weak/unrated` are consistent across `_TIER_ALIASES`, `_segs_to_tier`, `_TIER_ORDER`, `_TIER_LABEL`, the template classes `tl-tier-{key}`, and the CSS selectors. Item dict keys (`slug/name/thumb/monogram/evidence/note/order/segs`) match between `tier_list_view` and the template. ✓
