"""Every `images:` entry must be a mapping carrying a real `file:`.

Found 2026-11-09 by the product-images cron: 7 of 389 illustrated products stored
their photo as a bare filename string instead of the {file, source, source_url}
mapping the convention uses (see data/products/cosrx-the-retinol-0-1-cream.md).
Both shapes happen to render the same `<img>`, so the drift was invisible on the
site - but it crashes any consumer that reads the field as a mapping, which is how
it surfaced (AttributeError: 'str' object has no attribute 'get' while auditing
image coverage). A bare string also has nowhere to put `source`/`source_url`, so
those photos carry no provenance at all once attribution is rendered.

Normalising the 7 to mapping form is lossless. Their missing attribution is NOT
invented here: where the photo came from cannot be recovered from a file on disk,
and guessing a source would be a fabricated citation.
"""
import glob
import os
import re

import yaml


def _entries():
    for path in sorted(glob.glob("data/**/*.md", recursive=True)):
        text = open(path, encoding="utf-8", errors="replace").read()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        for entry in (fm.get("images") or []):
            yield os.path.basename(path)[:-3], entry


def test_every_image_entry_is_a_mapping():
    bad = [(s, e) for s, e in _entries() if not isinstance(e, dict)]
    assert not bad, (
        "images: entries must be mappings, not bare strings (a string has nowhere "
        "to record source/source_url, and breaks consumers reading .get):\n"
        + "\n".join(f"  [{s}] {e!r}" for s, e in bad))


def test_every_image_entry_names_a_file_that_exists():
    missing = []
    for slug, entry in _entries():
        if not isinstance(entry, dict):
            continue
        name = entry.get("file")
        if not name:
            missing.append((slug, "no file: key"))
        elif not os.path.exists(os.path.join("static/images", os.path.basename(name))):
            missing.append((slug, f"{name} absent from static/images"))
    assert not missing, "images: entries pointing at no self-hosted file:\n" + \
        "\n".join(f"  [{s}] {w}" for s, w in missing)
