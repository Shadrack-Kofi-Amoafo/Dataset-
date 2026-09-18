#!/usr/bin/env python3
"""Emitter for Phase 8.1 agent-foundations dataset (1,000 samples)."""
import json, random, re, sys, collections
from pools import PROJECTS, REQUESTS, OBSERVATIONS, ERRORS, ACTIONS_DONE, RESULTS, HYPOTHESES, DETAILS, HIGHER_DIFFICULTY, CLARIFY_TOPICS
from frames_a import CATS_A
from frames_b import CATS_B
from frames_c import CATS_C
from frames_d import CATS_D
from frames_hard import CATS_HARD

CATS = {}
for src in (CATS_A, CATS_B, CATS_C, CATS_D):
    CATS.update(src)

ROUNDS = 5
DIFF_MULTISET = [1] * 4 + [2] * 8 + [3] * 14 + [4] * 10 + [5] * 4  # 40 per category


def fillers(rng):
    proj, lang, files = rng.choice(PROJECTS)
    return {
        "proj": proj,
        "lang": lang,
        "files": files,
        "req": rng.choice(REQUESTS),
        "obs": rng.choice(OBSERVATIONS),
        "obs2": rng.choice(OBSERVATIONS),
        "err": rng.choice(ERRORS),
        "hyp": rng.choice(HYPOTHESES),
        "hyp2": rng.choice(HYPOTHESES),
        "done": rng.choice(ACTIONS_DONE),
        "res": rng.choice(RESULTS),
        "detail": rng.choice(DETAILS),
        "hard": rng.choice(HIGHER_DIFFICULTY),
        "topic": rng.choice(CLARIFY_TOPICS),
    }


def build_reasoning(lines, rng, difficulty, trap_pool, use_trap):
    n = 3 if difficulty <= 2 else rng.choice([4, 5])  # d1-2: 3; d3+: 4 or 5
    idx = list(range(len(lines)))
    rng.shuffle(idx)
    parts = [lines[i] for i in idx[:n]]
    if use_trap:
        parts.append(rng.choice(trap_pool))
    return " ".join(parts)


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
can could would should must do does did have has had if because while when where which who
what why how state agent agent's proj project user user's task repo repository request
next right wrong done fix fixing need needs needs""".split())
SIM_THRESHOLD = 0.60


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


REQ_TAILS = [
    "In this repository, that means checking it against the ask to {req_l} before anything else.",
    "Applied to '{req}', this keeps the one question that matters: what does observed behavior actually say?",
    "Here the concrete anchor is the request '{req}', and the principle decides how it gets handled.",
    "For '{req}' specifically, this turns a vague good intention into one checkable move.",
    "In the case of '{req}', the principle keeps action proportional to evidence.",
    "Concretely for '{req}', this is what separates an agent's judgment from a script's reflex.",
]
GENERIC_TAILS = [
    "Alongside the earlier clue that {obs}, the principle picks one sound next step instead of several shaky ones.",
    "For an ask shadowed by {err}, the agent's ledger and checks, not its enthusiasm, drive the next move.",
    "In a picture where {obs2}, the principle is what separates judgment from reflex.",
    "With the sign that {obs} on record, this turns a vague good intention into one checkable move.",
    "Given that {err} sits in the report, the principle keeps the next action proportional to evidence.",
    "Where the record shows {obs2}, continuation earns its place only through fresh evidence.",
]


SLOT_RE = re.compile(r"\{(\w+)\}")
CONTEXT_SENTENCES = [
    "The most recent observation on the board is that {obs}.",
    "The latest run also surfaced {err}.",
    "So far the working hypothesis in the room is {hyp}.",
    "Earlier in the session the agent {done}, which shaped the current picture.",
    "One extra clue under discussion is that {obs2}.",
    "A teammate mentions seeing {res} on a comparable run.",
    "The competing hunch being floated is {hyp2}.",
    "{detail}",
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
    if "{req}" in frame["i"]:
        req = f["req"]
        req_l = req[0].lower() + req[1:]
        return raw + " " + rng.choice(REQ_TAILS).format(req=req, req_l=req_l)
    return raw + " " + rng.choice(GENERIC_TAILS).format(**f)


def main():
    rng = random.Random(20260918)
    samples = []
    used_instr = set()
    used_ans = set()
    kept_words = []
    stats = collections.Counter()
    for cat, spec in CATS.items():
        local_rng = random.Random(1000 + list(CATS).index(cat))
        hard_frames = CATS_HARD[cat]
        diffs = DIFF_MULTISET[:]
        local_rng.shuffle(diffs)
        combos = [(fi, r) for r in range(ROUNDS) for fi in range(len(spec["frames"]))]
        assert len(combos) == len(diffs), (len(combos), len(diffs))
        entries = []
        for i, (fi, r) in enumerate(combos):
            frame = hard_frames[0] if diffs[i] == 5 else spec["frames"][fi]
            entries.append(((fi, r), frame, diffs[i]))
        used_proj_frame = set()
        for (fi, r), frame, diff in entries:
            instr = ans = None
            fkey = ("H",) if diff == 5 else (fi,)
            for _ in range(400):
                f = fillers(local_rng)
                if (fkey, f["proj"]) in used_proj_frame:
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
                used_proj_frame.add((fkey, f["proj"]))
                break
            assert instr is not None, (cat, fi, r)
            used_instr.add(instr)
            used_ans.add(ans)
            use_trap = diff >= 3 and local_rng.random() < 0.45
            reasoning = build_reasoning(spec["rs"], local_rng, diff, spec["t"], use_trap)
            sc = sentence_count(reasoning)
            assert 3 <= sc <= 7, (cat, sc)
            for v in (instr, ans, reasoning):
                assert v.isascii() and '"' not in v, v
            samples.append({
                "instruction": instr,
                "reasoning": reasoning,
                "answer": ans,
                "category": cat,
                "difficulty": diff,
            })
            stats[(cat, diff)] += 1
    # integrity
    instrs = [s["instruction"] for s in samples]
    assert len(set(instrs)) == len(instrs) == 1000, (len(samples), len(set(instrs)))
    cats = collections.Counter(s["category"] for s in samples)
    diffs = collections.Counter(s["difficulty"] for s in samples)
    print("category counts:", set(cats.values()), "total", sum(cats.values()))
    print("difficulty:", dict(sorted(diffs.items())))
    out = "level_8_1_agent_foundations.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=True) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
