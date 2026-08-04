# Routine Builder — Design Spec (MVP)

**Goal:** One self-contained page where a reader searches the product catalog, adds products to an AM or PM
routine, sees the live skeptical dashboard, and gets a shareable URL.

**Architecture:** A static page built by `build.py`, written to **both** `_site/routine.html` (the empty
"start here" page, HTTP 200) and `_site/404.html` (so GitHub Pages serves it for any shared `/r1/...` path).
The page is **self-contained** — inlined catalog JSON, inlined CSS (site tokens), inlined JS — because a shared
link is served at a deep path (`/skintiers/r1/aIOU6D/p46`) where relative asset URLs would 404. A
`<base href="{site base}/">` (build injects, e.g. `/skintiers/`) makes any product-page links resolve
correctly. No backend, no fetch.

## Scope (MVP)
IN: AM + PM phases, everything daily, search-driven add, add-order (no reorder), live dashboard, copyable URL.
OUT (grammar already supports; UI defers): weekly (`w`) phase, per-product cadence (`~N`), reordering,
"open in builder" links on curated routine pages, rich error notices, OG/share images.

## Components (one page, small JS modules)
1. **URL codec** (JS) mirroring `scripts/routine_string.py` (the AM/PM/daily subset): `parse(pathname) → model`,
   `encode(model) → "r1/a…/p…"`. Auto-sizes code width, `a`/`p` markers, no `~N`/`w` in MVP output.
   Verified against the SAME vectors the Python codec is tested on (see Testing) so the two cannot drift.
2. **Catalog** (inlined): the existing code-keyed `routine-catalog.json`
   `{v, p:{code:{s,n,c,t,g,a,th,m}}, i:{slug:{n,f?}}, notable:[[label,[members]]]}`.
3. **Search**: a text input filters catalog products by name + category substring (case-insensitive); each
   result row shows the product name + `[+ AM]` `[+ PM]` buttons.
4. **Model**: `{am: [code…], pm: [code…]}`, add-order. Same product may appear in AM and PM; adding a product
   already in that phase is a no-op (no exact-dup within a phase).
5. **Dashboard** (JS mirror of `routine_summary`): from the model + catalog, recompute on every change —
   - **strength**: mean of each distinct product's `g` (0–4) → Strong ≥3 / Solid ≥2.25 / Moderate ≥1.5 / Light.
   - **layered actives**: count distinct products carrying each non-filter active `a[]`; show `×N` when >1.
   - **does not contain**: each `notable` family with no member present.
   - **sunscreen**: actives that are UV filters (`i[a].f`) grouped → coverage `UVA` / `UVB` / `UVA + UVB`.
6. **Steps view**: AM and PM ordered lists; each row is a product badge (`th` photo or `m` monogram, framed in
   its tier `t` color) + name + `✕` remove.
7. **Share**: the URL *is* the state — `history.replaceState` updates `location.pathname` to
   `{base}r1/a…/p…` on every change; a **Copy link** button (`navigator.clipboard`) copies the full URL.

## Data flow
load → `parse(location.pathname)` → model → render(dashboard, steps). add/remove → mutate model → `encode` →
`replaceState` → re-render dashboard + steps. Search input → filter → render results (does not touch the URL).

## Error handling
- Malformed path → start from an empty model; never throw.
- A code with no catalog entry (product later unpublished) → skip it silently.
- Empty routine → dashboard shows a "search to add your first product" hint, not zeros.

## Files
- Create `templates/routine_builder.html` (the page: inlined `<style>`, `{{ catalog_json }}`, inlined
  `<script>`). The JS lives inline in this one template — no separate `static/*.js` file — to satisfy the
  self-contained requirement (a separate file would 404 at a deep `/r1/...` path).
- Modify `build.py`: compute `SITE_BASE` from `SITE_URL`; render the builder once and write it to both
  `routine.html` and `404.html`; inline the catalog JSON into it.
- Create `tests/fixtures/routine_vectors.json`: shared (path ↔ model) vectors.
- Create `tests/test_routine_url_js.py`: pytest that runs `node` over a JS harness asserting the JS codec
  round-trips every vector identically to what `routine_string.py` produces (skips with a clear message if
  `node` is unavailable).
- Modify `tests/test_routine_string.py` (or add): assert `routine_string.py` satisfies the same vectors, so
  Python and JS are pinned to one source of truth.
- Modify `tests/test_build.py`: assert `routine.html` and `404.html` are emitted, contain the inlined catalog,
  and carry the `<base href>`.

## Testing
- **Codec parity** is the load-bearing test: one `routine_vectors.json`, checked by both a Python test and a
  `node` test. If the JS and Python encoders ever disagree, CI fails.
- **Dashboard parity** (lighter): a `node` test computes strength / does-not-contain / UVA-UVB for one known
  routine and asserts the same values `routine_summary` produces for it. Prevents the JS dashboard from
  drifting from the Python one.
- **Build**: both HTML files emitted, catalog inlined, base href present.

## Hosting note (GitHub Pages)
Path routes have no server rewrite on Pages, so `404.html` is the fallback that serves `/r1/...`. The response
carries a 404 status but renders normally for a human; OG tags (deferred) would still preview. This is the only
way to serve this exact URL shape on a static host; documented in the builder spec of `docs/review-queue.md`.
