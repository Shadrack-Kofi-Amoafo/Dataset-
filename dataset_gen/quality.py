#!/usr/bin/env python3
"""Deep quality scanner for the final JSONL.

Flags: (a) near-duplicate pairs in the review tier (Jaccard >= 0.55 on
instructions, >= 0.60 on answers), (b) boilerplate answer/instruction
templates repeated across many samples, (c) weak samples via a composite
score: short answers, low artifact concreteness, hedging-without-substance.
Prints a ranked candidate-drop list; does not modify files.
"""
import json
import re
from collections import Counter
from itertools import combinations

PATH = "data/phase8/repo/level_8_3_repository_understanding.jsonl"
objs = [json.loads(l) for l in open(PATH, encoding="utf-8").read().strip().split("\n")]
N = len(objs)

def words(s):
    return frozenset(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())

def ngrams(s, n):
    w = re.sub(r"[^a-z0-9]+", " ", s.lower()).split()
    return frozenset(tuple(w[i:i+n]) for i in range(len(w) - n + 1))

def jaccard(a, b):
    if not a or not b:
        return 0.0
    i = len(a & b)
    return i / (len(a) + len(b) - i)

instr_ws = [words(o["instruction"]) for o in objs]
ans_ws = [words(o["answer"]) for o in objs]
ans_5g = [ngrams(o["answer"], 5) for o in objs]
ins_5g = [ngrams(o["instruction"], 5) for o in objs]

print("=== A. Near-duplicate review tier ===")
dup_flags = Counter()
pairs_shown = 0
for i, j in combinations(range(N), 2):
    ij = jaccard(instr_ws[i], instr_ws[j])
    if ij >= 0.55:
        aj = jaccard(ans_ws[i], ans_ws[j])
        g = jaccard(ans_5g[i], ans_5g[j])
        tier = "HARD" if ij >= 0.75 else ("HIGH" if (ij >= 0.62 or (ij >= 0.55 and aj >= 0.60)) else "REVIEW")
        if tier != "REVIEW":
            dup_flags[i] += 1; dup_flags[j] += 1
        if pairs_shown < 40 and (tier != "REVIEW" or aj >= 0.55):
            print(f"[{tier}] instr {ij:.2f} ans {aj:.2f} ans5g {g:.2f} :: {i+1} vs {j+1} [{objs[i]['category'][:14]}|{objs[j]['category'][:14]}] {objs[i]['instruction'][:70]!r} ~ {objs[j]['instruction'][:70]!r}")
            pairs_shown += 1
print("hard/high dup-flagged lines:", len(dup_flags))

print("\n=== B. Boilerplate / template clustering ===")
first6 = Counter(" ".join(re.sub(r"[^a-z0-9 ]", " ", o["instruction"].lower()).split()[:6]) for o in objs)
boiler_instr = {k: v for k, v in first6.items() if v >= 6}
print("instruction first-6-word clusters >=6:", len(boiler_instr))
for k, v in sorted(boiler_instr.items(), key=lambda kv: -kv[1])[:15]:
    print(f"  {v}x {k!r}")
# answer opening boilerplate
opener = Counter(tuple(re.sub(r"[^a-z0-9 ]", " ", o["answer"].lower()).split()[:4]) for o in objs)
op_b = {k: v for k, v in opener.items() if v >= 12}
print("answer first-4-word clusters >=12:", len(op_b))
for k, v in sorted(op_b.items(), key=lambda kv: -kv[1])[:12]:
    print(f"  {v}x {' '.join(k)!r}")
# repeated rare-ish 6-grams across answers (true template text)
g_map = Counter()
for grams in ans_5g:
    for g in grams:
        g_map[g] += 1
templ = {g: c for g, c in g_map.items() if c >= 6}
print("answer 5-grams repeated in >=6 samples:", len(templ))
for g, c in sorted(templ.items(), key=lambda kv: -kv[1])[:18]:
    print(f"  {c}x {' '.join(g)[:80]!r}")

