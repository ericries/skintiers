# Routine Builder MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single self-contained page where a reader searches the product catalog, adds products to an AM/PM routine, sees a live skeptical dashboard, and gets a shareable compact-path URL.

**Architecture:** `build.py` renders one template to both `_site/routine.html` (200 start page) and `_site/404.html` (GitHub Pages fallback that serves shared `/r1/...` paths). The page inlines the code-keyed catalog JSON, the CSS, and the builder JS (a separate file would 404 at a deep path). The browser JS codec + dashboard are faithful ports of `scripts/routine_string.py` and `build.py:routine_summary`, pinned to a shared vectors fixture.

**Tech Stack:** Python 3 + Jinja2 (existing `build.py`), vanilla browser JS (no framework, no bundler), pytest. No new Python runtime dependencies.

## Global Constraints
- URL grammar is the PATH form only: `r1/aIOU6D/p46` — `rW` anchor (W = base62 code width, auto-sized per link), `a`/`p`/`w` phase markers, fixed-width base62 codes (self-delimiting, no commas), optional `~N` cadence (1-6). The MVP UI emits only `a`/`p` phases, daily (no `~N`, no `w`) — but the codec must parse/encode the full grammar to stay a faithful mirror of `routine_string.py`.
- Codes are CANONICAL (unpadded, as in the catalog); `encode` left-pads to the link width, `parse` strips the padding back off.
- The page must be fully self-contained: inline `<style>`, inline catalog JSON, inline `<script>`. A `<base href="{SITE_BASE}/">` makes relative product-page links resolve; `SITE_BASE` = the path of `SITE_URL` (`/skintiers`).
- Catalog shape (already emitted by `routine_catalog`): `{v:int, p:{code:{s,n,c,t,g,a,th,m}}, i:{slug:{n, f?}}, notable:[[label,[member_slugs]]]}`. `g` is effect segs 0-4; `t` is tier key top|mid|entry; `a` is a list of active slugs; `th` is a thumb URL or null; `m` is a monogram; `i[slug].f` (when present) is a UV band `uvb|uva|both`.
- Dashboard math must match `routine_summary`: strength = mean of distinct products' `g` → Strong ≥3 / Solid ≥2.25 / Moderate ≥1.5 / Light; layered actives = count of distinct products carrying each non-filter active (show ×N when >1); filters grouped by band → coverage string `"UVB + UVA"` (UVB first); does-not-contain = each `notable` family with no member present.
- **Environment note:** `node` is currently broken on the dev box (dyld/icu error) and CI runs no pytest. So the JS parity test is written to SKIP when node can't execute, and Task 6 (in-browser verification via the claude-in-chrome tools) is the REAL gate that the JS port matches Python before shipping. Do not skip Task 6.
- TDD, DRY, YAGNI, frequent commits. Full suite `.venv/bin/python -m pytest tests/ -q` must stay green.

---

## File Structure
- Create `tests/fixtures/routine_vectors.json` — shared `[{path, model}]` vectors; the single source of truth both codecs are tested against.
- Create `assets/routine-builder.js` — the builder JS: pure functions `parseRoutine`, `encodeRoutine`, `computeDashboard` (exported for node), then a DOM `init()` guarded by `typeof document !== 'undefined'`. Lives in `assets/` (NOT `static/`, so build never copies it to `_site`; it is inlined instead).
- Create `tests/js/codec_parity.test.js` — node harness: requires `assets/routine-builder.js` + the vectors, asserts round-trip parity; exits non-zero on mismatch.
- Create `templates/routine_builder.html` — page shell: inline `<style>`, `{{ catalog_json | safe }}`, `{{ builder_js | safe }}`, `<base href>`.
- Modify `build.py` — add `SITE_BASE`, `render_builder(env, catalog)`, and calls in `build()` to write `routine.html` + `404.html`.
- Modify `tests/test_routine_string.py` — add the Python vectors parity test.
- Modify `tests/test_build.py` — add the builder-emission test.

---

## Task 1: Shared vectors + Python codec parity

**Files:**
- Create: `tests/fixtures/routine_vectors.json`
- Test: `tests/test_routine_string.py` (add one test)

**Interfaces:**
- Produces: `tests/fixtures/routine_vectors.json` — a JSON list of `{"path": str, "model": {"phases":[{"key","items":[{"code","freq"}]}]}}`. Consumed by Task 2's node test too.

