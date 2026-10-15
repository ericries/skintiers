#!/usr/bin/env python
"""Spend gate + ledger for Apify calls.

Apify is the only paid external service this project uses, and in 2026-10 the
account hit 50% of its monthly limit mid-cycle with no record of what the money
bought. There is no APIFY_TOKEN in this environment, so Apify is reachable only
through the MCP tool, which a script cannot call. This module therefore does the
two things a script CAN do: refuse calls that are predictably worthless, and
keep a ledger so the spend is attributable next cycle.

Usage:
    apify_gate.py check "<url-or-query>" [--essential]
        exit 0 + "ALLOW" -> make the call
        exit 1 + "DENY: <reason>" -> do NOT call Apify; ship without the field

    apify_gate.py log "<url-or-query>" --cu 0.0233 --used no [--actor rag-web-browser]
        record the outcome; run this after EVERY call, hit or miss

    apify_gate.py report [--all]
        what this cycle cost and what it bought

Three rules, in order of precedence:
  1. BLOCKED DOMAIN  - absolute, no override. These bot-block reliably; a call
     is guaranteed to buy a CAPTCHA page.
  2. ALREADY TRIED   - absolute, no override. One attempt per target, ever. If
     the first call missed, the answer is "unresolvable", not "try again".
  3. BUDGET CAP      - overridable with --essential for a page that genuinely
     cannot ship without the data.

Plus one query-quality rule: a non-URL query must carry a quoted phrase or a
site: operator. An unquoted keyword query for a brand whose name is a common
English word returns the wrong entity (observed: "reVive Light Therapy ..."
returned an ERP vendor and the Wikipedia article on light).
"""
import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "data" / "apify-ledger.jsonl"

# Hosts that reliably bot-block a headless browser. A call here buys a block
# page at full price. amazon is documented in the cron prompts themselves and
# was still called against in 2026-10; hence the mechanical check.
BLOCKED_HOSTS = (
    "amazon.", "walmart.com", "instagram.com", "facebook.com",
    "linkedin.com", "pinterest.", "tiktok.com", "x.com", "twitter.com",
)

# Soft cap on calls per calendar month. Calendar month approximates the billing
# cycle; override with APIFY_MAX_CALLS when the real cycle date is known.
MAX_CALLS_PER_MONTH = int(os.environ.get("APIFY_MAX_CALLS", "40"))


def normalize(target: str) -> str:
    """Collapse a URL or query to a dedup key."""
    t = " ".join(target.strip().lower().split())
    if t.startswith(("http://", "https://")):
        p = urlparse(t)
        return f"{p.netloc}{p.path}".rstrip("/")
    return t


def is_url(target: str) -> bool:
    return target.strip().lower().startswith(("http://", "https://"))


def blocked_host(target: str):
    """Return the offending host fragment, or None."""
    hay = urlparse(target).netloc.lower() if is_url(target) else target.lower()
    for host in BLOCKED_HOSTS:
        # match a site: operator in a query too, e.g. site:amazon.com
        if host in hay:
            return host
    return None


def read_ledger():
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def this_cycle(rows, today=None):
    today = today or date.today()
    prefix = today.strftime("%Y-%m")
    return [r for r in rows if str(r.get("date", "")).startswith(prefix)]


def check(target: str, essential: bool = False) -> tuple:
    """Return (allowed: bool, message: str)."""
    host = blocked_host(target)
    if host:
        return False, (
            f"DENY: '{host}' bot-blocks headless browsers. The call would buy a "
            f"block page at full price. Use the brand's own site, a primary "
            f"regulatory source, or ship the page without this field."
        )

    if not is_url(target):
        has_quote = '"' in target
        has_site = "site:" in target.lower()
        if not (has_quote or has_site):
            return False, (
                "DENY: bare keyword query. A non-URL query must carry a quoted "
                'phrase (e.g. "Exact Brand Name") or a site: operator, or Google '
                "returns the wrong entity. Re-run check with a disambiguated query."
            )

    key = normalize(target)
    prior = [r for r in read_ledger() if r.get("key") == key]
    if prior:
        p = prior[0]
        return False, (
            f"DENY: already attempted {p.get('date')} (used={p.get('used')}). "
            f"One attempt per target, ever. Mark the field unresolvable and ship."
        )

    cycle = this_cycle(read_ledger())
    if len(cycle) >= MAX_CALLS_PER_MONTH and not essential:
        return False, (
            f"DENY: {len(cycle)} calls already this cycle (cap {MAX_CALLS_PER_MONTH}). "
            f"Pass --essential only if the page genuinely cannot ship without it."
        )

    note = ""
    if is_url(target):
        note = " Known URL: prefer apify--web-fetch over rag-web-browser."
    return True, f"ALLOW (call {len(cycle) + 1}/{MAX_CALLS_PER_MONTH} this cycle).{note}"


