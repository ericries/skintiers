#!/usr/bin/env python3
"""Fetch a product's INCI + front photo from incidecoder via plain HTTP.

incidecoder.com (aka INKEEDecoder) is SERVER-SIDE rendered, so a normal HTTP GET
returns the full ordered ingredient list and the real product front-photo URL -
no Apify browser render needed. This collapses the most common product-fill cost
(fetch INCI + price + photo) into one cheap, cacheable call. Fall back to the
Apify browser only when this reports a miss (bad slug, or the brand page for
price/marketing claims, which incidecoder does not carry).

The page is cached to the source cache so a later critic can re-verify offline.

Usage:
  python scripts/inci_lookup.py "Paula's Choice Peptide Booster"
  python scripts/inci_lookup.py --slug paulas-choice-peptide-booster
  python scripts/inci_lookup.py --photo "Differin Adapalene Gel"   # just the photo URL
  python scripts/inci_lookup.py --json "..."
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request

BASE = "https://incidecoder.com/products/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
PHOTO_RE = re.compile(r'https://incidecoder-content[^"\']+?front_photo_original\.[a-z]+', re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
# ordered INCI lives inside the "showmore-section-ingredlist-short" block
BLOCK_RE = re.compile(r'id="showmore-section-ingredlist-short".*?</div>', re.I | re.S)
ING_RE = re.compile(r'href="/ingredients/[a-z0-9-]+"[^>]*>(.*?)</a>', re.I | re.S)


def slugify(name):
    s = (name or "").lower().replace("&", " and ")
    s = re.sub(r"['`.]", "", s)          # drop apostrophes/periods: paula's -> paulas
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def fetch(slug):
    req = urllib.request.Request(BASE + slug, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace"), r.geturl()


def parse(html):
    title = (TITLE_RE.search(html) or [None, ""])[1].strip()
    # a bad slug redirects/renders the generic homepage title
    if not title or title.lower().startswith("inkeedecoder - decode") or "ingredients (explained)" not in title.lower():
        return None
    photo = (PHOTO_RE.search(html) or [None])[0]
    block = BLOCK_RE.search(html)
    inci = []
    if block:
        for m in ING_RE.finditer(block.group(0)):
            name = re.sub(r"<[^>]+>", "", m.group(1))
            name = re.sub(r"\s+", " ", name).replace("​", "").strip()
            if name and name not in inci:
                inci.append(name)
    return {"title": title, "photo": photo, "inci": inci}


def lookup(name=None, slug=None):
    tried = []
    cands = [slug] if slug else []
    if name and not slug:
        base = slugify(name)
        cands = [base, base + "-serum", base + "-gel", base + "-cream"]
    for s in cands:
        if not s or s in tried:
            continue
        tried.append(s)
        try:
            html, final = fetch(s)
        except Exception:
            continue
        got = parse(html)
        if got:
            got["slug"] = s
            got["url"] = BASE + s
            got["_html"] = html
            return got
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name", nargs="?", help="product name")
    ap.add_argument("--slug", help="exact incidecoder slug (skip name guessing)")
    ap.add_argument("--photo", action="store_true", help="print only the front-photo URL")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)
    got = lookup(args.name, args.slug)
    if not got:
        print("MISS: no incidecoder product page found; try a different slug or the Apify browser.")
        return 1
    if not args.no_cache:
        try:
            subprocess.run([sys.executable, "scripts/source_cache.py", "put", got["url"]],
                           input=got["_html"], text=True, capture_output=True)
        except Exception:
            pass
    if args.photo:
        print(got["photo"] or "MISS: no front photo")
        return 0 if got["photo"] else 1
    if args.json:
        print(json.dumps({k: v for k, v in got.items() if k != "_html"}, ensure_ascii=False, indent=2))
        return 0
    print(f"title: {got['title']}")
    print(f"url:   {got['url']}")
    print(f"photo: {got['photo'] or '(none)'}")
    print(f"inci ({len(got['inci'])}): " + ", ".join(got["inci"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
