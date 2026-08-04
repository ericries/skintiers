#!/usr/bin/env python3
"""URL grammar for describing a skincare routine as a clean, versioned PATH.

    r1/aI,O,U,6,D/p4,Y~5,6/wM

  r1          anchor + grammar version fused into one short segment (r = routine, 1 = v1).
              A future breaking change is r2/... and the r1 parser keeps working.
  a.. p.. w.. one segment per phase: a leading marker (a=am, p=pm, w=weekly) then the
              phase's product CODES. An absent phase is simply an absent segment.
  code        a product's base62 code (variable length: 0..z, 10, ...), comma-separated
              within the segment, so no fixed width -> the product space is unbounded and
              the first 62 products are single characters (the compact floor).
  ~N          optional cadence on a code: applied N times/week (1-6); omitted = daily.

Path segments, marker letters, commas and ~ are all URL-safe unencoded, so the link
stays clean with no query string. On a static host (GitHub Pages) these paths are served
by the builder acting as 404.html, which reads location.pathname and renders client-side
from the code-keyed catalog build.py emits. This module is the spec of record; the
builder mirrors parse()/encode() in JS against the same vectors.
"""
import re
from urllib.parse import urlsplit

VERSION = "1"                                 # grammar version; URL anchor is "r" + VERSION
ANCHOR = "r" + VERSION                        # e.g. "r1"
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_MARK_TO_KEY = {"a": "am", "p": "pm", "w": "wk"}
_KEY_TO_MARK = {v: k for k, v in _MARK_TO_KEY.items()}
PHASE_ORDER = ("am", "pm", "wk")
_CODE_RE = re.compile(rf"^[{re.escape(B62)}]+$")
_ANCHOR_RE = re.compile(r"^r\d+$")


def _segments(s):
    """Path segments of a full URL, absolute path, or bare 'r1/...' string, sliced from
    the grammar anchor (r<version>) onward so any site prefix is ignored."""
    if not isinstance(s, str):
        raise ValueError("routine URL/path must be a str")
    path = urlsplit(s.strip()).path if ("://" in s or s.startswith("/")) else s.strip()
    parts = [seg for seg in path.split("/") if seg]
    for i, seg in enumerate(parts):
        if _ANCHOR_RE.match(seg):
            return parts[i:]
    return parts


def parse(s):
    """Parse a routine URL/path into {"phases": [{"key", "items": [{"code","freq"}]}]}.

    freq is an int 1-7 (7 = daily). Raises ValueError on anything malformed."""
    parts = _segments(s)
    if not parts or not _ANCHOR_RE.match(parts[0]):
        raise ValueError(f"missing anchor segment (expected {ANCHOR}/...)")
    if parts[0] != ANCHOR:
        raise ValueError(f"unsupported routine version: {parts[0]!r}")
    phases, seen = [], set()
    for seg in parts[1:]:
        mark, body = seg[0], seg[1:]
        if mark not in _MARK_TO_KEY:
            raise ValueError(f"unknown phase marker: {mark!r}")
        key = _MARK_TO_KEY[mark]
        if key in seen:
            raise ValueError(f"duplicate phase: {key!r}")
        seen.add(key)
        items = [_parse_item(t) for t in body.split(",")] if body else []
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
    """Serialize {"phases": [...]} to a canonical 'r1/...' path (no leading slash)."""
    by_key = {p["key"]: p["items"] for p in routine.get("phases", [])}
    segs = [ANCHOR]
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
        segs.append(_KEY_TO_MARK[key] + ",".join(toks))
    return "/".join(segs)


def to_url(routine, base=""):
    """Full URL/path for a routine. base may be '' , '/', or a site root ending in '/'."""
    return base + encode(routine)


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
