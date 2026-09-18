# Dataset-

Synthetic instruction-tuning datasets.

## Contents

- [`data/phase1/`](data/phase1/) — Phase 1: General Intelligence Foundation
  - `level_1_2_critical_causal_reasoning.jsonl` — 500 samples on critical and causal
    reasoning (confounding, interventions, counterfactuals, evidence quality, causal
    chains, bias, temporal reasoning, regression to the mean, uncertainty).
  - `level_1_2_critical_causal_reasoning_batch2.jsonl` — 200 further samples complementing
    the first batch, with no reused scenario, phrasing, or question template, weighted to
    difficulties 2-4.
  - Combined: **700 samples**. See [`data/phase1/README.md`](data/phase1/README.md) for the
    schema, distributions, and adversarial coverage.
- [`data/phase8/`](data/phase8/) — Phase 8: Agentic Autonomous Coding
  - `level_8_1_agent_foundations.jsonl` — 1,000 samples on agent-loop reasoning
    (task understanding, inspect-before-act, next-action selection, observation vs
    assumption, success/failure detection, plan revision, stopping conditions,
    verification, and related agent disciplines) across 25 categories with
    difficulty 1-5 and heavy adversarial coverage.
  - `web/level_8_1_agent_foundations_web.jsonl` — 1,000 further samples, the same
    level specialized for web development (35 categories: frontend, backend,
    data, tooling, debugging, testing, deployment, integration).
  - `level_8_2_task_decomposition_web.jsonl` — Level 8.2, 1,000 web samples on
    task decomposition (goal → requirements → subgoals → dependencies → order →
    execution → verification) across 25 categories with difficulty 1-5.
  - See [`data/phase8/README.md`](data/phase8/README.md) for the schema,
    distributions, and adversarial coverage.

## Validation

```
python3 data/phase1/validate_level_1_2.py
python3 data/phase8/validate_level_8_1.py
python3 data/phase8/web/validate_level_8_1_web.py
python3 data/phase8/decomp/validate_level_8_2_web.py
```

Checks each file's line count, JSON validity, the exact field set, allowed category values,
difficulty range, reasoning length in sentences, duplicate and near-duplicate scenarios, and
cross-file near-duplicates between the two batches. Prints the category and difficulty
distributions plus adversarial coverage counts.
