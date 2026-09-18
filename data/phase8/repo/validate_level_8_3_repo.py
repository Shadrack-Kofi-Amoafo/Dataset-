#!/usr/bin/env python3
"""Validator for level_8_3_repository_understanding.jsonl.

Checks: exact line count (1000), per-line JSON validity, exact 5-field set,
allowed category/difficulty values, difficulty distribution bands, reasoning
sentence count, field length minimums, exact-duplicate instructions, and
near-duplicate instruction pairs (word-set Jaccard). Prints distributions.
Exits 0 on pass, 1 on any failure.
"""
import json
import re
import sys
from collections import Counter
from itertools import combinations

PATH = "data/phase8/repo/level_8_3_repository_understanding.jsonl"
EXPECTED_LINES = 1000
FIELDS = ["instruction", "reasoning", "answer", "category", "difficulty"]
DIFFICULTIES = {"easy", "medium", "hard", "expert"}

CATEGORIES = {
    "adaptive_repository_understanding", "api_trace", "architecture_inference",
    "authentication_structure", "authorization_structure", "backend_structure",
    "bug_trace", "build_structure", "configuration_discovery", "context_selection",
    "control_flow", "cross_layer_reasoning", "data_flow", "database_structure",
    "deployment_structure", "dependency_reasoning", "dependency_reasoning",
    "entry_point_detection", "environment_reasoning", "feature_ownership",
    "file_relevance", "framework_detection", "frontend_structure",
    "generated_file_detection", "git_state", "hypothesis_verification",
    "legacy_code_detection", "missing_information", "monorepo_reasoning",
    "package_configuration", "repository_navigation", "repository_structure",
    "scope_control", "test_structure", "workspace_reasoning",
}

BANDS = {  # fraction of total, inclusive
    "easy": (0.07, 0.15),
    "medium": (0.16, 0.30),
    "hard": (0.34, 0.53),
    "expert": (0.18, 0.33),
}

ALLOWED_NON_ASCII = set("’‘“”—–…§×→←≥≤±")


def sentence_count(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'0-9])", text.strip())
    return len([p for p in parts if p.strip()])


def norm_words(text: str) -> frozenset:
    return frozenset(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def main() -> int:
    problems = []

    raw = open(PATH, "rb").read().decode("utf-8")
    lines = raw.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != EXPECTED_LINES:
        problems.append(f"line count {len(lines)} != {EXPECTED_LINES}")

    cats, diffs = Counter(), Counter()
    objs = []
    seen_norm = set()

    for n, line in enumerate(lines, 1):
        if not line.strip():
            problems.append(f"line {n}: blank")
            continue
        if not (line.startswith("{") and line.endswith("}")):
            problems.append(f"line {n}: not a bare JSON object")
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {n}: invalid JSON: {e}")
            continue
        if list(obj.keys()) != FIELDS:
            problems.append(f"line {n}: fields {list(obj.keys())} != {FIELDS}")
            continue
        for f in ("instruction", "reasoning", "answer"):
            v = obj[f]
            if not isinstance(v, str) or len(v.strip()) < 40:
                problems.append(f"line {n}: '{f}' missing or too short")
                continue
            for ch in v:
                if ord(ch) >= 128 and ch not in ALLOWED_NON_ASCII:
                    problems.append(f"line {n}: disallowed char {ch!r} in '{f}'")
                    break
        if obj["difficulty"] not in DIFFICULTIES:
            problems.append(f"line {n}: bad difficulty {obj['difficulty']!r}")
        if obj["category"] not in CATEGORIES:
            problems.append(f"line {n}: bad category {obj['category']!r}")
        sc = sentence_count(obj["reasoning"])
        if sc < 2 or sc > 7:
            problems.append(f"line {n}: reasoning has {sc} sentences (want 2-7)")
        key = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", obj["instruction"].lower())).strip()
        if key in seen_norm:
            problems.append(f"line {n}: duplicate instruction")
        seen_norm.add(key)
        cats[obj["category"]] += 1
        diffs[obj["difficulty"]] += 1
        objs.append(obj)

    total = len(objs)
    for d, (lo, hi) in BANDS.items():
        frac = diffs[d] / total if total else 0
        if not (lo <= frac <= hi):
            problems.append(f"difficulty {d}: {frac:.3f} outside [{lo}, {hi}]")

    # near-duplicate instructions via word-set Jaccard
    word_sets = [norm_words(o["instruction"]) for o in objs]
    near = 0
    for (i, a), (j, b) in combinations(enumerate(word_sets), 2):
        if not a or not b:
            continue
        inter = len(a & b)
        union = len(a | b)
        if inter / union >= 0.75:
            near += 1
            problems.append(f"lines {i+1} & {j+1}: near-duplicate instructions ({inter/union:.2f})")
            if near > 10:
                break

    print(f"Loaded: {total}")
    print(f"Difficulty: {dict(diffs)}")
    for d in ("easy", "medium", "hard", "expert"):
        frac = diffs[d] / total if total else 0
        print(f"  {d}: {diffs[d]} ({frac:.1%})")
    print(f"Categories ({len(cats)}):")
    for c in sorted(cats):
        print(f"  {c}: {cats[c]}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems[:50]:
            print(" -", p)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
