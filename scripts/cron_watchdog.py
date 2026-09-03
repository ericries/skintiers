#!/usr/bin/env python3
"""Expand data/cron-roster.yaml into one prompt file per intended cron and print a
manifest the watchdog cron (and the main session) use to restore any missing job.

Output per intended cron:
  - research-cache/cron-prompts/<name>.txt  (the exact prompt to pass to CronCreate)
  - a manifest line on stdout:  NAME<TAB>CRON<TAB>HEADER<TAB>FILE
    HEADER = the text inside the leading [SkinTiers ...] bracket of the prompt; this is
    what appears (untruncated) at the start of every job and is the stable match key
    against CronList.

This script does NOT call CronList/CronCreate (those are Claude tools, not CLI). It
only produces the intended set + prompt files; the watchdog Claude session diffs the
manifest against CronList and CronCreates whatever is missing.
"""
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROSTER = os.path.join(ROOT, "data", "cron-roster.yaml")
OUTDIR = os.path.join(ROOT, "research-cache", "cron-prompts")


def header_of(prompt):
    """The text inside the first [ ... ] bracket, e.g. 'SkinTiers daily fill: PRODUCT'."""
    m = re.search(r"\[([^\]]+)\]", prompt)
    return m.group(1).strip() if m else prompt.strip().splitlines()[0][:50]


def expand():
    doc = yaml.safe_load(open(ROSTER))
    template = doc["_fill_template"]
    intended = []  # (name, cron, prompt)
    for e in doc["crons"]:
        cron = e["cron"]
        if e.get("type"):
            t = e["type"]
            prompt = (
                template.replace("{TYPE}", t.upper())
                .replace("{type}", t)
                .replace("{CRITIC}", e.get("critic", ""))
                .replace("{PUBLISH}", e.get("publish", ""))
            )
            name = f"fill-{t}"
        else:
            prompt = e["prompt"]
            name = e.get("label") or header_of(prompt).lower().replace(" ", "-")
        intended.append((name, cron, prompt))
    return intended


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    intended = expand()
    # sanity: no leftover unexpanded template tokens in any fill prompt
    for name, cron, prompt in intended:
        for tok in ("{TYPE}", "{type}", "{CRITIC}", "{PUBLISH}"):
            if tok in prompt:
                sys.exit(f"ERROR: unexpanded {tok} in {name}")
    for name, cron, prompt in intended:
        path = os.path.join(OUTDIR, f"{name}.txt")
        with open(path, "w") as fh:
            fh.write(prompt if prompt.endswith("\n") else prompt + "\n")
        rel = os.path.relpath(path, ROOT)
        print(f"{name}\t{cron}\t{header_of(prompt)}\t{rel}")
    print(f"# {len(intended)} intended crons -> {os.path.relpath(OUTDIR, ROOT)}/", file=sys.stderr)


if __name__ == "__main__":
    main()
