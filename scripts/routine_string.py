#!/usr/bin/env python3
"""URL grammar for describing a skincare routine as an ordinary HTTP query string.

    routine.html?am=4,o,u,6,d&pm=4,Y~5,6&wk=M

  am= / pm= / wk=   one param per phase; an absent phase is simply an absent param.
                    Listing order within a value = application order.
  code              a product's base62 code (variable length: 0..z, 10, 11, ...),
                    comma-separated, so no fixed width -> the product space is unbounded.
  ~N                optional cadence: applied N times/week (1-6); omitted means daily.
  v (optional)      grammar version. Absent = v1 (this scheme). A future breaking change
                    adds ?v=2 and every v1 link still parses. Additive params (a title t=,
                    etc.) never break old links - unknown params are ignored by convention.

Everything is standard query syntax: it looks like a normal URL, is bookmarkable and
cacheable, and needs no percent-encoding (comma and ~ are URL-safe in a query). Codes
come from the append-only registry (product_codes.py); build.py emits a code-keyed
catalog the browser builder loads to resolve a URL entirely client-side. This module is
the spec of record; the builder mirrors parse()/encode() in JS against the same vectors.
"""
import re
from urllib.parse import parse_qsl, urlsplit

VERSION = "1"
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
PHASE_ORDER = ("am", "pm", "wk")             # canonical ordering; extensible
_CODE_RE = re.compile(rf"^[{re.escape(B62)}]+$")


def _query_of(s):
    """Accept a full URL, a '?...' search string, or a bare 'am=..&pm=..' query."""
    if not isinstance(s, str):
        raise ValueError("routine URL/query must be a str")
    s = s.strip()
    if "?" in s:
        return urlsplit(s).query
    return s.lstrip("?")


def parse(s):
    """Parse a routine URL/query into {"phases": [{"key", "items": [{"code","freq"}]}]}.

    freq is an int 1-7 (7 = daily). Raises ValueError on anything malformed."""
    pairs = parse_qsl(_query_of(s), keep_blank_values=True)
    params, seen = {}, set()
    for k, v in pairs:
        if k in PHASE_ORDER and k in seen:
            raise ValueError(f"duplicate phase param: {k!r}")
        seen.add(k)
        params[k] = v
    version = params.get("v", VERSION)
    if version != VERSION:
        raise ValueError(f"unsupported routine version: {version!r}")
    phases = []
    for key in PHASE_ORDER:
        if key not in params:
            continue
        items = [_parse_item(tok) for tok in params[key].split(",")] if params[key] else []
        phases.append({"key": key, "items": items})
    return {"phases": phases}


def _parse_item(tok):
    code, sep, freq = tok.partition("~")
    if not _CODE_RE.match(code):
        raise ValueError(f"invalid product code: {code!r}")
    f = 7
    if sep:
        if not freq.isdigit() or not (1 <= int(freq) <= 6):
            raise ValueError(f"cadence must be 1-6, got {freq!r}")
        f = int(freq)
    return {"code": code, "freq": f}


def encode(routine):
    """Serialize {"phases": [...]} to a canonical query string (no leading '?')."""
    by_key = {p["key"]: p["items"] for p in routine.get("phases", [])}
    parts = []
    for key in PHASE_ORDER:
        if key not in by_key:
            continue
        toks = []
        for it in by_key[key]:
            code = it["code"]
            if not _CODE_RE.match(code):
                raise ValueError(f"invalid product code: {code!r}")
            freq = it.get("freq", 7)
            toks.append(code if freq == 7 else f"{code}~{freq}")
        parts.append(f"{key}=" + ",".join(toks))
    return "&".join(parts)


def to_url(routine, page="routine.html"):
    q = encode(routine)
    return f"{page}?{q}" if q else page


def codes(routine):
    """Every distinct product code referenced, in first-seen order."""
    out, seen = [], set()
    for p in routine.get("phases", []):
        for it in p["items"]:
            if it["code"] not in seen:
                seen.add(it["code"])
                out.append(it["code"])
    return out


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        print(json.dumps(parse(sys.argv[1]), indent=2))
