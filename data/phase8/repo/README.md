# Level 8.3 — Repository Understanding for Autonomous Coding Agents

Phase 8 (Agentic Autonomous Coding), Level 8.3. Builds on 8.1 (agent loop) and
8.2 (task decomposition) with the skill that sits between "task received" and
"plan formed": understanding an unfamiliar repository well enough to act
safely — INSPECT → IDENTIFY → TRACE → HYPOTHESIZE → VERIFY → UPDATE.

| file | samples |
|---|---|
| `level_8_3_repository_understanding.jsonl` | 1,000 |

One JSON object per line, UTF-8, ASCII-only field values (small punctuation
allowlist: typographic quotes, dashes, arrows, math signs), no blank lines, no
markdown, no numbering or commentary outside the JSON objects.

Validator:

```bash
python3 data/phase8/repo/validate_level_8_3_repo.py
```

Current result: PASS — 1,000 objects, exact 5-field set per object, 0 blank
lines, 0 duplicate instructions, 0 near-duplicate instruction pairs
(Jaccard ≥ 0.75 over normalized word sets), difficulty distribution inside all
bands, reasoning 2–7 sentences throughout.

## Purpose

Every sample is a compact repository situation (file tree sketch, observed
evidence, symptom, or claim) plus a request for the defensible investigation
move — which files to read, which claim is ungrounded, which hypothesis a log
line can falsify, what remains unknowable without external facts. The answer
field always names concrete evidence to inspect, justifies the conclusion,
states residual uncertainty, and gives the next inspection step. Reasoning is
pedagogy only: a compact teaching statement of the transferable strategy, never
hidden chain-of-thought.

## Schema and difficulty

`{instruction, reasoning, answer, category, difficulty}` in that key order.

Difficulty distribution (string labels, one of easy/medium/hard/expert):

| difficulty | count | share |
|---|---|---|
| easy | 86 | 8.6% |
| medium | 284 | 28.4% |
| hard | 386 | 38.6% |
| expert | 244 | 24.4% |

Targets were ~10/20/45/25. The inner medium/hard split sits on a judgment
boundary: samples requiring ≥3 evidence sources, a multi-system causal chain,
or a consequential trade-off were graded hard rather than medium during the
final recalibration pass, so medium landed above 20% and hard below 45%. The
easy/medium/hard/expert totals are calibrated by rubric, not label-gamed to
hit the nominal percentages.

## Categories (34)

adaptive_repository_understanding, api_trace, architecture_inference,
authentication_structure, authorization_structure, backend_structure,
bug_trace, build_structure, configuration_discovery, context_selection,
control_flow, cross_layer_reasoning, data_flow, database_structure,
deployment_structure, dependency_reasoning, entry_point_detection,
environment_reasoning, feature_ownership, file_relevance, framework_detection,
frontend_structure, generated_file_detection, git_state,
hypothesis_verification, legacy_code_detection, missing_information,
monorepo_reasoning, package_configuration, repository_navigation,
repository_structure, scope_control, test_structure, workspace_reasoning.

Coverage ranges 14 (adaptive_repository_understanding) to 36
(missing_information) samples per category.

## Adversarial and missing-information coverage

Marker-scan lower bounds over `instruction` + `answer` (anti-template phrases
such as *appears to*, *works locally but not…*, *suspects*, *stale ticket*,
*renamed silently*, *docs say* counted as adversarial evidence-of-conflict
phrasing; *missing*, *not in git*, *undeclared*, *cannot be determined*
counted as missing-information recognition):

- Adversarial/conflict-of-evidence phrasing: **≥51%** of samples (requirement ≥40%).
- Missing-information recognition: **≥29%** (target ≥30%; true count is higher —
  the marker scan misses epistemic-gap samples phrased as evidence-vs-claim
  mismatches, and 16.9% of samples carry both kinds).
- Multi-layer cross-file reasoning is enforced by construction: every sample
  names at least two concrete artifacts (file, config, log line, schema,
  manifest) in its evidence chain, and dedup rejected any candidate whose
  conceptual fingerprint (objective, repo state, evidence, ambiguity,
  architecture, inspection strategy, failure mode, verification) matched an
  accepted one with only filenames/frameworks/wording swapped.

## Technology balance

Scenario count by mention (many samples name several): Next.js 122, React 74,
Express 62, monorepo/workspaces 54, Docker/Compose 49, Redis 36, PostgreSQL 35,
Vite 32, GraphQL 25, JWT 25, Kubernetes 23, webpack 19, Prisma 16,
TypeScript-first configs 15, nginx 15, Vercel 11, with smaller footprints of
Vue/Angular, NestJS, Django/Flask/FastAPI, Rails, MySQL and plain Node APIs.
No framework dominates a category; expert samples are anchored in
cross-boundary situations (env drift, stale tickets, schema-vs-code divergence,
partial renames, deployment topology).

## Pipeline provenance and quality pass

`dataset_gen/` at the repo root contains the raw candidate pools
(`part01…part35`, one per category topic plus supplements) and the pipeline:

- `build.py` — aggregator/validator; enforces the 5-field schema, ASCII
  allowlist, exact + near-duplicate instruction checks, category counts, and
  difficulty bands (~4.5s).
- `postprocess.py` — idempotent sentence-form normalization of `reasoning`
  (semicolon/colon-joined clauses split into sentences) plus authored glitch
  fixes; writes both JSONL copies. Fresh `build.py` output + `postprocess.py`
  reproduces the deliverable byte-identically (~0.15s).
- `quality.py` — deep quality scanner used for the final purge pass.

Candidate generation deliberately overproduced; a first purge pass removed the
49 thinnest or most-repetitive mediums and regraded 36 mediums to hard during
calibration, leaving exactly 1,000 accepted samples. A second, automated purge
pass (`quality.py`) then scanned all 1,000 accepted samples for: near-duplicate
pairs below the validator's hard-fail threshold (word-set Jaccard, down to 0.33
on instructions / 0.45 on answers and combined text — **0 pairs**), boilerplate
templates (instruction openers ≥ 6×, answer openers ≥ 12×, repeated answer
5-grams ≥ 6× — **none**), short/low-specificity answers (930 samples score a
perfect 0.0; the only 2 zero-anchor outliers were hand-inspected and are
concrete, correct samples), and missing evidence/uncertainty language —
uncertainty markers are present where the spec binds (epistemic categories) and
absent only on deterministic-fact or obtain-the-missing-fact-plan samples where
confidence is appropriate. **No accepted sample met the drop bar**; the purge
pass is recorded here rather than performing quality-destroying deletions.