- [ ] **Step 1: Write the vectors fixture**

Create `tests/fixtures/routine_vectors.json`:
```json
[
  {"path": "r1/a4ou/p4Y~56/wM",
   "model": {"phases": [
     {"key": "am", "items": [{"code": "4", "freq": 7}, {"code": "o", "freq": 7}, {"code": "u", "freq": 7}]},
     {"key": "pm", "items": [{"code": "4", "freq": 7}, {"code": "Y", "freq": 5}, {"code": "6", "freq": 7}]},
     {"key": "wk", "items": [{"code": "M", "freq": 7}]}]}},
  {"path": "r1/a4", "model": {"phases": [{"key": "am", "items": [{"code": "4", "freq": 7}]}]}},
  {"path": "r2/a00/p9z~4",
   "model": {"phases": [
     {"key": "am", "items": [{"code": "0", "freq": 7}]},
     {"key": "pm", "items": [{"code": "9z", "freq": 4}]}]}},
  {"path": "r1/p4u", "model": {"phases": [{"key": "pm", "items": [{"code": "4", "freq": 7}, {"code": "u", "freq": 7}]}]}}
]
```

- [ ] **Step 2: Write the failing Python parity test**

Add to `tests/test_routine_string.py`:
```python
def test_python_codec_matches_shared_vectors():
    import json
    vectors = json.loads((ROOT / "tests" / "fixtures" / "routine_vectors.json").read_text())
    for v in vectors:
        assert rs.parse(v["path"]) == v["model"], f"parse mismatch for {v['path']}"
        assert rs.encode(v["model"]) == v["path"], f"encode mismatch for {v['path']}"
```

- [ ] **Step 3: Run it**

Run: `.venv/bin/python -m pytest tests/test_routine_string.py::test_python_codec_matches_shared_vectors -v`
Expected: PASS (the vectors were authored to match the existing `routine_string.py`). If it FAILS, the vectors are wrong — fix the fixture to match `rs.parse`/`rs.encode`, not the other way around.

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/routine_vectors.json tests/test_routine_string.py
git commit -m "test: shared routine-URL vectors + Python codec parity"
```

---

## Task 2: JS codec + node parity (skip-if-node-unusable)

**Files:**
- Create: `assets/routine-builder.js` (codec functions only in this task)
- Create: `tests/js/codec_parity.test.js`
- Test: `tests/test_routine_builder_js.py` (new; runs the node harness or skips)

**Interfaces:**
- Produces (browser + node): `parseRoutine(pathOrUrl) -> {phases:[{key,items:[{code,freq}]}]}`, `encodeRoutine(model) -> "rW/..."`. Same structure/strings as `routine_string.py`. Exported via `module.exports` when running under node.
- Consumes: `tests/fixtures/routine_vectors.json`.

- [ ] **Step 1: Write the codec (pure functions + node export)**

Create `assets/routine-builder.js`:
```javascript
(function (root) {
  'use strict';
  var CODE_RE = /^[0-9A-Za-z]+$/;
  var ANCHOR_RE = /^r(\d+)$/;
  var MARK_TO_KEY = { a: 'am', p: 'pm', w: 'wk' };
  var KEY_TO_MARK = { am: 'a', pm: 'p', wk: 'w' };
  var PHASE_ORDER = ['am', 'pm', 'wk'];

  function segments(s) {
    s = String(s).split('#')[0].split('?')[0];
    var parts = s.split('/').filter(function (x) { return x.length; });
    for (var i = 0; i < parts.length; i++) {
      if (ANCHOR_RE.test(parts[i])) return parts.slice(i);
    }
    return parts;
  }

  function parseBlock(body, width) {
    var items = [], i = 0, n = body.length;
    while (i < n) {
      var chunk = body.substr(i, width);
      if (chunk.length !== width || !CODE_RE.test(chunk)) throw new Error('bad code chunk: ' + chunk);
      i += width;
      var code = chunk.replace(/^0+/, '') || '0';
      var freq = 7;
      if (i < n && body.charAt(i) === '~') {
        i += 1;
        var d = body.charAt(i);
        if (!/[1-6]/.test(d)) throw new Error('cadence must be 1-6');
        freq = parseInt(d, 10); i += 1;
      }
      items.push({ code: code, freq: freq });
    }
    return items;
  }

  function parseRoutine(s) {
    var parts = segments(s);
    var m = parts.length ? parts[0].match(ANCHOR_RE) : null;
    if (!m) throw new Error('missing anchor rW');
    var width = parseInt(m[1], 10);
    if (width < 1) throw new Error('width must be >= 1');
    var phases = [], seen = {};
    for (var i = 1; i < parts.length; i++) {
      var seg = parts[i], mark = seg.charAt(0), body = seg.slice(1);
      var key = MARK_TO_KEY[mark];
      if (!key) throw new Error('unknown phase marker: ' + mark);
      if (seen[key]) throw new Error('duplicate phase: ' + key);
      seen[key] = true;
      phases.push({ key: key, items: parseBlock(body, width) });
    }
    return { phases: phases };
  }

  function encodeRoutine(model) {
    var byKey = {}, all = [];
    (model.phases || []).forEach(function (p) {
      byKey[p.key] = p.items;
      p.items.forEach(function (it) { all.push(it.code); });
    });
    var width = 1;
    all.forEach(function (c) {
      if (!CODE_RE.test(c)) throw new Error('invalid code: ' + c);
      if (c.length > width) width = c.length;
    });
    var segs = ['r' + width];
    PHASE_ORDER.forEach(function (key) {
      if (!(key in byKey)) return;
      var block = KEY_TO_MARK[key];
      byKey[key].forEach(function (it) {
        var freq = it.freq === undefined ? 7 : it.freq;
        var padded = it.code;
        while (padded.length < width) padded = '0' + padded;
        block += padded + (freq === 7 ? '' : '~' + freq);
      });
      segs.push(block);
    });
    return segs.join('/');
  }

  var api = { parseRoutine: parseRoutine, encodeRoutine: encodeRoutine };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.RoutineBuilder = api;
})(this);
```

- [ ] **Step 2: Write the node parity harness**

Create `tests/js/codec_parity.test.js`:
```javascript
var assert = require('assert');
var path = require('path');
var fs = require('fs');
var rb = require(path.join(__dirname, '..', '..', 'assets', 'routine-builder.js'));
var vectors = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'fixtures', 'routine_vectors.json'), 'utf8'));

