#!/usr/bin/env python3
"""Emitter for Phase 8.2 DEEP task-decomposition web dataset.

Contract: 1,000 samples, 36 categories, difficulty as a STRING from
{easy, medium, hard, expert} with exact targets easy=100, medium=250,
hard=400, expert=250. Per-category quotas via divmod (25-29 per category).
Adversarial share driven by trap-line usage; marker properties carried by the
category designs and verified by d2validate.py.
"""
import json, random, re, collections
from pathlib import Path
from d2pools import PROJECTS, DGOALS, DOBS, AREAS, CONSTRAINTS, BOUNDARIES, RISKS, QUESTIONS
from d2frames_a import D2A
from d2frames_b import D2B
from d2frames_c import D2C
from d2frames_d import D2D
from d2frames_e import D2E
from d2frames_f import D2F
from d2frames_x import D2X

CATS = {}
for src in (D2A, D2B, D2C, D2D, D2E, D2F):
    CATS.update(src)
assert len(CATS) == 36
assert set(CATS) == set(D2X), (set(CATS) ^ set(D2X))
for cat in CATS:
    assert set(D2X[cat]) == {"i", "a"}

DIFF_TARGETS = {"easy": 100, "medium": 250, "hard": 400, "expert": 250}
DIFF_ORDER = ["easy", "medium", "hard", "expert"]
# adversarial (trap line appended to reasoning) probability per difficulty
TRAP_PROB = {"easy": 0.0, "medium": 0.30, "hard": 0.60, "expert": 0.75}
# reasoning sentence counts per difficulty (final total incl. trap <= 7)
SENT_N = {"easy": lambda r: 3, "medium": lambda r: r.choice([3, 4]),
          "hard": lambda r: r.choice([4, 5, 6]), "expert": lambda r: r.choice([5, 6])}


def per_cat_quotas():
    """divmod each difficulty across 36 cats; seeded remainder assignment."""
    quotas = {cat: {} for cat in CATS}
    r = random.Random(42660)
    for diff in DIFF_ORDER:
        total = DIFF_TARGETS[diff]
        base, rem = divmod(total, len(CATS))
        cats = list(CATS)
        r.shuffle(cats)
        for i, cat in enumerate(cats):
            quotas[cat][diff] = base + (1 if i < rem else 0)
    for cat in CATS:
        assert sum(quotas[cat].values()) >= 20
    return quotas


def fillers(rng):
    proj = rng.choice(PROJECTS)[0]
    return {
        "proj": proj,
        "goal": rng.choice(DGOALS),
        "constraint": rng.choice(CONSTRAINTS),
        "boundary": rng.choice(BOUNDARIES),
        "obs": rng.choice(DOBS),
        "risk": rng.choice(RISKS),
        "area": rng.choice(AREAS),
        "question": rng.choice(QUESTIONS),
    }


STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
can could would should must do does did have has had if because while when where which who
what why how state agent proj project user user's task tasks repo repository request
next right wrong done fix fixing need needs plan plans planned decompose decomposition
subtask subtasks goal given which order into under over between""".split())
SIM_THRESHOLD = 0.58
ANS_SIM_THRESHOLD = 0.92


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


SLOT_RE = re.compile(r"\{(\w+)\}")
CONTEXT_SENTENCES = [
    "The environment note says: {constraint}.",
    "The relevant boundary here is {boundary}.",
    "A recorded observation for this project: {obs}.",
    "The dominant risk on file is {risk}.",
    "The affected area is {area}.",
    "Stakeholders keep asking: {question}",
    "The architecture constraint on record: {constraint}.",
    "A second fact on file: {obs}.",
]
ANSWER_TAILS = [
    "Applied to '{goal}', this order is what keeps the plan executable instead of aspirational.",
    "With the constraint that {constraint}, skipping this ordering converts discipline into rework.",
    "At the boundary of {boundary}, these subtasks are what keep the two sides honest.",
    "Given the risk of {risk}, each subtask above carries its evidence before its optimism.",
    "Because the record shows that {obs}, the plan sequences verification before celebration.",
    "In {area}, this decomposition is the difference between governed change and hopeful change.",
    "For '{goal}', the subtasks above are sized by evidence, not by enthusiasm.",
    "This is the test '{goal}' applies to every candidate subtask: owned, verifiable, sequenced.",
    "The plan holds because it treats {risk} as an input to the calendar, not a surprise for it.",
    "Where {constraint} binds, the order above is what keeps the work reversible until proven.",
    "Across {boundary}, each subtask names its witness so neither side drifts on memory.",
    "For {area}, '{goal}' becomes schedulable only when these subtasks own their evidence.",
    "Because the needed data may not be exposed yet, the first subtask verifies that gap before any build.",
    "Where assumptions have been standing in for facts, the plan converts each into an explicit question with an owner.",
    "Given how much of '{goal}' depends on unstated information, recognizing the unknowns outranks writing code.",
]


def build_instruction(frame, f, rng):
    base = frame["i"]
    slots = set(SLOT_RE.findall(base))
    instr = base.format(**f)
    need = max(0, 4 - len(slots))
    if need:
        ctxs = CONTEXT_SENTENCES[:]
        rng.shuffle(ctxs)
        added = 0
        for c in ctxs:
            cslots = set(SLOT_RE.findall(c))
            if any(f[s] in instr for s in cslots):
                continue  # context would duplicate filler already in the instruction
            instr = instr + " " + c.format(**f)
            added += 1
            if added >= need:
                break
    return instr


def build_answer(frame, f, rng, rs_lines):
    base = frame["a"].format(**f)
    tails = ANSWER_TAILS[:]
    rng.shuffle(tails)
    tail = None
    for t in tails:
        txt = t.format(**f)
        if txt.rstrip(".") not in base:
            tail = txt
            break
    anchor = base
    while anchor in base:
        anchor = rng.choice(rs_lines)
    parts = [p for p in (tail, anchor) if p]
    rng.shuffle(parts)
    return base + " " + " ".join(parts)


def build_reasoning(lines, rng, difficulty, trap_pool):
    n = SENT_N[difficulty](rng)
    use_trap = rng.random() < TRAP_PROB[difficulty]
    if use_trap:
        n = min(n, 6)
    idx = list(range(len(lines)))
    rng.shuffle(idx)
    parts = [lines[i] for i in idx[:n]]
    if use_trap:
        parts.append(rng.choice(trap_pool))
    return " ".join(parts), use_trap


def main():
    rng = random.Random(20260918)
    quotas = per_cat_quotas()
    samples = []
    used_instr = set()
    used_ans = set()
    kept_words = []
    cat_ans_words = collections.defaultdict(list)
    trap_count = 0
    for ci, cat in enumerate(CATS):
        spec = CATS[cat]
        local_rng = random.Random(83770 + ci)
        slots = [d for d in DIFF_ORDER for _ in range(quotas[cat][d])]
        local_rng.shuffle(slots)
        frames = list(range(len(spec["frames"])))
        local_rng.shuffle(frames)
        cycle = frames * 4  # enough for >=29 non-expert slots
        fi_ptr = 0
        used_combo = set()
        for diff in slots:
            if diff == "expert":
                frame, fkey = D2X[cat], ("X",)
            else:
                frame = spec["frames"][cycle[fi_ptr]]
                fkey = (cycle[fi_ptr],)
                fi_ptr += 1
            instr = ans = None
            for _ in range(3000):
                f = fillers(local_rng)
                combo = (fkey, f["proj"], f["goal"], f["constraint"])
                if combo in used_combo:
                    continue
                cand = build_instruction(frame, f, local_rng)
                if cand in used_instr:
                    continue
                cw = words(cand)
                if any(jaccard(cw, kw) > SIM_THRESHOLD for kw in kept_words):
                    continue
                cand_ans = build_answer(frame, f, local_rng, spec["rs"])
                if cand_ans in used_ans:
                    continue
                aw = words(cand_ans)
                if any(jaccard(aw, ow) > ANS_SIM_THRESHOLD for ow in cat_ans_words[cat]):
                    continue
                instr, ans = cand, cand_ans
                kept_words.append(cw)
                cat_ans_words[cat].append(aw)
                used_combo.add(combo)
                break
            assert instr is not None, (cat, diff)
            used_instr.add(instr)
            used_ans.add(ans)
            reasoning, used_trap = build_reasoning(spec["rs"], local_rng, diff, spec["t"])
            trap_count += used_trap
            sc = sentence_count(reasoning)
            assert 3 <= sc <= 7, (cat, diff, sc)
            for v in (instr, ans, reasoning):
                assert v.isascii() and '"' not in v, v
            samples.append({
                "instruction": instr, "reasoning": reasoning, "answer": ans,
                "category": cat, "difficulty": diff,
            })
    instrs = [s["instruction"] for s in samples]
    assert len(set(instrs)) == len(instrs) == 1000, (len(samples), len(set(instrs)))
    assert len({s["answer"] for s in samples}) == 1000
    cats = collections.Counter(s["category"] for s in samples)
    diffs = collections.Counter(s["difficulty"] for s in samples)
    assert dict(diffs) == DIFF_TARGETS or all(diffs[d] == DIFF_TARGETS[d] for d in DIFF_TARGETS), dict(diffs)
    print("categories:", len(cats), "per-cat min/max:", min(cats.values()), max(cats.values()))
    print("difficulty:", {d: diffs[d] for d in DIFF_ORDER})
    print("adversarial (trap) samples:", trap_count, f"({trap_count/10:.1f}%)")
    out = Path(__file__).parent / "../level_8_2_deep_task_decomposition_web.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=True) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
