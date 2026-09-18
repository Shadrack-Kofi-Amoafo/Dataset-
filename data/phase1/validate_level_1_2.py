#!/usr/bin/env python3
"""Validation for data/phase1/level_1_2_critical_causal_reasoning.jsonl.

Checks: line count, one JSON object per line, exact field set and order,
allowed category values, difficulty range, no blank lines, no duplicate or
near-duplicate scenarios, and reports the category / difficulty distribution.

Usage: python3 data/phase1/validate_level_1_2.py
"""
import collections
import json
import os
import re
import sys

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "level_1_2_critical_causal_reasoning.jsonl")
EXPECTED_LINES = 500
FIELDS = ["instruction", "reasoning", "answer", "category", "difficulty"]
CATEGORIES = {
    "correlation_vs_causation", "confounding", "reverse_causality", "intervention",
    "counterfactual", "causal_chain", "competing_explanations", "evidence_quality",
    "selection_bias", "measurement_bias", "temporal_reasoning", "experimental_design",
    "regression_to_mean", "alternative_hypothesis", "causal_attribution", "uncertainty",
}
STOP = set("""a an the of to in and or is are was were be been for with on at by from that
this it its as than then so such not no more most some any all each per cent percent after
before""".split())
NEAR_DUP_THRESHOLD = 0.34
MIN_REASONING_SENTENCES = 3
MAX_REASONING_SENTENCES = 6


def sentences(text):
    return [part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part]


def words(text):
    return set(re.findall(r"[a-z']+", text.lower())) - STOP


def main():
    raw = open(PATH, encoding="utf-8").read()
    errors = []
    if "\n\n" in raw:
        errors.append("file contains a blank line")
    if not raw.endswith("\n"):
        errors.append("file does not end with a newline")
    body = [line for line in raw.split("\n") if line.strip()]
    if len(body) != EXPECTED_LINES:
        errors.append(f"expected {EXPECTED_LINES} lines, found {len(body)}")

    objs = []
    for n, line in enumerate(body, 1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {n}: invalid JSON ({exc})")
            continue
        if list(obj.keys()) != FIELDS:
            errors.append(f"line {n}: fields are {list(obj.keys())}, expected {FIELDS}")
        if obj.get("category") not in CATEGORIES:
            errors.append(f"line {n}: bad category {obj.get('category')!r}")
        if obj.get("difficulty") not in (1, 2, 3, 4):
            errors.append(f"line {n}: bad difficulty {obj.get('difficulty')!r}")
        for field in ("instruction", "reasoning", "answer"):
            value = obj.get(field)
            if not isinstance(value, str) or len(value.split()) < 10:
                errors.append(f"line {n}: {field} is too short or not a string")
        count = len(sentences(obj.get("reasoning", "")))
        if not MIN_REASONING_SENTENCES <= count <= MAX_REASONING_SENTENCES:
            errors.append(f"line {n}: reasoning has {count} sentences, "
                          f"expected {MIN_REASONING_SENTENCES}-{MAX_REASONING_SENTENCES}")
        objs.append(obj)

    seen = collections.Counter(o["instruction"] for o in objs)
    for text, count in seen.items():
        if count > 1:
            errors.append(f"duplicate instruction: {text[:70]}...")

    vectors = [words(o["instruction"]) for o in objs]
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            union = vectors[i] | vectors[j]
            if not union:
                continue
            score = len(vectors[i] & vectors[j]) / len(union)
            if score > NEAR_DUP_THRESHOLD:
                errors.append(f"near-duplicate scenarios on lines {i + 1} and {j + 1} "
                              f"(jaccard {score:.2f})")

    cats = collections.Counter(o["category"] for o in objs)
    diff = collections.Counter(o["difficulty"] for o in objs)
    print(f"file: {os.path.relpath(PATH)}")
    print(f"lines: {len(body)}   parsed objects: {len(objs)}   errors: {len(errors)}")
    print("\ncategory distribution")
    for name, count in cats.most_common():
        print(f"  {name:26s} {count:3d}  {count / len(objs) * 100:5.1f}%")
    print("\ndifficulty distribution")
    for level in sorted(diff):
        print(f"  {level}  {diff[level]:3d}  {diff[level] / len(objs) * 100:5.1f}%")
    hard = sum(v for k, v in diff.items() if k >= 2)
    print(f"\nsamples at difficulty 2-4: {hard} ({hard / len(objs) * 100:.1f}%)")
    print("reasoning sentence counts:",
          dict(sorted(collections.Counter(len(sentences(o["reasoning"])) for o in objs).items())))
    trap = re.compile(r"trap|tempting|misleading|overstat|inflat|artifact|coincid|"
                      r"not supported|unsupported|cannot be attributed|cannot be credited|"
                      r"does not establish|plausible alternative|may reflect|largely reflect|"
                      r"unlikely to", re.IGNORECASE)
    flagging = sum(1 for o in objs if trap.search(o["answer"]))
    insufficient = sum(1 for o in objs if re.search(
        r"cannot be determined|cannot determine|insufficient|is unknown|"
        r"cannot be established|cannot be split|cannot be identified|"
        r"is unidentifiable|cannot yet|not yet attributable|"
        r"cannot be cleanly attributed|cannot be judged", o["answer"], re.IGNORECASE))
    withheld = sum(1 for o in objs if re.search(
        r"not (yet )?(supported|established|attributed|credited|justified)|"
        r"cannot be (attributed|credited|determined|established|identified|split)|"
        r"does not (establish|show|support)|unknown|insufficient|unlikely to",
        o["answer"], re.IGNORECASE))
    print(f"answers that explicitly flag a misleading reading: {flagging}")
    print(f"answers that state the evidence is insufficient: {insufficient}")
    print(f"answers that withhold or qualify a causal conclusion: {withheld}")
    for message in errors:
        print("FAIL:", message)
    print("\nRESULT:", "PASS" if not errors else f"FAIL ({len(errors)} problem(s))")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