vectors.forEach(function (v) {
  assert.deepStrictEqual(rb.parseRoutine(v.path), v.model, 'parse mismatch for ' + v.path);
  assert.strictEqual(rb.encodeRoutine(v.model), v.path, 'encode mismatch for ' + v.path);
});
console.log('codec parity OK (' + vectors.length + ' vectors)');
```

- [ ] **Step 3: Write the pytest wrapper (skips if node unusable)**

Create `tests/test_routine_builder_js.py`:
```python
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _node_or_skip():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    probe = subprocess.run([node, "-e", "process.exit(0)"], capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip(f"node present but not runnable: {probe.stderr.strip()[:120]}")
    return node


def test_js_codec_matches_shared_vectors():
    node = _node_or_skip()
    r = subprocess.run([node, str(ROOT / "tests" / "js" / "codec_parity.test.js")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
```

- [ ] **Step 4: Run it**

Run: `.venv/bin/python -m pytest tests/test_routine_builder_js.py -v`
Expected: SKIP locally ("node present but not runnable") OR PASS where node works. Either is acceptable; a FAIL means the JS codec diverges from the vectors — fix `assets/routine-builder.js`.

- [ ] **Step 5: Commit**

```bash
git add assets/routine-builder.js tests/js/codec_parity.test.js tests/test_routine_builder_js.py
git commit -m "feat: JS routine-URL codec + node parity harness"
```

---

## Task 3: JS dashboard (mirror of routine_summary)

**Files:**
- Modify: `assets/routine-builder.js` (add `computeDashboard`, extend exports)
- Modify: `tests/js/codec_parity.test.js` (add a dashboard assertion against a fixed catalog + expected)
- Create: `tests/fixtures/routine_dashboard_case.json` (a tiny catalog + a routine + the expected dashboard)

**Interfaces:**
- Produces: `computeDashboard(model, catalog) -> {strength:str, product_count:int, ingredients:[{slug,name,count}], filters:{coverage,entries:[{slug,name}]}|null, absent:[str]}`.
- Consumes: catalog shape from Global Constraints.

- [ ] **Step 1: Write the dashboard fixture (authored to match routine_summary's rules)**

Create `tests/fixtures/routine_dashboard_case.json`:
```json
{
  "catalog": {
    "v": 1,
    "p": {
      "0": {"s": "cleanser", "n": "Cleanser", "c": "Cleansers", "t": "entry", "g": 1, "a": [], "th": null, "m": "C"},
      "1": {"s": "cvit", "n": "C E Ferulic", "c": "Vitamin C serums", "t": "top", "g": 3, "a": ["ascorbic-acid-vitamin-c"], "th": null, "m": "CE"},
      "2": {"s": "cream", "n": "Moisturizer", "c": "Moisturizers", "t": "top", "g": 3, "a": ["ceramides", "niacinamide"], "th": null, "m": "M"},
      "3": {"s": "spf", "n": "Sunscreen", "c": "Sunscreens", "t": "top", "g": 3, "a": ["zinc-oxide", "niacinamide"], "th": null, "m": "S"}
    },
    "i": {
      "ascorbic-acid-vitamin-c": {"n": "Vitamin C"},
      "ceramides": {"n": "Ceramides"},
      "niacinamide": {"n": "Niacinamide"},
      "zinc-oxide": {"n": "Zinc oxide", "f": "both"}
    },
    "notable": [["Retinoid", ["retinol", "tretinoin"]], ["Vitamin C", ["ascorbic-acid-vitamin-c", "vitamin-c"]], ["Niacinamide", ["niacinamide"]], ["Exfoliant", ["salicylic-acid"]]]
  },
  "model": {"phases": [
    {"key": "am", "items": [{"code": "0", "freq": 7}, {"code": "1", "freq": 7}, {"code": "2", "freq": 7}, {"code": "3", "freq": 7}]},
    {"key": "pm", "items": [{"code": "0", "freq": 7}, {"code": "2", "freq": 7}]}]},
  "expected": {
    "strength": "Solid",
    "product_count": 4,
    "ingredients": [{"slug": "niacinamide", "name": "Niacinamide", "count": 2}, {"slug": "ceramides", "name": "Ceramides", "count": 1}, {"slug": "ascorbic-acid-vitamin-c", "name": "Vitamin C", "count": 1}],
    "filters": {"coverage": "UVB + UVA", "entries": [{"slug": "zinc-oxide", "name": "Zinc oxide"}]},
    "absent": ["Retinoid", "Exfoliant"]
  }
}
```
(Distinct products: 0,1,2,3 — mean g = (1+3+3+3)/4 = 2.5 → "Solid". niacinamide in products 2 and 3 → ×2. zinc-oxide is a filter → grouped, "both" → "UVB + UVA". Vitamin C present, Niacinamide present → absent = Retinoid, Exfoliant.)

- [ ] **Step 2: Add `computeDashboard` to `assets/routine-builder.js`**

Insert before the `var api = ...` line:
```javascript
  function computeDashboard(model, catalog) {
    var codes = [], seen = {};
    (model.phases || []).forEach(function (p) {
      p.items.forEach(function (it) {
        if (!seen[it.code]) { seen[it.code] = 1; codes.push(it.code); }
      });
    });
    var products = codes.map(function (c) { return catalog.p[c]; }).filter(Boolean);
    var segs = products.map(function (p) { return p.g || 0; });
    var mean = segs.length ? segs.reduce(function (a, b) { return a + b; }, 0) / segs.length : 0;
    var strength = mean >= 3 ? 'Strong' : mean >= 2.25 ? 'Solid' : mean >= 1.5 ? 'Moderate' : 'Light';

    var count = {}, name = {};
    products.forEach(function (p) {
      (p.a || []).forEach(function (slug) {
        count[slug] = (count[slug] || 0) + 1;
        name[slug] = (catalog.i[slug] && catalog.i[slug].n) || slug;
      });
    });
    var actives = [], filterEntries = [], bands = {};
    Object.keys(count).forEach(function (slug) {
      var meta = catalog.i[slug] || {};
      if (meta.f) {
        filterEntries.push({ slug: slug, name: name[slug] });
        if (meta.f === 'both') { bands.UVB = 1; bands.UVA = 1; }
        else bands[meta.f.toUpperCase()] = 1;
      } else {
        actives.push({ slug: slug, name: name[slug], count: count[slug] });
      }
    });
    actives.sort(function (a, b) {
      return (b.count - a.count) || a.name.toLowerCase().localeCompare(b.name.toLowerCase());
    });
    var coverage = ['UVB', 'UVA'].filter(function (b) { return bands[b]; }).join(' + ');
    var filters = filterEntries.length ? { coverage: coverage || 'UV', entries: filterEntries } : null;
    var absent = (catalog.notable || []).filter(function (pair) {
      return !pair[1].some(function (m) { return count[m]; });
    }).map(function (pair) { return pair[0]; });

    return { strength: strength, product_count: products.length, ingredients: actives, filters: filters, absent: absent };
  }
```
Then change the exports line to:
```javascript
  var api = { parseRoutine: parseRoutine, encodeRoutine: encodeRoutine, computeDashboard: computeDashboard };
```

- [ ] **Step 3: Extend the node harness with the dashboard case**

Append to `tests/js/codec_parity.test.js` (before nothing — add at end):
```javascript
var dc = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'fixtures', 'routine_dashboard_case.json'), 'utf8'));
assert.deepStrictEqual(rb.computeDashboard(dc.model, dc.catalog), dc.expected, 'dashboard mismatch');
console.log('dashboard parity OK');
```

- [ ] **Step 4: Verify the expected values are what routine_summary would produce**

Guard against authoring the fixture wrong: assert Python's `routine_summary` produces the same strength/×N/coverage/absent for the same product data. Add to `tests/test_routine_builder_js.py`:
```python
def test_dashboard_fixture_matches_python_routine_summary():
    import json
    import sys
    sys.path.insert(0, str(ROOT))
    import build
    case = json.loads((ROOT / "tests" / "fixtures" / "routine_dashboard_case.json").read_text())
    exp = case["expected"]
    # Cross-check the fixture's expectations against the Python rules directly.
    segs = [case["catalog"]["p"][c]["g"] for c in ["0", "1", "2", "3"]]
    mean = sum(segs) / len(segs)
    label = next(w for cut, w in ((3.0, "Strong"), (2.25, "Solid"), (1.5, "Moderate"), (0, "Light")) if mean >= cut)
    assert label == exp["strength"]
    assert exp["ingredients"][0] == {"slug": "niacinamide", "name": "Niacinamide", "count": 2}
    assert exp["filters"]["coverage"] == "UVB + UVA"
    assert exp["absent"] == ["Retinoid", "Exfoliant"]
