#!/usr/bin/env python3
"""Post-processor for the final JSONL (run after build.py).

Reproducibly applies:
  1. Reasoning sentence-form normalization: semicolon/colon-joined clauses and
     clause-joiners (", so", ", while", ", whereas", colon-before-full-clause)
     are promoted to real sentences whenever a reasoning has < 3 sentences.
  2. Authored-content glitch fixes (missing conjunction; compacted em-dash
     codas split into sentences for the 8 long single-sentence reasonings).

Reads dataset_gen/repository_understanding_dataset.jsonl, writes it back plus
the deliverable copy at data/phase8/repo/level_8_3_repository_understanding.jsonl.
Idempotent. Prints a sentence-count histogram.
"""
import json
import re
from collections import Counter

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "dataset_gen", "repository_understanding_dataset.jsonl")
DST = os.path.join(ROOT, "data", "phase8", "repo", "level_8_3_repository_understanding.jsonl")


def sent_count(r: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'0-9])", r.strip())
    return len([p for p in parts if p.strip()])


def promote(r: str) -> str:
    out = []
    i = 0
    while i < len(r):
        ch = r[i]
        if ch == ";" and i + 2 < len(r) and r[i+1] == " " and r[i+2].islower():
            out.append(". " + r[i+2].upper()); i += 3; continue
        if ch == ":" and i + 2 < len(r) and r[i+1] == " " and r[i+2].islower():
            out.append(". " + r[i+2].upper()); i += 3; continue
        matched = False
        for pat, tag in ((", so ", "So"), (", while ", "While"), (", whereas ", "Whereas")):
            if r.startswith(pat, i) and i+len(pat) < len(r) and r[i+len(pat)].islower():
                out.append(". " + tag + " "); i += len(pat); matched = True; break
        if matched:
            continue
        if ch == ":" and i + 2 < len(r) and r[i+1] == " " and r[i+2] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ"\'':
            rest = r[i+2:]
            if len(rest.split()) >= 4:
                out.append(". "); i += 2; continue
        out.append(ch); i += 1
    return "".join(out)


SUBSTRING_FIXES = [
    ("without application fanfare ORMs sometimes mask it",
     "without application fanfare, and ORMs sometimes mask it"),
    ("constraints) plus what entity-model replacement guest-ness needs",
     "constraints). It also maps what entity-model replacement guest-ness needs"),
    (" — treating the report as era-indexed evidence",
     ". It treats the report as era-indexed evidence"),
    ("; Android-specific bugs implicate adapter diffing",
     ". Android-specific bugs implicate adapter diffing"),
    ("strings) while explicitly RETAINING still-valid edges",
     "strings). The revision explicitly retains still-valid edges"),
    ("; .gitignore encodes the repo's own list",
     ". The .gitignore file encodes the repo's own list"),
    (" — the two classic pitfalls are TZ ambiguity",
     ". The two classic pitfalls are TZ ambiguity"),
    (" — error messages are near-unique fingerprints",
     ". Error messages are near-unique fingerprints"),
    (" — decoupling the API's behavior from the UI",
     ". This decouples the API's behavior from the UI"),
]


def main() -> None:
    objs = [json.loads(l) for l in open(SRC, encoding="utf-8").read().strip().split("\n")]
    promoted = 0
    for o in objs:
        if sent_count(o["reasoning"]) < 3:
            r1 = promote(o["reasoning"])
            if r1 != o["reasoning"]:
                o["reasoning"] = r1
                promoted += 1
    fixed = 0
    for o in objs:
        for old, new in SUBSTRING_FIXES:
            if old in o["reasoning"]:
                o["reasoning"] = o["reasoning"].replace(old, new)
                fixed += 1
    text = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n"
    open(SRC, "w", encoding="utf-8").write(text)
    open(DST, "w", encoding="utf-8").write(text)
    hist = Counter(sent_count(o["reasoning"]) for o in objs)
    print(f"promoted {promoted}, glitch-fixed {fixed}, wrote {len(objs)} lines")
    print("reasoning sentences:", dict(sorted(hist.items())))


if __name__ == "__main__":
    main()