def log(target: str, cu: float, used: bool, actor: str, note: str = "") -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "date": date.today().isoformat(),
        "key": normalize(target),
        "target": target,
        "actor": actor,
        "cu": cu,
        "used": bool(used),
        "note": note,
    }
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def report(show_all: bool = False) -> str:
    rows = read_ledger()
    scope = rows if show_all else this_cycle(rows)
    if not scope:
        return "no Apify calls recorded" + ("" if show_all else " this cycle")
    cu = sum(float(r.get("cu") or 0) for r in scope)
    hits = [r for r in scope if r.get("used")]
    lines = [
        f"calls: {len(scope)} (cap {MAX_CALLS_PER_MONTH})",
        f"compute units: {cu:.4f}",
        f"data actually used: {len(hits)}/{len(scope)}"
        f" ({100 * len(hits) // max(1, len(scope))}%)",
    ]
    wasted = [r for r in scope if not r.get("used")]
    if wasted:
        lines.append("wasted calls:")
        for r in wasted[-10:]:
            lines.append(f"  {r.get('date')}  {str(r.get('target'))[:70]}")
    return "\n".join(lines)


def _selftest() -> int:
    """Exercise the three rules without touching the real ledger."""
    global LEDGER
    import tempfile
    failures = []

    def expect(cond, label):
        if not cond:
            failures.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        LEDGER = Path(tmp) / "ledger.jsonl"

        ok, msg = check("https://www.amazon.com/dp/B0C7JT5W2P")
        expect(not ok and "bot-block" in msg, "amazon URL should be denied")

        ok, msg = check('site:amazon.com "reVive Light Therapy"')
        expect(not ok, "site:amazon query should be denied")

        ok, _ = check("reVive Light Therapy Essentials buy price")
        expect(not ok, "bare keyword query should be denied")

        ok, _ = check('"reVive Light Therapy Essentials" price')
        expect(ok, "quoted query should be allowed")

        ok, msg = check("https://revivelighttherapy.com/products/essentials")
        expect(ok and "web-fetch" in msg, "known URL should allow and suggest web-fetch")

        log("https://revivelighttherapy.com/products/essentials", 0.01, False, "rag-web-browser")
        ok, msg = check("https://revivelighttherapy.com/products/essentials/")
        expect(not ok and "already attempted" in msg, "repeat target should be denied")

        for i in range(MAX_CALLS_PER_MONTH):
            log(f"https://example{i}.com/p", 0.01, False, "web-fetch")
        ok, _ = check('"brand new thing" price')
        expect(not ok, "over-cap should be denied")
        ok, _ = check('"brand new thing" price', essential=True)
        expect(ok, "--essential should override the cap")

        rep = report()
        expect("data actually used: 0/" in rep, "report should show a 0% hit rate")

    if failures:
        print("SELFTEST FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("selftest: all checks passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="may I call Apify for this target?")
    c.add_argument("target")
    c.add_argument("--essential", action="store_true",
                   help="override the budget cap (never the blocklist or dedup)")

    g = sub.add_parser("log", help="record the outcome of a call")
    g.add_argument("target")
    g.add_argument("--cu", type=float, required=True, help="computeUnits from the run result")
    g.add_argument("--used", choices=["yes", "no"], required=True,
                   help="did the returned data actually ship on a page?")
    g.add_argument("--actor", default="rag-web-browser")
    g.add_argument("--note", default="")

    r = sub.add_parser("report", help="what this cycle cost and bought")
    r.add_argument("--all", action="store_true")

    sub.add_parser("selftest", help="run built-in checks")

    a = ap.parse_args()

    if a.cmd == "selftest":
        return _selftest()
    if a.cmd == "check":
        ok, msg = check(a.target, a.essential)
        print(msg)
        return 0 if ok else 1
    if a.cmd == "log":
        log(a.target, a.cu, a.used == "yes", a.actor, a.note)
        print(f"logged: {normalize(a.target)[:70]} cu={a.cu} used={a.used}")
        return 0
    if a.cmd == "report":
        print(report(a.all))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
