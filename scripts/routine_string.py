#!/usr/bin/env python3
"""Compact, URL-safe grammar for describing a skincare routine (a "routine string").

    r1.a0A1f2z.p0A3k~34m

  r1          grammar version (forward-compatible; parsers reject an unknown major).
  .X...       a phase block: leading marker X = a(m) | p(m) | w(eekly), then tokens.
  token       a 2-char base62 product CODE, optionally "~N" cadence (N times/week, 1-6).
              Codes are fixed width, so tokens need no separator between them.
  default     a code with no "~N" means daily. The same code may appear in >1 phase.

Codes come from the append-only registry data/routine-codes.yaml (see product_codes.py),
so the string stays tiny and stable: an 8-product routine is ~20 chars vs ~180 with slugs.
It is meant to live in a URL *fragment* (#...): never sent to a server, no length limit,
no percent-encoding needed. This module is the spec of record; the browser builder mirrors
parse()/encode() in JS against the same vectors. base62 width 2 addresses 3,844 products;
a future v2 widens the code and this version tag keeps old links valid.

Canonical form: encode() emits phases in PHASE_ORDER and drops the default cadence, so
parse->encode is idempotent.
"""
import re

VERSION = "r1"
CODE_W = 2                                   # base62 code width (3,844 products)
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_MARK_TO_KEY = {"a": "am", "p": "pm", "w": "wk"}
_KEY_TO_MARK = {v: k for k, v in _MARK_TO_KEY.items()}
PHASE_ORDER = ("am", "pm", "wk")             # canonical ordering
_CODE_RE = re.compile(rf"^[{re.escape(B62)}]{{{CODE_W}}}$")


def parse(s):
    """Parse a routine string into {"phases": [{"key", "items": [{"code","freq"}]}]}.

    freq is an int 1-7 (7 = daily). Raises ValueError on anything malformed.
    """
    if not isinstance(s, str):
        raise ValueError("routine string must be a str")
    s = s.strip()
    parts = s.split(".")
    if not parts or parts[0] != VERSION:
        raise ValueError(f"unsupported routine-string version: {parts[0]!r}")
    phases, seen = [], set()
    for block in parts[1:]:
        if not block:
            raise ValueError("empty phase block")
        mark, body = block[0], block[1:]
        if mark not in _MARK_TO_KEY:
            raise ValueError(f"unknown phase marker: {mark!r}")
        key = _MARK_TO_KEY[mark]
        if key in seen:
            raise ValueError(f"duplicate phase: {key!r}")
        seen.add(key)
        phases.append({"key": key, "items": _parse_block(body)})
    return {"phases": phases}


def _parse_block(body):
    items, i, n = [], 0, len(body)
    while i < n:
        code = body[i:i + CODE_W]
        if not _CODE_RE.match(code):
            raise ValueError(f"invalid product code: {code!r}")
        i += CODE_W
        freq = 7
        if i < n and body[i] == "~":
            i += 1
            if i >= n or not body[i].isdigit():
                raise ValueError("cadence must be a digit 1-6")
            freq = int(body[i])
            if not (1 <= freq <= 6):
                raise ValueError(f"cadence out of range: {freq}")
            i += 1
        items.append({"code": code, "freq": freq})
    return items


def encode(routine):
    """Serialize {"phases": [...]} back to a canonical routine string."""
    by_key = {p["key"]: p["items"] for p in routine.get("phases", [])}
    segs = [VERSION]
    for key in PHASE_ORDER:
        if key not in by_key:
            continue
        block = _KEY_TO_MARK[key]
        for it in by_key[key]:
            code = it["code"]
            if not _CODE_RE.match(code):
                raise ValueError(f"invalid product code: {code!r}")
            freq = it.get("freq", 7)
            block += code if freq == 7 else f"{code}~{freq}"
        segs.append(block)
    return ".".join(segs)


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