print("\n=== C. Weakness scoring ===")
ARTIFACT_PATTERNS = [
    r"[\w./-]+\.\w{1,5}\b",                       # file with extension / dotted file ends
    r"\b(?:src|app|apps|pages|server|packages|pkg|docs|tests?|spec|e2e|config|configs|dist|build|out|public|components?|containers?|routes|services|modules|api|lib|plugins|hooks|migrations|models|controllers|resolvers|middleware|utils|helpers|scripts|bin|cmd|deploy|infra|k8s|helm|charts)/[\w./-]+",  # known-dir relative path
    r"\b[a-z][\w-]*/[a-z][\w./-]+",                # any bare relative path (server/routes/v1)
    r"\b/[a-z][\w./{}:-]+",                        # absolute path or route (/api/v2/users)
    r"\b(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b",
    r"@[\w-]+/[\w.-]+",                            # scoped package
    r"\b[a-z]+_[a-z][a-z0-9_]*\b",                 # snake_case identifier (2+ segs)
    r"\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b",        # camelCase identifier
    r"\b[A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)+\b",      # PascalCase symbol
    r"\b(?:npm|npx|pnpm|yarn|node|git|curl|psql|docker|kubectl|helm|redis-cli|nc|openssl|bash|sh|python3?|pip|cargo|go)\s+[\w-]+",  # command
    r"\bv\d+\.\d+(?:\.\d+)?\b",                    # version
    r"\b[45]\d\d\b",                               # HTTP status
    r":\b\d{2,5}\b",                               # port-like
    r"\b\d+(?:ms|s|MB|GB|kb|%)\b",                 # units
    r"\bp\d\d\b|\bp99\b",                          # percentiles
    r"\b[a-z][a-z0-9_-]{2,}/",                     # bare trailing-slash dir (routes/, services/)
]
ARTIFACT = re.compile("|".join(f"(?:{p})" for p in ARTIFACT_PATTERNS))
def conc_count(text):
    return len(set(m.group(0) for m in ARTIFACT.finditer(text)))
HEDGE = re.compile(r"\b(might|maybe|perhaps|probably|possibly|likely)\b", re.I)
scores = []
for k, o in enumerate(objs):
    a, ins = o["answer"], o["instruction"]
    alen = len(a)
    conc = len(ARTIFACT.findall(a)) + len(ARTIFACT.findall(ins))
    hed = len(HEDGE.findall(a))
    because = a.lower().count("because") + a.lower().count("therefore") + a.lower().count("since ")
    score = 0.0
    score += max(0, (700 - alen)) / 700.0          # short answers penalized (up to 1.0)
    if conc == 0: score += 2.0                     # no concrete artifact anywhere
    elif conc == 1: score += 0.7
    elif conc == 2: score += 0.25
    if hed >= 4 and because == 0: score += 0.6     # hedge spam without causal anchor
    score += min(dup_flags[k], 2) * 1.5            # near-dup boost
    scores.append((score, k, o))

for g, c in templ.items():
    pass  # template text considered in clustering report above

ranked = sorted(scores, key=lambda t: -t[0])
print("line  score alen conc hedges category        difficulty  instruction")
for s, k, o in ranked[:80]:
    a, ins = o["answer"], o["instruction"]
    cc = conc_count(a) + conc_count(ins)
    hed = len(HEDGE.findall(a))
    print(f"{k+1:5d}  {s:4.2f} {len(a):5d} {cc:4d} {hed:6d} {o['category'][:14]:14s}  {o['difficulty']:6s}  {ins[:90]!r}")

# score distribution shape
buckets = Counter(round(s, 1) for s, k, o in scores)
print("\nscore histogram:", dict(sorted(buckets.items())))

# per-category weakness tally for backfill targeting
cat_weak = Counter(o["category"] for s, k, o in ranked[:150])
print("\nweak-by-category (top150):", dict(cat_weak.most_common()))
diff_weak = Counter(o["difficulty"] for s, k, o in ranked[:150])
print("weak-by-difficulty (top150):", dict(diff_weak.most_common()))