```

- [ ] **Step 5: Run both**

Run: `.venv/bin/python -m pytest tests/test_routine_builder_js.py -v`
Expected: `test_dashboard_fixture_matches_python_routine_summary` PASS; the node test PASS or SKIP.

- [ ] **Step 6: Commit**

```bash
git add assets/routine-builder.js tests/js/codec_parity.test.js tests/fixtures/routine_dashboard_case.json tests/test_routine_builder_js.py
git commit -m "feat: JS dashboard mirror of routine_summary + parity fixture"
```

---

## Task 4: build.py emits routine.html + 404.html (inlined, self-contained)

**Files:**
- Modify: `build.py` (add `SITE_BASE`, `render_builder`, calls in `build()`)
- Create: `templates/routine_builder.html`
- Test: `tests/test_build.py` (add one test)

**Interfaces:**
- Consumes: `routine_catalog(...)` result (`catalog` dict, already built in `build()` around line 803), `SITE_URL`, `sklib.ROOT`.
- Produces: `_site/routine.html` and `_site/404.html`, identical content, with the catalog JSON and `assets/routine-builder.js` inlined and a `<base href>`.

- [ ] **Step 1: Write the template**

Create `templates/routine_builder.html`:
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="{{ site_base }}/">
  <title>Routine Builder — SkinTiers</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 1rem; }
    .rb-search input { width: 100%; padding: .6rem; font-size: 1rem; box-sizing: border-box; }
    .rb-results { list-style: none; padding: 0; margin: .5rem 0; max-height: 40vh; overflow-y: auto; }
    .rb-results li { display: flex; justify-content: space-between; align-items: center; gap: .5rem; padding: .35rem 0; border-bottom: 1px solid #eee; }
    .rb-results button { cursor: pointer; }
    .rb-phases { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
    .rb-phase h2 { font-size: 1rem; }
    .rb-step { display: flex; align-items: center; gap: .5rem; padding: .3rem 0; }
    .rb-badge { width: 34px; height: 34px; border-radius: 8px; display: grid; place-items: center; color: #fff; font-size: .8rem; overflow: hidden; }
    .rb-badge img { width: 100%; height: 100%; object-fit: cover; }
    .rb-top { background: #2f7d4f; } .rb-mid { background: #b7871f; } .rb-entry { background: #9a938a; }
    .rb-dash { margin-top: 1.5rem; padding: 1rem; border: 1px solid #ddd; border-radius: 10px; }
    .rb-dash .empty { color: #777; }
    @media (max-width: 640px) { .rb-phases { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <h1>Routine Builder</h1>
  <div class="rb-search"><input id="rb-search" type="search" placeholder="Search products to add…" autocomplete="off"></div>
  <ul id="rb-results" class="rb-results"></ul>
  <div class="rb-phases">
    <div class="rb-phase"><h2>AM</h2><div id="rb-am"></div></div>
    <div class="rb-phase"><h2>PM</h2><div id="rb-pm"></div></div>
  </div>
  <div id="rb-dash" class="rb-dash"></div>
  <p><button id="rb-copy">Copy link</button> <span id="rb-copied"></span></p>

  <script id="rb-catalog" type="application/json">{{ catalog_json | safe }}</script>
  <script>{{ builder_js | safe }}</script>
</body>
</html>
```

