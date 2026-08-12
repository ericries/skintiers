#!/usr/bin/env python3
"""Backfill a `posted:` date (the video's ORIGINAL upload date) onto every video
card in data/*/*.md, so the Feed page can order cards by when the video was posted.

Why line-based editing instead of frontmatter round-trip: dumping the whole
frontmatter back through yaml would reflow every multi-line `thesis:`/`note:`
string and produce enormous, unreviewable diffs. Instead we locate each video
entry's `url:` line inside the `videos:` block and insert a `posted:` sibling key
right after it, touching nothing else. Idempotent: entries that already have a
`posted:` key are skipped, so re-running only fills the gaps (e.g. after a harvest
that could not reach yt-dlp).

Usage:
  python scripts/backfill_video_dates.py            # backfill all data files
  python scripts/backfill_video_dates.py --dry-run  # report what it would do
  python scripts/backfill_video_dates.py FILE...     # only these files
"""
import re
import subprocess
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def fetch_upload_date(url):
    """Return the video's upload date as 'YYYY-MM-DD' via yt-dlp, or None on failure."""
    try:
        r = subprocess.run(
            ["yt-dlp", "--skip-download", "--no-warnings", "--print",
             "%(upload_date)s", url],
            capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = (r.stdout or "").strip().splitlines()
    if not out:
        return None
    raw = out[0].strip()
    if not re.fullmatch(r"\d{8}", raw):        # "NA" or empty -> unknown
        return None
    return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"


def videos_block_span(lines):
    """Return (start, end) line indices of the `videos:` block inside frontmatter,
    or None. `end` is exclusive. The block runs from the `videos:` line to the next
    top-level (column-0) key or the closing `---`."""
    if not lines or lines[0].rstrip() != "---":
        return None
    # find closing frontmatter fence
    fm_end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            fm_end = i
            break
    if fm_end is None:
        return None
    start = None
    for i in range(1, fm_end):
        if lines[i].rstrip() == "videos:":
            start = i
            break
    if start is None:
        return None
    end = fm_end
    for i in range(start + 1, fm_end):
        # a new top-level key (no leading space, not a list item) closes the block
        if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-"):
            end = i
            break
    return start, end


def entry_spans(lines, start, end):
    """Yield (entry_start, entry_end) for each `- ...` list item in [start+1, end)."""
    idxs = [i for i in range(start + 1, end) if lines[i].startswith("- ")]
    for n, s in enumerate(idxs):
        e = idxs[n + 1] if n + 1 < len(idxs) else end
        yield s, e


def process_file(path, cache, dry_run=False):
    """Insert `posted:` into every dateless video entry in `path`. Returns
    (n_filled, n_unresolved)."""
    text = path.read_text()
    lines = text.split("\n")
    span = videos_block_span(lines)
    if not span:
        return 0, 0
    start, end = span
    # Work back-to-front so earlier insertions don't shift later indices.
    inserts = []          # (insert_at_index, new_line)
    filled = unresolved = 0
    for es, ee in list(entry_spans(lines, start, end)):
        entry = lines[es:ee]
        if any(re.match(r"\s+posted:", ln) for ln in entry):
            continue      # already dated
        url = None
        url_line_off = None
        for off, ln in enumerate(entry):
            m = re.match(r"\s+url:\s*(\S+)", ln)
            if m:
                url = m.group(1).strip()
                url_line_off = off
                break
        if not url:
            continue
        if url not in cache:
            cache[url] = fetch_upload_date(url)
        posted = cache[url]
        if not posted:
            unresolved += 1
            print(f"  UNRESOLVED {path.name}: {url}")
            continue
        indent = re.match(r"(\s+)", entry[url_line_off]).group(1)
        inserts.append((es + url_line_off + 1, f"{indent}posted: '{posted}'"))
        filled += 1
    if inserts and not dry_run:
        for at, new_line in sorted(inserts, reverse=True):
            lines.insert(at, new_line)
        path.write_text("\n".join(lines))
    return filled, unresolved


def main(argv):
    dry = "--dry-run" in argv
    files = [Path(a).resolve() for a in argv if not a.startswith("--")]
    if not files:
        files = sorted(DATA.glob("*/*.md"))
    cache = {}
    total_filled = total_unresolved = touched = 0
    for f in files:
        filled, unresolved = process_file(f, cache, dry_run=dry)
        if filled or unresolved:
            try:
                shown = f.relative_to(DATA.parent)
            except ValueError:
                shown = f.name
            print(f"{shown}: +{filled} dated, {unresolved} unresolved")
            touched += 1
        total_filled += filled
        total_unresolved += unresolved
    print(f"\n{'DRY RUN: ' if dry else ''}filled {total_filled} cards across {touched} files"
          f"; {total_unresolved} unresolved (left dateless).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
