#!/usr/bin/env python3
"""Keep the condition / goal / list queues filled by mining the video archive.

The discovery hubs (conditions, goals, best-of lists) had no producer, so they
drained and stalled. This mines the titles of every video we have fetched a
transcript for (research-cache/transcripts/*.txt) plus every carded video title,
counts how often the archive talks about each candidate hub concept, and queues
the ones that (a) clear a frequency floor, (b) have no page yet, and (c) are not
already queued. The candidate map below IS the brainstorm, encoded as data so it
stays reusable: extend it and re-run as the archive grows.

Nothing is auto-created; it only appends to the type queues, which the daily
condition/goal/list crons then build (and the CURATE-DON'T-SKIP + cross-feed
behaviour keeps flowing).

Usage:
  python scripts/discover_hubs.py            # queue new hubs above the floor
  python scripts/discover_hubs.py --dry-run  # just report, queue nothing
  python scripts/discover_hubs.py --min 2    # change the frequency floor
"""
import argparse
import glob
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Each candidate hub: type, slug, human name, and the regexes whose hits in the
# archive signal demand. Only concepts NOT already covered as pages are queued.
CANDIDATES = [
    # --- conditions ---
    ("condition", "hormonal-acne", "Hormonal acne", [r"hormonal acne"]),
    ("condition", "body-acne", "Body acne (back & chest)", [r"body acne", r"back acne", r"bacne", r"chest acne"]),
    ("condition", "blackheads", "Blackheads & sebaceous filaments", [r"blackhead", r"sebaceous filament"]),
    ("condition", "acne-scars", "Acne scars (atrophic & PIE)", [r"acne scar", r"\bscars\b", r"scarring", r"pitted"]),
    ("condition", "hidradenitis-suppurativa", "Hidradenitis suppurativa", [r"hidradenitis", r"\bhs\b"]),
    ("condition", "milia", "Milia", [r"milia"]),
    ("condition", "large-pores", "Enlarged pores", [r"large pore", r"enlarged pore", r"shrink.{0,10}pore", r"minimi.{0,6}pore"]),
    ("condition", "sun-damage-photoaging", "Sun damage & photoaging", [r"sun damage", r"photoaging", r"photo-?aging", r"sun spot"]),
    ("condition", "hyperhidrosis", "Hyperhidrosis (excessive sweating)", [r"hyperhidrosis", r"excessive sweat", r"sweaty"]),
    ("condition", "hair-loss", "Hair loss & thinning", [r"hair loss", r"thinning hair", r"hair thinning", r"alopecia"]),
    ("condition", "keloids-hypertrophic-scars", "Keloids & hypertrophic scars", [r"keloid", r"hypertrophic scar"]),
    ("condition", "strawberry-legs", "Strawberry legs", [r"strawberry legs"]),
    ("condition", "dandruff", "Dandruff", [r"dandruff", r"flaky scalp", r"itchy scalp"]),
    # --- goals ---
    ("goal", "mens-skincare", "Men's skincare routine", [r"\bmen'?s?\b.{0,20}skin", r"skincare for men", r"men'?s? (routine|skincare|grooming)"]),
    ("goal", "fade-dark-spots", "Fading dark spots & even tone", [r"dark spot", r"even.{0,6}tone", r"even skin"]),
    ("goal", "pore-minimizing", "Pore minimizing & oil control", [r"minimi.{0,6}pore", r"oil control", r"shrink.{0,10}pore", r"reduce.{0,10}pore"]),
    ("goal", "reduce-redness", "Reducing facial redness", [r"reduce.{0,10}redness", r"calm.{0,10}redness", r"facial redness", r"flushing"]),
    ("goal", "firming-skin-tightening", "Firming & skin tightening", [r"firm(ing|er)?\b", r"skin tightening", r"sagging", r"laxity"]),
    ("goal", "glowing-skin", "Glowing / radiant skin", [r"glow(ing)?\b", r"radian", r"\bdull(ness)?\b"]),
    ("goal", "smooth-texture", "Smoothing skin texture", [r"skin texture", r"rough (skin|texture)", r"bumpy skin", r"smooth.{0,10}skin"]),
    ("goal", "pregnancy-safe-skincare", "Pregnancy-safe skincare", [r"pregnan", r"breastfeed", r"nursing"]),
    ("goal", "sensitive-skin-routine", "Sensitive skin routine", [r"sensitive skin"]),
    ("goal", "neck-chest-care", "Neck & chest (décolletage) care", [r"\bneck\b", r"d[eé]colletage", r"crepey"]),
    ("goal", "eye-area-care", "Under-eye & eye-area care", [r"under.?eye", r"eye cream", r"puffiness", r"eye area"]),
    ("goal", "beginner-minimalist-routine", "Beginner / minimalist routine", [r"beginner", r"minimalist", r"simple routine", r"starter routine"]),
    # --- lists ---
    ("list", "best-retinol-products", "Best retinol & retinoid products", [r"best retino", r"retinol product", r"top retino"]),
    ("list", "best-dark-spot-products", "Best products for dark spots / hyperpigmentation", [r"dark spot", r"hyperpigmentation product", r"fade.{0,10}spot"]),
    ("list", "best-tinted-sunscreens", "Best tinted sunscreens", [r"tinted sunscreen", r"tinted spf"]),
    ("list", "best-mineral-sunscreens", "Best mineral (zinc) sunscreens", [r"mineral sunscreen", r"zinc sunscreen", r"physical sunscreen"]),
    ("list", "best-acne-products-by-evidence", "Best acne products by evidence", [r"best acne", r"acne products", r"clear (acne|skin)"]),
    ("list", "best-body-acne-treatments", "Best body-acne treatments", [r"body acne", r"back acne", r"bacne"]),
    ("list", "best-eye-creams", "Best eye creams", [r"eye cream", r"best under.?eye"]),
    ("list", "best-hydrating-serums", "Best hydrating / hyaluronic serums", [r"hydrating serum", r"hyaluronic", r"hydration"]),
    ("list", "best-affordable-drugstore-dupes", "Best affordable drugstore dupes", [r"drugstore", r"affordable", r"\bdupe", r"budget"]),
    ("list", "am-pm-routine-by-evidence", "AM/PM routine by evidence", [r"morning routine", r"night(time)? routine", r"am.{0,3}pm", r"skincare routine"]),
]