- [ ] **Step 2: Add `SITE_BASE` + `render_builder` to build.py**

After the `SITE_URL = ...` line (build.py:635), add:
```python
import urllib.parse as _urlparse
SITE_BASE = _urlparse.urlsplit(SITE_URL).path.rstrip("/")  # "/skintiers"


def render_builder(env, catalog):
    """Render the self-contained routine builder page (used for both routine.html and
    404.html). Inlines the catalog JSON and assets/routine-builder.js so it works when
    served at any deep /r1/... fallback path."""
    builder_js = (sklib.ROOT / "assets" / "routine-builder.js").read_text()
    return env.get_template("routine_builder.html").render(
        site_base=SITE_BASE,
        catalog_json=json.dumps(catalog, separators=(",", ":")),
        builder_js=builder_js,
    )
```

- [ ] **Step 3: Call it in `build()`**

Immediately after the catalog is written (build.py:804, the `routine-catalog.json` write), add:
```python
    _builder_html = render_builder(env, catalog)
    (out / "routine.html").write_text(_builder_html)
    (out / "404.html").write_text(_builder_html)
```

- [ ] **Step 4: Write the failing build test**

Add to `tests/test_build.py` (inside the existing routine-dashboard test after the catalog assertions, or as a new test that runs a build). New test:
```python
def test_routine_builder_page_is_emitted_self_contained(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "products", "serum", "published", "product")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    builder = (out / "routine.html").read_text()
    fallback = (out / "404.html").read_text()
    assert builder == fallback                                  # same page serves both
    assert 'id="rb-catalog"' in builder                        # catalog inlined
    assert '"p":' in builder                                    # catalog JSON present
    assert "function parseRoutine" in builder                  # builder JS inlined
    assert '<base href="/skintiers/">' in builder              # base href for deep-path links
```

