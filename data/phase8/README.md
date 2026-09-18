# Level 8.1 — Agent Foundations

Phase 8 (Agentic Autonomous Coding), Level 8.1 of the training set.

| file | samples |
|---|---|
| `level_8_1_agent_foundations.jsonl` | 1,000 |
| [`web/level_8_1_agent_foundations_web.jsonl`](web/) | 1,000 |
| `level_8_2_task_decomposition_web.jsonl` | 1,000 |
| `level_8_2_deep_task_decomposition_web.jsonl` | 1,000 |

The `web/` variant specializes the same level for web-development environments
(35 categories across frontend, backend, data, tooling, debugging, testing, and
deployment reasoning). See [`web/README.md`](web/README.md). Its validator is
`web/validate_level_8_1_web.py`.

Level 8.2 (`level_8_2_task_decomposition_web.jsonl`, web specialization) teaches
decomposing web objectives into minimal ordered verifiable subtasks across 25
categories (goal decomposition, requirements, dependencies, prerequisites,
ordering, domain decompositions, risk, blocking, scope, verification, adaptive
replanning): 40 samples per category, difficulty targets met exactly
(100/200/350/250/100), adversarial-marker lower bound 99%. Generator and
validator live in [`decomp/`](decomp/); run
`python3 data/phase8/decomp/validate_level_8_2_web.py`.

Level 8.2 deep (`level_8_2_deep_task_decomposition_web.jsonl`) is the harder
companion: deep decomposition of realistic, ambiguous, cross-layer web work
across 36 categories (everything in the first 8.2 set plus authorization,
monorepo, migration, integration, unknown-information, backward-compatibility,
regression, architecture, state-management, accessibility, responsive-design,
and dependency-upgrade decomposition). It teaches the full chain
GOAL → REQUIREMENTS → UNKNOWN INFO → SYSTEM BOUNDARIES → SUBGOALS →
DEPENDENCIES → PREREQUISITES → ORDER → PARALLELISM → IMPLEMENTATION →
VERIFICATION → CONTINGENCIES → REPLANNING with twenty named reasoning
challenges (hidden dependencies, UI-needs-missing-API-data, migration-before-
code, vague bug reports, shared prerequisites, parallel-vs-sequential,
architecture conflicts, inspection-first, over/under-decomposition, backward
compat, production-data awareness, shared-component regression, auth vs authz,
multi-origin bugs, build-gated deploy, behavior-preserving refactor, and
monolith/modular/monorepo-aware decomposition). Difficulty is a STRING from
{easy, medium, hard, expert} with exact targets 100/250/400/250 favoring
hard+expert; per-category counts 27-29. Measured markers: multi-layer 99.7%
(target ≥50%), missing-information recognition 50.1% (≥30%), adaptive/
conditional 62.7% (≥30%), substantive verification 99.0% (≥25%), scope-control
59.7% (≥20%), adversarial realism 51.4% (≥40%). Semantic dedup: max instruction
Jaccard 0.567 within file, 0.412 against the first 8.2 file (0 pairs > 0.60).
Generator and validator live in [`deep/`](deep/); run
`python3 data/phase8/deep/d2validate.py`.

One JSON object per line, UTF-8, ASCII-only field values, no blank lines, single trailing newline.

Validator:

```bash
python3 data/phase8/validate_level_8_1.py
```

Current result: PASS — 1,000 objects, 0 exact duplicates, 0 near-duplicate instructions
(Jaccard over stopword- and glue-stripped word sets, threshold 0.62), 0 answers repeated
more than twice.

## Purpose

Teach a coding model the reasoning loop required for autonomous software agents:

UNDERSTAND → INSPECT → PLAN → ACT → OBSERVE → EVALUATE → CONTINUE / REVISE / STOP

Samples are state-based: most present a compact repository or environment state plus
observations and ask what the agent should do (or conclude) next. The dataset trains
OBSERVATION → DECISION → ACTION → RESULT → UPDATED DECISION rather than
question → code-answer.

## Schema

Every line has exactly these fields, in this order:

| field         | type   | meaning                                                        |
|---------------|--------|----------------------------------------------------------------|
| `instruction` | string | Self-contained scenario, environment state, and request         |
| `reasoning`   | string | 3-7 sentences of pedagogical rationale, no chain-of-thought     |
| `answer`      | string | The defensible next action, decision, or conclusion             |
| `category`    | string | One of the 25 labels below                                      |
| `difficulty`  | int    | 1-5                                                             |

## Categories (40 samples each)

task_understanding, requirement_extraction, constraint_identification,
information_gap_detection, observation_before_action, environment_inspection,
next_action_selection, tool_selection, action_sequencing, plan_vs_action,
state_tracking, goal_tracking, observation_vs_assumption,
action_result_interpretation, success_detection, failure_detection, plan_revision,
recovery_reasoning, stopping_conditions, verification, unnecessary_action_detection,
risk_aware_action, dependency_awareness, context_management, agent_loop_reasoning.

## Difficulty distribution

| level | share | notes |
|---|---|---|
| 1 | 100 (10%) | direct single-step reasoning |
| 2 | 200 (20%) | one inference beyond surface |
| 3 | 350 (35%) | evidence-guided decisions |
| 4 | 250 (25%) | multi-signal weighing, tradeoffs |
| 5 | 100 (10%) | competing hypotheses, state tracking, safest-path selection |

Difficulty comes from reasoning complexity, not verbosity: level-5 items present
several observations, competing hypotheses, or constraint conflicts and ask for the
single discriminating probe or the safest defensible order.

## Adversarial coverage

Validator lower bound: 58% of samples carry adversarial phrasing (premature-action
warnings, false-green traps, unverified-success flags, clarification branches).
Adversarial situations embedded across the set include: commands that succeed while
the task remains incomplete, tests passing while requirements stay unverified,
wrong initial hypotheses, user-pointed files that are not the real fault site,
symptoms that only mirror a deeper cause, existing implementations that already
solve the ask, dependency drift masquerading as code bugs, and cases where the
defensible answer is to stop, ask, or gather evidence.

## Generation provenance

Built by a curated archetype-and-pool synthesizer (`gen.py`, `pools.py`,
`frames_*.py`) covering 9 question archetypes per category (225 distinct concepts),
instantiated over 60 projects spanning 13 language ecosystems, 40 user requests,
48 observations, 40 error signatures, 20 completed-action states, 15 result types,
and 15 hypotheses. The emitter enforces uniqueness (exact and Jaccard),
per-(frame, project) non-repetition, exact-answer non-repetition, ASCII/quoting
rules, reasoning length 3-7 sentences, and the exact category/difficulty targets
before writing the file. Regenerate with `python3 gen.py` (deterministic, seeded).
