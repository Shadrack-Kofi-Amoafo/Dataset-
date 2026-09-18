#!/usr/bin/env python3
"""Build and validate the final repository-understanding dataset.

Assembles all part files, validates structure and content invariants,
computes difficulty/category distributions, runs near-duplicate
heuristics, and (if valid) writes repository_understanding_dataset.jsonl.
"""
import glob
import importlib.util
import json
import re
import sys
from collections import Counter

ALLOWED_FIELDS = {"instruction", "reasoning", "answer", "category", "difficulty"}
DIFFICULTIES = ("easy", "medium", "hard", "expert")
ALLOWED_NONASCII = set("’‘“”—–…§×→←≥≤±")

TARGET_TOTAL = 1000
EASY_LO, EASY_HI = 0.07, 0.15     # ~10% target band
MED_LO, MED_HI = 0.16, 0.30       # ~20% guide; inner medium/hard split is calibration-judgment
HARD_LO, HARD_HI = 0.34, 0.53     # ~45%
EXP_LO, EXP_HI = 0.18, 0.33       # ~25%

CATEGORY_RE = re.compile(r"^[a-z][a-z_]+$")


def load_samples():
    samples = []
    for path in sorted(glob.glob("part*_*.py")):
        spec = importlib.util.spec_from_file_location("mod", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for i, s in enumerate(mod.SAMPLES):
            samples.append((path, i, s))
    return samples


def norm_text(t):
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def shingles(text, n=7):
    words = norm_text(text).split()
    if len(words) < n:
        return {" ".join(words)}
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    samples = load_samples()
    print(f"Loaded from parts: {len(samples)}")

    problems = []

    # ---- structural validation
    for path, i, s in samples:
        tag = f"{path}[{i}]"
        keys = set(s.keys())
        if keys != ALLOWED_FIELDS:
            problems.append(f"{tag}: bad fields {sorted(keys ^ ALLOWED_FIELDS)}")
            continue
        for f in ("instruction", "reasoning", "answer"):
            if not isinstance(s[f], str) or len(s[f].strip()) < 40:
                problems.append(f"{tag}: {f} too short/invalid")
        if not isinstance(s.get("category"), str) or not CATEGORY_RE.match(s.get("category", "")):
            problems.append(f"{tag}: bad category {s.get('category')!r}")
        if s.get("difficulty") not in DIFFICULTIES:
            problems.append(f"{tag}: bad difficulty {s.get('difficulty')!r}")
        # JSON-encodable check
        try:
            json.dumps(s)
        except Exception as e:
            problems.append(f"{tag}: not JSON-serializable: {e}")
        # ASCII hygiene on emitted content
        for f in ALLOWED_FIELDS:
            for ch in s[f]:
                if ord(ch) > 127 and ch not in ALLOWED_NONASCII:
                    problems.append(f"{tag}: non-ascii {ch!r} in {f}")
                    break

    # ---- exact & near-duplicate detection
    seen_exact = {}
    for path, i, s in samples:
        key = norm_text(s["instruction"])
        if key in seen_exact:
            problems.append(f"{path}[{i}]: EXACT duplicate of {seen_exact[key]}")
        else:
            seen_exact[key] = f"{path}[{i}]"

    shingles_idx = [(f"{p}[{i}]", shingles(s["instruction"] + " " + s["answer"][:400])) for p, i, s in samples]
    near_dupes = []
    for a in range(len(shingles_idx)):
        for b in range(a + 1, len(shingles_idx)):
            sim = jaccard(shingles_idx[a][1], shingles_idx[b][1])
            if sim > 0.45:
                near_dupes.append((shingles_idx[a][0], shingles_idx[b][0], round(sim, 3)))
    near_dupes.sort(key=lambda x: -x[2])
    for t1, t2, sim in near_dupes[:40]:
        print(f"  NEAR-DUPE {sim}: {t1} ~~ {t2}")

    # ---- distributions
    diff_count = Counter(s["difficulty"] for _, _, s in samples)
    cat_count = Counter(s["category"] for _, _, s in samples)
    total = len(samples)
    print("\nDifficulty:", dict(diff_count))
    for d, lo, hi in (("easy", EASY_LO, EASY_HI), ("medium", MED_LO, MED_HI),
                      ("hard", HARD_LO, HARD_HI), ("expert", EXP_LO, EXP_HI)):
        frac = diff_count.get(d, 0) / total
        flag = "OK" if lo <= frac <= hi else "OUT OF BAND"
        print(f"  {d}: {diff_count.get(d, 0)} ({frac:.1%}) {flag}")
    print("\nCategories:")
    for c, n in sorted(cat_count.items()):
        print(f"  {c}: {n}")
    if len(cat_count) != 34:
        print(f"  WARNING: {len(cat_count)} categories (expected 34)")

    print(f"\nStructural problems: {len(problems)}")
    for p in problems[:60]:
        print("  " + p)

    if problems:
        print("\nNOT writing output: fix problems first.")
        sys.exit(1)

    if total != TARGET_TOTAL:
        print(f"\nTotal {total} != {TARGET_TOTAL}: purge required (see below).")
        sys.exit(2)

    out = "repository_understanding_dataset.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        for _, _, s in samples:
            obj = {k: s[k] for k in ("instruction", "reasoning", "answer", "category", "difficulty")}
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"\nWrote {out} ({total} lines)")


if __name__ == "__main__":
    main()