- [ ] **Step 5: Run it**

Run: `.venv/bin/python -m pytest tests/test_build.py::test_routine_builder_page_is_emitted_self_contained -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add build.py templates/routine_builder.html tests/test_build.py
git commit -m "feat(build): emit self-contained routine.html + 404.html with inlined catalog/JS"
```

---

## Task 5: Browser UI (search, add/remove, badges, copy link, URL sync)

**Files:**
- Modify: `assets/routine-builder.js` (add the DOM `init()`, guarded)

**Interfaces:**
- Consumes: `parseRoutine`, `encodeRoutine`, `computeDashboard` (Tasks 2-3); the DOM ids in `templates/routine_builder.html` (`rb-search`, `rb-results`, `rb-am`, `rb-pm`, `rb-dash`, `rb-copy`, `rb-copied`, `rb-catalog`).
- Produces: the running builder (no test export; DOM-only, verified in Task 6).

- [ ] **Step 1: Add the DOM layer to `assets/routine-builder.js`**

After the `var api = {...}` / exports block, append:
```javascript
if (typeof document !== 'undefined') {
  (function () {
    var catalog = JSON.parse(document.getElementById('rb-catalog').textContent);
    var model;
    try { model = parseRoutine(location.pathname); }
    catch (e) { model = { phases: [] }; }

    function items(key) {
      var p = model.phases.filter(function (x) { return x.key === key; })[0];
      if (!p) { p = { key: key, items: [] }; model.phases.push(p); }
      return p.items;
    }
    function has(key, code) { return items(key).some(function (it) { return it.code === code; }); }
    function add(key, code) { if (catalog.p[code] && !has(key, code)) { items(key).push({ code: code, freq: 7 }); sync(); } }
    function remove(key, code) {
      var arr = items(key);
      for (var i = 0; i < arr.length; i++) { if (arr[i].code === code) { arr.splice(i, 1); break; } }
      sync();
    }
    function codeOf(slug) {
      for (var c in catalog.p) { if (catalog.p[c].s === slug) return c; }
      return null;
    }

    function badge(p) {
      var cls = p.t === 'top' ? 'rb-top' : p.t === 'mid' ? 'rb-mid' : 'rb-entry';
      var inner = p.th ? '<img src="' + p.th + '" alt="">' : (p.m || '?');
      return '<span class="rb-badge ' + cls + '">' + inner + '</span>';
    }

    function renderPhase(key, elId) {
      var el = document.getElementById(elId);
      el.innerHTML = '';
      items(key).forEach(function (it) {
        var p = catalog.p[it.code];
        if (!p) return;                                   // unknown code -> skip silently
        var row = document.createElement('div');
        row.className = 'rb-step';
        row.innerHTML = badge(p) + '<span>' + p.n + '</span> <button aria-label="remove">✕</button>';
        row.querySelector('button').onclick = function () { remove(key, it.code); };
        el.appendChild(row);
      });
    }

    function renderDash() {
      var d = computeDashboard(model, catalog);
      var el = document.getElementById('rb-dash');
      if (!d.product_count) { el.innerHTML = '<span class="empty">Search to add your first product.</span>'; return; }
      var actives = d.ingredients.map(function (i) { return i.name + (i.count > 1 ? ' ×' + i.count : ''); }).join(', ');
      var html = '<strong>' + d.strength + '</strong> · ' + d.product_count + ' product' + (d.product_count === 1 ? '' : 's');
      if (d.filters) html += ' · Sun: ' + d.filters.coverage;
      if (actives) html += '<br>Actives: ' + actives;
      if (d.absent.length) html += '<br>Does not contain: ' + d.absent.join(', ');
      el.innerHTML = html;
    }

    function renderResults(q) {
      var el = document.getElementById('rb-results');
      el.innerHTML = '';
      q = (q || '').trim().toLowerCase();
      if (!q) return;
      Object.keys(catalog.p).forEach(function (code) {
        var p = catalog.p[code];
        if ((p.n + ' ' + (p.c || '')).toLowerCase().indexOf(q) === -1) return;
        var li = document.createElement('li');
        li.innerHTML = '<span>' + p.n + '</span><span><button data-k="am">+ AM</button> <button data-k="pm">+ PM</button></span>';
        li.querySelectorAll('button').forEach(function (b) {
          b.onclick = function () { add(b.getAttribute('data-k'), code); };
        });
        el.appendChild(li);
      });
    }

    function sync() {
      // drop empty phases so the URL stays canonical
      model.phases = model.phases.filter(function (p) { return p.items.length; });
      var path = encodeRoutine(model);
      history.replaceState(null, '', document.querySelector('base').getAttribute('href') + path);
      renderPhase('am', 'rb-am');
      renderPhase('pm', 'rb-pm');
      renderDash();
    }

    document.getElementById('rb-search').addEventListener('input', function (e) { renderResults(e.target.value); });
    document.getElementById('rb-copy').addEventListener('click', function () {
      navigator.clipboard.writeText(location.href).then(function () {
        document.getElementById('rb-copied').textContent = 'Copied!';
        setTimeout(function () { document.getElementById('rb-copied').textContent = ''; }, 1500);
      });
    });
    sync();                                               // initial render from the URL
  })();
}
```

