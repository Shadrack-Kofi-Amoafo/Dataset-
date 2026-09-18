#!/usr/bin/env python3
"""Emitter for Phase 8.2 task-decomposition web dataset (1,000 samples, 25 categories, 40 each)."""
import json, random, re, collections
from dpools import PROJECTS, ERRORS, DGOALS, DPLAN_ITEMS, DOBS, DNEW_FACTS, DHARD, DTOPICS, AREAS
from dframes_1 import DCATS_1
from dframes_2 import DCATS_2
from dframes_3 import DCATS_3
from dframes_4 import DCATS_4
from dframes_5 import DCATS_5
from dframes_hard import DCATS_HARD

CATS = {}
for src in (DCATS_1, DCATS_2, DCATS_3, DCATS_4, DCATS_5):
    CATS.update(src)
assert len(CATS) == 25

ROUNDS_TOTAL = 40
DIFF_MULTISET = [1] * 4 + [2] * 8 + [3] * 14 + [4] * 10 + [5] * 4  # 40 per category


def fillers(rng):
    proj, lang, files = rng.choice(PROJECTS)
    obs = rng.choice(DOBS)
    obs2 = obs
    while obs2 == obs:
        obs2 = rng.choice(DOBS)
    return {
        "proj": proj, "lang": lang, "files": files,
        "goal": rng.choice(DGOALS),
        "obs": obs, "obs2": obs2,
        "err": rng.choice(ERRORS),
        "hyp": rng.choice(DOBS),
        "hyp2": rng.choice(DOBS),
        "done": rng.choice(DPLAN_ITEMS),
        "res": rng.choice(DNEW_FACTS),
        "detail": rng.choice(DNEW_FACTS),
        "hard": rng.choice(DHARD),
        "topic": rng.choice(DTOPICS),
        "area": rng.choice(AREAS),
        "plan": rng.choice(DPLAN_ITEMS),
        "newfact": rng.choice(DNEW_FACTS),
    }


STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
can could would should must do does did have has had if because while when where which who
what why how state agent agent's proj project user user's task tasks repo repository request
next right wrong done fix fixing need needs plan plans planned decompose decomposition
subtask subtasks goal for given which order""".split())
SIM_THRESHOLD = 0.58


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


SLOT_RE = re.compile(r"\{(\w+)\}")
CONTEXT_SENTENCES = [
    "The repository note records that {obs2}.",
    "The plan under discussion already contains '{plan}'.",
    "A second observation on file is that {obs2}.",
    "The twist attached to this task: {hard}.",
    "An earlier assumption being questioned: {newfact}.",
]

REQ_TAILS = [
    "Here that principle applies directly to decomposing '{goal}'.",
    "In this goal's case, it decides what the plan keeps and what it cuts.",
    "Applied to '{goal}', this is what makes the plan executable rather than aspirational.",
    "For '{goal}' specifically, this is the test each candidate subtask must pass.",
]
GENERIC_TAILS = [
    "Applied beside the observation that {obs}, the principle decides the plan's shape.",
    "With the complication that {hard}, this is what makes the plan defensible.",
    "In a plan already containing '{plan}', this is how the cut gets made.",
    "Given the finding that {newfact}, the principle keeps the plan honest.",
]


def build_instruction(frame, f, rng):
    base = frame["i"]
    slots = set(SLOT_RE.findall(base))
    instr = base.format(**f)
    if len(slots) < 3:
        instr = instr + " " + rng.choice(CONTEXT_SENTENCES).format(**f)
    return instr


def build_answer(frame, f, rng):
    raw = frame["a"]
    if "{" in raw:
        return raw.format(**f)
    if "{goal}" in frame["i"]:
        return raw + " " + rng.choice(REQ_TAILS).format(goal=f["goal"])
    return raw + " " + rng.choice(GENERIC_TAILS).format(**f)


def build_reasoning(lines, rng, difficulty, trap_pool, use_trap):
    n = 3 if difficulty <= 2 else rng.choice([4, 5])
    idx = list(range(len(lines)))
    rng.shuffle(idx)
    parts = [lines[i] for i in idx[:n]]
    if use_trap:
        parts.append(rng.choice(trap_pool))
    return " ".join(parts)


def main():
    rng = random.Random(20250917)
    samples = []
    used_instr = set()
    used_ans = set()
    kept_words = []
    for ci, cat in enumerate(CATS):
        spec = CATS[cat]
        local_rng = random.Random(97030 + ci)
        diffs = DIFF_MULTISET[:]
        local_rng.shuffle(diffs)
        combos = [(fi, r) for r in range(5) for fi in range(len(spec["frames"]))]
        assert len(combos) == len(diffs) == 40, (cat, len(combos))
        used_proj_frame = set()
        for (fi, r), diff in zip(combos, diffs):
            frame = DCATS_HARD[cat][0] if diff == 5 else spec["frames"][fi]
            instr = ans = None
            fkey = ("H",) if diff == 5 else (fi,)
            for _ in range(500):
                f = fillers(local_rng)
                if (fkey, f["proj"], f["goal"]) in used_proj_frame:
                    continue
                cand = build_instruction(frame, f, local_rng)
                if cand in used_instr:
                    continue
                cw = words(cand)
                if any(jaccard(cw, kw) > SIM_THRESHOLD for kw in kept_words):
                    continue
                cand_ans = build_answer(frame, f, local_rng)
                if cand_ans in used_ans:
                    continue
                instr, ans = cand, cand_ans
                kept_words.append(cw)
                used_proj_frame.add((fkey, f["proj"], f["goal"]))
                break
            assert instr is not None, (cat, fi, r, diff)
            used_instr.add(instr)
            used_ans.add(ans)
            use_trap = diff >= 3 and local_rng.random() < 0.45
            reasoning = build_reasoning(spec["rs"], local_rng, diff, spec["t"], use_trap)
            sc = sentence_count(reasoning)
            assert 3 <= sc <= 7, (cat, sc)
            for v in (instr, ans, reasoning):
                assert v.isascii() and '"' not in v, v
            samples.append({
                "instruction": instr, "reasoning": reasoning, "answer": ans,
                "category": cat, "difficulty": diff,
            })
    instrs = [s["instruction"] for s in samples]
    assert len(set(instrs)) == len(instrs) == 1000, (len(samples), len(set(instrs)))
    cats = collections.Counter(s["category"] for s in samples)
    diffs = collections.Counter(s["difficulty"] for s in samples)
    print("categories:", len(cats), "per-cat:", set(cats.values()), "total:", sum(cats.values()))
    print("difficulty:", dict(sorted(diffs.items())))
    out = "../level_8_2_task_decomposition_web.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=True) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
