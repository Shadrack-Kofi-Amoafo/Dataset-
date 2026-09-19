#!/usr/bin/env python3
"""Builder for Level 8.4 (Tool & Terminal Use, web specialization).

Reads authored candidate chunks (cNN.jsonl) in sorted order, drops the internal
``_f`` flag field, enforces the 5-field schema, rejects duplicate instructions,
and writes the deliverable JSONL with keys in canonical order.

Usage: python3 build_8_4.py [--dry-run]
"""
import glob
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CAND = os.path.join(HERE, "cand", "c*.jsonl")
OUT = os.path.join(HERE, "level_8_4_tool_terminal_use_web.jsonl")

FIELDS = ["instruction", "reasoning", "answer", "category", "difficulty"]
DIFFICULTIES = {"easy", "medium", "hard", "expert"}
CATEGORIES = {
    "tool_selection", "terminal_reasoning", "shell_command_reasoning",
    "file_inspection", "file_search", "safe_file_modification",
    "git_operations", "package_manager_reasoning", "dependency_installation",
    "process_management", "port_diagnostics", "server_execution",
    "build_tool_reasoning", "test_runner_usage", "browser_devtools",
    "network_inspection", "api_testing", "database_cli", "log_analysis",
    "environment_configuration", "tool_output_interpretation",
    "command_failure_recovery", "tool_result_verification", "safe_tool_use",
    "multi_tool_workflow", "adaptive_tool_selection",
}
ALLOWED_NON_ASCII = set("\u2019\u2018\u201c\u201d\u2014\u2013\u2026\u00a7\u00d7\u2192\u2190\u2265\u2264\u00b1")


def key(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()


MIN_CLAUSE = 42


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def split_clause(text: str, marker: str, minimum: int = MIN_CLAUSE, repl: str = None):
    """Split the longest sentence in `text` at `marker`, optionally replacing the
    marker with `repl` so the continuation stays grammatical."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    idx = max(range(len(parts)), key=lambda i: len(parts[i]))
    s = parts[idx]
    pat = marker.strip()
    pos, tail = None, None
    for m in re.finditer(re.escape(pat), s):
        left, right = s[: m.start()], s[m.end():].strip()
        if repl:
            right = f"{repl} {right}"
        if len(left) >= minimum and len(right) >= minimum:
            pos, tail = m.start(), right
            break
    if pos is None:
        return None
    left = s[:pos].rstrip(",; ").rstrip() + "."
    right = tail.strip().rstrip(".")
    if not re.search(r"[.!?]$", right):
        right += "."
    parts[idx] = left + " " + _cap(right)
    return " ".join(parts)


def cleanup(t: str) -> str:
    t = re.sub(r"\. And ([a-z])", lambda m: ". " + m.group(1).upper(), t)
    t = re.sub(r"\. But ([a-z])", lambda m: ". However, " + m.group(1), t)
    return re.sub(r"\s+", " ", t).strip()


def normalize_reasoning(text: str) -> str:
    """For reasoning that reads as too few sentences, split semicolon/colon and
    so/which clause joins into separate sentences so it reads as 3-6 short
    pedagogical sentences. Idempotent: already well-formed text is untouched."""
    text = re.sub(r"\s+", " ", text.strip())
    if text and not text.endswith((".", "!", "?")):
        text += "."

    def count(t):
        return len([p for p in re.split(r"(?<=[.!?])\s+", t.strip()) if p.strip()])

    if count(text) < 3:
        for marker, repl in ((";", None), (":", None), (", and ", "And"),
                             (", but ", "But"), (", so ", "So")):
            guard = 0
            while count(text) < 3 and guard < 8:
                nxt = split_clause(text, marker, repl=repl)
                if nxt is None or nxt == text:
                    break
                text = nxt
                guard += 1
            if count(text) >= 3:
                break

    # Readability pass: break run-on sentences, using only clause joins whose
    # continuation reads grammatically as its own sentence.
    for marker, repl in ((", and ", "And"), (", but ", "But"),
                         (", so ", "So"), (";", None), (":", None)):
        guard = 0
        while count(text) < 5 and guard < 4:
            lens = [len(s) for s in re.split(r"(?<=[.!?])\s+", text.strip())]
            nxt = split_clause(text, marker, minimum=75, repl=repl)
            if nxt is None or nxt == text:
                break
            if max(len(s) for s in re.split(r"(?<=[.!?])\s+", nxt.strip())) >= max(lens):
                break
            text = nxt
            guard += 1
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    problems = []
    objs, seen = [], set()
    for path in sorted(glob.glob(CAND)):
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"{os.path.basename(path)}:{n}: bad JSON: {e}")
                continue
            o.pop("_f", None)
            for f in FIELDS:
                if isinstance(o.get(f), str):
                    o[f] = re.sub(r"\s+", " ", o[f]).strip()
            if "reasoning" in o and isinstance(o["reasoning"], str):
                o["reasoning"] = cleanup(normalize_reasoning(o["reasoning"]))
            if list(o.keys()) != FIELDS:
                problems.append(f"{os.path.basename(path)}:{n}: fields {list(o.keys())}")
                continue
            if o["category"] not in CATEGORIES:
                problems.append(f"{os.path.basename(path)}:{n}: category {o['category']!r}")
            if o["difficulty"] not in DIFFICULTIES:
                problems.append(f"{os.path.basename(path)}:{n}: difficulty {o['difficulty']!r}")
            for f in ("instruction", "reasoning", "answer"):
                v = o[f]
                if not isinstance(v, str) or len(v.strip()) < 40:
                    problems.append(f"{os.path.basename(path)}:{n}: '{f}' too short")
                    continue
                for ch in v:
                    if ord(ch) >= 128 and ch not in ALLOWED_NON_ASCII:
                        problems.append(f"{os.path.basename(path)}:{n}: char {ch!r} in {f}")
                        break
            k = key(o["instruction"])
            if k in seen:
                problems.append(f"{os.path.basename(path)}:{n}: duplicate instruction")
            seen.add(k)
            objs.append(o)

    cats = Counter(o["category"] for o in objs)
    diffs = Counter(o["difficulty"] for o in objs)
    print(f"candidates: {len(objs)}")
    print("difficulty:", dict(diffs))
    print("categories:", len(cats))
    for c in sorted(cats):
        print(f"  {c}: {cats[c]}")
    missing = CATEGORIES - set(cats)
    if missing:
        problems.append(f"categories with no samples: {sorted(missing)}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems[:40]:
            print(" -", p)
        return 1
    if "--dry-run" in sys.argv:
        print("\ndry run: nothing written")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        for o in objs:
            fh.write(json.dumps({f: o[f] for f in FIELDS}, ensure_ascii=True) + "\n")
    print(f"\nwrote {OUT} ({len(objs)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