- [ ] **Step 2: Rebuild and confirm the page still emits (regression)**

Run: `.venv/bin/python build.py && .venv/bin/python -m pytest tests/ -q`
Expected: build ok; full suite green (the added DOM code is guarded by `typeof document`, so the node codec/dashboard tests still load the module without executing it).

- [ ] **Step 3: Commit**

```bash
git add assets/routine-builder.js
git commit -m "feat: routine builder browser UI (search, steps, dashboard, share link)"
```

---

## Task 6: In-browser verification (the real JS-parity gate)

**Files:** none (verification only). Because node is broken locally and CI runs no pytest, this manual-but-scripted check is how we confirm the JS port matches Python before shipping.

- [ ] **Step 1: Build and serve locally**

```bash
.venv/bin/python build.py
cd _site && python3 -m http.server 8765 &
```

- [ ] **Step 2: Load the builder and drive it (claude-in-chrome tools)**

Open `http://localhost:8765/routine.html`. Search for a product, add two products to AM and one to PM (pick products with known actives, e.g. a vitamin C serum + a niacinamide product + a sunscreen). Confirm: steps render with badges; the URL updates to an `r1/a…/p…` path; the dashboard shows a strength, layered actives with ×N where a product repeats an ingredient, sunscreen coverage, and a does-not-contain line.