def corpus():
    parts = []
    for f in glob.glob(str(ROOT / "research-cache" / "transcripts" / "*.txt")):
        try:
            parts.append(pathlib.Path(f).read_text(encoding="utf-8").splitlines()[0])
        except Exception:
            pass
    try:
        out = subprocess.run(["grep", "-rh", "^  title:", str(ROOT / "data")],
                             capture_output=True, text=True)
        parts += [l[len("  title:"):].strip() for l in out.stdout.splitlines()]
    except Exception:
        pass
    return "\n".join(parts).lower()


def _exists(t, slug):
    d = {"condition": "conditions", "goal": "goals", "list": "lists"}[t]
    return (ROOT / "data" / d / f"{slug}.md").exists()


def _queued(t):
    f = ROOT / "data" / "queues" / f"{t}s.yaml"
    return f.read_text(encoding="utf-8").lower() if f.exists() else ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min", type=int, default=2, help="frequency floor (default 2)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    text = corpus()
    queued = {t: _queued(t) for t in ("condition", "goal", "list")}

    scored = []
    for t, slug, name, pats in CANDIDATES:
        hits = sum(len(re.findall(p, text)) for p in pats)
        if hits < args.min:
            continue
        if _exists(t, slug):
            continue
        if slug in queued[t] or name.lower() in queued[t]:
            continue
        scored.append((hits, t, slug, name))
    scored.sort(reverse=True)

    for hits, t, slug, name in scored:
        print(f"HITx{hits:>3}  [{t}]  {name}")
    print(f"\n{len(scored)} new hub candidate(s) above floor {args.min}.")
    if args.dry_run or not scored:
        return 0
    for hits, t, slug, name in scored:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "sk"), "queue-add", name,
                        "--type", t, "--source",
                        f"discover_hubs: {hits} mentions across the video archive; no {t} hub yet"],
                       capture_output=True, text=True)
    print(f"queued {len(scored)} hub candidate(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
