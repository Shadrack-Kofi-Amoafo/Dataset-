# Level 8.4 — Tool & Terminal Use (Web Development Specialization)

Phase 8 (Agentic Autonomous Coding), Level 8.4. Where 8.1 covers the agent loop,
8.2 decomposition and 8.3 repository understanding, this level trains the layer
that actually touches the machine: **selecting, executing and interpreting tools**
while working on real web-development repositories.

Loop taught throughout: **UNDERSTAND → SELECT TOOL → INSPECT → ACT →
INTERPRET OUTPUT → VERIFY → CONTINUE OR RECOVER**.

| file | samples |
|---|---|
| `level_8_4_tool_terminal_use_web.jsonl` | 1,000 |

One JSON object per line, UTF-8, ASCII-only field values, no markdown, no blank
lines, no numbering or commentary outside the JSON objects. Keys in this order:
`{"instruction","reasoning","answer","category","difficulty}` — exactly five
fields per object.

## Validation

```bash
python3 data/phase8/tools/validate_level_8_4_tools_web.py
```

Current result: **PASS** — 1,000 objects; bare-object JSON on every line; exact
5-field set and key order; all categories and difficulties in the allowed sets;
difficulty bands inside limits; reasoning 3–5 sentences everywhere (target was
3–6); minimum field lengths; ASCII policy; **0 duplicate instructions,
0 near-duplicate instruction pairs (word-set Jaccard ≥ 0.62), 0 overlapping
sample pairs (5-gram shingle containment ≥ 0.45)** across all 1000 objects.

## Purpose and design

Every sample is a compact tool-use situation inside a web project — a command
and its output, an environment fact, a symptom reported in one layer and
observed in another — plus a request for the defensible next action. Answers
name the concrete inspection, the tool choice with its justification, the
interpretation the evidence supports (and what it does *not* support), and a
verification step. Reasoning is pedagogy only: a compact statement of the
transferable discipline, never hidden chain-of-thought.

The corpus encodes the epistemics required by the brief: tool output is
evidence not truth; commands must match the repository and environment;
destructive actions need attribution and preview; failure triggers diagnosis
rather than repetition; exit status is not task success; and important changes
are verified from an independent observation.

## Distributions

Difficulty (string labels):

| difficulty | count | share |
|---|---|---|
| easy | 57 | 5.7% |
| medium | 266 | 26.6% |
| hard | 395 | 39.5% |
| expert | 282 | 28.2% |

Categories (26), counts: tool_selection 40, terminal_reasoning 40,
shell_command_reasoning 40, file_inspection 38, file_search 38,
safe_file_modification 38, git_operations 40, package_manager_reasoning 40,
dependency_installation 34, process_management 34, port_diagnostics 34,
server_execution 34, build_tool_reasoning 35, test_runner_usage 36,
browser_devtools 42, network_inspection 46, api_testing 42, database_cli 34,
log_analysis 47, environment_configuration 37, tool_output_interpretation 40,
command_failure_recovery 40, tool_result_verification 31, safe_tool_use 40,
multi_tool_workflow 40, adaptive_tool_selection 40.

Average length: instruction 32 words, reasoning 55 words, answer 80 words
(1.14 MB total) — denser than 8.3 because tool-use answers are command-level.

## Coverage of the required proportions

Marker scans over `instruction` + `answer` give lower bounds; the engineered
shares (author flags set during candidate drafting) are the true design
targets. Both are reported because conceptual traps are frequently phrased
without any literal marker.

| requirement | marker-scan lower bound | engineered share |
|---|---|---|
| adversarial traps / misleading tool results (≥40%) | **52.4%** | 76.3% |
| interpreting unexpected output or recovering from failure (≥30%) | **79.5%** | 76.9% (adversarial ∪ recovery) |
| choosing among multiple plausible tools or actions (≥30%) | **73.4%** | 29.7% framed as explicit competing-tool selection, plus every `tool_selection` / `adaptive_tool_selection` sample (80) where selection is the whole question |

Missing-information recognition (`missing`, `cannot be determined`, `not
recorded`, `unverifiable`, …) floors at **14.7%** by scan; more samples phrase
the epistemic gap as "the evidence supports X but not Y" without those words.

## Semantic deduplication

Each sample is built around a distinct *underlying tool-use problem*, not a
distinct command string: the corpus contains no framework-swapped twins (e.g.
only one lockfile-drift reasoning, one port-ownership attribution, one
buffering-vs-hang discrimination, one `--force-with-lease` safety argument).
Deduplication was enforced twice: (1) during authoring, candidates were
rejected if their objective, evidence shape, ambiguity, tool comparison and
failure mode matched an accepted sample; (2) automatically, the validator
reports 0 near-duplicate instruction pairs at Jaccard ≥ 0.62 and 0 sample pairs
with 5-gram shingle containment ≥ 0.45 (thresholds well below the levels where
paraphrase duplicates appear — the closest pair in the corpus is far under them).

## Technology balance

Mentions per technology across instruction + answer (samples name several):
git 151, environment/config files 144, CI pipelines 108, shell text tools
(`sed`/`awk`/`grep`/`rg`) 102, browser DevTools 79, npm 70, make/build tooling
68, SQL & database CLIs 58, Docker/Compose 51, Node runtime 40, socket
inspection (`ss`/`lsof`) 36, `curl` 33, Python/Rails/other stacks 20,
monorepo workspaces 17, Express 14, `jq` 13, PostgreSQL/`psql` 12,
OS/platform differences 12, TypeScript/`tsc` 10, pnpm 8, systemd 8, Vite 7,
test runners 6, Kubernetes 5, Redis 3, nginx 3, Prisma 3, webpack 2.

This is deliberate: the level is about tool reasoning, so no framework is a
precondition for any sample, and swapping a framework never changes the answer.

## Pipeline provenance

`cand/c01.jsonl … cand/c54.jsonl` hold the authored candidate chunks
(one JSON object per line, plus an internal `_f` flag recording
adversarial / competing-tool-choice / recovery design intent). The pipeline:

- `build_8_4.py` — aggregator + gatekeeper: drops the internal flag field,
  normalizes whitespace, splits over-long reasoning clauses into sentences so
  reasoning reads as 3–5 sentences, enforces the 5-field schema, ASCII policy,
  category/difficulty sets, exact-duplicate rejection and category minimums,
  then writes the deliverable. Idempotent: re-running reproduces the file
  byte-identically.
- `validate_level_8_4_tools_web.py` above — independent validator with the
  near-duplicate and coverage audits.

Overproduction was not needed: candidates were authored against per-category
topic ledgers with explicit dedup keys, so the acceptance rate is high while
the automated audits still report zero duplicates. Weak or redundant drafts
were deleted at authoring time rather than admitted and re-labelled.
