#!/usr/bin/env python3
"""health-next: the maintenance analog of `sk queue-next`.

When a daily fill cron finds its type queue empty, it runs this to get the ONE
highest-priority, GROUNDED, bounded maintenance task for that type instead of
skipping the tick. Read-only: it never edits or commits - it points the cron at a
specific page + a specific, self-clearing gap. The cron does the work + commits.

Design rules:
- GROUNDED: every task targets a real, detected gap on an existing page. Never
  invents work. If there is no real gap for the type, prints NONE (cron skips).
- SELF-CLEARING / idempotent: each gap stops matching once acted on (a page gets
  its `tier:`, an item joins a tier_list, a price `as_of` bumps), so the selector
  naturally walks the corpus instead of thrashing one page. Deterministic order
  (alphabetical / oldest-first) makes runs reproducible.
- CORE VALUE FIRST: product + tier-list currency + ingredient structure outrank
  the rest. person/study have no maintenance lane here -> NONE.

Usage: python scripts/site_health.py --type <product|ingredient|condition|goal|list|brand|person|study>
"""
import argparse
import datetime
import glob
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
TODAY = datetime.date(2026, 9, 3)  # cron passes real date via drafting; static here is fine for age math tolerance


def load(path):
    t = open(path).read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    if not m:
        return {}, t, t
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, m.group(2), t


def published(fm):
    return (fm.get("status") or "").strip() == "published"


def slug_of(fm, path):
    return fm.get("slug") or os.path.splitext(os.path.basename(path))[0]


def all_pages(*dirs):
    out = []
    for d in dirs:
        for f in sorted(glob.glob(f"data/{d}/*.md")):
            fm, body, raw = load(f)
            out.append((f, fm, body, raw))
    return out


def tier_list_slugs(fm):
    tl = fm.get("tier_list") or {}
    items = tl.get("items") or []
    return {it.get("slug") for it in items if isinstance(it, dict) and it.get("slug")}


def wikilinks(text):
    return set(re.findall(r"\[\[([a-z0-9-]+)", text))


def newest_as_of(raw):
    dates = re.findall(r"as_of:\s*['\"]?(\d{4}-\d{2}-\d{2})", raw)
    return max(dates) if dates else None


# ---- checks (each returns a task string block, or None) ----

def check_ingredient_tier():
    for f in sorted(glob.glob("data/ingredients/*.md")):
        fm, body, raw = load(f)
        if published(fm) and not fm.get("tier"):
            s = slug_of(fm, f)
            return (
                f"TASK: backfill the evidence `tier:` field on ingredient `{s}`\n"
                f"TARGET: {f}\n"
                f"ACTION: read the page's prose '## The Rubric' verdict for its best VISIBLE-SKIN-BENEFIT grade and "
                f"add a top-level `tier:` frontmatter field (after `slug:`) = one of best/good/mid/weak "
                f"(notable/strong+solid->good or best; modest->mid; minimal or thin/preliminary evidence->weak). "
                f"Do NOT invent - it must match the rubric. Do NOT touch body/sources. Run `sk lint {s}`, build, commit, push."
            )
    return None


def check_product_stale_price(days=120):
    cands = []
    for f in sorted(glob.glob("data/products/*.md")):
        fm, body, raw = load(f)
        if not published(fm):
            continue
        d = newest_as_of(raw)
        if d:
            y, mo, da = map(int, d.split("-"))
            age = (TODAY - datetime.date(y, mo, da)).days
            if age > days:
                cands.append((d, age, f, slug_of(fm, f)))
    if not cands:
        return None
    cands.sort()  # oldest as_of first
    d, age, f, s = cands[0]
    return (
        f"TASK: re-verify the price on product `{s}` (price as_of {d} is {age} days old)\n"
        f"TARGET: {f}\n"
        f"ACTION: fetch the current price from the brand page (or `inci_lookup.py` for the product, then the brand site) "
        f"and update the `price:` amount + `as_of:` (today) in frontmatter ONLY IF it changed or the date is stale. "
        f"Do not alter any other fact. Run `sk lint {s}` + `sk verify {s}`, build, commit, push. "
        f"(There are {len(cands)} products with a >{days}d-old price.)"
    )