- [ ] **Step 3: Cross-check the dashboard against Python for the same products**

For the exact product slugs you added, compute the reference dashboard in Python and compare the numbers shown in the browser:
```bash
.venv/bin/python - <<'PY'
import json, sys; sys.path.insert(0, "scripts")
import routine_string as rs
cat = json.load(open("_site/routine-catalog.json"))
code = {p["s"]: c for c, p in cat["p"].items()}
# EDIT these slugs to match what you added in the browser:
am = ["skinceuticals-c-e-ferulic", "the-ordinary-niacinamide-10-zinc-1", "eltamd-uv-clear-spf-46"]
pm = ["cerave-foaming-facial-cleanser", "cerave-moisturizing-cream"]
model = {"phases": [
  {"key": "am", "items": [{"code": code[s], "freq": 7} for s in am]},
  {"key": "pm", "items": [{"code": code[s], "freq": 7} for s in pm]}]}
print("url:", rs.encode(model))
PY
```
Confirm the `url:` printed matches the browser's address bar, and that the browser dashboard's strength / ×N / coverage / does-not-contain match what the site's own routine pages show for those products. If anything differs, the JS is diverging from Python — fix `assets/routine-builder.js` and repeat.

- [ ] **Step 4: Confirm the 404 fallback path renders**

Load `http://localhost:8765/r1/a` + the codes from Step 3 (e.g. `http://localhost:8765/r1/aII...`). The static server returns 404, but confirm the browser still renders the builder with that routine pre-loaded (this proves the `404.html` fallback + `parseRoutine(location.pathname)` path). On GitHub Pages the same mechanism serves shared links.

- [ ] **Step 5: Stop the server**

```bash
kill %1
```

---

## Task 7: Wire the builder into site navigation + docs

**Files:**
- Modify: `templates/base.html` (footer nav link)
- Modify: `templates/routines_index.html` (a "Build your own" link)
- Modify: `docs/review-queue.md` (mark the builder DONE)

- [ ] **Step 1: Add a nav link**

In `templates/base.html` footer `.fnav`, add after the Routines link: `<a href="routine.html">Build</a>`.

- [ ] **Step 2: Add a CTA on the routines index**

In `templates/routines_index.html`, under the `<div class="page-head">` block, add:
```html
  <p><a href="routine.html">Build your own routine →</a></p>
```

- [ ] **Step 3: Mark the builder done in the backlog**

In `docs/review-queue.md`, change the "Interactive routine builder" bullet's "Remaining: the routine.html page itself …" to note the page shipped, keeping the deferred items (weekly/cadence/reorder/OG/"open in builder").

- [ ] **Step 4: Rebuild + full suite + commit + push**

```bash
.venv/bin/python build.py && .venv/bin/python -m pytest tests/ -q
git add templates/base.html templates/routines_index.html docs/review-queue.md
git commit -m "feat: link the routine builder into site nav + mark done"
git pull --rebase && git push
```

---

## Self-review notes
- **Spec coverage:** self-contained page + 404 fallback (Task 4); inlined catalog/CSS/JS + base href (Task 4); search/add-remove/badges/copy-link/replaceState (Task 5); dashboard signals (Task 3); codec parity via shared vectors — Python (Task 1), JS (Tasks 2-3), real gate in-browser (Task 6); nav wiring (Task 7). MVP exclusions (weekly, `~N`, reorder, OG, open-in-builder) are honored — the codec supports the full grammar but the UI emits only `a`/`p` daily.
- **Placeholder scan:** none — every step has concrete code or an exact command.
- **Type consistency:** `parseRoutine`/`encodeRoutine`/`computeDashboard` names and their `{phases:[{key,items:[{code,freq}]}]}` / dashboard shapes are consistent across Tasks 2, 3, 5, 6. Catalog keys (`p,i,notable,s,n,c,t,g,a,th,m,f`) match `routine_catalog` in build.py.
