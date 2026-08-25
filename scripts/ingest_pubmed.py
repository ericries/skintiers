#!/usr/bin/env python3
"""Auto-ingest recent HIGH-QUALITY dermatology studies from PubMed into the study
queue, so the daily study-fill cron drafts them under the normal 3-primary-source +
Opus-critic discipline. This NEVER auto-publishes; it only proposes grounded, sourced
candidates - the same bar as a human adding to the queue.

The "very high" source filter (edit the lists below to tune):
  - a small allowlist of top dermatology / cosmetic-science journals + Cochrane,
  - restricted to RCTs / systematic reviews / meta-analyses,
  - on skincare-relevant topics (to exclude unrelated derm, e.g. skin-cancer surgery),
  - published recently, English, human studies.
Dedupes by PMID against existing study pages AND the study queue, then auto queue-adds.

Usage:
    python scripts/ingest_pubmed.py             # fetch, dedupe, auto queue-add
    python scripts/ingest_pubmed.py --dry-run   # print candidates, do not queue
"""
import argparse
import glob
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# --- The very-high-quality source filter -------------------------------------
JOURNALS = [
    "Cochrane Database Syst Rev", "J Am Acad Dermatol", "Br J Dermatol",
    "JAMA Dermatol", "J Invest Dermatol", "Dermatol Surg", "J Drugs Dermatol",
    "J Cosmet Dermatol", "J Eur Acad Dermatol Venereol", "Am J Clin Dermatol",
]
TYPES = ["Randomized Controlled Trial", "Systematic Review", "Meta-Analysis"]
# Must be about the SKIN (gates out dry-eye / obstetric / haematology Cochrane reviews
# that merely mention a topic word like "topical").
SKIN = ["skin", "cutaneous", "dermatolog*", "epidermis", "epidermal", "facial", "stratum corneum"]
# ...and about a topical-skincare topic we actually cover.
TOPICS = [
    "topical", "cosmetic", "sunscreen", "moisturizer", "moisturiser", "emollient",
    "acne", "rosacea", "melasma", "hyperpigmentation", "photoaging", "photoageing",
    "retinoid", "retinol", "tretinoin", "adapalene", "niacinamide", "azelaic acid",
    "hyaluronic acid", "ceramide", "skin barrier", "vitamin C", "salicylic acid",
    "benzoyl peroxide", "peptide", "bakuchiol", "antioxidant", "cleanser",
]
# Procedures / devices / systemics are a later, out-of-scope phase for a topical-skincare
# directory - exclude by title so laser/filler/injection trials never enter the queue.
EXCLUDE_TITLE = [
    "laser", "botulinum", "filler", "mesotherapy", "injection", "injectable",
    "shock wave", "shockwave", "phototherapy", "microneedling", "radiofrequency",
    "surgery", "surgical", "peel", "excision", "graft", "biostimulator",
    "neonat", "venepuncture", "supplementation", "dietary", "poly-l-lactic",
    "toxin", "platysma",
]
RECENT_DAYS = 1095   # ~3 years
MAX_FETCH = 120      # widened 2026-08-25: with sort=date the newest ~68 were all
                     # already ingested, so retmax=30 returned "no new" every run;
                     # a deeper window resurfaces the un-ingested tail (dedup still applies)

_PMID_RE = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)")


def build_term():
    j = " OR ".join(f'"{x}"[Journal]' for x in JOURNALS)
    t = " OR ".join(f'"{x}"[Publication Type]' for x in TYPES)
    skin = " OR ".join(f'{x}[Title/Abstract]' for x in SKIN)
    top = " OR ".join(f'"{x}"[Title/Abstract]' for x in TOPICS)
    excl = " OR ".join(f'"{x}"[Title]' for x in EXCLUDE_TITLE)
    return (f"({j}) AND ({t}) AND ({skin}) AND ({top}) "
            f"NOT ({excl}) AND "
            f'("last {RECENT_DAYS} days"[dp]) AND English[lang] AND humans[mh]')


def existing_pmids():
    """PMIDs already covered on the site (study pages) or already queued."""
    seen = set()
    for f in glob.glob(str(ROOT / "data" / "studies" / "*.md")):
        seen.update(_PMID_RE.findall(pathlib.Path(f).read_text(encoding="utf-8")))
    ql = ROOT / "data" / "queues" / "studies.yaml"
    if ql.exists():
        seen.update(_PMID_RE.findall(ql.read_text(encoding="utf-8")))
    return seen


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "skintiers-ingest/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def esearch(term, retmax):
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json",
                                "retmax": retmax, "sort": "date"})
    data = json.loads(_get(f"{EUTILS}/esearch.fcgi?{q}"))
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids):
    q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "json"})
    res = json.loads(_get(f"{EUTILS}/esummary.fcgi?{q}")).get("result", {})
    out = []
    for pid in res.get("uids", []):
        r = res[pid]
        authors = r.get("authors") or []
        first = authors[0]["name"].split()[0] if authors else ""   # last name
        out.append({"pmid": pid, "title": (r.get("title", "") or "").rstrip("."),
                    "journal": r.get("source", ""), "year": (r.get("pubdate", "") or "")[:4],
                    "first_author": first})
    return out


def candidate_name(s):
    return f"{s['first_author']} {s['year']} {s['title'][:90]} (PMID {s['pmid']})".strip()


def queue_add(name, source):
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sk"), "queue-add", name,
                    "--type", "study", "--source", source], check=False,
                   capture_output=True, text=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Auto-ingest high-quality PubMed studies into the queue.")
    ap.add_argument("--dry-run", action="store_true", help="print candidates, do not queue")
    ap.add_argument("--max", type=int, default=MAX_FETCH, help="max PubMed results to consider")
    args = ap.parse_args(argv)

    pmids = esearch(build_term(), args.max)
    have = existing_pmids()
    new = [p for p in pmids if p not in have]
    if not new:
        print(f"searched {len(pmids)}; no new high-quality studies to add.")
        return 0
    added = 0
    for s in esummary(new):
        name = candidate_name(s)
        src = f"https://pubmed.ncbi.nlm.nih.gov/{s['pmid']}/"
        print(("DRY  " if args.dry_run else "add  ") + f"[{s['journal']} {s['year']}] {name}")
        if not args.dry_run:
            queue_add(name, src)
            added += 1
    print(f"\n{len(new)} new candidate(s); {added} queued." if not args.dry_run
          else f"\n{len(new)} new candidate(s) (dry run).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
