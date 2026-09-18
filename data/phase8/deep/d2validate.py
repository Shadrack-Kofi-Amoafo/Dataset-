#!/usr/bin/env python3
"""Validator for the Phase 8.2 DEEP task-decomposition web dataset.

Checks:
- 1,000 rows, exact 5-key schema, difficulty string in {easy, medium, hard, expert}
- exact difficulty targets 100/250/400/250; 36 categories; per-category 20..34
- content hygiene: ASCII, no double quotes, non-empty, sentence bounds
- uniqueness: exact instruction/answer dedup, within-file instruction near-dup cap,
  cross-file near-dup check against the prior 8.2 dataset
- marker targets: multi-layer >= 50%, missing-info >= 30%, adaptive >= 30%,
  verification >= 25%, scope-control >= 20%, adversarial >= 40%
"""
import json, re, sys, collections
from pathlib import Path

FILE = Path(__file__).parent / "../level_8_2_deep_task_decomposition_web.jsonl"
PRIOR = Path(__file__).parent / "../level_8_2_task_decomposition_web.jsonl"

sys.path.insert(0, str(Path(__file__).parent))
from d2frames_a import D2A
from d2frames_b import D2B
from d2frames_c import D2C
from d2frames_d import D2D
from d2frames_e import D2E
from d2frames_f import D2F

CATS = {}
for src in (D2A, D2B, D2C, D2D, D2E, D2F):
    CATS.update(src)
assert len(CATS) == 36

DIFFS = {"easy": 100, "medium": 250, "hard": 400, "expert": 250}
MARKERS = {
    "multi_layer": 0.50,
    "missing_info": 0.30,
    "adaptive": 0.30,
    "verification": 0.25,
    "scope_control": 0.20,
    "adversarial": 0.40,
}

STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
can could would should must do does did have has had if because while when where which who
what why how state agent proj project user user's task tasks repo repository request
next right wrong done fix fixing need needs plan plans planned decompose decomposition
subtask subtasks goal given which order into under over between""".split())


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def jaccard(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


LAYER_GROUPS = [
    re.compile(r"ui|interface|component|render|css|browser|front.?end|pixel|screen|visual|client|viewport|\bdom\b|layout|responsive", re.I),
    re.compile(r"\bapi|endpoint|graphql|webhook|contract|postmessage", re.I),
    re.compile(r"server|service|worker|\bqueue\b|\bjob\b|middleware|backend|daemon", re.I),
    re.compile(r"database|schema|migration|quer|index|persist|storage|table|backfill|replica", re.I),
    re.compile(r"auth|session|token|permission|credential|oauth|rbac|privilege", re.I),
    re.compile(r"deploy|\bci\b|cache|cdn|config|environment|pipeline|release|staging|production|runtime|rollback|\bflag", re.I),
]
MISSING_RE = re.compile(r"missing information|not expose|unknown|absence|undocumented|unwritten|uncertain|unmeasured|no one (knows|can)|\bgap|elicit|verify absence|missing api|never written|ghost|unknowns|hearsay|assumption|vague|uncharacteri|forgot|guess|unseen|unresolved|unanswered|unstated|no test suite|hidden dependenc|missing data|rumor", re.I)
ADAPT_RE = re.compile(r"rollback|fallback|replan|pivot|contingenc|degrad|renegotiat|cohort|brownout|flag[- ]gat|conditional|adapt|drill|canary|resume|revers", re.I)
VERIF_RE = re.compile(r"test|verif|witness|evidence|monitor|baseline|metric|probe|canary|dashboard|smoke|regression|suite|assert|scan|checkpoint|checksum", re.I)
SCOPE_RE = re.compile(r"scope|out.of.scope|minimal footprint|park|parked|parking|boundar|defer|separate (ticket|series|artifact)|displacement|exclud|restrain|declin|not-now", re.I)

T_LINES = set()
for cat in CATS:
    for t in CATS[cat]["t"]:
        T_LINES.add(t)


def marker_flags(sample):
    blob = sample["instruction"] + " " + sample["answer"] + " " + sample["reasoning"]
    flags = {
        "multi_layer": sum(1 for g in LAYER_GROUPS if g.search(blob)) >= 2,
        "missing_info": bool(MISSING_RE.search(blob)),
        "adaptive": bool(ADAPT_RE.search(blob)),
        "verification": bool(VERIF_RE.search(blob)),
        "scope_control": bool(SCOPE_RE.search(blob)),
        "adversarial": any(t in sample["reasoning"] for t in T_LINES),
    }
    return flags


def main():
    rows = []
    with open(FILE, encoding="utf-8") as fh:
        for ln in fh:
            rows.append(json.loads(ln))
    assert len(rows) == 1000, len(rows)
    for r in rows:
        assert set(r) == {"instruction", "reasoning", "answer", "category", "difficulty"}, set(r)
        assert r["difficulty"] in DIFFS, r["difficulty"]
        assert r["category"] in CATS, r["category"]
        for k in ("instruction", "reasoning", "answer"):
            v = r[k]
            assert isinstance(v, str) and v.strip(), k
            assert v.isascii() and '"' not in v, v
        sc = sentence_count(r["reasoning"])
        assert 3 <= sc <= 7, (r["category"], sc)
        assert sentence_count(r["answer"]) >= 2, r["category"]
        assert len(r["instruction"]) >= 40
        assert r["reasoning"] != r["answer"] and r["answer"] != r["instruction"]

    diffs = collections.Counter(r["difficulty"] for r in rows)
    assert all(diffs[d] == DIFFS[d] for d in DIFFS), dict(diffs)
    cats = collections.Counter(r["category"] for r in rows)
    assert len(cats) == 36, len(cats)
    assert min(cats.values()) >= 20 and max(cats.values()) <= 34, (min(cats.values()), max(cats.values()))
    print("difficulty OK:", {d: diffs[d] for d in sorted(DIFFS)})
    print("categories OK: 36, per-cat range", min(cats.values()), "-", max(cats.values()))

    instrs = [r["instruction"] for r in rows]
    answers = [r["answer"] for r in rows]
    assert len(set(instrs)) == 1000 and len(set(answers)) == 1000
    print("exact dedup OK: 1000 unique instructions and answers")

    iw = [words(t) for t in instrs]
    hot_in = 0
    for i in range(1000):
        for j in range(i + 1, 1000):
            s = jaccard(iw[i], iw[j])
            if s > hot_in:
                hot_in = s
                hot_pair = (i, j)
    print(f"within-file instruction max jaccard: {hot_in:.3f} (rows {hot_pair})")
    assert hot_in < 0.62, hot_in

    aw = [words(t) for t in answers]
    cat_idx = collections.defaultdict(list)
    for i, r in enumerate(rows):
        cat_idx[r["category"]].append(i)
    cross_hot = 0
    for i in range(1000):
        for j in range(i + 1, 1000):
            if rows[i]["category"] == rows[j]["category"]:
                continue
            s = jaccard(aw[i], aw[j])
            if s > cross_hot:
                cross_hot = s
    print(f"cross-category answer max jaccard: {cross_hot:.3f}")
    assert cross_hot < 0.85, cross_hot

    prior_instr = []
    with open(PRIOR, encoding="utf-8") as fh:
        for ln in fh:
            prior_instr.append(json.loads(ln)["instruction"])
    pw = [words(t) for t in prior_instr]
    x_hot, x_over = 0, 0
    for i in range(1000):
        for j in range(len(pw)):
            s = jaccard(iw[i], pw[j])
            if s > x_hot:
                x_hot = s
                x_pair = (i, j)
            if s > 0.60:
                x_over += 1
    print(f"cross-file vs prior 8.2: max jaccard {x_hot:.3f} (new row {x_pair[0]}, prior row {x_pair[1]}), pairs>0.60: {x_over}")
    assert x_hot < 0.70, x_hot

    counts = collections.Counter()
    for r in rows:
        fl = marker_flags(r)
        for k, v in fl.items():
            counts[k] += v
    print("marker rates:")
    ok = True
    for k, thr in MARKERS.items():
        rate = counts[k] / 1000
        status = "OK " if rate >= thr else "FAIL"
        if rate < thr:
            ok = False
        print(f"  {status} {k}: {rate:.1%} (target >= {thr:.0%})")
    assert ok, "marker targets missed"
    n_adv = counts["adversarial"]
    res_n = [sentence_count(r["reasoning"]) for r in rows]
    print(f"reasoning sentences: min {min(res_n)}, max {max(res_n)}; adversarial rows {n_adv}")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
