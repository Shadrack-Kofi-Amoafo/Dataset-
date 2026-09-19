#!/usr/bin/env python3
"""Validator for level_8_4_tool_terminal_use_web.jsonl.

Checks: line count, per-line JSON validity and bare-object form, the exact
5-field set in order, allowed category and difficulty values, difficulty
distribution bands, minimum field lengths, reasoning sentence count (3-6),
ASCII policy, exact-duplicate and near-duplicate instructions (word-set
Jaccard), near-duplicate full samples (5-gram shingle containment), and
adversarial / tool-choice / recovery coverage from marker scans. Prints
distributions. Exit 0 on pass, 1 on any failure.
"""
import json
import os
import re
import sys
from collections import Counter
from itertools import combinations

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "level_8_4_tool_terminal_use_web.jsonl")
EXPECTED_LINES = 1000
FIELDS = ["instruction", "reasoning", "answer", "category", "difficulty"]
DIFFICULTIES = {"easy", "medium", "hard", "expert"}

CATEGORIES = {
    "tool_selection", "terminal_reasoning", "shell_command_reasoning",
    "file_inspection", "file_search", "safe_file_modification",
    "git_operations", "package_manager_reasoning", "dependency_installation",
    "process_management", "port_diagnostics", "server_execution",
    "build_tool_reasoning", "test_runner_usage", "browser_devtools",
    "network_inspection", "api_testing", "database_cli", "log_analysis",
    "environment_configuration", "tool_output_interpretation",
    "command_failure_recovery", "tool_result_verification", "safe_tool_use",
    "multi_tool_workflow", "adaptive_tool_selection",
}

BANDS = {"easy": (0.04, 0.15), "medium": (0.16, 0.32),
         "hard": (0.32, 0.48), "expert": (0.20, 0.32)}
ALLOWED_NON_ASCII = set("\u2019\u2018\u201c\u201d\u2014\u2013\u2026\u00a7\u00d7\u2192\u2190\u2265\u2264\u00b1")

ADV_MARKERS = [
    "appears to", "appears ", "seems ", "says the", "claims", "asserts",
    "works locally", "works in dev", "reports success", "misleading",
    "stale", "wrong conclusion", "not evidence", "silently", "false",
    "inconsist", "but the", "although", "yet the", "says ", "believes",
    "assume", "assum", "instead of", "trap", "conflict", "contradict",
    "reports it", "clean", "zero", "cannot be", "is not proof",
    "does not prove", "says one", "docs", "documentation", "ticket",
]
MISSING_MARKERS = ["missing", "not recorded", "cannot be determined", "absent",
                   "unverifiable", "unknown", "no record", "not visible",
                   "could not", "unable to", "does not establish", "cannot tell"]


def sentences(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'0-9])", text.strip())
    return len([p for p in parts if p.strip()])


def words(text: str):
    return frozenset(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def shingles(text: str, k: int = 5):
    toks = re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()
    return set(tuple(toks[i:i + k]) for i in range(max(0, len(toks) - k + 1)))


def main() -> int:
    problems = []
    raw = open(PATH, "rb").read().decode("utf-8")
    lines = raw.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != EXPECTED_LINES:
        problems.append(f"line count {len(lines)} != {EXPECTED_LINES}")

    objs, seen = [], set()
    cats, diffs = Counter(), Counter()
    for n, line in enumerate(lines, 1):
        if not line.strip():
            problems.append(f"line {n}: blank")
            continue
        if not (line.startswith("{") and line.endswith("}")):
            problems.append(f"line {n}: not a bare JSON object")
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {n}: invalid JSON: {e}")
            continue
        if list(o.keys()) != FIELDS:
            problems.append(f"line {n}: fields {list(o.keys())}")
            continue
        if o["category"] not in CATEGORIES:
            problems.append(f"line {n}: category {o['category']!r}")
        if o["difficulty"] not in DIFFICULTIES:
            problems.append(f"line {n}: difficulty {o['difficulty']!r}")
        for f in ("instruction", "reasoning", "answer"):
            v = o[f]
            if not isinstance(v, str) or len(v.strip()) < 60:
                problems.append(f"line {n}: '{f}' missing or too short")
                continue
            if f != "answer" and len(v.split()) > 260:
                problems.append(f"line {n}: '{f}' too long")
            for ch in v:
                if ord(ch) >= 128 and ch not in ALLOWED_NON_ASCII:
                    problems.append(f"line {n}: disallowed char {ch!r} in '{f}'")
                    break
        sc = sentences(o["reasoning"])
        if sc < 3 or sc > 6:
            problems.append(f"line {n}: reasoning has {sc} sentences (want 3-6)")
        if len(o["answer"].split()) < 45:
            problems.append(f"line {n}: answer too thin ({len(o['answer'].split())} words)")
        k = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", o["instruction"].lower())).strip()
        if k in seen:
            problems.append(f"line {n}: duplicate instruction")
        seen.add(k)
        cats[o["category"]] += 1
        diffs[o["difficulty"]] += 1
        objs.append(o)

    total = len(objs) or 1
    for d, (lo, hi) in BANDS.items():
        frac = diffs[d] / total
        if not (lo <= frac <= hi):
            problems.append(f"difficulty {d}: {frac:.3f} outside [{lo}, {hi}]")
    for c in CATEGORIES:
        if cats[c] < 20:
            problems.append(f"category {c}: only {cats[c]} samples")

    # near-duplicate instructions (word-set Jaccard)
    ws = [words(o["instruction"]) for o in objs]
    near = 0
    for (i, a), (j, b) in combinations(enumerate(ws), 2):
        inter = len(a & b)
        union = len(a | b)
        if union and inter / union >= 0.62:
            near += 1
            problems.append(f"lines {i+1} & {j+1}: near-duplicate instructions ({inter/union:.2f})")
    # near-duplicate whole samples (shingle containment)
    sh = [shingles(o["instruction"] + " " + o["answer"]) for o in objs]
    dup = 0
    worst = []
    for i in range(len(objs)):
        for j in range(i + 1, len(objs)):
            small = min(len(sh[i]), len(sh[j]))
            if not small:
                continue
            cont = len(sh[i] & sh[j]) / small
            if cont >= 0.55:
                dup += 1
                worst.append((cont, i + 1, j + 1))
    for cont, i, j in sorted(worst, reverse=True)[:10]:
        problems.append(f"lines {i} & {j}: sample overlap {cont:.2f}")

    text_all = [(o["instruction"] + " " + o["answer"]).lower() for o in objs]
    adv = sum(any(m in t for m in ADV_MARKERS) for t in text_all)
    mis = sum(any(m in t for m in MISSING_MARKERS) for t in text_all)
    print(f"Loaded: {total}")
    for d in ("easy", "medium", "hard", "expert"):
        print(f"  {d}: {diffs[d]} ({diffs[d]/total:.1%})")
    print(f"Categories ({len(cats)}): " + ", ".join(f"{c}={cats[c]}" for c in sorted(cats)))
    print(f"adversarial/conflict phrasing: {adv/total:.1%}")
    print(f"missing-information recognition: {mis/total:.1%}")
    print(f"near-duplicate instruction pairs: {near}; overlapping sample pairs: {dup}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems[:40]:
            print(" -", p)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
