#!/usr/bin/env python3
"""Validator for the Level 1.2 critical and causal reasoning dataset.

Validates every Level 1.2 file listed in EXPECTED, using that file's expected
line count. Checks:

  * exactly one JSON object per line, no blank lines, no trailing whitespace
  * exactly the five required keys, in order
  * category drawn from the fixed 16-label taxonomy
  * difficulty is an integer 1-4
  * no duplicate instructions, and no near-duplicate instruction/answer pairs
    (Jaccard similarity over stopword-stripped word sets)
  * reasoning length between 3 and 6 sentences
  * no hidden chain-of-thought markers
  * ASCII only, no raw double quotes inside field values

Reports the difficulty and category distributions plus keyword-detected counts
of adversarial framings, insufficiency answers, and conditional answers. Those
counts are lower bounds, not audited classifications.

Run:
    python3 validate_level_1_2.py
"""
import collections
import json
import re
import sys
from pathlib import Path

FILES = {
    "level_1_2_critical_causal_reasoning.jsonl": 500,
    "level_1_2_critical_causal_reasoning_batch2.jsonl": 200,
}
NEAR_DUP_THRESHOLD = 0.34
MIN_REASONING_SENTENCES = 3
MAX_REASONING_SENTENCES = 6
CATEGORIES = {
    "correlation_vs_causation", "confounding", "reverse_causality",
    "causal_chain", "counterfactual", "intervention", "competing_explanations",
    "selection_bias", "measurement_bias", "regression_to_mean",
    "temporal_reasoning", "evidence_quality", "experimental_design",
    "uncertainty", "causal_attribution", "alternative_hypothesis",
}
REQUIRED_KEYS = ["instruction", "reasoning", "answer", "category", "difficulty"]
COT_MARKERS = ["let's think", "let's reason", "step by step", "first, we",
               "chain of thought", "we begin by", "as an ai"]
STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
per cent percent can could would should will may might must do does did have has had if
because while when where which who whom whose what why how""".split())

TRAP_PATTERNS = re.compile(
    r"trap|tempting|misleading|overstat|inflat|artifact|coincid|not supported|unsupported|"
    r"cannot be attributed|cannot be credited|does not establish|plausible alternative|"
    r"may reflect|largely reflect|unlikely to|reversed|circular|restates|does not follow",
    re.I)
INSUFFICIENT_PATTERNS = re.compile(
    r"cannot be determined|cannot determine|insufficient|is unknown|cannot be established|"
    r"cannot be identified|cannot be split|no single cause|cannot be assigned", re.I)
CONDITIONAL_PATTERNS = re.compile(
    r"if |unless|depend|conditional|may |might |plausib|likely|unlikely|cannot", re.I)


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def validate(path, expected_lines):
    errors, notes = [], []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            raw = line.rstrip("\n")
            if not raw.strip():
                errors.append(f"line {lineno}: blank line")
                continue
            if raw != raw.strip():
                errors.append(f"line {lineno}: leading/trailing whitespace")
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"line {lineno}: invalid JSON ({exc})")
                continue
            if not isinstance(obj, dict):
                errors.append(f"line {lineno}: not a JSON object")
                continue
            keys = list(obj.keys())
            if keys != REQUIRED_KEYS:
                errors.append(f"line {lineno}: keys {keys} != {REQUIRED_KEYS}")
                continue
            if obj["category"] not in CATEGORIES:
                errors.append(f"line {lineno}: invalid category {obj['category']!r}")
            if not isinstance(obj["difficulty"], int) or not 1 <= obj["difficulty"] <= 4:
                errors.append(f"line {lineno}: difficulty out of range {obj['difficulty']!r}")
            for field in ("instruction", "reasoning", "answer"):
                value = obj[field]
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"line {lineno}: {field} is empty or not a string")
                    continue
                if '"' in value:
                    errors.append(f"line {lineno}: raw double quote in {field}")
                if not value.isascii():
                    errors.append(f"line {lineno}: non-ASCII in {field}")
                for marker in COT_MARKERS:
                    if marker in value.lower():
                        errors.append(f"line {lineno}: chain-of-thought marker {marker!r} in {field}")
            sc = sentence_count(obj["reasoning"])
            if not MIN_REASONING_SENTENCES <= sc <= MAX_REASONING_SENTENCES:
                errors.append(f"line {lineno}: reasoning has {sc} sentences "
                              f"(expected {MIN_REASONING_SENTENCES}-{MAX_REASONING_SENTENCES})")
            rows.append((lineno, obj))

    if len(rows) != expected_lines:
        errors.append(f"expected {expected_lines} objects, found {len(rows)}")

    instr_index = collections.defaultdict(list)
    for lineno, obj in rows:
        instr_index[obj["instruction"].strip().lower()].append(lineno)
    for instruction, linenos in instr_index.items():
        if len(linenos) > 1:
            errors.append(f"duplicate instruction on lines {linenos}: {instruction[:80]!r}")

    near = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            li, a = rows[i]
            lj, b = rows[j]
            for field in ("instruction", "answer"):
                wa, wb = words(a[field]), words(b[field])
                union = wa | wb
                if not union:
                    continue
                sim = len(wa & wb) / len(union)
                if sim > NEAR_DUP_THRESHOLD:
                    near.append((round(sim, 3), field, li, lj, a[field][:70]))
    if near:
        near.sort(reverse=True)
        for sim, field, li, lj, snippet in near[:20]:
            errors.append(f"near-duplicate {field} ({sim}) lines {li}/{lj}: {snippet!r}")

    return rows, errors, notes


def report(rows, expected_lines):
    cats = collections.Counter(o["category"] for _, o in rows)
    diffs = collections.Counter(o["difficulty"] for _, o in rows)
    print(f"objects: {len(rows)} (expected {expected_lines})")
    print(f"difficulty: {dict(sorted(diffs.items()))}")
    print(f"categories: {dict(cats.most_common())}")
    sc = collections.Counter(sentence_count(o["reasoning"]) for _, o in rows)
    print(f"reasoning sentence counts: {dict(sorted(sc.items()))}")
    print("answers flagging a misleading reading (lower bound): "
          f"{sum(1 for _, o in rows if TRAP_PATTERNS.search(o['answer']))}")
    print("answers that are insufficient-evidence (lower bound): "
          f"{sum(1 for _, o in rows if INSUFFICIENT_PATTERNS.search(o['answer']))}")
    print("answers that are conditional/uncertain (lower bound): "
          f"{sum(1 for _, o in rows if CONDITIONAL_PATTERNS.search(o['answer']))}")


def main():
    base = Path(__file__).parent
    exit_code = 0
    total = 0
    all_rows = {}
    for name, expected in FILES.items():
        path = base / name
        print(f"== {name}")
        if not path.exists():
            print(f"FAIL: {name} is missing")
            exit_code = 1
            continue
        rows, errors, _ = validate(path, expected)
        report(rows, expected)
        if errors:
            exit_code = 1
            print(f"FAIL: {len(errors)} problem(s)")
            for err in errors[:50]:
                print("  -", err)
        else:
            print("PASS")
        print()
        total += len(rows)
        all_rows[name] = rows

    names = [n for n in FILES if n in all_rows]
    for a_i in range(len(names)):
        for b_i in range(a_i + 1, len(names)):
            na, nb = names[a_i], names[b_i]
            hits = []
            for _, a in all_rows[na]:
                for _, b in all_rows[nb]:
                    for field in ("instruction", "answer"):
                        wa, wb = words(a[field]), words(b[field])
                        union = wa | wb
                        if union and len(wa & wb) / len(union) > NEAR_DUP_THRESHOLD:
                            hits.append((field, a["instruction"][:60], b["instruction"][:60]))
            print(f"cross-file near-duplicates ({na} vs {nb}): {len(hits)}")
            if hits:
                exit_code = 1
                for field, ia, ib in hits[:10]:
                    print(f"  - {field}: {ia!r} / {ib!r}")

    print(f"total Level 1.2 samples across {len(FILES)} files: {total}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
