#!/usr/bin/env python3
"""Append-only registry mapping product slug <-> compact base62 code (see routine_string).

A code is assigned to a product once and NEVER changed or reused - so routine-string URLs
stay valid forever, even after a product is unpublished. data/routine-codes.yaml holds the
map; build.py syncs it (minting codes for new products) and emits a code-keyed catalog the
browser routine builder loads.
"""
import glob
import pathlib

import yaml

from routine_string import B62

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "routine-codes.yaml"
PRODUCTS = ROOT / "data" / "products"


def to_code(n):
    """Shortest base62 rendering of an index (0->"0", 61->"z", 62->"10"). Unbounded:
    codes are comma-delimited in the URL, so they need no fixed width and the product
    space has no ceiling."""
    if n < 0:
        raise ValueError("index must be non-negative")
    if n == 0:
        return B62[0]
    s = ""
    while n > 0:
        s = B62[n % 62] + s
        n //= 62
    return s


def to_index(code):
    n = 0
    for c in code:
        n = n * 62 + B62.index(c)
    return n


def load(registry=None):
    registry = pathlib.Path(registry) if registry else REGISTRY
    if registry.exists():
        return yaml.safe_load(registry.read_text()) or {}
    return {}


def save(reg, registry=None):
    registry = pathlib.Path(registry) if registry else REGISTRY
    ordered = dict(sorted(reg.items(), key=lambda kv: to_index(kv[1])))  # stable, readable diff
    registry.write_text(yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True))


def product_slugs():
    return sorted(pathlib.Path(f).stem for f in glob.glob(str(PRODUCTS / "*.md")))


def sync(slugs=None, persist=True, registry=None):
    """Mint codes for any new slugs (append-only) and return the full slug->code map.

    registry defaults to data/routine-codes.yaml; build.py passes the active data
    dir's registry so tmp-data test builds stay isolated from the real one."""
    reg = load(registry)
    slugs = product_slugs() if slugs is None else slugs
    nxt = max((to_index(c) for c in reg.values()), default=-1) + 1
    changed = False
    for slug in sorted(slugs):               # sorted -> deterministic regardless of caller order
        if slug not in reg:
            reg[slug] = to_code(nxt)
            nxt += 1
            changed = True
    if persist and changed:
        save(reg, registry)
    return reg


if __name__ == "__main__":
    reg = sync()
    print(f"{len(reg)} products coded -> {REGISTRY.relative_to(ROOT)}")
    for slug, code in list(sorted(reg.items(), key=lambda kv: to_index(kv[1])))[:12]:
        print(f"  {code}  {slug}")