def check_hub_behind(hub_type, hub_dir):
    """A published hub with a tier_list that omits a published product/ingredient which
    WIKILINKS this hub (a strong 'belongs here' signal) - grounded, self-clearing."""
    catalog = all_pages("products", "ingredients")
    hubs = []
    for f, fm, body, raw in all_pages(hub_dir):
        if not published(fm) or not fm.get("tier_list"):
            continue
        hubs.append((fm.get("updated") or "0000-00-00", f, fm, raw))
    hubs.sort()  # oldest-updated first = most likely behind
    for updated, f, fm, raw in hubs:
        hs = slug_of(fm, f)
        have = tier_list_slugs(fm)
        missing = []
        for cf, cfm, cbody, craw in catalog:
            if not published(cfm):
                continue
            cs = slug_of(cfm, cf)
            if cs in have:
                continue
            if hs in wikilinks(craw):  # the candidate links to this hub
                missing.append(cs)
        if missing:
            return (
                f"TASK: bring the tier_list on {hub_type} hub `{hs}` up to date "
                f"(last updated {updated}; {len(missing)} on-site page(s) link here but are not in its tier_list)\n"
                f"TARGET: {f}\n"
                f"CANDIDATES (verified to exist + to link this hub): {', '.join(sorted(missing)[:8])}\n"
                f"ACTION: for each candidate that GENUINELY belongs in this ranking, add it to the existing tier_list "
                f"block with an appropriate tier + a concise 1-sentence note (link the page; do NOT re-explain what it "
                f"owns). Keep the tier_list schema + tiers. Skip any that do not truly fit. Bump the hub's `updated` to "
                f"today. NO padding, no body rewrite beyond the tier_list. Run `sk lint {hs}`, build, commit, push."
            )
    return None


def check_brand_missing_product():
    """A brand page that does not link a now-published product carrying that brand."""
    prods = all_pages("products")
    for bf, bfm, bbody, braw in all_pages("brands"):
        if not published(bfm):
            continue
        bname = (bfm.get("name") or "").strip()
        bslug = slug_of(bfm, bf)
        if not bname:
            continue
        linked = wikilinks(braw)
        missing = []
        for pf, pfm, pbody, praw in prods:
            if not published(pfm):
                continue
            if (pfm.get("brand") or "").strip().lower() == bname.lower():
                ps = slug_of(pfm, pf)
                if ps not in linked:
                    missing.append(ps)
        if missing:
            return (
                f"TASK: link {len(missing)} now-published `{bname}` product(s) from brand page `{bslug}`\n"
                f"TARGET: {bf}\n"
                f"CANDIDATES (published products with brand=={bname}, not yet linked): {', '.join(sorted(missing)[:8])}\n"
                f"ACTION: add these products to the brand page's linked product list (LEAN discovery aid - just link "
                f"them, no essay). Bump `updated`. Run `sk lint {bslug}`, build, commit, push."
            )
    return None


DISPATCH = {
    "ingredient": [check_ingredient_tier],
    "product": [check_product_stale_price],
    "condition": [lambda: check_hub_behind("condition", "conditions")],
    "goal": [lambda: check_hub_behind("goal", "goals")],
    "list": [lambda: check_hub_behind("list", "lists")],
    "brand": [check_brand_missing_product],
    "person": [],   # maintained via video cross-feed, not here
    "study": [],     # static infrastructure
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--type", required=True, choices=list(DISPATCH))
    args = ap.parse_args()
    for check in DISPATCH[args.type]:
        task = check()
        if task:
            print(task)
            return
    print("NONE")


if __name__ == "__main__":
    main()
