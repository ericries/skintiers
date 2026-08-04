#!/usr/bin/env python3
"""Compact, URL-safe grammar for describing a skincare routine (a "routine string").

    r1.am:slugA,slugB@3.pm:slugC,slugA

  r1        grammar version (forward-compatible; parsers reject an unknown major).
  .KEY:     a phase - KEY is am|pm (wk reserved). Listing order = application order.
  slug      a product page slug, charset [a-z0-9-]. Same slug may repeat across phases.
  @N        optional cadence: applied N times/week (1-7); omitted means daily.

The string is meant to live in a URL *fragment* (#...), so it is never sent to a
server, has no practical length limit, and needs no percent-encoding. This module is
the spec of record; the browser builder mirrors parse()/encode() in JS and is checked
against the same vectors in tests.

Canonical form: encode() emits phases in PHASE_ORDER and drops the default (daily)
cadence, so parse->encode is idempotent.
"""
import re

VERSION = "r1"
PHASE_ORDER = ("am", "pm", "wk")   # canonical ordering; "wk" reserved for later use
_SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def parse(s):
    """Parse a routine string into {"phases": [{"key", "items": [{"slug","freq"}]}]}.

    freq is an int 1-7 (7 = daily). Raises ValueError on anything malformed.
    """
    if not isinstance(s, str):
        raise ValueError("routine string must be a str")
    s = s.strip()
    parts = s.split(".")
    if not parts or parts[0] != VERSION:
        raise ValueError(f"unsupported routine-string version: {parts[0]!r}")
    phases = []
    seen_keys = set()
    for seg in parts[1:]:
        if ":" not in seg:
            raise ValueError(f"phase missing ':' -> {seg!r}")
        key, _, body = seg.partition(":")
        if key not in PHASE_ORDER:
            raise ValueError(f"unknown phase key: {key!r}")
        if key in seen_keys:
            raise ValueError(f"duplicate phase: {key!r}")
        seen_keys.add(key)
        items = []
        if body:
            for tok in body.split(","):
                items.append(_parse_item(tok))
        phases.append({"key": key, "items": items})
    return {"phases": phases}


def _parse_item(tok):
    slug, sep, freq = tok.partition("@")
    if not _SLUG_RE.match(slug):
        raise ValueError(f"invalid slug: {slug!r}")
    f = 7
    if sep:
        if not freq.isdigit() or not (1 <= int(freq) <= 7):
            raise ValueError(f"cadence must be 1-7, got {freq!r}")
        f = int(freq)
    return {"slug": slug, "freq": f}


def encode(routine):
    """Serialize {"phases": [...]} back to a canonical routine string."""
    by_key = {p["key"]: p["items"] for p in routine.get("phases", [])}
    segs = [VERSION]
    for key in PHASE_ORDER:
        if key not in by_key:
            continue
        toks = []
        for it in by_key[key]:
            slug = it["slug"]
            if not _SLUG_RE.match(slug):
                raise ValueError(f"invalid slug: {slug!r}")
            freq = it.get("freq", 7)
            toks.append(slug if freq == 7 else f"{slug}@{freq}")
        segs.append(f"{key}:" + ",".join(toks))
    return ".".join(segs)


def slugs(routine):
    """Every distinct product slug referenced, in first-seen order (for catalog lookup)."""
    out, seen = [], set()
    for p in routine.get("phases", []):
        for it in p["items"]:
            if it["slug"] not in seen:
                seen.add(it["slug"])
                out.append(it["slug"])
    return out


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        print(json.dumps(parse(sys.argv[1]), indent=2))
