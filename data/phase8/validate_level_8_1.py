#!/usr/bin/env python3
"""Validator for Phase 8.1 agent-foundations dataset (1,000 samples).

Checks structural validity, category taxonomy, difficulty 1-5,
reasoning sentence counts 3-7, ASCII and quoting constraints,
chain-of-thought markers, exact and near-duplicate instructions,
Jaccard near-duplicates across paired instruction+answer sets,
plus distribution and adversarial-marker reports.
"""
import collections
import json
import re
import sys
from pathlib import Path

FILE = "level_8_1_agent_foundations.jsonl"
EXPECTED = 1000
CATEGORIES = {
    "task_understanding", "requirement_extraction", "constraint_identification",
    "information_gap_detection", "observation_before_action",
    "environment_inspection", "next_action_selection", "tool_selection",
    "action_sequencing", "plan_vs_action", "state_tracking", "goal_tracking",
    "observation_vs_assumption", "action_result_interpretation",
    "success_detection", "failure_detection", "plan_revision",
    "recovery_reasoning", "stopping_conditions", "verification",
    "unnecessary_action_detection", "risk_aware_action",
    "dependency_awareness", "context_management", "agent_loop_reasoning",
}
REQUIRED_KEYS = ["instruction", "reasoning", "answer", "category", "difficulty"]
COT_MARKERS = ["chain of thought", "let me think step by step",
               "step-by-step process:", "my hidden reasoning", "scratchpad"]
STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
per cent percent can could would should will may might must do does did have has had if
because while when where which who whom whose what why how state agent agent's proj
project user user's task repo repository request next right""".split())
NEAR_DUP_THRESHOLD = 0.62

ADV_PATTERNS = re.compile(
    r"premature|tempting|before (any|inspection|editing|touching|modifying)|"
    r"not yet|not sufficient|unverified|green suite (is|are|while)|pass(es|ed)? (do|does) not|"
    r"risk|rather than editing|without (evidence|inspection|verification)|assumption|"
    r"cannot conclude|only (that|means)|does not (prove|establish|mean)|still (open|remains)|"
    r"ask|clarif", re.I)


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def main():
    path = Path(__file__).parent / FILE
    errors = []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            raw = line.rstrip("\n")
            if not raw.strip():
                errors.append(f"line {lineno}: blank line")
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"line {lineno}: invalid JSON ({exc})")
                continue
            if list(obj.keys()) != REQUIRED_KEYS:
                errors.append(f"line {lineno}: bad keys")
            if obj["category"] not in CATEGORIES:
                errors.append(f"line {lineno}: bad category {obj['category']!r}")
            if not isinstance(obj["difficulty"], int) or not 1 <= obj["difficulty"] <= 5:
                errors.append(f"line {lineno}: difficulty {obj['difficulty']!r}")
            for field in ("instruction", "reasoning", "answer"):
                v = obj[field]
                if not isinstance(v, str) or not v.strip():
                    errors.append(f"line {lineno}: empty {field}")
                    continue
                if '"' in v or not v.isascii():
                    errors.append(f"line {lineno}: quoting/ascii issue in {field}")
                for m in COT_MARKERS:
                    if m in v.lower():
                        errors.append(f"line {lineno}: CoT marker {m!r} in {field}")
            sc = sentence_count(obj["reasoning"])
            if not 3 <= sc <= 7:
                errors.append(f"line {lineno}: reasoning {sc} sentences")
            rows.append(obj)

    if len(rows) != EXPECTED:
        errors.append(f"expected {EXPECTED}, got {len(rows)}")

    seen = collections.Counter(o["instruction"] for o in rows)
    for instr, n in seen.items():
        if n > 1:
            errors.append(f"duplicate instruction x{n}: {instr[:60]!r}")
    ans_seen = collections.Counter(o["answer"] for o in rows)
    ans_dups = sum(1 for n in ans_seen.values() if n > 2)
    print(f"answers repeated more than twice (distinct): {ans_dups}")

    # near-duplicate instructions, and paired instruction+answer overlap
    tokens = [(words(o["instruction"]), words(o["answer"])) for o in rows]
    near_i = near_pair = 0
    examples_i, examples_p = [], []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            si = jaccard(tokens[i][0], tokens[j][0])
            if si > NEAR_DUP_THRESHOLD:
                near_i += 1
                if len(examples_i) < 8:
                    examples_i.append((round(si, 2), i, j))
            sp = jaccard(tokens[i][0] | tokens[i][1], tokens[j][0] | tokens[j][1])
            if sp > 0.72:
                near_pair += 1
                if len(examples_p) < 8:
                    examples_p.append((round(sp, 2), i, j))

    cats = collections.Counter(o["category"] for o in rows)
    diffs = collections.Counter(o["difficulty"] for o in rows)
    sc = collections.Counter(sentence_count(o["reasoning"]) for o in rows)
    adv = sum(1 for o in rows if ADV_PATTERNS.search(o["answer"]) or ADV_PATTERNS.search(o["reasoning"]))

    print(f"objects: {len(rows)} (expected {EXPECTED})")
    print("difficulty:", dict(sorted(diffs.items())))
    print(f"categories distinct: {len(cats)}, per-category: {set(cats.values())}")
    print("reasoning sentences:", dict(sorted(sc.items())))
    print(f"adversarial/phrasing markers (lower bound): {adv} ({adv/len(rows)*100:.0f}%)")
    print(f"near-duplicate instructions >{NEAR_DUP_THRESHOLD}: {near_i}")
    for ex in examples_p[:5]:
        print("  pair-sample:", ex)
    if near_pair:
        print(f"high overall-overlap pairs >0.72 (sampled window): {near_pair}")

    if errors or near_i:
        for e in errors[:30]:
            print("ERR:", e)
        if near_i:
            print("near-instruction samples:", examples_i)
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
