#!/usr/bin/env python3
"""Validator for the Phase 8.1 web-specialization dataset (1,000 samples, 35 categories)."""
import collections
import json
import re
import sys
from pathlib import Path

FILE = "level_8_1_agent_foundations_web.jsonl"
EXPECTED = 1000
CATEGORIES = {
    "web_task_understanding", "requirement_extraction", "frontend_inspection",
    "backend_inspection", "repository_structure", "dependency_inspection",
    "package_configuration", "browser_inspection", "network_inspection",
    "api_reasoning", "html_reasoning", "css_reasoning", "javascript_reasoning",
    "typescript_reasoning", "react_reasoning", "nextjs_reasoning",
    "nodejs_reasoning", "database_reasoning", "git_reasoning", "tool_selection",
    "next_action_selection", "plan_vs_action", "state_tracking",
    "hypothesis_testing", "debugging_decision", "test_result_interpretation",
    "build_result_interpretation", "requirement_verification",
    "failure_recovery", "stopping_conditions", "frontend_backend_integration",
    "dependency_reasoning", "configuration_reasoning", "regression_detection",
    "autonomous_web_workflow",
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
    r"not yet|not sufficient|unverified|green (suite|board|build)|pass(es|ed)? (do|does) not|"
    r"risk|rather than editing|without (evidence|inspection|verification)|assumption|"
    r"cannot conclude|only (that|means)|does not (prove|establish|mean)|still (open|remains)|"
    r"ask|clarif|guessing|lottery|symptom|root cause|evidence", re.I)


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

    tokens = [(words(o["instruction"]), words(o["answer"])) for o in rows]
    near_i = near_pair = 0
    examples_p = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            si = jaccard(tokens[i][0], tokens[j][0])
            if si > NEAR_DUP_THRESHOLD:
                near_i += 1
            sp = jaccard(tokens[i][0] | tokens[i][1], tokens[j][0] | tokens[j][1])
            if sp > 0.72:
                near_pair += 1
                if len(examples_p) < 5:
                    examples_p.append((round(sp, 2), i, j))

    cats = collections.Counter(o["category"] for o in rows)
    diffs = collections.Counter(o["difficulty"] for o in rows)
    sc = collections.Counter(sentence_count(o["reasoning"]) for o in rows)
    adv = sum(1 for o in rows if ADV_PATTERNS.search(o["answer"]) or ADV_PATTERNS.search(o["reasoning"]))
    ask_next = sum(1 for o in rows if "what should the agent do next" in o["instruction"].lower())
    web_marker = re.compile(r"api|browser|css|html|dom|react|next|node|express|route|endpoint|http|url|page|component|server|client|npm|webpack|deploy|cors|cookie|session|sql|postgres|sqlite|frontend|backend|typescript|javascript|middleware|hydration|viewport|stylesheet", re.I)
    webmed = sum(1 for o in rows if not web_marker.search(o["instruction"] + " " + o["answer"]))

    print(f"objects: {len(rows)} (expected {EXPECTED})")
    print("difficulty:", dict(sorted(diffs.items())))
    print(f"categories distinct: {len(cats)}, per-category min/max: {min(cats.values())}/{max(cats.values())}")
    print("reasoning sentences:", dict(sorted(sc.items())))
    print(f"adversarial/evidence markers (lower bound): {adv} ({adv/len(rows)*100:.0f}%)")
    print(f"'what should the agent do next' phrasing: {ask_next}")
    print(f"samples lacking obvious web markers: {webmed}")
    print(f"near-duplicate instructions >{NEAR_DUP_THRESHOLD}: {near_i}")
    print(f"high overall-overlap pairs >0.72: {near_pair}, samples: {examples_p}")

    if errors or near_i or ans_dups:
        for e in errors[:30]:
            print("ERR:", e)
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
