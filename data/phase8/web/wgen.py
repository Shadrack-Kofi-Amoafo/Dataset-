#!/usr/bin/env python3
"""Emitter for Phase 8.1 web-specialization dataset (1,000 samples, 35 categories)."""
import json, random, re, sys, collections
from wpools import WPROJECTS, WREQUESTS, WOBSERVATIONS, WERRORS, WACTIONS_DONE, WRESULTS, WHYPOTHESES, WDETAILS, WHARD, WTOPICS
from wframes_1 import WCATS_1
from wframes_2 import WCATS_2
from wframes_3 import WCATS_3
from wframes_4 import WCATS_4
from wframes_5 import WCATS_5
from wframes_hard import WCATS_HARD

CATS = {}
for src in (WCATS_1, WCATS_2, WCATS_3, WCATS_4, WCATS_5):
    CATS.update(src)
CAT_ORDER = list(CATS)
NCAT = len(CAT_ORDER)
assert NCAT == 35

DIFF_TARGETS = {1: 100, 2: 200, 3: 350, 4: 250, 5: 100}


def fillers(rng):
    proj, lang, files = rng.choice(WPROJECTS)
    return {
        "proj": proj, "lang": lang, "files": files,
        "req": rng.choice(WREQUESTS),
        "obs": rng.choice(WOBSERVATIONS),
        "obs2": rng.choice(WOBSERVATIONS),
        "err": rng.choice(WERRORS),
        "hyp": rng.choice(WHYPOTHESES),
        "hyp2": rng.choice(WHYPOTHESES),
        "done": rng.choice(WACTIONS_DONE),
        "res": rng.choice(WRESULTS),
        "detail": rng.choice(WDETAILS),
        "hard": rng.choice(WHARD),
        "topic": rng.choice(WTOPICS),
    }


STOPWORDS = set("""a an the of to in and or is are was were be been being for with on at by from
that this these those it its as than then so such not no nor more most some any all each
can could would should must do does did have has had if because while when where which who
what why how state agent agent's proj project user user's task repo repository request
next right wrong done fix fixing need needs""".split())
SIM_THRESHOLD = 0.60


def words(text):
    return {w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS}


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def sentence_count(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


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


def build_answer(frame, f, rng):
    raw = frame["a"]
    if "{" in raw:
        return raw.format(**f)
    if "{req}" in frame["i"]:
        req = f["req"]
        req_l = req[0].lower() + req[1:]
        return raw + " " + rng.choice(REQ_TAILS).format(req=req, req_l=req_l)
    return raw + " " + rng.choice(GENERIC_TAILS).format(**f)


def build_reasoning(lines, rng, difficulty, trap_pool, use_trap):
    n = 3 if difficulty <= 2 else rng.choice([4, 5])
    idx = list(range(len(lines)))
    rng.shuffle(idx)
    parts = [lines[i] for i in idx[:n]]
    if use_trap:
        parts.append(rng.choice(trap_pool))
    return " ".join(parts)


def diff_quotas(target):
    q, rem = divmod(target, NCAT)
    return [q + 1 if i < rem else q for i in range(NCAT)]


def main():
    rng = random.Random(80808)
    samples = []
    used_instr = set()
    used_ans = set()
    kept_words = []
    quota_by_diff = {d: diff_quotas(t) for d, t in DIFF_TARGETS.items()}
    for ci, cat in enumerate(CAT_ORDER):
        spec = CATS[cat]
        local_rng = random.Random(43100 + ci)
        diffs = []
        for d in (1, 2, 3, 4, 5):
            diffs += [d] * quota_by_diff[d][ci]
        local_rng.shuffle(diffs)
        n_cat = len(diffs)
        combos = [(fi, r) for r in range(6) for fi in range(len(spec["frames"]))][:n_cat]
        assert len(combos) == n_cat, (cat, len(combos), n_cat)
        used_proj_frame = set()
        for (fi, r), diff in zip(combos, diffs):
            frame = WCATS_HARD[cat][0] if diff == 5 else spec["frames"][fi]
            instr = ans = None
            fkey = ("H",) if diff == 5 else (fi,)
            for _ in range(500):
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
                "instruction": instr,
                "reasoning": reasoning,
                "answer": ans,
                "category": cat,
                "difficulty": diff,
            })
    instrs = [s["instruction"] for s in samples]
    assert len(set(instrs)) == len(instrs) == 1000, (len(samples), len(set(instrs)))
    cats = collections.Counter(s["category"] for s in samples)
    diffs = collections.Counter(s["difficulty"] for s in samples)
    print("categories:", len(cats), "min/max per cat:", min(cats.values()), max(cats.values()), "total:", sum(cats.values()))
    print("difficulty:", dict(sorted(diffs.items())))
    out = "level_8_1_agent_foundations_web.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=True) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
