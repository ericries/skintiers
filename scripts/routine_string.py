#!/usr/bin/env python3
"""URL grammar for describing a skincare routine as a clean, compact PATH.

    r1/aIOU6D/p4Y~56/wM

  rW          anchor: r = routine, W = the base62 code WIDTH for THIS link (1, 2, ...).
              The width is auto-sized to the routine's largest product code and travels
              in the URL, so the link decodes forever no matter how big the catalog grows
              (a small routine stays width 1 even after the catalog passes 62 products).
              Grammar is v1; a future grammar change would use a different prefix letter.
  a.. p.. w.. one segment per phase (a=am, p=pm, w=weekly); an absent phase is absent.
  codes       fixed-width base62 product codes, concatenated with NO delimiter (the fixed
              width makes them self-delimiting - that is what removes the commas).
  ~N          optional cadence written right after a code: N times/week (1-6); omit = daily.

Everything is URL-safe unencoded, so no query string and no percent-encoding. On a static
host (GitHub Pages) these paths are served by the builder acting as 404.html, which reads
location.pathname + the code-keyed catalog build.py emits and renders client-side. This
module is the spec of record; the builder mirrors parse()/encode() in JS against the same
vectors. Codes here are CANONICAL (unpadded, as in the catalog); encode() left-pads them
to the link's width and parse() strips the padding back off.
"""
import re
from urllib.parse import urlsplit

GRAMMAR = 1                                   # grammar version (for the catalog); anchor is "r"+width
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_MARK_TO_KEY = {"a": "am", "p": "pm", "w": "wk"}
_KEY_TO_MARK = {v: k for k, v in _MARK_TO_KEY.items()}
PHASE_ORDER = ("am", "pm", "wk")
_CODE_RE = re.compile(rf"^[{re.escape(B62)}]+$")
_ANCHOR_RE = re.compile(r"^r(\d+)$")


def _segments(s):
    """Path segments of a full URL, absolute path, or bare 'r1/...' string, sliced from
    the anchor (r<width>) onward so any site prefix is ignored."""
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

    Codes are returned canonical (unpadded). freq is 1-7 (7 = daily). Raises ValueError
    on anything malformed."""
    parts = _segments(s)
    m = _ANCHOR_RE.match(parts[0]) if parts else None
    if not m:
        raise ValueError("missing anchor segment (expected rW/...)")
    width = int(m.group(1))
    if width < 1:
        raise ValueError("code width must be >= 1")
    phases, seen = [], set()
    for seg in parts[1:]:
        if not seg:
            raise ValueError("empty phase segment")
        mark, body = seg[0], seg[1:]
        if mark not in _MARK_TO_KEY:
            raise ValueError(f"unknown phase marker: {mark!r}")
        key = _MARK_TO_KEY[mark]
        if key in seen:
            raise ValueError(f"duplicate phase: {key!r}")
        seen.add(key)
        phases.append({"key": key, "items": _parse_block(body, width)})
    return {"phases": phases}


def _parse_block(body, width):
    items, i, n = [], 0, len(body)
    while i < n:
        chunk = body[i:i + width]
        if len(chunk) != width or not _CODE_RE.match(chunk):
            raise ValueError(f"code chunk is not width {width}: {chunk!r}")
        i += width
        code = chunk.lstrip("0") or "0"       # strip the left-pad back to canonical
        freq = 7
        if i < n and body[i] == "~":
            i += 1
            if i >= n or not body[i].isdigit() or not (1 <= int(body[i]) <= 6):
                raise ValueError("cadence must be a digit 1-6")
            freq = int(body[i])
            i += 1
        items.append({"code": code, "freq": freq})
    return items


def encode(routine):
    """Serialize {"phases": [...]} to a canonical 'rW/...' path (no leading slash). The
    width is the length of the longest code used, so small routines stay narrow."""
    by_key = {p["key"]: p["items"] for p in routine.get("phases", [])}
    all_codes = [it["code"] for k in by_key for it in by_key[k]]
    for c in all_codes:
        if not _CODE_RE.match(c):
            raise ValueError(f"invalid product code: {c!r}")
    width = max((len(c) for c in all_codes), default=1)
    segs = [f"r{width}"]
    for key in PHASE_ORDER:
        if key not in by_key:
            continue
        block = _KEY_TO_MARK[key]
        for it in by_key[key]:
            freq = it.get("freq", 7)
            block += it["code"].rjust(width, "0") + ("" if freq == 7 else f"~{freq}")
        segs.append(block)
    return "/".join(segs)


def to_url(routine, base=""):
    """Full URL/path for a routine. base may be '', '/', or a site root ending in '/'."""
    return base + encode(routine)


def codes(routine):
    """Every distinct product code referenced, in first-seen order (canonical)."""
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
